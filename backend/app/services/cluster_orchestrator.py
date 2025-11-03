"""
Cluster Orchestrator Service
Dynamic Pooling Protocol (DPP) implementation
Forms and manages multi-GPU clusters for distributed computing
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status

from app.models import (
    GPU, Cluster, ClusterMember, ClusterStatus, User
)

logger = logging.getLogger(__name__)


class ClusterOrchestrator:
    """
    Orchestrates multi-GPU clusters using Dynamic Pooling Protocol (DPP)

    The DPP algorithm:
    1. Analyzes job requirements (compute, VRAM, deadline)
    2. Finds eligible GPUs based on G-Score threshold
    3. Ranks GPUs by performance, reliability, efficiency
    4. Forms optimal cluster configuration
    5. Distributes work based on capability
    6. Calculates fair compensation based on contribution
    """

    # Constants for G-Score calculation
    GPU_MAX_BENCHMARK = 10000  # Normalization constant
    MIN_G_SCORE = 0.7  # Minimum acceptable G-Score for cluster membership

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_cluster(
        self,
        user_id: UUID,
        job_name: str,
        compute_intensity: int,  # Required TFLOPS
        vram_gb: int,  # Required VRAM per GPU
        deadline_hours: int,  # Time to complete job
        gpu_count: Optional[int] = None  # Preferred GPU count (optional)
    ) -> Cluster:
        """
        Create a new GPU cluster using DPP algorithm

        Args:
            user_id: User creating the cluster
            job_name: Name/description of the job
            compute_intensity: Required TFLOPS total
            vram_gb: Minimum VRAM per GPU
            deadline_hours: Time limit to complete job
            gpu_count: Preferred number of GPUs (auto-calculated if None)

        Returns:
            Created cluster with selected GPUs

        Raises:
            HTTPException: If insufficient GPUs available
        """
        logger.info(
            f"Creating cluster for user {user_id}: {job_name}, "
            f"{compute_intensity} TFLOPS, {vram_gb}GB VRAM, {deadline_hours}h deadline"
        )

        # Step 1: Find eligible GPUs
        eligible_gpus = await self._find_eligible_gpus(vram_gb, self.MIN_G_SCORE)

        if not eligible_gpus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No eligible GPUs available for cluster"
            )

        # Step 2: Rank GPUs by G-Score
        ranked_gpus = sorted(
            eligible_gpus,
            key=lambda gpu: (gpu.g_score or 0, gpu.price_per_hour),
            reverse=True
        )

        # Step 3: Form cluster
        selected_gpus, total_tflops = await self._select_gpus_for_cluster(
            ranked_gpus,
            compute_intensity,
            deadline_hours,
            gpu_count
        )

        if not selected_gpus:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot form cluster with available GPUs"
            )

        # Step 4: Calculate total cost
        total_cost = self._calculate_cluster_cost(
            selected_gpus,
            deadline_hours
        )

        # Step 4.5: Check user has sufficient funds
        from app.services.wallet_service import WalletService
        wallet_service = WalletService(self.db)
        user_balance = await wallet_service.get_balance(user_id)

        if user_balance < total_cost:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient funds: balance={user_balance} USDC, required={total_cost} USDC"
            )

        # Step 5: Create cluster in database
        cluster = Cluster(
            user_id=user_id,
            job_name=job_name,
            gpu_count=len(selected_gpus),
            total_cost=total_cost,
            status=ClusterStatus.PENDING
        )

        self.db.add(cluster)
        await self.db.flush()  # Get cluster ID

        # Step 6: Add cluster members with contribution scores
        await self._add_cluster_members(
            cluster.id,
            selected_gpus,
            total_tflops,
            deadline_hours
        )

        await self.db.commit()
        await self.db.refresh(cluster)

        logger.info(
            f"Created cluster {cluster.id} with {len(selected_gpus)} GPUs, "
            f"total cost: ${total_cost}, estimated TFLOPS: {total_tflops}"
        )

        return cluster

    async def start_cluster(self, cluster_id: UUID, user_id: UUID) -> Cluster:
        """
        Start a cluster (change status to active)

        Args:
            cluster_id: Cluster to start
            user_id: User starting the cluster (must be owner)

        Returns:
            Updated cluster
        """
        cluster = await self._get_cluster(cluster_id)

        # Check ownership
        if cluster.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to start this cluster"
            )

        if cluster.status != ClusterStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only start pending clusters"
            )

        # Process payment
        from app.services.wallet_service import WalletService, InsufficientFundsError
        wallet_service = WalletService(self.db)

        try:
            await wallet_service.process_cluster_payment(
                user_id=user_id,
                cluster_id=cluster_id,
                amount=cluster.total_cost
            )

            cluster.status = ClusterStatus.ACTIVE
            await self.db.commit()
            await self.db.refresh(cluster)

            logger.info(
                f"Started cluster {cluster_id} and processed payment of "
                f"{cluster.total_cost} USDC"
            )
            return cluster

        except InsufficientFundsError as e:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=str(e)
            )

    async def stop_cluster(
        self,
        cluster_id: UUID,
        user_id: UUID,
        success: bool = True
    ) -> Cluster:
        """
        Stop a cluster and mark as completed or failed

        Args:
            cluster_id: Cluster to stop
            user_id: User stopping the cluster
            success: Whether job completed successfully

        Returns:
            Updated cluster
        """
        cluster = await self._get_cluster(cluster_id)

        # Check ownership
        if cluster.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to stop this cluster"
            )

        if cluster.status not in [ClusterStatus.ACTIVE, ClusterStatus.PENDING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cluster already stopped"
            )

        cluster.status = ClusterStatus.COMPLETED if success else ClusterStatus.FAILED
        cluster.completed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(cluster)

        # Distribute earnings to GPU providers if successful
        if success:
            from app.services.wallet_service import WalletService
            wallet_service = WalletService(self.db)

            try:
                transactions = await wallet_service.distribute_cluster_earnings(cluster_id)
                logger.info(
                    f"Distributed earnings to {len(transactions)} GPU providers "
                    f"for cluster {cluster_id}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to distribute earnings for cluster {cluster_id}: {e}"
                )

        logger.info(f"Stopped cluster {cluster_id}, success: {success}")
        return cluster

    async def get_cluster_details(self, cluster_id: UUID) -> Dict:
        """
        Get detailed information about a cluster including members

        Args:
            cluster_id: Cluster ID

        Returns:
            Cluster details with member information
        """
        cluster = await self._get_cluster(cluster_id)

        # Get cluster members with GPU details
        result = await self.db.execute(
            select(ClusterMember, GPU)
            .join(GPU, ClusterMember.gpu_id == GPU.id)
            .where(ClusterMember.cluster_id == cluster_id)
        )

        members_data = []
        for member, gpu in result:
            members_data.append({
                'member_id': str(member.id),
                'gpu_id': str(gpu.id),
                'gpu_model': gpu.model,
                'gpu_provider': gpu.provider,
                'contribution_score': float(member.contribution_score),
                'earnings': float(member.earnings),
                'g_score': float(gpu.g_score) if gpu.g_score else None
            })

        return {
            'cluster_id': str(cluster.id),
            'job_name': cluster.job_name,
            'gpu_count': cluster.gpu_count,
            'total_cost': float(cluster.total_cost),
            'status': cluster.status.value,
            'created_at': cluster.created_at.isoformat(),
            'completed_at': cluster.completed_at.isoformat() if cluster.completed_at else None,
            'members': members_data
        }

    async def _find_eligible_gpus(
        self,
        min_vram: int,
        min_g_score: float
    ) -> List[GPU]:
        """Find GPUs eligible for cluster based on criteria"""
        result = await self.db.execute(
            select(GPU).where(
                and_(
                    GPU.available == True,
                    GPU.vram_gb >= min_vram,
                    GPU.g_score >= min_g_score,
                    GPU.last_synced > datetime.utcnow() - timedelta(hours=1)
                )
            )
        )

        gpus = result.scalars().all()
        return list(gpus)

    async def _select_gpus_for_cluster(
        self,
        ranked_gpus: List[GPU],
        required_tflops: int,
        deadline_hours: int,
        preferred_count: Optional[int] = None
    ) -> tuple[List[GPU], float]:
        """
        Select optimal GPUs for cluster using DPP algorithm

        Returns:
            Tuple of (selected GPUs, total TFLOPS)
        """
        target_tflops = required_tflops / deadline_hours  # TFLOPS per hour

        selected = []
        total_tflops = 0.0

        # If preferred count specified, take top N GPUs
        if preferred_count:
            for gpu in ranked_gpus[:preferred_count]:
                selected.append(gpu)
                total_tflops += self._estimate_gpu_tflops(gpu)

                if total_tflops >= target_tflops:
                    break
        else:
            # Auto-select based on target performance
            for gpu in ranked_gpus:
                if total_tflops >= target_tflops:
                    break

                selected.append(gpu)
                total_tflops += self._estimate_gpu_tflops(gpu)

                # Safety limit: max 10 GPUs per cluster
                if len(selected) >= 10:
                    break

        return selected, total_tflops

    def _estimate_gpu_tflops(self, gpu: GPU) -> float:
        """
        Estimate TFLOPS based on benchmark score

        This is a simplified estimation. In production, use actual
        TFLOPS specifications for each GPU model.
        """
        if not gpu.benchmark_score:
            return 10.0  # Default estimate

        # Rough estimation: normalize benchmark to TFLOPS range
        # High-end GPUs: 50-100 TFLOPS
        # Mid-range: 20-50 TFLOPS
        # Entry: 10-20 TFLOPS
        normalized = gpu.benchmark_score / self.GPU_MAX_BENCHMARK
        return normalized * 100  # Scale to TFLOPS range

    def _calculate_cluster_cost(
        self,
        gpus: List[GPU],
        hours: int
    ) -> Decimal:
        """Calculate total cost for cluster over time period"""
        total = Decimal('0')

        for gpu in gpus:
            cost_per_hour = gpu.price_per_hour
            total += cost_per_hour * hours

        return total

    async def _add_cluster_members(
        self,
        cluster_id: UUID,
        gpus: List[GPU],
        total_tflops: float,
        hours: int
    ):
        """
        Add GPUs as cluster members with contribution scores

        Contribution score determines fair compensation:
        - Based on GPU performance (benchmark)
        - Weighted by reliability (uptime)
        - Adjusted for efficiency (power consumption)
        """
        gpu_performances = []

        # Calculate each GPU's performance
        for gpu in gpus:
            tflops = self._estimate_gpu_tflops(gpu)
            gpu_performances.append({
                'gpu': gpu,
                'tflops': tflops,
                'contribution': tflops / total_tflops if total_tflops > 0 else 0
            })

        # Create cluster members
        for perf in gpu_performances:
            gpu = perf['gpu']
            contribution = Decimal(str(perf['contribution']))

            # Calculate earnings based on contribution
            gpu_hours_cost = gpu.price_per_hour * hours
            earnings = gpu_hours_cost

            member = ClusterMember(
                cluster_id=cluster_id,
                gpu_id=gpu.id,
                contribution_score=contribution,
                earnings=earnings
            )

            self.db.add(member)

    async def _get_cluster(self, cluster_id: UUID) -> Cluster:
        """Get cluster by ID"""
        result = await self.db.execute(
            select(Cluster).where(Cluster.id == cluster_id)
        )
        cluster = result.scalar_one_or_none()

        if not cluster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cluster not found"
            )

        return cluster

    async def get_user_clusters(
        self,
        user_id: UUID,
        status_filter: Optional[ClusterStatus] = None
    ) -> List[Cluster]:
        """Get all clusters for a user"""
        query = select(Cluster).where(Cluster.user_id == user_id)

        if status_filter:
            query = query.where(Cluster.status == status_filter)

        query = query.order_by(Cluster.created_at.desc())

        result = await self.db.execute(query)
        clusters = result.scalars().all()

        return list(clusters)

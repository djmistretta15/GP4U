"""
Cluster API Routes
Multi-GPU cluster management with DPP algorithm
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models import User, ClusterStatus
from app.schemas import ClusterCreate, Cluster as ClusterSchema
from app.services.cluster_orchestrator import ClusterOrchestrator

router = APIRouter()


@router.post("/", response_model=ClusterSchema, status_code=201)
async def create_cluster(
    cluster_data: ClusterCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new multi-GPU cluster using DPP algorithm

    The Dynamic Pooling Protocol (DPP):
    1. Analyzes job requirements
    2. Finds eligible GPUs (VRAM, G-Score threshold)
    3. Ranks by performance, reliability, efficiency
    4. Forms optimal cluster configuration
    5. Calculates fair compensation for each GPU

    Args:
        cluster_data: Job requirements
            - job_name: Description of the job
            - compute_intensity: Required TFLOPS
            - vram_gb: Minimum VRAM per GPU
            - deadline_hours: Time limit to complete
            - gpu_count: Preferred number of GPUs (optional)

    Returns:
        Created cluster with selected GPUs and pricing

    Example Request:
        ```json
        {
          "job_name": "LLM Training - GPT-3 Clone",
          "compute_intensity": 1000,
          "vram_gb": 40,
          "deadline_hours": 24,
          "gpu_count": 4
        }
        ```

    Raises:
        404: No eligible GPUs available
        400: Cannot form cluster with available resources
    """
    orchestrator = ClusterOrchestrator(db)

    cluster = await orchestrator.create_cluster(
        user_id=current_user.id,
        job_name=cluster_data.job_name,
        compute_intensity=cluster_data.compute_intensity,
        vram_gb=cluster_data.vram_gb,
        deadline_hours=cluster_data.deadline_hours,
        gpu_count=cluster_data.gpu_count
    )

    return cluster


@router.get("/my-clusters", response_model=List[ClusterSchema])
async def get_my_clusters(
    status: Optional[ClusterStatus] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all clusters for current user

    Query Parameters:
        status: Filter by cluster status (pending, active, completed, failed)

    Returns:
        List of user's clusters
    """
    orchestrator = ClusterOrchestrator(db)

    clusters = await orchestrator.get_user_clusters(
        user_id=current_user.id,
        status_filter=status
    )

    return clusters


@router.get("/{cluster_id}")
async def get_cluster_details(
    cluster_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed cluster information including all members

    Shows:
    - Cluster configuration
    - All member GPUs
    - Contribution scores
    - Earnings distribution
    - Status and timestamps

    Args:
        cluster_id: Cluster UUID

    Returns:
        Detailed cluster information

    Raises:
        404: Cluster not found
        403: Not authorized (not cluster owner)
    """
    orchestrator = ClusterOrchestrator(db)

    # Get cluster to check ownership
    cluster = await orchestrator._get_cluster(cluster_id)
    if cluster.user_id != current_user.id:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this cluster"
        )

    details = await orchestrator.get_cluster_details(cluster_id)
    return details


@router.post("/{cluster_id}/start", response_model=ClusterSchema)
async def start_cluster(
    cluster_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Start a cluster (activate pending cluster)

    Changes cluster status from PENDING to ACTIVE.
    Marks the official start time for billing.

    Args:
        cluster_id: Cluster to start

    Returns:
        Updated cluster with ACTIVE status

    Raises:
        400: Cluster not in pending state
        403: Not authorized
    """
    orchestrator = ClusterOrchestrator(db)

    cluster = await orchestrator.start_cluster(
        cluster_id=cluster_id,
        user_id=current_user.id
    )

    return cluster


@router.post("/{cluster_id}/stop", response_model=ClusterSchema)
async def stop_cluster(
    cluster_id: UUID,
    success: bool = Query(True, description="Whether job completed successfully"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Stop a cluster and mark as completed or failed

    Finalizes the cluster job and calculates final costs.

    Query Parameters:
        success: True for COMPLETED, False for FAILED

    Args:
        cluster_id: Cluster to stop

    Returns:
        Updated cluster with final status

    Raises:
        400: Cluster already stopped
        403: Not authorized
    """
    orchestrator = ClusterOrchestrator(db)

    cluster = await orchestrator.stop_cluster(
        cluster_id=cluster_id,
        user_id=current_user.id,
        success=success
    )

    return cluster


@router.get("/{cluster_id}/members")
async def get_cluster_members(
    cluster_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get cluster members (GPUs) with contribution scores

    Shows how work is distributed across GPUs and
    how earnings are calculated based on contribution.

    Args:
        cluster_id: Cluster UUID

    Returns:
        List of cluster members with details

    Raises:
        404: Cluster not found
        403: Not authorized
    """
    orchestrator = ClusterOrchestrator(db)

    # Check ownership
    cluster = await orchestrator._get_cluster(cluster_id)
    if cluster.user_id != current_user.id:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this cluster"
        )

    details = await orchestrator.get_cluster_details(cluster_id)
    return {
        "cluster_id": details['cluster_id'],
        "gpu_count": details['gpu_count'],
        "members": details['members']
    }


@router.get("/simulate/estimate")
async def simulate_cluster_estimate(
    compute_intensity: int = Query(..., description="Required TFLOPS", ge=1),
    vram_gb: int = Query(..., description="Minimum VRAM per GPU", ge=1),
    deadline_hours: int = Query(..., description="Time limit in hours", ge=1, le=168),
    gpu_count: Optional[int] = Query(None, description="Preferred GPU count", ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """
    Simulate cluster creation to estimate cost (no auth required)

    Useful for users to preview cluster pricing before creating.

    Query Parameters:
        compute_intensity: Required TFLOPS
        vram_gb: Minimum VRAM per GPU
        deadline_hours: Time limit (1-168 hours / 1 week max)
        gpu_count: Preferred number of GPUs (optional)

    Returns:
        Estimated cluster configuration and cost
    """
    orchestrator = ClusterOrchestrator(db)

    # Find eligible GPUs
    eligible = await orchestrator._find_eligible_gpus(
        min_vram=vram_gb,
        min_g_score=orchestrator.MIN_G_SCORE
    )

    if not eligible:
        return {
            "feasible": False,
            "message": "No eligible GPUs available with specified requirements"
        }

    # Rank GPUs
    ranked = sorted(
        eligible,
        key=lambda g: (g.g_score or 0, g.price_per_hour),
        reverse=True
    )

    # Select GPUs
    selected, total_tflops = await orchestrator._select_gpus_for_cluster(
        ranked,
        compute_intensity,
        deadline_hours,
        gpu_count
    )

    if not selected:
        return {
            "feasible": False,
            "message": "Cannot form cluster with available resources"
        }

    # Calculate cost
    total_cost = orchestrator._calculate_cluster_cost(selected, deadline_hours)

    return {
        "feasible": True,
        "gpu_count": len(selected),
        "estimated_tflops": total_tflops,
        "total_cost": float(total_cost),
        "cost_per_hour": float(total_cost / deadline_hours) if deadline_hours > 0 else 0,
        "gpus": [
            {
                "model": gpu.model,
                "provider": gpu.provider,
                "g_score": float(gpu.g_score) if gpu.g_score else None,
                "price_per_hour": float(gpu.price_per_hour)
            }
            for gpu in selected
        ]
    }

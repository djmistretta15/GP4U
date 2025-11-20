"""
MVP Integration Tests
Tests for GPU Lease Ledger endpoints
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_create_gpu():
    """Test GPU creation"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/gpus/?model=RTX%204090&vram_gb=24"
        )
        assert response.status_code == 201
        data = response.json()
        assert data["model"] == "RTX 4090"
        assert data["vram_gb"] == 24
        assert data["status"] == "available"
        assert "id" in data
        return data["id"]


@pytest.mark.asyncio
async def test_list_gpus():
    """Test listing GPUs"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/gpus/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_gpu_lifecycle():
    """Test complete GPU lifecycle with provenance"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create GPU
        create_response = await client.post(
            "/api/gpus/?model=RTX%203090&vram_gb=24"
        )
        assert create_response.status_code == 201
        gpu_id = create_response.json()["id"]
        
        # Get GPU details
        get_response = await client.get(f"/api/gpus/{gpu_id}")
        assert get_response.status_code == 200
        gpu = get_response.json()
        assert gpu["status"] == "available"
        
        # Update status to leased
        update_response = await client.patch(
            f"/api/gpus/{gpu_id}",
            json={"status": "leased"}
        )
        assert update_response.status_code == 200
        updated_gpu = update_response.json()
        assert updated_gpu["status"] == "leased"
        assert updated_gpu["available"] is False
        
        # Get provenance
        provenance_response = await client.get(
            f"/api/gpus/{gpu_id}/provenance"
        )
        assert provenance_response.status_code == 200
        events = provenance_response.json()
        assert len(events) >= 2  # registered + status_changed
        
        # Verify event types
        event_types = [e["event_type"] for e in events]
        assert "registered" in event_types
        assert "status_changed" in event_types


@pytest.mark.asyncio
async def test_blockchain_anchor():
    """Test blockchain anchor hashing"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create GPU to get events
        create_response = await client.post(
            "/api/gpus/?model=Test%20GPU&vram_gb=16"
        )
        gpu_id = create_response.json()["id"]
        
        # Get events
        provenance_response = await client.get(
            f"/api/gpus/{gpu_id}/provenance"
        )
        events = provenance_response.json()
        event_ids = [e["id"] for e in events]
        
        # Create anchor
        anchor_response = await client.post(
            "/api/anchors/hash",
            json={"event_ids": event_ids}
        )
        assert anchor_response.status_code == 200
        anchor = anchor_response.json()
        assert "hash" in anchor
        assert len(anchor["hash"]) == 64  # SHA256 hex length
        assert anchor["event_count"] == len(event_ids)


@pytest.mark.asyncio
async def test_status_transitions():
    """Test all status transitions"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create GPU
        create_response = await client.post(
            "/api/gpus/?model=Status%20Test&vram_gb=12"
        )
        gpu_id = create_response.json()["id"]
        
        statuses = ["leased", "maintenance", "available"]
        
        for status in statuses:
            response = await client.patch(
                f"/api/gpus/{gpu_id}",
                json={"status": status}
            )
            assert response.status_code == 200
            assert response.json()["status"] == status
        
        # Verify provenance has all transitions
        provenance = await client.get(f"/api/gpus/{gpu_id}/provenance")
        events = provenance.json()
        assert len(events) >= 4  # registered + 3 status changes

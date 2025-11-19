"""
Blockchain Anchor API
Simple stub for hashing event payloads (MVP)
"""
import hashlib
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models import ProvenanceEvent
from app.schemas import BlockchainAnchorRequest, BlockchainAnchorResponse

router = APIRouter()


@router.post("/hash", response_model=BlockchainAnchorResponse)
async def hash_events(
    request: BlockchainAnchorRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a blockchain anchor hash from provenance events.
    
    This is a simple stub that:
    1. Fetches the specified events
    2. Concatenates their payloads
    3. Returns a SHA256 hash
    
    In production, this would write to an actual blockchain.
    """
    # Fetch events
    result = await db.execute(
        select(ProvenanceEvent).where(
            ProvenanceEvent.id.in_(request.event_ids)
        )
    )
    events = result.scalars().all()
    
    if len(events) != len(request.event_ids):
        raise HTTPException(
            status_code=404,
            detail="One or more events not found"
        )
    
    # Build payload to hash
    payload_data = []
    for event in events:
        payload_data.append({
            "id": str(event.id),
            "gpu_id": str(event.gpu_id),
            "event_type": event.event_type.value,
            "payload": event.payload_json,
            "timestamp": event.created_at.isoformat()
        })
    
    # Create hash
    payload_str = json.dumps(payload_data, sort_keys=True)
    hash_digest = hashlib.sha256(payload_str.encode()).hexdigest()
    
    return BlockchainAnchorResponse(
        hash=hash_digest,
        event_count=len(events),
        timestamp=datetime.utcnow()
    )

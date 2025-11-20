"""
User Feedback API Routes
Collects user feedback for MVP validation
"""
from typing import Optional
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models import User

router = APIRouter()


class FeedbackCreate(BaseModel):
    """Feedback submission schema"""
    rating: int = Field(..., ge=1, le=5, description="1-5 star rating")
    feature: str = Field(..., description="Feature being rated (search, arbitrage, booking, etc.)")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional feedback text")
    page: Optional[str] = Field(None, description="Page where feedback was given")
    

class FeedbackResponse(BaseModel):
    """Feedback response schema"""
    id: UUID
    user_id: UUID
    rating: int
    feature: str
    comment: Optional[str]
    page: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback: FeedbackCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit user feedback
    
    Used for MVP validation to test hypotheses about user satisfaction.
    
    Args:
        feedback: Rating (1-5), feature name, optional comment
        current_user: Authenticated user
        
    Returns:
        Created feedback record
    """
    from app.models import UserFeedback
    import uuid
    
    feedback_record = UserFeedback(
        id=uuid.uuid4(),
        user_id=current_user.id,
        rating=feedback.rating,
        feature=feedback.feature,
        comment=feedback.comment,
        page=feedback.page,
        created_at=datetime.utcnow()
    )
    
    db.add(feedback_record)
    await db.commit()
    await db.refresh(feedback_record)
    
    # Log feedback for analytics
    import structlog
    logger = structlog.get_logger()
    logger.info(
        "user.feedback",
        component="feedback",
        action="submit",
        user_id=str(current_user.id),
        rating=feedback.rating,
        feature=feedback.feature,
        page=feedback.page,
        has_comment=bool(feedback.comment)
    )
    
    return feedback_record


@router.get("/stats")
async def get_feedback_stats(
    feature: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get aggregated feedback statistics
    
    Args:
        feature: Optional filter by feature name
        
    Returns:
        Average rating, count, distribution
    """
    from app.models import UserFeedback
    from sqlalchemy import select, func
    
    query = select(
        func.avg(UserFeedback.rating).label("avg_rating"),
        func.count(UserFeedback.id).label("total_count"),
        func.count(func.distinct(UserFeedback.user_id)).label("unique_users")
    )
    
    if feature:
        query = query.where(UserFeedback.feature == feature)
    
    result = await db.execute(query)
    stats = result.first()
    
    # Get rating distribution
    dist_query = select(
        UserFeedback.rating,
        func.count(UserFeedback.id).label("count")
    ).group_by(UserFeedback.rating)
    
    if feature:
        dist_query = dist_query.where(UserFeedback.feature == feature)
    
    dist_result = await db.execute(dist_query)
    distribution = {row[0]: row[1] for row in dist_result}
    
    return {
        "average_rating": float(stats[0]) if stats[0] else 0,
        "total_feedback": stats[1],
        "unique_users": stats[2],
        "rating_distribution": distribution
    }

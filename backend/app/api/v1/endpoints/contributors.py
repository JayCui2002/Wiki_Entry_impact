"""
Contributors API endpoints
贡献者相关的API端点
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional, Dict, Any
import structlog
import asyncio
from datetime import datetime

from app.core.database import get_db
from app.models.contributor import Contributor
from app.services.impact_calculator import ImpactCalculator, ContributionMetrics
from app.core.redis_client import redis_client

logger = structlog.get_logger()
router = APIRouter()

# Dependency to get an instance of the ImpactCalculator
def get_impact_calculator() -> ImpactCalculator:
    """
    Dependency to provide an instance of the ImpactCalculator.
    This ensures a new instance is created per request if needed,
    or can be adapted to use a singleton pattern with caching.
    """
    return ImpactCalculator()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_contributors(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=2000, description="Number of records to return"),
    language: Optional[str] = Query(None, description="Filter by primary language"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    min_impact_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum impact score"),
    sort_by: str = Query("overall_impact_score", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db),
    impact_calculator: ImpactCalculator = Depends(get_impact_calculator)
):
    """
    Get list of contributors with filtering and pagination
    获取带过滤和分页的贡献者列表
    """
    logger.info(f"Fetching contributors with filters: language={language}, is_active={is_active}")
    
    try:
        # Build query with filters
        query = select(Contributor)
        
        if language:
            query = query.where(Contributor.primary_language == language)
        
        if is_active is not None:
            query = query.where(Contributor.is_active == is_active)
        
        if min_impact_score is not None:
            query = query.where(Contributor.overall_impact_score >= min_impact_score)  # type: ignore
        
        # Apply sorting
        sort_column = getattr(Contributor, sort_by, Contributor.overall_impact_score)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())  # type: ignore
        else:
            query = query.order_by(sort_column.asc())  # type: ignore
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        contributors = result.scalars().all()
        
        # Convert to response format
        response_data = []
        for contributor in contributors:
            data = contributor.to_dict(include_sensitive=False)
            # Add computed fields
            data["contribution_type"] = impact_calculator.classify_contributor_type(
                ContributionMetrics.from_contributor(contributor)
            )
            response_data.append(data)
        
        return response_data
        
    except Exception as e:
        logger.error("Error fetching contributors", error=e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{contributor_id}", response_model=Dict[str, Any])
async def get_contributor(
    contributor_id: int = Path(..., description="Contributor ID"),
    include_detailed: bool = Query(False, description="Include detailed metrics"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific contributor
    获取特定贡献者的详细信息
    """
    logger.info(f"Fetching contributor {contributor_id}")
    
    try:
        # Fetch contributor
        query = select(Contributor).where(Contributor.id == contributor_id)
        result = await db.execute(query)
        contributor = result.scalar_one_or_none()
        
        if not contributor:
            raise HTTPException(status_code=404, detail="Contributor not found")
        
        # Convert to response format
        data = contributor.to_dict(include_sensitive=True)
        
        if include_detailed:
            # Add detailed impact analysis
            if redis_client.is_connected:
                cache_key = f"impact:contributor:{contributor_id}"
                cached_metrics = await redis_client.get(cache_key)
                
                if cached_metrics:
                    data["detailed_metrics"] = cached_metrics
                else:
                    data["detailed_metrics"] = {
                        "message": "Detailed metrics not available in cache. Run impact analysis first."
                    }
            else:
                data["detailed_metrics"] = {
                    "message": "Detailed metrics not available (Redis disabled). Run impact analysis first."
                }
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching contributor {contributor_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{contributor_id}/impact", response_model=Dict[str, Any])
async def get_contributor_impact(
    contributor_id: int = Path(..., description="Contributor ID"),
    recalculate: bool = Query(False, description="Force recalculation of metrics"),
    db: AsyncSession = Depends(get_db),
    impact_calculator: ImpactCalculator = Depends(get_impact_calculator)
):
    """
    Get impact metrics for a specific contributor
    获取特定贡献者的影响指标
    """
    logger.info(f"Fetching impact metrics for contributor {contributor_id}")
    
    try:
        # Fetch contributor
        query = select(Contributor).where(Contributor.id == contributor_id)
        result = await db.execute(query)
        contributor = result.scalar_one_or_none()
        
        if not contributor:
            raise HTTPException(status_code=404, detail="Contributor not found")
        
        cache_key = f"impact:contributor:{contributor_id}"
        
        if not recalculate and redis_client.is_connected:
            # Try to get from cache first
            cached_metrics = await redis_client.get(cache_key)
            if cached_metrics:
                return {
                    "contributor_id": contributor_id,
                    "metrics": cached_metrics,
                    "cached": True,
                    "timestamp": cached_metrics.get("calculated_at")
                }
        
        # If not cached or recalculation requested, calculate metrics
        # Note: In a real implementation, you would fetch actual edit history
        # For this demo, we'll use placeholder data
        edit_history = []  # This would be populated from database
        discussion_data = {}  # This would be populated from Wikipedia API
        
        metrics = await impact_calculator.calculate_comprehensive_impact(
            contributor, edit_history, discussion_data
        )
        
        return {
            "contributor_id": contributor_id,
            "metrics": metrics.__dict__,
            "cached": False,
            "timestamp": func.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating impact for contributor {contributor_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search/", response_model=List[Dict[str, Any]])
async def search_contributors(
    query: str = Query(..., min_length=2, description="Search query"),
    search_type: str = Query("username", regex="^(username|display_name|all)$"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Search contributors by username or display name
    按用户名或显示名称搜索贡献者
    """
    logger.info(f"Searching contributors with query: {query}")
    
    try:
        # Build search query
        search_filter = None
        
        if search_type == "username":
            search_filter = Contributor.wikipedia_username.ilike(f"%{query}%")  # type: ignore
        elif search_type == "display_name":
            search_filter = Contributor.display_name.ilike(f"%{query}%")  # type: ignore
        else:  # search_type == "all"
            search_filter = or_(
                Contributor.wikipedia_username.ilike(f"%{query}%"),  # type: ignore
                Contributor.display_name.ilike(f"%{query}%")  # type: ignore
            )
        
        db_query = select(Contributor).where(
            and_(search_filter, Contributor.is_active == True)
        ).order_by(
            Contributor.overall_impact_score.desc()  # type: ignore
        ).limit(limit)
        
        result = await db.execute(db_query)
        contributors = result.scalars().all()
        
        # Convert to response format
        response_data = []
        for contributor in contributors:
            data = contributor.to_dict(include_sensitive=False)
            response_data.append(data)
            
        return response_data
        
    except Exception as e:
        logger.error(f"Error searching contributors: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats/overview", response_model=Dict[str, Any])
async def get_contributor_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get overview statistics about contributors
    获取贡献者的概览统计数据
    """
    logger.info("Fetching contributor statistics")
    
    try:
        # Total contributors
        total_contributors_query = select(func.count(Contributor.id))
        total_contributors = await db.scalar(total_contributors_query)
        
        # Active contributors
        active_contributors_query = select(func.count(Contributor.id)).where(Contributor.is_active == True)
        active_contributors = await db.scalar(active_contributors_query)
        
        # Average impact score
        avg_impact_query = select(func.avg(Contributor.overall_impact_score))
        avg_impact_score = await db.scalar(avg_impact_query)
        
        # Top 5 contributors by impact
        top_contributors_query = select(
            Contributor.display_name, Contributor.overall_impact_score
        ).order_by(
            Contributor.overall_impact_score.desc()
        ).limit(5)
        top_contributors_result = await db.execute(top_contributors_query)
        top_contributors = [
            {"name": row[0], "score": row[1]} for row in top_contributors_result.all()
        ]
        
        return {
            "total_contributors": total_contributors,
            "active_contributors": active_contributors,
            "average_impact_score": round(avg_impact_score, 2) if avg_impact_score else 0,
            "top_contributors": top_contributors,
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{contributor_id}/calculate-impact", response_model=Dict[str, Any])
async def trigger_impact_calculation(
    contributor_id: int = Path(..., description="Contributor ID"),
    force_refresh: bool = Query(False, description="Force refresh from Wikipedia API"),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger a background task to calculate impact for a contributor.
    This would typically be handled by a Celery worker.
    """
    logger.info(f"Triggering impact calculation for contributor {contributor_id}")
    
    # In a real application, you would dispatch a background task:
    # calculate_impact_task.delay(contributor_id, force_refresh)
    
    return {
        "message": "Impact calculation task dispatched",
        "contributor_id": contributor_id,
        "detail": "This is a mock endpoint. In production, this would trigger a Celery task."
    }


@router.get("/compare/", response_model=Dict[str, Any])
async def compare_contributors(
    contributor_ids: str = Query(..., description="Comma-separated contributor IDs"),
    metrics: str = Query("all", description="Metrics to compare (all, impact, activity, quality)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare multiple contributors based on selected metrics
    根据选定指标比较多个贡献者
    """
    try:
        ids = [int(id.strip()) for id in contributor_ids.split(",")]
        if len(ids) < 2 or len(ids) > 5:
            raise HTTPException(400, "Please provide 2 to 5 contributor IDs")
        
        # This is a mock implementation. A real one would fetch and format data.
        return {
            "message": "Comparison data would be generated here.",
            "compared_contributors": ids,
            "metrics_requested": metrics
        }
        
    except ValueError:
        raise HTTPException(400, "Invalid contributor IDs provided")
    except Exception as e:
        logger.error(f"Error comparing contributors: {e}")
        raise HTTPException(500, "Internal server error")
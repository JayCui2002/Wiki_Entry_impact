"""
Contributors API endpoints
贡献者相关的API端点
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional, Dict, Any
import structlog

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
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
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
            # The following block is ignored due to linter limitations with SQLAlchemy models
            data["contribution_type"] = impact_calculator.classify_contributor_type(  # type: ignore
                ContributionMetrics(
                    contributor_id=contributor.id,  # type: ignore
                    total_volume_score=0,  # These would come from actual calculations
                    additive_score=contributor.additive_contribution_score,  # type: ignore
                    maintenance_score=contributor.maintenance_contribution_score,  # type: ignore
                    discussion_impact_score=contributor.discussion_impact_score,  # type: ignore
                    quality_score=0,
                    collaboration_score=contributor.collaboration_network_score,  # type: ignore
                    temporal_consistency_score=0,
                    overall_impact_score=contributor.overall_impact_score  # type: ignore
                )
            )
            response_data.append(data)
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error fetching contributors: {e}")
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
    获取贡献者概览统计信息
    """
    logger.info("Fetching contributor statistics")
    
    try:
        # Check cache first
        cache_key = "stats:contributors:overview"
        cached_stats = await redis_client.get(cache_key)
        
        if cached_stats:
            return cached_stats
        
        # Calculate statistics
        total_contributors = await db.scalar(
            select(func.count(Contributor.id))
        )
        
        active_contributors = await db.scalar(
            select(func.count(Contributor.id)).where(Contributor.is_active == True)
        )
        
        avg_impact_score = await db.scalar(
            select(func.avg(Contributor.overall_impact_score))
        )
        
        top_contributors = await db.execute(
            select(Contributor)
            .where(Contributor.is_active == True)
            .order_by(Contributor.overall_impact_score.desc())  # type: ignore
            .limit(10)
        )
        top_contributors_list = top_contributors.scalars().all()
        
        # Language distribution
        language_stats = await db.execute(
            select(
                Contributor.primary_language,
                func.count(Contributor.id).label("count")
            )
            .group_by(Contributor.primary_language)
            .order_by(func.count(Contributor.id).desc())
        )
        language_distribution = {
            row.primary_language: row.count 
            for row in language_stats.fetchall()
        }
        
        # Contribution type distribution
        content_creators = await db.scalar(
            select(func.count(Contributor.id))
            .where(Contributor.additive_contribution_score > Contributor.maintenance_contribution_score)  # type: ignore
        )
        
        maintainers = await db.scalar(
            select(func.count(Contributor.id))
            .where(Contributor.maintenance_contribution_score > Contributor.additive_contribution_score)  # type: ignore
        )
        
        total_contributors_val = total_contributors or 0
        content_creators_val = content_creators or 0
        maintainers_val = maintainers or 0

        stats = {
            "total_contributors": total_contributors,
            "active_contributors": active_contributors,
            "average_impact_score": round(float(avg_impact_score or 0), 2),
            "top_contributors": [
                contributor.to_dict(include_sensitive=False) 
                for contributor in top_contributors_list
            ],
            "language_distribution": language_distribution,
            "contribution_types": {
                "content_creators": content_creators_val,
                "maintainers": maintainers_val,
                "balanced": total_contributors_val - content_creators_val - maintainers_val
            },
            "generated_at": func.now()
        }
        
        # Cache for 30 minutes
        await redis_client.set(cache_key, stats, expire=1800)
        
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching contributor statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{contributor_id}/calculate-impact", response_model=Dict[str, Any])
async def trigger_impact_calculation(
    contributor_id: int = Path(..., description="Contributor ID"),
    force_refresh: bool = Query(False, description="Force refresh from Wikipedia API"),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger impact calculation for a specific contributor
    触发特定贡献者的影响计算
    """
    logger.info(f"Triggering impact calculation for contributor {contributor_id}")
    
    try:
        # Fetch contributor
        query = select(Contributor).where(Contributor.id == contributor_id)
        result = await db.execute(query)
        contributor = result.scalar_one_or_none()
        
        if not contributor:
            raise HTTPException(status_code=404, detail="Contributor not found")
        
        # In a real implementation, this would trigger background processing
        # For now, we'll return a task ID placeholder
        task_id = f"impact_calc_{contributor_id}_{func.now()}"
        
        # Store task info in cache
        await redis_client.set(
            f"task:{task_id}",
            {
                "task_id": task_id,
                "contributor_id": contributor_id,
                "status": "queued",
                "created_at": func.now(),
                "force_refresh": force_refresh
            },
            expire=3600
        )
        
        return {
            "task_id": task_id,
            "contributor_id": contributor_id,
            "status": "queued",
            "message": "Impact calculation has been queued for processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering impact calculation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/compare/", response_model=Dict[str, Any])
async def compare_contributors(
    contributor_ids: str = Query(..., description="Comma-separated contributor IDs"),
    metrics: str = Query("all", description="Metrics to compare (all, impact, activity, quality)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare multiple contributors across different metrics
    比较多个贡献者的不同指标
    """
    logger.info(f"Comparing contributors: {contributor_ids}")
    
    try:
        # Parse contributor IDs
        try:
            ids = [int(id.strip()) for id in contributor_ids.split(",")]
            if len(ids) > 10:  # Limit comparison to 10 contributors
                raise HTTPException(status_code=400, detail="Maximum 10 contributors can be compared")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid contributor IDs format")
        
        # Fetch contributors
        query = select(Contributor).where(Contributor.id.in_(ids))
        result = await db.execute(query)
        contributors = {c.id: c for c in result.scalars().all()}
        
        # Check if all contributors were found
        missing_ids = set(ids) - set(contributors.keys())  # type: ignore
        if missing_ids:
            raise HTTPException(
                status_code=404, 
                detail=f"Contributors not found: {list(missing_ids)}"
            )
        
        # Prepare comparison data
        comparison_data = {
            "contributors": {},
            "metrics_summary": {},
            "rankings": {}
        }
        
        # Get metrics for each contributor
        for contributor_id, contributor in contributors.items():
            contributor_data = contributor.to_dict(include_sensitive=False)
            
            # Add cached impact metrics if available
            cache_key = f"impact:contributor:{contributor_id}"
            cached_metrics = await redis_client.get(cache_key)
            if cached_metrics:
                contributor_data["detailed_metrics"] = cached_metrics
            
            comparison_data["contributors"][contributor_id] = contributor_data
        
        # Calculate rankings
        if metrics in ["all", "impact"]:
            impact_ranking = sorted(
                contributors.items(),
                key=lambda x: x[1].overall_impact_score,  # type: ignore
                reverse=True
            )
            comparison_data["rankings"]["impact"] = [
                {"contributor_id": c_id, "rank": idx + 1, "score": c.overall_impact_score}
                for idx, (c_id, c) in enumerate(impact_ranking)
            ]
        
        return comparison_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing contributors: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 
"""
Analytics endpoints
分析相关的API端点
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import structlog

from app.core.database import get_db
from app.models.contributor import Contributor

logger = structlog.get_logger()
router = APIRouter()

@router.get("/trends")
async def get_impact_trends(db: AsyncSession = Depends(get_db)):
    """Return average impact scores grouped by month."""
    logger.info("Fetching impact trends")

    try:
        query = (
            select(
                func.date_trunc("month", Contributor.last_data_update).label("month"),
                func.avg(Contributor.overall_impact_score).label("avg_score"),
                func.count(Contributor.id).label("contributors"),
            )
            .group_by("month")
            .order_by("month")
        )

        result = await db.execute(query)
        trends = [
            {
                "month": row.month.strftime("%Y-%m") if row.month else None,
                "average_score": float(row.avg_score or 0),
                "contributors": int(row.contributors or 0),
            }
            for row in result
        ]

        return {"trends": trends}
    except Exception as e:
        logger.error("Error fetching trends", error=e, exc_info=True)
        raise HTTPException(500, "Internal server error")

@router.get("/distributions")
async def get_contribution_distributions(db: AsyncSession = Depends(get_db)):
    """Return average additive and maintenance contribution scores."""
    logger.info("Fetching contribution distributions")

    try:
        query = select(
            func.avg(Contributor.additive_contribution_score).label("avg_additive"),
            func.avg(Contributor.maintenance_contribution_score).label("avg_maintenance"),
        )

        result = await db.execute(query)
        row = result.one()

        return {
            "additive": float(row.avg_additive or 0),
            "maintenance": float(row.avg_maintenance or 0),
        }
    except Exception as e:
        logger.error("Error fetching distributions", error=e, exc_info=True)
        raise HTTPException(500, "Internal server error")


@router.get("/correlations")
async def get_metric_correlations(db: AsyncSession = Depends(get_db)):
    """Return correlations between contribution metrics and overall score."""
    logger.info("Fetching metric correlations")

    try:
        query = select(
            func.corr(Contributor.additive_contribution_score, Contributor.overall_impact_score).label("additive_overall"),
            func.corr(Contributor.maintenance_contribution_score, Contributor.overall_impact_score).label("maintenance_overall"),
        )
        result = await db.execute(query)
        row = result.one()

        return {
            "additive_vs_overall": float(row.additive_overall or 0),
            "maintenance_vs_overall": float(row.maintenance_overall or 0),
        }
    except Exception as e:
        logger.error("Error fetching correlations", error=e, exc_info=True)
        raise HTTPException(500, "Internal server error")


@router.get("/reports")
async def generate_reports(db: AsyncSession = Depends(get_db)):
    """Return a summary report of contributor statistics."""
    logger.info("Generating analytics report")

    try:
        result = await db.execute(
            select(
                func.count(Contributor.id),
                func.avg(Contributor.overall_impact_score),
                func.max(Contributor.overall_impact_score),
            )
        )
        total, avg_score, max_score = result.one()

        return {
            "total_contributors": int(total or 0),
            "average_score": float(avg_score or 0),
            "max_score": float(max_score or 0),
        }
    except Exception as e:
        logger.error("Error generating report", error=e, exc_info=True)
        raise HTTPException(500, "Internal server error")

"""
Analysis Sessions API endpoints
分析会话相关的API端点
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import List, Optional, Dict, Any
import structlog
from datetime import datetime

from app.core.database import get_db
from app.models.analysis_session import AnalysisSession
from app.models.contributor import Contributor

logger = structlog.get_logger()
router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_analysis_sessions(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    status: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all analysis sessions with pagination
    获取所有分析会话（分页）
    """
    logger.info("Fetching analysis sessions", limit=limit, offset=offset, status=status)
    
    try:
        # Build query
        query = select(AnalysisSession).order_by(desc(AnalysisSession.started_at))
        
        if status:
            query = query.where(AnalysisSession.analysis_status == status)
        
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        return [session.to_dict() for session in sessions]
        
    except Exception as e:
        logger.error("Error fetching analysis sessions", error=e)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{session_id}", response_model=Dict[str, Any])
async def get_analysis_session(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific analysis session
    获取特定分析会话的详细信息
    """
    logger.info("Fetching analysis session details", session_id=session_id)
    
    try:
        # Get session
        session_result = await db.execute(
            select(AnalysisSession).where(AnalysisSession.id == session_id)
        )
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Analysis session not found")
        
        return session.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching analysis session", session_id=session_id, error=e)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{session_id}/contributors", response_model=List[Dict[str, Any]])
async def get_session_contributors(
    session_id: int,
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all contributors found in a specific analysis session
    获取特定分析会话中发现的所有贡献者
    """
    logger.info("Fetching contributors for session", session_id=session_id)
    
    try:
        # Verify session exists
        session_result = await db.execute(
            select(AnalysisSession).where(AnalysisSession.id == session_id)
        )
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Analysis session not found")
        
        # Get contributors from this session
        query = select(Contributor).where(
            Contributor.analysis_session_id == session_id
        ).order_by(
            desc(Contributor.overall_impact_score)
        ).limit(limit).offset(offset)
        
        result = await db.execute(query)
        contributors = result.scalars().all()
        
        # Convert to response format
        response_data = []
        for contributor in contributors:
            data = contributor.to_dict(include_sensitive=False)
            response_data.append(data)
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching session contributors", session_id=session_id, error=e)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{session_id}")
async def delete_analysis_session(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an analysis session and all its associated contributors
    删除分析会话及其关联的所有贡献者
    """
    logger.info("Deleting analysis session", session_id=session_id)
    
    try:
        # Get session
        session_result = await db.execute(
            select(AnalysisSession).where(AnalysisSession.id == session_id)
        )
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Analysis session not found")
        
        # Delete associated contributors
        contributors_result = await db.execute(
            select(Contributor).where(Contributor.analysis_session_id == session_id)
        )
        contributors = contributors_result.scalars().all()
        
        for contributor in contributors:
            await db.delete(contributor)
        
        # Delete session
        await db.delete(session)
        await db.commit()
        
        logger.info("Analysis session deleted successfully", session_id=session_id)
        return {"message": "Analysis session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("Error deleting analysis session", session_id=session_id, error=e)
        raise HTTPException(status_code=500, detail="Internal server error") 
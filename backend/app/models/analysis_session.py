"""
Analysis Session model for tracking Wikipedia page analysis sessions
用于追踪维基百科页面分析会话的模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import Dict, List
import uuid

from ..core.database import Base


class AnalysisSession(Base):
    """
    Model for tracking analysis sessions of Wikipedia pages
    用于追踪维基百科页面分析会话的模型
    """
    __tablename__ = "analysis_sessions"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Page information
    page_url = Column(String(1000), nullable=False)
    page_title = Column(String(500), nullable=False)
    page_language = Column(String(10), default="en")
    
    # Analysis metadata
    analysis_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    total_contributors_found = Column(Integer, default=0)
    total_revisions_analyzed = Column(Integer, default=0)
    
    # Error information
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Analysis summary
    summary_stats = Column(JSON, default=dict)  # Store summary statistics
    
    def __repr__(self):
        return f"<AnalysisSession(id={self.id}, title='{self.page_title}', status='{self.analysis_status}')>"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "uuid": self.uuid,
            "page_url": self.page_url,
            "page_title": self.page_title,
            "page_language": self.page_language,
            "analysis_status": self.analysis_status,
            "total_contributors_found": self.total_contributors_found,
            "total_revisions_analyzed": self.total_revisions_analyzed,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at is not None else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at is not None else None,
            "summary_stats": self.summary_stats
        } 
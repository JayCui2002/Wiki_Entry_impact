# pyright: ignore-all  # 忽略Pyright在此文件的所有类型检查
# 关闭Pyright关于SQLAlchemy列类型的误报

"""
Contributor model for Wikipedia contributors analysis
维基百科贡献者分析的贡献者模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import Dict, List, Optional
import uuid

from ..core.database import Base


class Contributor(Base):
    """
    Model for Wikipedia contributors and their impact metrics
    维基百科贡献者及其影响指标的模型
    """
    __tablename__ = "contributors"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Wikipedia user information
    wikipedia_username = Column(String(255), unique=True, index=True, nullable=False)
    wikipedia_user_id = Column(Integer, unique=True, index=True, nullable=True)
    
    # Basic contributor information
    display_name = Column(String(255), nullable=True)
    user_page_url = Column(String(500), nullable=True)
    talk_page_url = Column(String(500), nullable=True)
    
    # Registration and activity dates
    registration_date = Column(DateTime(timezone=True), nullable=True)
    first_edit_date = Column(DateTime(timezone=True), nullable=True)
    last_edit_date = Column(DateTime(timezone=True), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    is_bot = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    
    # Basic statistics
    total_edits = Column(Integer, default=0)
    total_pages_created = Column(Integer, default=0)
    total_pages_edited = Column(Integer, default=0)
    
    # Content contribution metrics
    total_bytes_added = Column(Integer, default=0)
    total_bytes_removed = Column(Integer, default=0)
    net_bytes_contribution = Column(Integer, default=0)
    
    # Quality metrics
    reverted_edits_count = Column(Integer, default=0)
    revert_rate = Column(Float, default=0.0)  # Percentage of edits that were reverted
    
    # Discussion and collaboration metrics
    talk_page_edits = Column(Integer, default=0)
    discussion_participation_score = Column(Float, default=0.0)
    
    # Impact scoring
    overall_impact_score = Column(Float, default=0.0)
    additive_contribution_score = Column(Float, default=0.0)
    maintenance_contribution_score = Column(Float, default=0.0)
    discussion_impact_score = Column(Float, default=0.0)
    
    # Language and topic analysis
    primary_language = Column(String(10), default="en")
    languages_contributed = Column(JSON, default=list)  # List of language codes
    topic_areas = Column(JSON, default=dict)  # Dictionary of topic areas and scores
    
    # Time-based activity patterns
    activity_pattern = Column(JSON, default=dict)  # Activity by hour/day/month
    peak_activity_hours = Column(JSON, default=list)
    
    # Collaboration patterns
    frequent_collaborators = Column(JSON, default=list)  # List of usernames
    collaboration_network_score = Column(Float, default=0.0)
    
    # Data update tracking
    last_data_update = Column(DateTime(timezone=True), server_default=func.now())
    data_freshness_score = Column(Float, default=1.0)  # 1.0 = fresh, 0.0 = stale
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign key relationships
    system_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    # system_user = relationship("User", back_populates="contributor_profile")
    # edits = relationship("EditHistory", back_populates="contributor")
    # impact_metrics = relationship("ImpactMetrics", back_populates="contributor")
    
    def __repr__(self):
        return f"<Contributor(id={self.id}, username='{self.wikipedia_username}')>"
    
    def calculate_impact_scores(self) -> Dict[str, float]:
        total_bytes_added_val = float(getattr(self, 'total_bytes_added', 0) or 0)
        revert_rate_val = float(getattr(self, 'revert_rate', 0) or 0)
        total_edits_val = float(getattr(self, 'total_edits', 0) or 0)
        net_bytes_val = float(getattr(self, 'net_bytes_contribution', 0) or 0)
        talk_page_edits_val = float(getattr(self, 'talk_page_edits', 0) or 0)
        discussion_participation_val = float(getattr(self, 'discussion_participation_score', 0) or 0)
        collab_network_val = float(getattr(self, 'collaboration_network_score', 0) or 0)

        additive_score = 0.0
        if total_bytes_added_val > 0:
            quality_factor = max(0.1, 1.0 - revert_rate_val)
            additive_score = (total_bytes_added_val / 1000) * quality_factor

        maintenance_score = 0.0
        if total_edits_val > 0:
            edit_frequency_factor = min(1.0, total_edits_val / 100)
            net_contribution_factor = max(0.0, net_bytes_val / 1000)
            maintenance_score = edit_frequency_factor * net_contribution_factor

        discussion_score = 0.0
        if talk_page_edits_val > 0:
            discussion_score = (talk_page_edits_val / 10) * discussion_participation_val

        overall_score = (
            additive_score * 0.4 +
            maintenance_score * 0.3 +
            discussion_score * 0.2 +
            collab_network_val * 0.1
        )

        return {
            "additive": round(additive_score, 2),
            "maintenance": round(maintenance_score, 2),
            "discussion": round(discussion_score, 2),
            "overall": round(overall_score, 2)
        }
    
    def update_impact_scores(self):
        """
        Update all impact scores based on current data
        根据当前数据更新所有影响分数
        """
        scores = self.calculate_impact_scores()
        self.additive_contribution_score = scores["additive"]
        self.maintenance_contribution_score = scores["maintenance"]
        self.discussion_impact_score = scores["discussion"]
        self.overall_impact_score = scores["overall"]
    
    def calculate_revert_rate(self, total_reverted: int = None) -> float:
        """
        Calculate the revert rate for this contributor
        计算此贡献者的回退率
        """
        if total_reverted is not None:
            self.reverted_edits_count = total_reverted
        
        if self.total_edits == 0:
            return 0.0
        
        revert_rate = float(getattr(self, 'reverted_edits_count', 0) or 0) / float(getattr(self, 'total_edits', 1) or 1)
        self.revert_rate = round(revert_rate, 4)
        return self.revert_rate
    
    def get_contribution_type_ratio(self) -> Dict[str, float]:
        """
        Get the ratio of additive vs maintenance contributions
        获取增量与维护贡献的比率
        """
        additive_val = float(getattr(self, 'additive_contribution_score', 0) or 0)
        maintenance_val = float(getattr(self, 'maintenance_contribution_score', 0) or 0)
        total_score = additive_val + maintenance_val
        
        if total_score == 0:
            return {"additive": 0.0, "maintenance": 0.0}
        
        return {
            "additive": round(additive_val / total_score, 2),
            "maintenance": round(maintenance_val / total_score, 2)
        }
    
    def to_dict(self, include_sensitive: bool = False) -> Dict:
        """
        Convert contributor object to dictionary
        将贡献者对象转换为字典
        """
        data = {
            "id": self.id,
            "uuid": self.uuid,
            "wikipedia_username": self.wikipedia_username,
            "display_name": self.display_name,
            "is_active": self.is_active,
            "is_bot": self.is_bot,
            "is_admin": self.is_admin,
            "total_edits": self.total_edits,
            "total_pages_created": self.total_pages_created,
            "total_pages_edited": self.total_pages_edited,
            "net_bytes_contribution": self.net_bytes_contribution,
            "revert_rate": self.revert_rate,
            "overall_impact_score": self.overall_impact_score,
            "additive_contribution_score": self.additive_contribution_score,
            "maintenance_contribution_score": self.maintenance_contribution_score,
            "discussion_impact_score": self.discussion_impact_score,
            "primary_language": self.primary_language,
            "topic_areas": self.topic_areas,
            "contribution_type_ratio": self.get_contribution_type_ratio(),
            "last_data_update": self.last_data_update.isoformat() if self.last_data_update else None,
        }
        
        if include_sensitive:
            data.update({
                "wikipedia_user_id": self.wikipedia_user_id,
                "user_page_url": self.user_page_url,
                "talk_page_url": self.talk_page_url,
                "registration_date": self.registration_date.isoformat() if self.registration_date else None,
                "first_edit_date": self.first_edit_date.isoformat() if self.first_edit_date else None,
                "last_edit_date": self.last_edit_date.isoformat() if self.last_edit_date else None,
                "languages_contributed": self.languages_contributed,
                "activity_pattern": self.activity_pattern,
                "frequent_collaborators": self.frequent_collaborators,
            })
        
        return data
    
    def needs_data_update(self, threshold_days: int = 7) -> bool:
        """
        Check if contributor data needs updating
        检查贡献者数据是否需要更新
        """
        if not self.last_data_update:
            return True
        
        from datetime import datetime, timedelta
        threshold_date = datetime.now() - timedelta(days=threshold_days)
        # This comparison requires last_data_update to be timezone-aware if threshold_date is.
        # Assuming both are offset-naive or both are offset-aware (which they should be with server_default=func.now())
        return self.last_data_update < threshold_date 
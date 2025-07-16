"""
Impact Calculator Service
贡献者影响评估计算服务

This module implements the core algorithms for assessing contributor impact
on wiki entry formation, including differentiation between additive and 
maintenance contributions.
"""

import math
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re
from dataclasses import dataclass

from ..models.contributor import Contributor
from ..core.redis_client import redis_client
import structlog

logger = structlog.get_logger()


@dataclass
class EditAnalysis:
    """
    Data structure for individual edit analysis
    单个编辑分析的数据结构
    """
    edit_id: int
    contributor_id: int
    page_id: int
    timestamp: datetime
    size_change: int
    is_new_page: bool
    is_revert: bool
    is_minor: bool
    comment: str
    content_added: int
    content_removed: int
    text_complexity_score: float
    semantic_significance: float


@dataclass
class ContributionMetrics:
    """
    Comprehensive contribution metrics for a contributor
    贡献者的综合贡献指标
    """
    contributor_id: int
    total_volume_score: float
    additive_score: float
    maintenance_score: float
    discussion_impact_score: float
    quality_score: float
    collaboration_score: float
    temporal_consistency_score: float
    overall_impact_score: float


class ImpactCalculator:
    """
    Main class for calculating contributor impact metrics
    计算贡献者影响指标的主类
    """
    
    def __init__(self):
        self.cache_expiry = 3600  # 1 hour cache
        self.weights = {
            'volume': 0.25,
            'additive': 0.20,
            'maintenance': 0.15,
            'discussion': 0.15,
            'quality': 0.15,
            'collaboration': 0.10
        }
    
    async def calculate_comprehensive_impact(
        self, 
        contributor: Contributor,
        edit_history: List[EditAnalysis],
        discussion_data: Optional[Dict] = None
    ) -> ContributionMetrics:
        """
        Calculate comprehensive impact metrics for a contributor
        计算贡献者的综合影响指标
        """
        logger.info(f"Calculating impact for contributor {contributor.wikipedia_username}")
        
        # Check cache first
        cache_key = f"impact:contributor:{contributor.id}"
        cached_result = await redis_client.get(cache_key)
        if cached_result:
            logger.info("Returning cached impact metrics")
            return ContributionMetrics(**cached_result)
        
        # Calculate individual metric components
        volume_score = self._calculate_volume_impact(edit_history)
        additive_score = self._calculate_additive_impact(edit_history)
        maintenance_score = self._calculate_maintenance_impact(edit_history)
        discussion_score = self._calculate_discussion_impact(discussion_data or {})
        quality_score = self._calculate_quality_score(edit_history)
        collaboration_score = self._calculate_collaboration_score(edit_history)
        temporal_score = self._calculate_temporal_consistency(edit_history)
        
        # Calculate overall impact score
        overall_score = self._calculate_weighted_overall_score({
            'volume': volume_score,
            'additive': additive_score,
            'maintenance': maintenance_score,
            'discussion': discussion_score,
            'quality': quality_score,
            'collaboration': collaboration_score
        })
        
        metrics = ContributionMetrics(
            contributor_id=contributor.id,
            total_volume_score=volume_score,
            additive_score=additive_score,
            maintenance_score=maintenance_score,
            discussion_impact_score=discussion_score,
            quality_score=quality_score,
            collaboration_score=collaboration_score,
            temporal_consistency_score=temporal_score,
            overall_impact_score=overall_score
        )
        
        # Cache the results
        await redis_client.set(
            cache_key, 
            metrics.__dict__, 
            expire=self.cache_expiry
        )
        
        return metrics
    
    def _calculate_volume_impact(self, edit_history: List[EditAnalysis]) -> float:
        """
        Calculate impact based on volume of contributions
        基于贡献量计算影响
        """
        if not edit_history:
            return 0.0
        
        total_edits = len(edit_history)
        total_content_added = sum(edit.content_added for edit in edit_history)
        
        # Apply logarithmic scaling to prevent dominance by volume alone
        edit_score = math.log(total_edits + 1) * 2
        content_score = math.log(total_content_added + 1) * 0.1
        
        # Normalize to 0-100 scale
        volume_score = min(100, edit_score + content_score)
        
        return round(volume_score, 2)
    
    def _calculate_additive_impact(self, edit_history: List[EditAnalysis]) -> float:
        """
        Calculate impact from additive contributions (new content creation)
        计算增量贡献的影响（新内容创建）
        """
        if not edit_history:
            return 0.0
        
        # Focus on new page creations and substantial content additions
        new_page_score = 0
        content_addition_score = 0
        
        for edit in edit_history:
            if edit.is_new_page:
                # New page creation gets high weight
                page_value = min(50, edit.content_added / 100)  # Cap at 50 points per page
                semantic_bonus = edit.semantic_significance * 10
                new_page_score += page_value + semantic_bonus
            
            elif edit.content_added > 100:  # Substantial additions
                # Weight by content quality and significance
                addition_value = min(10, edit.content_added / 500)
                complexity_bonus = edit.text_complexity_score * 2
                semantic_bonus = edit.semantic_significance * 3
                content_addition_score += addition_value + complexity_bonus + semantic_bonus
        
        # Combine scores with diminishing returns
        total_additive = new_page_score * 1.5 + content_addition_score
        
        # Apply logarithmic scaling and normalize
        additive_score = min(100, math.log(total_additive + 1) * 15)
        
        return round(additive_score, 2)
    
    def _calculate_maintenance_impact(self, edit_history: List[EditAnalysis]) -> float:
        """
        Calculate impact from maintenance contributions (editing existing content)
        计算维护贡献的影响（编辑现有内容）
        """
        if not edit_history:
            return 0.0
        
        maintenance_edits = [
            edit for edit in edit_history 
            if not edit.is_new_page and not edit.is_revert
        ]
        
        if not maintenance_edits:
            return 0.0
        
        # Evaluate maintenance contributions
        improvement_score = 0
        consistency_score = 0
        
        for edit in maintenance_edits:
            # Positive maintenance: net positive changes
            if edit.size_change > 0:
                improvement_value = min(5, abs(edit.size_change) / 100)
                quality_bonus = edit.text_complexity_score * 1.5
                improvement_score += improvement_value + quality_bonus
            
            # Quality maintenance: minimal size change but high semantic value
            elif abs(edit.size_change) < 50 and edit.semantic_significance > 0.7:
                consistency_score += edit.semantic_significance * 3
        
        # Calculate frequency factor (consistent maintenance)
        edit_span_days = self._calculate_edit_span_days(maintenance_edits)
        frequency_factor = min(2.0, len(maintenance_edits) / max(1, edit_span_days / 30))
        
        # Combine scores
        total_maintenance = (improvement_score + consistency_score) * frequency_factor
        
        # Normalize to 0-100 scale
        maintenance_score = min(100, total_maintenance)
        
        return round(maintenance_score, 2)
    
    def _calculate_discussion_impact(self, discussion_data: Dict) -> float:
        """
        Calculate impact on discussions regarding changes
        计算对变更讨论的影响
        """
        if not discussion_data:
            return 0.0
        
        talk_page_edits = discussion_data.get('talk_page_edits', 0)
        discussion_initiations = discussion_data.get('discussion_initiations', 0)
        discussion_responses = discussion_data.get('discussion_responses', 0)
        consensus_building = discussion_data.get('consensus_building_score', 0.0)
        conflict_resolution = discussion_data.get('conflict_resolution_score', 0.0)
        
        # Weight different types of discussion participation
        initiation_score = discussion_initiations * 5  # Starting discussions is valuable
        response_score = discussion_responses * 2      # Responding is also valuable
        consensus_score = consensus_building * 15      # Building consensus is highly valuable
        resolution_score = conflict_resolution * 20   # Resolving conflicts is very valuable
        
        # Apply logarithmic scaling to talk page edits
        talk_score = math.log(talk_page_edits + 1) * 3
        
        total_discussion = (
            initiation_score + response_score + 
            consensus_score + resolution_score + talk_score
        )
        
        # Normalize to 0-100 scale
        discussion_score = min(100, total_discussion)
        
        return round(discussion_score, 2)
    
    def _calculate_quality_score(self, edit_history: List[EditAnalysis]) -> float:
        """
        Calculate quality score based on edit patterns and outcomes
        基于编辑模式和结果计算质量分数
        """
        if not edit_history:
            return 0.0
        
        total_edits = len(edit_history)
        reverted_edits = sum(1 for edit in edit_history if edit.is_revert)
        
        # Base quality from revert rate (inverse relationship)
        revert_rate = reverted_edits / total_edits if total_edits > 0 else 0
        quality_base = max(0, 100 - (revert_rate * 200))  # Heavy penalty for reverts
        
        # Bonus for complexity and semantic significance
        avg_complexity = np.mean([edit.text_complexity_score for edit in edit_history])
        avg_semantic = np.mean([edit.semantic_significance for edit in edit_history])
        
        complexity_bonus = avg_complexity * 20
        semantic_bonus = avg_semantic * 30
        
        # Minor edit penalty (too many minor edits might indicate low impact)
        minor_edits = sum(1 for edit in edit_history if edit.is_minor)
        minor_rate = minor_edits / total_edits if total_edits > 0 else 0
        minor_penalty = minor_rate * 20
        
        quality_score = quality_base + complexity_bonus + semantic_bonus - minor_penalty
        quality_score = max(0, min(100, quality_score))
        
        return round(quality_score, 2)
    
    def _calculate_collaboration_score(self, edit_history: List[EditAnalysis]) -> float:
        """
        Calculate collaboration score based on editing patterns
        基于编辑模式计算协作分数
        """
        if not edit_history:
            return 0.0
        
        # Group edits by page to find collaborative patterns
        page_edits = {}
        for edit in edit_history:
            if edit.page_id not in page_edits:
                page_edits[edit.page_id] = []
            page_edits[edit.page_id].append(edit)
        
        collaboration_indicators = 0
        total_pages = len(page_edits)
        
        for page_id, edits in page_edits.items():
            # Look for collaborative patterns
            if len(edits) > 1:
                # Multiple edits on same page suggests ongoing collaboration
                collaboration_indicators += min(5, len(edits) - 1)
            
            # Check for discussion-like comment patterns
            discussion_comments = sum(
                1 for edit in edits 
                if any(keyword in edit.comment.lower() for keyword in 
                      ['discuss', 'talk', 'comment', 'response', 'reply'])
            )
            collaboration_indicators += discussion_comments * 2
        
        # Normalize by page count and scale
        if total_pages > 0:
            collaboration_score = min(100, (collaboration_indicators / total_pages) * 20)
        else:
            collaboration_score = 0
        
        return round(collaboration_score, 2)
    
    def _calculate_temporal_consistency(self, edit_history: List[EditAnalysis]) -> float:
        """
        Calculate temporal consistency of contributions
        计算贡献的时间一致性
        """
        if len(edit_history) < 2:
            return 50.0  # Neutral score for insufficient data
        
        # Sort edits by timestamp
        sorted_edits = sorted(edit_history, key=lambda x: x.timestamp)
        
        # Calculate time intervals between edits
        intervals = []
        for i in range(1, len(sorted_edits)):
            interval = (sorted_edits[i].timestamp - sorted_edits[i-1].timestamp).days
            intervals.append(interval)
        
        if not intervals:
            return 50.0
        
        # Calculate consistency metrics
        avg_interval = np.mean(intervals)
        interval_std = np.std(intervals)
        
        # Prefer regular, sustained contribution patterns
        if avg_interval > 0:
            consistency_ratio = 1 - min(1, interval_std / avg_interval)
        else:
            consistency_ratio = 0
        
        # Calculate span and regularity
        total_span_days = (sorted_edits[-1].timestamp - sorted_edits[0].timestamp).days
        if total_span_days > 0:
            regularity_score = min(100, (len(edit_history) / total_span_days) * 365 * 10)
        else:
            regularity_score = 0
        
        # Combine metrics
        temporal_score = (consistency_ratio * 50) + (regularity_score * 0.5)
        temporal_score = max(0, min(100, temporal_score))
        
        return round(temporal_score, 2)
    
    def _calculate_weighted_overall_score(self, component_scores: Dict[str, float]) -> float:
        """
        Calculate weighted overall impact score
        计算加权整体影响分数
        """
        overall_score = sum(
            component_scores[component] * self.weights[component]
            for component in self.weights.keys()
            if component in component_scores
        )
        
        return round(overall_score, 2)
    
    def _calculate_edit_span_days(self, edits: List[EditAnalysis]) -> int:
        """
        Calculate the span of days between first and last edit
        计算第一次和最后一次编辑之间的天数跨度
        """
        if len(edits) < 2:
            return 1
        
        sorted_edits = sorted(edits, key=lambda x: x.timestamp)
        span = (sorted_edits[-1].timestamp - sorted_edits[0].timestamp).days
        return max(1, span)
    
    async def compare_contributors(
        self, 
        contributor_ids: List[int]
    ) -> Dict[int, ContributionMetrics]:
        """
        Compare multiple contributors and return their metrics
        比较多个贡献者并返回他们的指标
        """
        results = {}
        
        for contributor_id in contributor_ids:
            cache_key = f"impact:contributor:{contributor_id}"
            cached_result = await redis_client.get(cache_key)
            
            if cached_result:
                results[contributor_id] = ContributionMetrics(**cached_result)
            else:
                logger.warning(f"No cached metrics found for contributor {contributor_id}")
        
        return results
    
    def classify_contributor_type(self, metrics: ContributionMetrics) -> str:
        """
        Classify contributor based on their contribution pattern
        根据贡献模式对贡献者进行分类
        """
        additive_ratio = metrics.additive_score / max(1, metrics.additive_score + metrics.maintenance_score)
        
        if additive_ratio > 0.7:
            return "Content Creator"
        elif additive_ratio < 0.3:
            return "Maintainer"
        elif metrics.discussion_impact_score > 70:
            return "Community Builder"
        elif metrics.collaboration_score > 70:
            return "Collaborator"
        else:
            return "Balanced Contributor" 
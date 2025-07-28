"""
Impact Calculator Service
贡献者影响评估计算服务

This module implements the core algorithms for assessing contributor impact
on wiki entry formation, including differentiation between additive and 
maintenance contributions.
"""

import asyncio
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

    @classmethod
    def from_contributor(cls, contributor: "Contributor") -> "ContributionMetrics":
        """
        Create a ContributionMetrics instance from a Contributor model instance.
        This is useful when you need to classify a contributor without a full
        recalculation, using the scores stored in the database.
        """
        return cls(
            contributor_id=contributor.id,
            total_volume_score=0,  # Not directly stored, placeholder
            additive_score=contributor.additive_contribution_score,
            maintenance_score=contributor.maintenance_contribution_score,
            discussion_impact_score=contributor.discussion_impact_score,
            quality_score=0,  # Not directly stored, placeholder
            collaboration_score=contributor.collaboration_network_score,
            temporal_consistency_score=0,  # Not directly stored, placeholder
            overall_impact_score=contributor.overall_impact_score
        )


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
            contributor_id=int(contributor.id),
            total_volume_score=float(volume_score),
            additive_score=float(additive_score),
            maintenance_score=float(maintenance_score),
            discussion_impact_score=float(discussion_score),
            quality_score=float(quality_score),
            collaboration_score=float(collaboration_score),
            temporal_consistency_score=float(temporal_score),
            overall_impact_score=float(overall_score)
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
        volume_score = min(100.0, edit_score + content_score)
        
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
        additive_score = min(100.0, math.log(total_additive + 1) * 10)
        
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
        
        # Normalize to 0-100 scale, boosting the score slightly to match additive scale
        maintenance_score = min(100.0, math.log(total_maintenance + 1) * 12)
        
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
        response_score = discussion_responses * 2
        consensus_score = consensus_building * 10
        conflict_score = conflict_resolution * 8
        
        # Total score with logarithmic scaling
        total_discussion = initiation_score + response_score + consensus_score + conflict_score
        discussion_impact = min(100.0, math.log(total_discussion + 1) * 15)
        
        return round(discussion_impact, 2)

    def _calculate_quality_score(self, edit_history: List[EditAnalysis]) -> float:
        """
        Calculate quality score based on edit characteristics
        基于编辑特征计算质量分数
        """
        if not edit_history:
            return 0.0
        
        # Factors: reverts received, complexity, semantic value
        revert_rate = sum(1 for e in edit_history if e.is_revert) / len(edit_history)
        avg_complexity = np.mean([e.text_complexity_score for e in edit_history])
        avg_semantic_sig = np.mean([e.semantic_significance for e in edit_history])
        
        # Quality score penalizes reverts and rewards complexity/significance
        revert_penalty = revert_rate * 50
        quality_score = (avg_complexity * 30) + (avg_semantic_sig * 70) - revert_penalty
        
        return max(0.0, min(100.0, quality_score))

    def _calculate_collaboration_score(self, edit_history: List[EditAnalysis]) -> float:
        """
        Calculate collaboration score based on co-editing patterns
        基于共同编辑模式计算协作分数
        """
        if not edit_history:
            return 0.0
            
        # This is a simplified model. A full implementation would require a graph
        # of co-editorship across pages.
        
        # Here, we'll simulate it based on number of unique pages edited
        # as a proxy for breadth of collaboration.
        
        unique_pages = {edit.page_id for edit in edit_history}
        num_unique_pages = len(unique_pages)
        
        # More pages edited suggests wider collaboration.
        # Logarithmic scale to value diversity but with diminishing returns.
        collaboration_score = math.log(num_unique_pages + 1) * 20
        
        # A more advanced metric could involve:
        # - Number of other users who edited the same page within a time window.
        # - Positive/negative interactions in edit summaries (e.g., "thanks", "reverted").
        # - Participation in WikiProjects.
        
        return min(100.0, collaboration_score)

    def _calculate_temporal_consistency(self, edit_history: List[EditAnalysis]) -> float:
        """
        Calculate score based on the consistency of contributions over time
        基于贡献随时间的一致性计算分数
        """
        if not edit_history or len(edit_history) < 5:
            return 0.0

        timestamps = sorted([edit.timestamp for edit in edit_history])
        
        # Calculate time between edits
        inter_edit_times = [(timestamps[i] - timestamps[i-1]).total_seconds() 
                            for i in range(1, len(timestamps))]
        
        if not inter_edit_times:
            return 0.0
            
        # Use coefficient of variation to measure consistency (lower is better)
        mean_time = np.mean(inter_edit_times)
        std_dev = np.std(inter_edit_times)
        
        if mean_time == 0:
            return 0.0 # Avoid division by zero
            
        coeff_of_variation = std_dev / mean_time
        
        # Convert to a score from 0-100 (1 - CV, capped at 0-1 range)
        consistency_score = max(0, 1 - coeff_of_variation) * 100
        
        # Factor in total activity period
        total_duration_days = (timestamps[-1] - timestamps[0]).days
        duration_bonus = min(20, math.log(total_duration_days + 1))
        
        final_score = min(100.0, consistency_score + duration_bonus)
        
        return round(final_score, 2)
    
    def _calculate_weighted_overall_score(self, component_scores: Dict[str, float]) -> float:
        """
        Calculate the final weighted overall impact score
        计算最终加权综合影响分数
        """
        overall_score = sum(
            component_scores.get(metric, 0) * self.weights.get(metric, 0)
            for metric in self.weights
        )
        
        return round(overall_score, 2)
    
    def _calculate_edit_span_days(self, edits: List[EditAnalysis]) -> int:
        """
        Calculate the number of days between the first and last edit
        计算第一次和最后一次编辑之间的天数
        """
        if not edits or len(edits) < 2:
            return 1
        
        timestamps = sorted([e.timestamp for e in edits])
        span = timestamps[-1] - timestamps[0]
        return max(1, span.days)

    async def compare_contributors(
        self, 
        contributor_ids: List[int]
    ) -> Dict[int, ContributionMetrics]:
        """
        Compare impact metrics for a list of contributors
        比较贡献者列表的影响指标
        """
        # In a real app, this would be a more optimized query
        tasks = [
            self.calculate_comprehensive_impact(
                await Contributor.get(id), [], {}
            ) for id in contributor_ids
        ]
        results = await asyncio.gather(*tasks)
        return {res.contributor_id: res for res in results}

    def classify_contributor_type(self, metrics: ContributionMetrics) -> str:
        """
        Classify the contributor into a type based on their metric ratios
        根据贡献者的指标比率将其分类
        """
        if metrics.overall_impact_score < 5:
            return "Newcomer"  # 新手

        total_impact = metrics.additive_score + metrics.maintenance_score
        
        if total_impact == 0:
            return "Newcomer"
            
        additive_ratio = metrics.additive_score / total_impact
        
        if additive_ratio > 0.7:
            return "Architect"  # 架构师 (主要进行内容创建)
        
        elif additive_ratio < 0.3:
            return "Gardener"  # 园丁 (主要进行维护和改进)
        
        else:
            return "Artisan"  # 工匠 (平衡的贡献者)
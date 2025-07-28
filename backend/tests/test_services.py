"""
Tests for service layer components
服务层组件测试
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from faker import Faker

from app.services.impact_calculator import (
    ImpactCalculator, 
    EditAnalysis, 
    ContributionMetrics
)
from app.models.contributor import Contributor

fake = Faker("zh_CN")


class TestImpactCalculator:
    """
    影响计算器测试类
    """
    
    def setup_method(self):
        """
        每个测试方法前的设置
        """
        self.calculator = ImpactCalculator()
    
    def test_volume_impact_calculation(self):
        """
        测试基于贡献量的影响计算
        """
        # 空编辑历史
        empty_edits = []
        volume_score = self.calculator._calculate_volume_impact(empty_edits)
        assert volume_score == 0.0
        
        # 创建测试编辑数据
        test_edits = [
            EditAnalysis(
                edit_id=i,
                contributor_id=1,
                page_id=1,
                timestamp=datetime.now(),
                size_change=100,
                is_new_page=False,
                is_revert=False,
                is_minor=False,
                comment=f"编辑 {i}",
                content_added=50,
                content_removed=10,
                text_complexity_score=0.5,
                semantic_significance=0.6
            ) for i in range(10)
        ]
        
        volume_score = self.calculator._calculate_volume_impact(test_edits)
        assert volume_score > 0
        assert volume_score <= 100  # 分数应该在合理范围内
    
    def test_additive_impact_calculation(self):
        """
        测试增量贡献影响计算
        """
        # 测试新页面创建
        new_page_edits = [
            EditAnalysis(
                edit_id=1,
                contributor_id=1,
                page_id=1,
                timestamp=datetime.now(),
                size_change=1000,
                is_new_page=True,
                is_revert=False,
                is_minor=False,
                comment="创建新页面",
                content_added=1000,
                content_removed=0,
                text_complexity_score=0.8,
                semantic_significance=0.9
            )
        ]
        
        additive_score = self.calculator._calculate_additive_impact(new_page_edits)
        assert additive_score > 0
        
        # 测试内容添加
        content_addition_edits = [
            EditAnalysis(
                edit_id=2,
                contributor_id=1,
                page_id=2,
                timestamp=datetime.now(),
                size_change=500,
                is_new_page=False,
                is_revert=False,
                is_minor=False,
                comment="添加大量内容",
                content_added=500,
                content_removed=0,
                text_complexity_score=0.7,
                semantic_significance=0.8
            )
        ]
        
        content_score = self.calculator._calculate_additive_impact(content_addition_edits)
        assert content_score > 0
    
    def test_maintenance_impact_calculation(self):
        """
        测试维护贡献影响计算
        """
        # 创建维护类型的编辑
        maintenance_edits = [
            EditAnalysis(
                edit_id=i,
                contributor_id=1,
                page_id=1,
                timestamp=datetime.now() - timedelta(days=i),
                size_change=50 if i % 2 == 0 else -20,  # 交替的正负变化
                is_new_page=False,
                is_revert=False,
                is_minor=True,
                comment=f"维护编辑 {i}",
                content_added=50 if i % 2 == 0 else 0,
                content_removed=0 if i % 2 == 0 else 20,
                text_complexity_score=0.6,
                semantic_significance=0.7
            ) for i in range(5)
        ]
        
        maintenance_score = self.calculator._calculate_maintenance_impact(maintenance_edits)
        assert maintenance_score >= 0
        assert maintenance_score <= 100
    
    def test_discussion_impact_calculation(self):
        """
        测试讨论影响计算
        """
        # 空讨论数据
        empty_discussion = {}
        discussion_score = self.calculator._calculate_discussion_impact(empty_discussion)
        assert discussion_score == 0.0
        
        # 完整讨论数据
        full_discussion = {
            "talk_page_edits": 20,
            "discussion_initiations": 5,
            "discussion_responses": 15,
            "consensus_building_score": 0.8,
            "conflict_resolution_score": 0.6
        }
        
        discussion_score = self.calculator._calculate_discussion_impact(full_discussion)
        assert discussion_score > 0
        assert discussion_score <= 100
    
    def test_quality_score_calculation(self):
        """
        测试质量分数计算
        """
        # 高质量编辑（无回退，复杂度高）
        high_quality_edits = [
            EditAnalysis(
                edit_id=i,
                contributor_id=1,
                page_id=1,
                timestamp=datetime.now(),
                size_change=100,
                is_new_page=False,
                is_revert=False,
                is_minor=False,
                comment="高质量编辑",
                content_added=100,
                content_removed=0,
                text_complexity_score=0.9,
                semantic_significance=0.8
            ) for i in range(5)
        ]
        
        quality_score = self.calculator._calculate_quality_score(high_quality_edits)
        assert quality_score > 50  # 高质量应该得到高分
        
        # 低质量编辑（有回退）
        low_quality_edits = [
            EditAnalysis(
                edit_id=i,
                contributor_id=1,
                page_id=1,
                timestamp=datetime.now(),
                size_change=50,
                is_new_page=False,
                is_revert=True if i % 2 == 0 else False,
                is_minor=False,
                comment="低质量编辑",
                content_added=50,
                content_removed=0,
                text_complexity_score=0.2,
                semantic_significance=0.1
            ) for i in range(4)
        ]
        
        low_quality_score = self.calculator._calculate_quality_score(low_quality_edits)
        assert low_quality_score < quality_score  # 低质量分数应该更低
    
    def test_collaboration_score_calculation(self):
        """
        测试协作分数计算
        """
        # 多页面编辑（表示协作范围广）
        multi_page_edits = [
            EditAnalysis(
                edit_id=i,
                contributor_id=1,
                page_id=i % 5,  # 编辑5个不同页面
                timestamp=datetime.now(),
                size_change=100,
                is_new_page=False,
                is_revert=False,
                is_minor=False,
                comment=f"编辑页面 {i % 5}",
                content_added=100,
                content_removed=0,
                text_complexity_score=0.5,
                semantic_significance=0.5
            ) for i in range(10)
        ]
        
        collab_score = self.calculator._calculate_collaboration_score(multi_page_edits)
        assert collab_score > 0
        assert collab_score <= 100
    
    def test_temporal_consistency_calculation(self):
        """
        测试时间一致性计算
        """
        # 编辑历史少于5个
        few_edits = [
            EditAnalysis(
                edit_id=1,
                contributor_id=1,
                page_id=1,
                timestamp=datetime.now(),
                size_change=100,
                is_new_page=False,
                is_revert=False,
                is_minor=False,
                comment="编辑1",
                content_added=100,
                content_removed=0,
                text_complexity_score=0.5,
                semantic_significance=0.5
            )
        ]
        
        consistency_score = self.calculator._calculate_temporal_consistency(few_edits)
        assert consistency_score == 0.0
        
        # 规律的编辑时间序列
        regular_edits = [
            EditAnalysis(
                edit_id=i,
                contributor_id=1,
                page_id=1,
                timestamp=datetime.now() - timedelta(days=i),
                size_change=100,
                is_new_page=False,
                is_revert=False,
                is_minor=False,
                comment=f"编辑 {i}",
                content_added=100,
                content_removed=0,
                text_complexity_score=0.5,
                semantic_significance=0.5
            ) for i in range(10)
        ]
        
        regular_score = self.calculator._calculate_temporal_consistency(regular_edits)
        assert regular_score > 0
    
    def test_weighted_overall_score(self):
        """
        测试加权综合分数计算
        """
        component_scores = {
            'volume': 80.0,
            'additive': 70.0,
            'maintenance': 60.0,
            'discussion': 50.0,
            'quality': 90.0,
            'collaboration': 40.0
        }
        
        overall_score = self.calculator._calculate_weighted_overall_score(component_scores)
        assert 0 <= overall_score <= 100
        assert isinstance(overall_score, float)
    
    def test_contributor_classification(self):
        """
        测试贡献者分类功能
        """
        # 新手贡献者（总体影响低）
        newcomer_metrics = ContributionMetrics(
            contributor_id=1,
            total_volume_score=2.0,
            additive_score=1.0,
            maintenance_score=1.0,
            discussion_impact_score=0.0,
            quality_score=10.0,
            collaboration_score=5.0,
            temporal_consistency_score=0.0,
            overall_impact_score=3.0
        )
        
        classification = self.calculator.classify_contributor_type(newcomer_metrics)
        assert classification == "Newcomer"
        
        # 架构师（主要进行内容创建）
        architect_metrics = ContributionMetrics(
            contributor_id=2,
            total_volume_score=80.0,
            additive_score=70.0,
            maintenance_score=20.0,
            discussion_impact_score=30.0,
            quality_score=85.0,
            collaboration_score=60.0,
            temporal_consistency_score=75.0,
            overall_impact_score=75.0
        )
        
        classification = self.calculator.classify_contributor_type(architect_metrics)
        assert classification == "Architect"
        
        # 园丁（主要进行维护）
        gardener_metrics = ContributionMetrics(
            contributor_id=3,
            total_volume_score=60.0,
            additive_score=15.0,
            maintenance_score=80.0,
            discussion_impact_score=40.0,
            quality_score=70.0,
            collaboration_score=75.0,
            temporal_consistency_score=85.0,
            overall_impact_score=65.0
        )
        
        classification = self.calculator.classify_contributor_type(gardener_metrics)
        assert classification == "Gardener"
        
        # 工匠（平衡的贡献者）
        artisan_metrics = ContributionMetrics(
            contributor_id=4,
            total_volume_score=70.0,
            additive_score=50.0,
            maintenance_score=60.0,
            discussion_impact_score=55.0,
            quality_score=80.0,
            collaboration_score=65.0,
            temporal_consistency_score=70.0,
            overall_impact_score=68.0
        )
        
        classification = self.calculator.classify_contributor_type(artisan_metrics)
        assert classification == "Artisan" 
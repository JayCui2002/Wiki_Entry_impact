#!/usr/bin/env python3
"""
Debug script for contributor type classification
调试贡献者类型分类的脚本
"""

import sys
import os

# 添加backend路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# 创建简化的测试类
class MockContributionMetrics:
    def __init__(self, overall_score, additive_score, maintenance_score):
        self.overall_impact_score = overall_score
        self.additive_score = additive_score
        self.maintenance_score = maintenance_score

def classify_contributor_type_simple(metrics):
    """
    简化版的贡献者分类逻辑
    """
    print(f"调试信息: 总分={metrics.overall_impact_score}, 增量={metrics.additive_score}, 维护={metrics.maintenance_score}")
    
    if metrics.overall_impact_score < 5:
        return "Newcomer"  # 新手

    total_impact = metrics.additive_score + metrics.maintenance_score
    print(f"总影响分: {total_impact}")
    
    if total_impact == 0:
        return "Newcomer"
        
    additive_ratio = metrics.additive_score / total_impact
    print(f"增量比例: {additive_ratio:.2f}")
    
    if additive_ratio > 0.7:
        return "Architect"  # 架构师
    elif additive_ratio < 0.3:
        return "Gardener"  # 园丁
    else:
        return "Artisan"  # 工匠

def test_classification():
    """测试不同的分数组合"""
    print("🧪 测试贡献者分类逻辑")
    print("=" * 50)
    
    test_cases = [
        # 总分低于5 - 应该是Newcomer
        {"name": "真正的新手", "overall": 2, "additive": 1, "maintenance": 1},
        
        # 总分够高但增量维护都是0 - 应该是Newcomer
        {"name": "分数异常", "overall": 10, "additive": 0, "maintenance": 0},
        
        # 正常的架构师
        {"name": "内容创建者", "overall": 25, "additive": 20, "maintenance": 5},
        
        # 正常的园丁
        {"name": "维护者", "overall": 30, "additive": 5, "maintenance": 25},
        
        # 正常的工匠
        {"name": "平衡贡献者", "overall": 40, "additive": 20, "maintenance": 20},
        
        # 边界测试
        {"name": "边界架构师", "overall": 15, "additive": 7.1, "maintenance": 2.9},
        {"name": "边界园丁", "overall": 15, "additive": 2.9, "maintenance": 7.1},
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['name']}:")
        metrics = MockContributionMetrics(
            overall_score=case['overall'],
            additive_score=case['additive'],
            maintenance_score=case['maintenance']
        )
        
        result = classify_contributor_type_simple(metrics)
        print(f"   结果: {result}")
        
        # 分析结果
        if result == "Newcomer":
            if case['overall'] < 5:
                print("   ✅ 正确: 总分太低")
            elif case['additive'] + case['maintenance'] == 0:
                print("   ✅ 正确: 增量+维护=0")
            else:
                print("   ❌ 意外: 不应该是新手")
        else:
            print("   ✅ 正确: 有经验的贡献者")

def test_real_world_scenarios():
    """测试真实世界的场景"""
    print("\n\n🌍 真实场景测试")
    print("=" * 50)
    
    # 模拟一些真实的分数范围
    real_cases = [
        {"name": "编辑新手", "overall": 3.2, "additive": 1.5, "maintenance": 1.2},
        {"name": "活跃编辑者", "overall": 12.8, "additive": 8.3, "maintenance": 2.1},
        {"name": "维护专家", "overall": 18.5, "additive": 2.8, "maintenance": 14.7},
        {"name": "全能贡献者", "overall": 35.6, "additive": 18.2, "maintenance": 16.9},
    ]
    
    for case in real_cases:
        print(f"\n{case['name']}:")
        metrics = MockContributionMetrics(
            overall_score=case['overall'],
            additive_score=case['additive'],
            maintenance_score=case['maintenance']
        )
        
        result = classify_contributor_type_simple(metrics)
        print(f"   分类: {result}")

if __name__ == "__main__":
    test_classification()
    test_real_world_scenarios()
    
    print("\n\n💡 建议:")
    print("如果所有用户都被分类为Newcomer，可能的原因:")
    print("1. overall_impact_score 总是 < 5")
    print("2. additive_score + maintenance_score = 0")
    print("3. 分数计算逻辑有问题")
    print("\n检查实际数据库中的分数值以确定具体问题。") 
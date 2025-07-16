"""
临时测试数据插入脚本
用于添加一些示例贡献者数据，以便测试前端功能
"""

import asyncio
import os
import sys

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.database import AsyncSessionLocal
from app.models.contributor import Contributor
from sqlalchemy.future import select

async def add_test_data():
    """添加测试贡献者数据"""
    session = AsyncSessionLocal()
    
    try:
        # 测试数据 - 不同类型的贡献者
        test_contributors = [
            {
                "wikipedia_username": "ArchitectBob",
                "wikipedia_user_id": 12345,
                "display_name": "ArchitectBob",
                "total_edits": 1500,
                "total_pages_created": 85,
                "total_bytes_added": 45000,
                "overall_impact_score": 75.5,
                "additive_contribution_score": 60.2,  # 高创建分数
                "maintenance_contribution_score": 15.3,  # 低维护分数
                "discussion_impact_score": 12.0,
                "quality_score": 82.1,
                "collaboration_network_score": 45.0,
                "is_active": True
            },
            {
                "wikipedia_username": "GardenerAlice", 
                "wikipedia_user_id": 12346,
                "display_name": "GardenerAlice",
                "total_edits": 3200,
                "total_pages_created": 12,
                "total_bytes_added": 28000,
                "overall_impact_score": 68.3,
                "additive_contribution_score": 18.5,  # 低创建分数
                "maintenance_contribution_score": 49.8,  # 高维护分数
                "discussion_impact_score": 15.2,
                "quality_score": 89.4,
                "collaboration_network_score": 62.0,
                "is_active": True
            },
            {
                "wikipedia_username": "ArtisanCharlie",
                "wikipedia_user_id": 12347,
                "display_name": "ArtisanCharlie", 
                "total_edits": 890,
                "total_pages_created": 45,
                "total_bytes_added": 22000,
                "overall_impact_score": 52.7,
                "additive_contribution_score": 28.9,  # 平衡分数
                "maintenance_contribution_score": 23.8,  # 平衡分数
                "discussion_impact_score": 18.5,
                "quality_score": 76.2,
                "collaboration_network_score": 38.0,
                "is_active": True
            },
            {
                "wikipedia_username": "NewcomerDave",
                "wikipedia_user_id": 12348,
                "display_name": "NewcomerDave",
                "total_edits": 15,
                "total_pages_created": 1,
                "total_bytes_added": 800,
                "overall_impact_score": 2.1,  # 低分数 - 应该是Newcomer
                "additive_contribution_score": 1.2,
                "maintenance_contribution_score": 0.9,
                "discussion_impact_score": 0.5,
                "quality_score": 45.0,
                "collaboration_network_score": 5.0,
                "is_active": True
            }
        ]
        
        for contrib_data in test_contributors:
            # 检查是否已存在 - 使用用户名而不是ID
            stmt = select(Contributor).where(Contributor.wikipedia_username == contrib_data["wikipedia_username"])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if not existing:
                contributor = Contributor(**contrib_data)
                session.add(contributor)
                print(f"添加了贡献者: {contrib_data['wikipedia_username']}")
            else:
                # 更新现有贡献者的数据
                for key, value in contrib_data.items():
                    setattr(existing, key, value)
                print(f"更新了贡献者: {contrib_data['wikipedia_username']}")
        
        await session.commit()
        print("✅ 测试数据添加完成！")
        print("\n现在您可以在前端看到不同类型的贡献者了：")
        print("- ArchitectBob (Architect - 主要创建内容)")
        print("- GardenerAlice (Gardener - 主要维护内容)")  
        print("- ArtisanCharlie (Artisan - 平衡贡献)")
        print("- NewcomerDave (Newcomer - 新手)")
        
    except Exception as e:
        await session.rollback()
        print(f"❌ 错误: {e}")
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(add_test_data()) 
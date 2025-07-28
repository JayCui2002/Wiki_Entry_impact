"""
Tests for database models
数据模型测试
"""

import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

fake = Faker("zh_CN")


class TestUserModel:
    """
    User模型测试类
    """
    
    @pytest_asyncio.async_test
    async def test_create_user(self, test_db_session: AsyncSession, sample_user_data):
        """
        测试用户创建
        """
        # 创建用户实例
        user = User(
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            full_name=sample_user_data["full_name"]
        )
        user.set_password(sample_user_data["password"])
        
        # 添加到数据库
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)
        
        # 验证用户属性
        assert user.id is not None
        assert user.username == sample_user_data["username"]
        assert user.email == sample_user_data["email"]
        assert user.full_name == sample_user_data["full_name"]
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.uuid is not None
    
    def test_password_hashing(self):
        """
        测试密码哈希功能
        """
        password = "test_password_123"
        user = User(username="testuser", email="test@example.com")
        
        # 设置密码
        user.set_password(password)
        
        # 验证密码哈希
        assert user.hashed_password is not None
        assert user.hashed_password != password  # 密码已哈希
        assert user.verify_password(password) is True  # 验证正确密码
        assert user.verify_password("wrong_password") is False  # 验证错误密码
    
    def test_user_to_dict(self):
        """
        测试用户对象转字典功能
        """
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="测试用户"
        )
        
        # 测试基本转换
        user_dict = user.to_dict()
        assert "username" in user_dict
        assert "email" not in user_dict  # 默认不包含敏感信息
        
        # 测试包含敏感信息的转换
        user_dict_with_sensitive = user.to_dict(include_sensitive=True)
        assert "email" in user_dict_with_sensitive
        assert "notification_settings" in user_dict_with_sensitive
    
    def test_user_login_tracking(self):
        """
        测试用户登录信息跟踪
        """
        user = User(username="testuser", email="test@example.com")
        initial_login_count = user.login_count
        
        # 模拟登录
        user.update_login_info()
        
        assert user.login_count == initial_login_count + 1
        assert user.failed_login_attempts == 0
        assert user.account_locked is False
    
    def test_failed_login_attempts(self):
        """
        测试失败登录尝试计数和账户锁定
        """
        user = User(username="testuser", email="test@example.com")
        
        # 模拟多次失败登录
        for i in range(4):
            user.increment_failed_login()
            assert user.is_account_locked() is False
        
        # 第5次失败登录应该锁定账户
        user.increment_failed_login()
        assert user.is_account_locked() is True
        assert user.failed_login_attempts == 5
    
    def test_user_can_be_deleted(self):
        """
        测试用户删除权限检查
        """
        # 普通用户可以被删除
        regular_user = User(username="regular", email="regular@example.com")
        assert regular_user.can_be_deleted() is True
        
        # 超级用户不能被删除
        super_user = User(
            username="admin", 
            email="admin@example.com", 
            is_superuser=True
        )
        assert super_user.can_be_deleted() is False
    
    def test_user_repr(self):
        """
        测试用户对象字符串表示
        """
        user = User(
            id=1,
            username="testuser",
            email="test@example.com"
        )
        
        repr_str = repr(user)
        assert "testuser" in repr_str
        assert "test@example.com" in repr_str
        assert "id=1" in repr_str 
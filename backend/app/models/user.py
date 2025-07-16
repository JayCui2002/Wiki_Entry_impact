# pyright: reportGeneralTypeIssues=false
# 关闭Pyright对SQLAlchemy列的类型警告，避免Column类型布尔运算报错

"""
User model for authentication and user management
用于身份验证和用户管理的用户模型
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
import uuid

from ..core.database import Base

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """
    User model for system authentication and management
    系统认证和管理的用户模型
    """
    __tablename__ = "users"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # User information
    full_name = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, default=0)
    
    # User preferences and settings
    preferences = Column(JSON, default=dict)
    notification_settings = Column(JSON, default=dict)
    
    # Account status
    account_locked = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    locked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    # Note: These will be defined when we create the related models
    # contributions = relationship("Contribution", back_populates="user")
    # audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hash a password using bcrypt
        使用bcrypt哈希密码
        """
        return pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        # type: ignore[call-arg]
        return pwd_context.verify(password, str(self.hashed_password))
    
    def set_password(self, password: str):
        """
        Set user password with hashing
        设置用户密码并进行哈希处理
        """
        self.hashed_password = self.hash_password(password)
    
    def to_dict(self, include_sensitive=False):
        """
        Convert user object to dictionary
        将用户对象转换为字典
        """
        data = {
            "id": self.id,
            "uuid": self.uuid,
            "username": self.username,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "preferences": self.preferences,
        }
        
        if include_sensitive:
            data.update({
                "email": self.email,
                "notification_settings": self.notification_settings,
            })
        
        return data
    
    def update_login_info(self):
        """
        Update login information when user logs in
        用户登录时更新登录信息
        """
        self.last_login = func.now()
        self.login_count += 1
        self.failed_login_attempts = 0
        self.account_locked = False
        self.locked_at = None
    
    def increment_failed_login(self):
        """
        Increment failed login attempts and lock account if needed
        增加失败登录尝试次数，必要时锁定账户
        """
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:  # Lock after 5 failed attempts
            self.account_locked = True
            self.locked_at = func.now()
    
    def is_account_locked(self) -> bool:
        # type: ignore[return-value]
        return bool(self.account_locked)
    
    def can_be_deleted(self) -> bool:
        # type: ignore[return-value]
        return not bool(self.is_superuser) 
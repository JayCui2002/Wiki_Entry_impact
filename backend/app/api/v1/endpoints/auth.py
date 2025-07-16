"""
Authentication endpoints
认证相关的API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import structlog

from app.core.database import get_db
from app.models.user import User
from app.core.security import create_access_token, create_refresh_token

logger = structlog.get_logger()
router = APIRouter()

@router.post("/login/access-token", response_model=dict)
async def login_access_token(
    db: AsyncSession = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    OAuth2兼容的令牌登录，为将来的请求获取访问令牌。
    """
    query = select(User).where(User.username == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not user.verify_password(form_data.password):
        logger.warning("Failed login attempt", username=form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif user.is_active is False:
        logger.warning("Inactive user login attempt", username=form_data.username)
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    logger.info("User logged in successfully", username=user.username)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

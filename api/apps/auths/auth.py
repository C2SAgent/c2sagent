from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings
from model.model_agent import UserConfig
from .database import get_db
from model.api_model.model_auth import TokenData
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str):
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    """生成密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "last_activity": datetime.utcnow().timestamp()})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    """创建刷新令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)  # 注意这里改为 AsyncSession
):
    """异步获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # 检查最后活动时间（30分钟无操作失效）
        last_activity = datetime.fromtimestamp(payload.get("last_activity", 0))
        if (datetime.utcnow() - last_activity) > timedelta(minutes=30):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="由于长时间未操作，Token已失效"
            )
        
        # 异步查询用户
        result = await db.execute(
            select(UserConfig).where(UserConfig.name == username)
        )
        user = result.scalars().first()
        
        if user is None:
            raise credentials_exception
        return user
    except JWTError as e:
        raise credentials_exception
        
async def get_current_active_user(
    current_user: UserConfig = Depends(get_current_user)
):
    """获取当前活跃用户"""
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="用户未激活")
    return current_user
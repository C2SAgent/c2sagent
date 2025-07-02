from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .config import settings
from .schemas import TokenData
from model.model_agent import UserConfig
from .auth import oauth2_scheme
from .database import SessionLocal, get_db

async def get_token_data(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    """解析并验证JWT Token"""
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
        return TokenData(username=username)
    except JWTError:
        raise credentials_exception

async def verify_token(
    request: Request,
    token_data: Annotated[TokenData, Depends(get_token_data)],
    db: Annotated[Session, Depends(get_db)]
) -> UserConfig:
    """全局依赖：验证Token有效性并检查用户状态"""
    user = db.query(UserConfig).filter(UserConfig.name == token_data.username).first()
    # if not user or not user.is_active:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="用户不存在或未激活"
    #     )
    
    # 检查最后活动时间（30分钟无操作失效）
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="缺少Authorization头"
            )
            
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        last_activity = datetime.fromtimestamp(payload.get("last_activity", 0))
        if (datetime.utcnow() - last_activity) > timedelta(minutes=30):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="由于长时间未操作，请重新登录"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token验证失败: {str(e)}"
        )
    
    return user
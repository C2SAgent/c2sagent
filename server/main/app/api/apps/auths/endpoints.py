from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated
from model import model_agent as models
from model.api_model import model_auth
from . import auth
from .database import engine, get_db
from .config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# 创建数据库表（异步引擎会自动处理）
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


app = FastAPI(on_startup=[init_db])


@app.post("/token", response_model=model_auth.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """异步登录接口，返回访问令牌和刷新令牌"""
    logger.info(f"Login attempt for username: {form_data.username}")

    # 异步查询用户
    try:
        result = await db.execute(
            select(models.UserConfig).where(
                models.UserConfig.name == form_data.username
            )
        )
        user = result.scalars().first()

        if not user or not auth.verify_password(form_data.password, user.password):
            logger.warning(f"Invalid credentials for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 创建令牌
        access_token = auth.create_access_token(
            data={"sub": user.name},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        refresh_token = auth.create_refresh_token(
            data={"sub": user.name},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        logger.info(f"User {user.name} logged in successfully")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@app.post("/refresh-token", response_model=model_auth.Token)
async def refresh_access_token(request: Request, db: AsyncSession = Depends(get_db)):
    """异步刷新访问令牌"""
    try:
        refresh_token = request.headers.get("Authorization", "").split(" ")[1]
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username = payload.get("sub")

        if not username:
            logger.warning("Invalid refresh token: missing subject")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        # 验证用户是否存在
        result = await db.execute(
            select(models.UserConfig).where(models.UserConfig.name == username)
        )
        if not result.scalars().first():
            logger.warning(f"User not found: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        new_access_token = auth.create_access_token(
            data={"sub": username},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        logger.info(f"Refreshed token for user: {username}")
        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except (JWTError, IndexError) as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )


@app.get("/users/me", response_model=model_auth.UserInDB)
async def read_users_me(
    current_user: Annotated[models.UserConfig, Depends(auth.get_current_active_user)],
):
    """获取当前用户信息"""
    return current_user


@app.post("/register", response_model=model_auth.UserInDB)
async def register_user(
    user_data: model_auth.UserCreate, db: AsyncSession = Depends(get_db)
):
    """异步用户注册"""
    try:
        # 检查用户名是否已存在
        result = await db.execute(
            select(models.UserConfig).where(models.UserConfig.name == user_data.name)
        )
        if result.scalars().first():
            logger.warning(f"Username already exists: {user_data.name}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        # 创建新用户
        hashed_password = auth.get_password_hash(user_data.password)
        new_user = models.UserConfig(
            name=user_data.name,
            password=hashed_password,
            core_llm_name=user_data.core_llm_name,
            core_llm_url=user_data.core_llm_url,
            core_llm_key=user_data.core_llm_key,
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logger.info(f"New user registered: {user_data.name}")
        return new_user
    except Exception as e:
        await db.rollback()
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@app.post("/logout")
async def logout(
    current_user: models.UserConfig = Depends(auth.get_current_active_user),
):
    """用户登出（实际应用中应实现令牌黑名单）"""
    logger.info(f"User {current_user.name} logged out")
    return {"message": "Successfully logged out"}

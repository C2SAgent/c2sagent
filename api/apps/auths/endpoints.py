from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated
from model import model_agent as models
from . import schemas, auth
from .database import engine, get_db
from .config import settings
from sqlalchemy.orm import Session
from jose import JWTError, jwt

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.UserConfig).filter(models.UserConfig.name == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(
        data={"sub": user.name},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = auth.create_refresh_token(
        data={"sub": user.name},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@app.post("/refresh-token", response_model=schemas.Token)
async def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # 生成新的访问Token
        new_access_token = auth.create_access_token(
            data={"sub": username},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,  # 刷新Token不变
            "token_type": "bearer",
        }
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@app.get("/users/me", response_model=schemas.UserInDB)
async def read_users_me(
    current_user: Annotated[models.UserConfig, Depends(auth.get_current_active_user)]
):
    return current_user

@app.post("/register", response_model=schemas.UserInDB)
async def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    db_user = db.query(models.UserConfig).filter(models.UserConfig.name == user.name).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.UserConfig(
        name=user.name,
        password=hashed_password,
        core_llm_name=user.core_llm_name,
        core_llm_url=user.core_llm_url,
        core_llm_key=user.core_llm_key
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/logout")
async def logout(
    current_user: models.UserConfig = Depends(auth.get_current_active_user)
):
    # 在实际应用中，您可能需要将Token加入黑名单
    return {"message": "Successfully logged out"}
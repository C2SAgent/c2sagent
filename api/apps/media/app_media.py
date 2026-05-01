from datetime import datetime
import json
import uuid

from fastapi import (
    Body,
    Depends,
    FastAPI,
    Request,
)
from fastapi.encoders import jsonable_encoder

from api.apps.agent.database import engine
from api.apps.auths import auth
from api.utils.api_utils import BaseResponse
from api.utils.db_utils import create_init_db
from core import config as settings
from core.db.base import DatabaseManager
from model import model_agent as models

DATABASE_URL = settings.DATABASE_URL
db = DatabaseManager(DATABASE_URL)


from api.utils.db_utils import create_init_db

app = FastAPI(on_startup=[create_init_db(engine, models.Base)])


@app.get("/list", response_model=BaseResponse)
async def do_media_list(
    request: Request,
    current_user: models.UserConfig = Depends(auth.get_current_active_user),
):
    medias = await db.fetch_all(models.UserAndMedia, {"user_id": current_user.id})
    return {"data": jsonable_encoder(medias)}


@app.post("/update", response_model=BaseResponse)
async def do_media_update(
    request: Request,
    name: str = Body(...),
    jct: str = Body(...),
    sessdata: str = Body(...),
    current_user: models.UserConfig = Depends(auth.get_current_active_user),
):
    await db.update(
        models.UserAndMedia,
        {"user_id": current_user.id, "name": name, "jct": jct, "sessdata": sessdata},
    )
    return BaseResponse()

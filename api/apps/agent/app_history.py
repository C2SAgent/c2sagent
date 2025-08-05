from datetime import datetime
from fastapi import Body, FastAPI, Query, Request, Depends
from api.apps.auths import auth
from api.utils.api_utils import BaseResponse, ListResponse
from core.db.base import DatabaseManager
from model import model_agent as models
from core.db.base_mongo import MongoDBManager
from api.apps.agent.config import settings

from .database import engine

DATABASE_URL = settings.DATABASE_URL
db = DatabaseManager(DATABASE_URL)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


app = FastAPI(on_startup=[init_db])


@app.get("/list", response_model=ListResponse)
async def do_list_session(
    request: Request,
    current_user: models.UserConfig = Depends(auth.get_current_active_user),
):
    """Endpoint to interact with the Agent.

    Args:
        request (AgentRequest): Contains all the parameters needed to query the agent.

    Returns:
        AgentResponse: The response from the agent.
    """
    mongo = MongoDBManager()
    try:
        await mongo.connect()
        sessions = await mongo.get_sessions(user_id=str(current_user.id))
    finally:
        await mongo.close()
    return ListResponse(data=sessions)


@app.get("/load", response_model=BaseResponse)
async def do_load_session(
    request: Request,
    session_id: str = Query(...),
    current_user: models.UserConfig = Depends(auth.get_current_active_user),
):
    mongo = MongoDBManager()
    try:
        await mongo.connect()
        session = await mongo.get_session_by_ids(
            user_id=str(current_user.id), session_id=session_id
        )
    finally:
        await mongo.close()
    print(session)
    return BaseResponse(data=session)


@app.post("/create", response_model=BaseResponse)
async def do_create_session(
    request: Request,
    current_user: models.UserConfig = Depends(auth.get_current_active_user),
):
    mongo = MongoDBManager()
    try:
        await mongo.connect()
        question_msg = {
            "role": "system",
            "content": "您好，我们是一个智能团队，叫小C，有什么安排的都可以向我提呦~~~",
            "timestamp": datetime.now().isoformat(),
        }
        session_id = await mongo.create_session(str(current_user.id), question_msg)
        result = await mongo.get_session_by_ids(str(current_user.id), session_id)
    finally:
        await mongo.close()

    return BaseResponse(data=result)


@app.post("/delete", response_model=BaseResponse)
async def do_delete_session(
    request: Request,
    session_id: str = Body(...),
    current_user: models.UserConfig = Depends(auth.get_current_active_user),
):
    mongo = MongoDBManager()
    try:
        await mongo.connect()
        result = await mongo.delete_session(session_id)
    finally:
        await mongo.close()
    return BaseResponse(data=result)

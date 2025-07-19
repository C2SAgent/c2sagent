from typing import Annotated
from fastapi import Body, FastAPI, Depends, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder
from grpc import Status
from api.apps.auths import auth
from api.apps.auths.dependencies import token_required
from api.utils.api_utils import BaseResponse, ListResponse
from core.db.base import DatabaseManager
from model.api_model import model_create_agent
from model import model_agent as models
from api.apps.agent.config import settings
from .database import engine, get_db
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL
db = DatabaseManager(DATABASE_URL)

# 异步创建表
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

app = FastAPI(on_startup=[init_db])

@app.post("/create", response_model=BaseResponse)
async def do_agent_create(
    request: Request,
    name: str = Body(...),
    description: str = Body(""),
    llm_name: str = Body(""),
    llm_url: str = Body(""),
    llm_key: str = Body(""),
    version: str = Body("1.0.0"),
    streaming: bool = Body(False),
    examples: list[str] = Body([]),
    current_user: models.UserConfig = Depends(auth.get_current_active_user)
):
    """异步创建Agent"""
    try:
        await db.insert(models.AgentCard, {
            "name": name,
            "description": description,
            "version": version,
            "streaming": streaming,
            "examples": examples,
            "user_id": current_user.id,
            "llm_name": llm_name,
            "llm_url": llm_url,
            "llm_key": llm_key
        })
        logger.info(f"User {current_user.id} created agent: {name}")
        return BaseResponse()
    except Exception as e:
        logger.error(f"Agent creation failed: {str(e)}")
        raise HTTPException(
            status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent creation failed"
        )

@app.get("/list", response_model=ListResponse)
async def do_agent_list(
    current_user: Annotated[models.UserConfig, Depends(auth.get_current_active_user)]
):
    """异步获取用户Agent列表"""
    try:
        agents = await db.fetch_all(models.AgentCard, {"user_id": current_user.id})
        return {"data": jsonable_encoder(agents)}
    except Exception as e:
        logger.error(f"Failed to list agents: {str(e)}")
        raise HTTPException(
            status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list agents"
        )

@app.post("/delete", response_model=BaseResponse)
async def do_agent_delete(
    request: Request,
    id: int = Body(...),
    current_user: models.UserConfig = Depends(auth.get_current_active_user)
):
    """异步删除Agent"""
    try:
        # 先验证Agent属于当前用户
        agent = await db.fetch_one(models.AgentCard, id=id, user_id=current_user.id)
        if not agent:
            raise HTTPException(
                status_code=Status.HTTP_404_NOT_FOUND,
                detail="Agent not found or not owned by user"
            )
            
        await db.delete(models.AgentCard, id=id)
        logger.info(f"User {current_user.id} deleted agent ID: {id}")
        return BaseResponse()
    except Exception as e:
        logger.error(f"Agent deletion failed: {str(e)}")
        raise HTTPException(
            status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent deletion failed"
        )

@app.post("/corr_mcp", response_model=BaseResponse)
async def do_agent_corr_mcp(
    request: Request,
    agent_card_id: int = Body(...),
    mcp_server_id: int = Body(...),
    current_user: models.UserConfig = Depends(auth.get_current_active_user)
):
    """关联Agent和MCP服务"""
    try:
        # 验证Agent属于当前用户
        agent = await db.fetch_one(models.AgentCard, id=agent_card_id, user_id=current_user.id)
        if not agent:
            raise HTTPException(
                status_code=Status.HTTP_404_NOT_FOUND,
                detail="Agent not found or not owned by user"
            )
            
        await db.insert(models.AgentCardAndMcpServer, {
            "agent_card_id": agent_card_id,
            "mcp_server_id": mcp_server_id
        })
        logger.info(f"User {current_user.id} linked agent {agent_card_id} to MCP {mcp_server_id}")
        return BaseResponse()
    except Exception as e:
        logger.error(f"MCP correlation failed: {str(e)}")
        raise HTTPException(
            status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to correlate agent with MCP"
        )

@app.post("/discorr_mcp", response_model=BaseResponse)
async def do_agent_discorr_mcp(
    request: Request,
    agent_card_id: int = Body(...),
    mcp_server_id: int = Body(...),
    current_user: models.UserConfig = Depends(auth.get_current_active_user)
):
    """取消Agent和MCP服务关联"""
    try:
        # 验证关联关系存在
        relation = await db.fetch_one(
            models.AgentCardAndMcpServer,
            agent_card_id=agent_card_id,
            mcp_server_id=mcp_server_id
        )
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No such correlation exists"
            )
            
        await db.delete(
            models.AgentCardAndMcpServer,
            agent_card_id=agent_card_id,
            mcp_server_id=mcp_server_id
        )
        logger.info(f"User {current_user.id} unlinked agent {agent_card_id} from MCP {mcp_server_id}")
        return BaseResponse()
    except Exception as e:
        logger.error(f"MCP disconnection failed: {str(e)}")
        raise HTTPException(
            status_code=Status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disconnect agent from MCP"
        )

@app.get("/find_mcp", response_model=BaseResponse)
async def do_find_mcp(
    request: Request,
    agent_card_id: int = Query(...),
    current_user: models.UserConfig = Depends(auth.get_current_active_user)
):
    """查找Agent关联的MCP服务"""
    try:
        # 验证Agent属于当前用户
        agent = await db.fetch_one(models.AgentCard, id=agent_card_id, user_id=current_user.id)
        if not agent:
            raise HTTPException(
                status_code=Status.HTTP_404_NOT_FOUND,
                detail="Agent not found or not owned by user"
            )
            
        relation = await db.fetch_one(
            models.AgentCardAndMcpServer,
            agent_card_id=agent_card_id
        )
        
        if not relation:
            return {"data": None}
            
        mcp_server = await db.fetch_one(models.McpServer, id=relation.mcp_server_id)
        logger.info(f"Found MCP {relation.mcp_server_id} for agent {agent_card_id}")
        return {"data": jsonable_encoder(mcp_server)}
    except Exception as e:
        logger.error(f"Failed to find MCP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find MCP server"
        )
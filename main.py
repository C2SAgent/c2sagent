from fastapi import FastAPI
from api.apps.auths.endpoints import app as auth_app
from api.apps.agent.manager_agent_card import app as manager_agent
from api.apps.agent.manager_mcp_server import app as manager_mcp
from api.apps.agent.app_a2a_client import app as a2a_app
from api.apps.agent.app_mcp_client import app as mcp_app
from fastapi.middleware.cors import CORSMiddleware

from src_mcp.mcp_client import lifespan

# 创建主应用
app = FastAPI(title="C2SAgent", lifespan=lifespan)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该更严格
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载认证子应用
app.mount("/auth", auth_app)
app.mount("/agent", manager_agent)
app.mount("/mcp", manager_mcp)
app.mount("/chat", a2a_app)
app.mount("/mcp_client", mcp_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI
from api.apps.auths.endpoints import app as auth_app
from api.apps.agent.manager_agent_card import app as agent_app
from api.apps.agent.manager_mcp_server import app as mcp_app
from fastapi.middleware.cors import CORSMiddleware

# 创建主应用
app = FastAPI(title="C2SAgent")

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
app.mount("/agent", agent_app)
app.mount("/mcp", mcp_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
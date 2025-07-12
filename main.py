import os
from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src_mcp.mcp_client import lifespan

from api.apps.auths.endpoints import app as app_auth
from api.apps.agent.manager_agent_card import app as manager_agent
from api.apps.agent.manager_mcp_server import app as manager_mcp
from api.apps.agent.app_a2a import app as app_a2a
from api.apps.agent.app_mcp import app as app_mcp
from api.apps.agent.app_history import app as app_history

from src_a2a.a2a_server import main as main_a2a
from src_mcp.mcp_server.server.mcp_server import main as main_mcp


# 创建主应用
app = FastAPI(title="C2SAgent", lifespan=lifespan)

# 静态文件位置
static_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=f"{static_dir}/static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc/redoc.standalone.js",
    )


# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该更严格
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载认证子应用
app.mount("/app_auth", app_auth)
app.mount("/manager_agent", manager_agent)
app.mount("/manager_mcp", manager_mcp)
app.mount("/app_a2a", app_a2a)
app.mount("/app_mcp", app_mcp)
app.mount("/app_history", app_history)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
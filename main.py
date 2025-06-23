from fastapi import FastAPI
from project.view.server_chat import router_chat, lifespan

# 初始化 FastAPI 应用
app = FastAPI(title="MCP Client", lifespan=lifespan)
app.include_router(router_chat.chat_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
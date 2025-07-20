# 初始化
from model.model_agent import AgentCard  # 假设这是之前定义的模型
from core.db.base import PostgreSQLCRUD

db = PostgreSQLCRUD("postgresql://ChenXAn:ChenXAn@localhost:5432/manager_agent")

# 插入数据
new_agent = db.insert(
    AgentCard, {"name": "AI Assistant", "description": "智能助手", "streaming": True}
)

# 查询单条
agent = db.fetch_one(AgentCard, {"name": "AI Assistant"})
print(agent.id, agent.name)

# 查询多条
agents = db.fetch_all(AgentCard, order_by="id desc", limit=10)
for a in agents:
    print(a.name)

# 更新
updated = db.update(AgentCard, {"id": 1}, {"description": "新版智能助手"})
print(f"Updated {updated} records")

# 删除
deleted = db.delete(AgentCard, {"id": 1})
print(f"Deleted {deleted} records")

# 使用上下文管理
with PostgreSQLCRUD("postgresql://ChenXAn:ChenXAn@localhost:5432/manager_agent") as db:
    agent = db.fetch_one(AgentCard, {"name": "AI Assistant"})
    db.update(AgentCard, {"id": agent.id}, {"version": "2.0"})

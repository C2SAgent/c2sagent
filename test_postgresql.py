# 初始化
from model.model_agent import AgentCard  # 假设这是之前定义的模型
from core.db.base import DatabaseManager

# 初始化数据库连接
db = DatabaseManager("postgresql://postgres:postgre@localhost/manager_agent")

# 创建所有表（首次运行时需要）
# db.create_all_tables()

# 插入AgentCard记录
new_agent = db.insert(AgentCard, {
    "name": "AI Assistant",
    "description": "智能助手",
    "streaming": True
})

# 查询所有AgentCard
agents = db.fetch_all(AgentCard)
for agent in agents:
    print(agent.name, agent.description)

# 条件查询
python_agents = db.fetch_all(
    AgentCard,
    filters={"name": "AI Assistant"},
    order_by="id desc",
    limit=5
)

# 更新记录
updated_count = db.update(
    AgentCard,
    filters={"id": 1},
    update_data={"description": "新版智能助手"}
)

# 删除记录
deleted_count = db.delete(AgentCard, {"id": 1})

# 使用上下文管理
with DatabaseManager("postgresql://postgres:postgre@localhost/manager_agent") as db:
    agent = db.fetch_one(AgentCard, {"name": "AI Assistant"})
    if agent:
        db.update(AgentCard, {"id": agent.id}, {"version": "2.0"})

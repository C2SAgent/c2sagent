# main.py
import asyncio
from datetime import datetime, timedelta

# from core.db.base import DatabaseManager
from core.db.base_mindsdb import TimeSeriesService
from core.db.database import init_db, get_db_session
from api.apps.agent.config import settings
from model.model_agent import AgentCard
from model.model_timeseries import DataSource


# MindsDB配置
MINDSDB_CONFIG = {
    "host": "localhost",
    "port": 47335,  # MindsDB 默认端口是 47335，不是 5432
    "user": "mindsdb_user",  # MindsDB 默认用户可能是 'mindsdb'
    "password": "mindsdb_password",
    "database": "mindsdb",  # 保持为 mindsdb，这是 MindsDB 的系统数据库
}


async def main():
    # 初始化数据库
    # DATABASE_URL = settings.DATABASE_URL
    # db = DatabaseManager(DATABASE_URL)

    # agent_finds = await db.fetch_all(AgentCard, {"user_id": 36})
    # print(agent_finds)
    # await init_db()

    # # 创建服务实例
    data_points = {
        "id": 1,
        "name": "test",
        "params": [{"value": i * 10} for i in range(100, 0, -1)],
    }
    db = TimeSeriesService(
        MINDSDB_CONFIG, "postgresql+asyncpg://postgres:postgre@localhost/timeseries"
    )
    await db.save_time_series_data(DataSource, data_points)
    # # 获取数据库会话
    # # async for session in get_db_session():
    #     # 示例1: 保存时序数据
    # data_points = [
    #     {'timestamp': datetime.now() - timedelta(days=i), 'value': i * 10}
    #     for i in range(100, 0, -1)
    # ]

    # # 假设我们已经有一个数据源ID为1
    # await service.save_time_series_data(1, data_points)
    # print("Data saved successfully")

    # # 示例2: 训练模型
    # training_params = {
    #     'window': 10,
    #     'horizon': 5
    # }
    # training_result = await service.train_model(1, training_params)
    # print("Model trained:", training_result)

    # # 示例3: 进行预测
    # predictions = await service.predict_future_values(1, 5)
    # print("Predictions:", predictions)


if __name__ == "__main__":
    asyncio.run(main())

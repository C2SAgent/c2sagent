from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from datetime import datetime
import os

load_dotenv()

# 配置MongoDB连接（从环境变量读取更安全）
MONGO_URI = os.getenv(
    "MONGO_URI", "mongodb://root:your_secure_password@localhost:27017/"
)
DB_NAME = "chatdb"
COLLECTION_NAME = "sessions"


class MongoDBManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None

    async def connect(self):
        """建立数据库连接"""
        try:
            self.client = AsyncIOMotorClient(MONGO_URI)
            self.db = self.client[DB_NAME]
            self.collection = self.db[COLLECTION_NAME]
            print(
                f"Connected to MongoDB! Database: {DB_NAME}, Collection: {COLLECTION_NAME}"
            )
        except PyMongoError as e:
            print(f"Connection failed: {e}")
            raise

    async def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()
            print("Connection closed.")

    # ------------------- CRUD 操作 -------------------
    async def create_session(self, user_id: str, initial_message: dict) -> str:
        """创建新会话"""
        session_data = {
            "session_id": f"sess_{datetime.now().timestamp()}",
            "user_id": user_id,
            "title": initial_message["content"][:50],  # 截取前50个字符作为标题
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": [initial_message],
        }

        try:
            result = await self.collection.insert_one(session_data)
            print(f"Created session with ID: {result.inserted_id}")
            return session_data["session_id"]
        except PyMongoError as e:
            print(f"Create failed: {e}")
            raise

    async def get_sessions(self, user_id: str, limit: int = 10) -> list:
        """获取用户最近的会话"""
        try:
            cursor = (
                self.collection.find(
                    {"user_id": user_id},
                    {
                        "_id": 0,
                        "session_id": 1,
                        "title": 1,
                        "created_at": 1,
                        "messages": {"$slice": 1},
                    },
                )
                .sort("updated_at", -1)
                .limit(limit)
            )

            return await cursor.to_list(length=limit)
        except PyMongoError as e:
            print(f"Query failed: {e}")
            raise

    async def get_session_by_ids(self, user_id: str, session_id: str) -> dict:
        """查询特定用户的特定会话（精确匹配）"""
        try:
            session = await self.collection.find_one(
                {"user_id": user_id, "session_id": session_id}, {"_id": 0}
            )
            return session
        except PyMongoError as e:
            print(f"Query failed: {e}")
            raise

    async def add_message(self, session_id: str, message: dict) -> int:
        """向会话追加消息"""
        try:
            result = await self.collection.update_one(
                {"session_id": session_id},
                {
                    "$push": {"messages": message},
                    "$set": {
                        "updated_at": datetime.now().isoformat(),
                        "title": message["content"][:50],  # 更新标题为最新消息的前50个字符
                    },
                },
            )
            print(
                f"Added message to session {session_id}. Modified count: {result.modified_count}"
            )
            return result.modified_count
        except PyMongoError as e:
            print(f"Update failed: {e}")
            raise

    async def delete_session(self, session_id: str) -> int:
        """删除会话"""
        try:
            result = await self.collection.delete_one({"session_id": session_id})
            print(f"Deleted {result.deleted_count} session(s)")
            return result.deleted_count
        except PyMongoError as e:
            print(f"Delete failed: {e}")
            raise


# ------------------- 异步使用示例 -------------------
async def main():
    mongo = MongoDBManager()

    try:
        await mongo.connect()

        # 创建测试会话
        test_msg = {
            "role": "user",
            "content": "Hello Async Mongo!",
            "timestamp": datetime.now().isoformat(),
        }
        session_id = await mongo.create_session("test_user", test_msg)

        # 查询会话
        session = await mongo.get_session_by_ids("test_user", session_id)
        print("Session:", session)

        # 添加新消息
        new_msg = {
            "role": "assistant",
            "content": "Hi there! How can I help?",
            "timestamp": datetime.now().isoformat(),
        }
        await mongo.add_message(session_id, new_msg)

        # 查询更新后的会话
        updated_session = await mongo.get_session_by_ids("test_user", session_id)
        print("Updated session:", updated_session)

        # 获取用户所有会话
        sessions = await mongo.get_sessions("test_user")
        print("User sessions:", sessions)

        # 清理测试数据
        # await mongo.delete_session(session_id)

    finally:
        await mongo.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

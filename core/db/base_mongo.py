from pymongo import MongoClient
from pymongo.errors import PyMongoError
from datetime import datetime
import os

# 配置MongoDB连接（从环境变量读取更安全）
MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:your_secure_password@localhost:27017/")
DB_NAME = "chatdb"
COLLECTION_NAME = "sessions"

class MongoDBManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        
    def connect(self):
        """建立数据库连接"""
        try:
            self.client = MongoClient(MONGO_URI)
            self.db = self.client[DB_NAME]
            self.collection = self.db[COLLECTION_NAME]
            print(f"Connected to MongoDB! Database: {DB_NAME}, Collection: {COLLECTION_NAME}")
        except PyMongoError as e:
            print(f"Connection failed: {e}")
            raise

    def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()
            print("Connection closed.")

    # ------------------- CRUD 操作 ------------------- 
    def create_session(self, user_id: str, initial_message: dict):
        """创建新会话"""
        session_data = {
            "session_id": f"sess_{datetime.now().timestamp()}",
            "user_id": user_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "messages": [initial_message]
        }
        
        try:
            result = self.collection.insert_one(session_data)
            print(f"Created session with ID: {result.inserted_id}")
            return session_data["session_id"]
        except PyMongoError as e:
            print(f"Create failed: {e}")
            return None

    def get_sessions(self, user_id: str, limit: int = 10):
        """获取用户最近的会话"""
        try:
            sessions = self.collection.find(
                {"user_id": user_id},
                {"_id": 0, "session_id": 1, "created_at": 1, "messages": {"$slice": 1}}  # 只返回第一条消息摘要
            ).sort("updated_at", -1).limit(limit)
            
            return list(sessions)
        except PyMongoError as e:
            print(f"Query failed: {e}")
            return []

    def get_session_by_ids(self, user_id: str, session_id: str):
        """查询特定用户的特定会话（精确匹配）"""
        try:
            session = self.collection.find_one(
                {
                    "user_id": user_id,
                    "session_id": session_id
                },
                {"_id": 0}  # 排除MongoDB默认的_id字段
            )
            return session
        except PyMongoError as e:
            print(f"Query failed: {e}")
            return None

    def add_message(self, session_id: str, message: dict):
        """向会话追加消息"""
        try:
            result = self.collection.update_one(
                {"session_id": session_id},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": datetime.now()}
                }
            )
            print(f"Added message to session {session_id}. Modified count: {result.modified_count}")
            return result.modified_count
        except PyMongoError as e:
            print(f"Update failed: {e}")
            return 0

    def delete_session(self, session_id: str):
        """删除会话"""
        try:
            result = self.collection.delete_one({"session_id": session_id})
            print(f"Deleted {result.deleted_count} session(s)")
            return result.deleted_count
        except PyMongoError as e:
            print(f"Delete failed: {e}")
            return 0

# ------------------- 使用示例 ------------------- 
if __name__ == "__main__":
    mongo = MongoDBManager()
    
    try:
        mongo.connect()
        
        # 创建测试会话
        test_msg = {
            "role": "user",
            "content": "Hello MongoDB!",
            "timestamp": datetime.now()
        }
        session_id = mongo.create_session("36", test_msg)
        
        # 查询会话
        sessions = mongo.get_session_by_ids("36", session_id)
        print(sessions)
        # print(f"Found {len(sessions)} sessions:")
        # for sess in sessions:
        #     print(f" - {sess['session_id']} (Created at: {sess['created_at']})")
        
        # # 添加新消息
        # new_msg = {
        #     "role": "assistant",
        #     "content": "Hi there! How can I help?",
        #     "timestamp": datetime.now()
        # }
        # mongo.add_message(session_id, new_msg)
        
        # 删除会话（取消注释执行）
        # mongo.delete_session(session_id)
        
    finally:
        mongo.close()
// mongo-init.js

/**
 * MongoDB 初始化脚本
 * 功能：创建数据库、集合、索引
 * 执行方式：通过Docker容器启动时自动执行
 */

// ==================== 数据库初始化 ====================
print("=> 开始初始化数据库...");

// 创建/切换到 chatdb 数据库
db = db.getSiblingDB('chatdb');
print(`=> 数据库创建成功: ${db.getName()}`);

// ==================== 集合初始化 ====================
// 创建 sessions 集合（如果不存在）
if (!db.getCollectionNames().includes("sessions")) {
  db.createCollection("sessions");
  print("=> 集合创建成功: sessions");
} else {
  print("=> 集合已存在: sessions");
}

// ==================== 索引创建 ====================
print("=> 开始创建索引...");

// 为 sessions 集合创建索引
try {
  // 用户ID索引（加速按用户查询）
  db.sessions.createIndex(
    { "user_id": 1 },
    { name: "idx_user_id" }
  );
  
  // 会话ID唯一索引
  db.sessions.createIndex(
    { "session_id": 1 },
    { 
      name: "idx_session_id_unique",
      unique: true 
    }
  );
  
  // 更新时间倒序索引（用于最近会话排序）
  db.sessions.createIndex(
    { "updated_at": -1 },
    { name: "idx_updated_at_desc" }
  );
  
  print("=> 索引创建成功");
  printjson(db.sessions.getIndexes());
} catch (e) {
  print(`=> 索引创建失败: ${e}`);
}

// ==================== 测试数据 ====================
// 仅开发环境插入测试数据

print("=> 正在插入开发测试数据...");

const testSessions = [
  {
    session_id: "dev_session_1",
    user_id: "dev_user_001",
    created_at: new Date(),
    updated_at: new Date(),
    title: "开发测试会话1",
    messages: [
      {
        role: "user",
        content: "这是一个测试消息",
        timestamp: new Date()
      },
      {
        role: "assistant",
        content: "这是AI回复内容",
        timestamp: new Date()
      }
    ]
  },
  {
    session_id: "dev_session_2",
    user_id: "dev_user_002",
    created_at: new Date(),
    updated_at: new Date(),
    title: "开发测试会话2",
    messages: [
      {
        role: "user",
        content: "另一个测试对话",
        timestamp: new Date()
      }
    ]
  }
];

try {
  const result = db.sessions.insertMany(testSessions);
  print(`=> 插入 ${result.insertedCount} 条测试数据`);
} catch (e) {
  print(`=> 测试数据插入失败: ${e}`);
}


// ==================== 验证 ====================
print("\n=> 初始化结果验证:");
printjson({
  database: db.getName(),
  collections: db.getCollectionNames(),
  sessionCount: db.sessions.countDocuments(),
  indexes: db.sessions.getIndexes()
});

print("\n===== 初始化完成 =====");
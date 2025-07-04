-- 创建user_config表
CREATE TABLE user_config (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    core_llm_name VARCHAR(255),
    core_llm_url VARCHAR(255),
    core_llm_key VARCHAR(255),
    UNIQUE name
);

-- 创建llm_config表
CREATE TABLE llm_config (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(255) NOT NULL,
    key VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user_config (id) ON DELETE CASCADE
);

-- 创建关联表user_config_and_llm_config
CREATE TABLE user_config_and_llm_config (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    llm_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user_config (id) ON DELETE CASCADE,
    FOREIGN KEY (llm_id) REFERENCES llm_config (id) ON DELETE CASCADE,
    UNIQUE (user_id, llm_id)  -- 防止重复关联
);

-- 创建agent_card表（表名统一小写）
CREATE TABLE agent_card (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    url VARCHAR(255),
    version VARCHAR(50),
    streaming BOOLEAN,
    examples JSONB,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user_config (id) ON DELETE CASCADE
);

-- 创建skill表（修复原skills拼写不一致）
CREATE TABLE skill (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tags JSONB,
    examples JSONB
);

-- 创建input_mode表（表名改为下划线风格）
CREATE TABLE input_mode (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- 创建output_mode表（表名改为下划线风格）
CREATE TABLE output_mode (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- 创建agent_card_and_skill关联表（修复外键引用）
CREATE TABLE agent_card_and_skill (
    id SERIAL PRIMARY KEY,
    agent_card_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    FOREIGN KEY (agent_card_id) REFERENCES agent_card (id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skill (id) ON DELETE CASCADE,
    UNIQUE (agent_card_id, skill_id)
);

-- 创建agent_card_and_input_mode关联表（修复列名不一致）
CREATE TABLE agent_card_and_input_mode (
    id SERIAL PRIMARY KEY,
    agent_card_id INTEGER NOT NULL,
    input_mode_id INTEGER NOT NULL,
    FOREIGN KEY (agent_card_id) REFERENCES agent_card (id) ON DELETE CASCADE,
    FOREIGN KEY (input_mode_id) REFERENCES input_mode (id) ON DELETE CASCADE,
    UNIQUE (agent_card_id, input_mode_id)
);

-- 创建agent_card_and_output_mode关联表
CREATE TABLE agent_card_and_output_mode (
    id SERIAL PRIMARY KEY,
    agent_card_id INTEGER NOT NULL,
    output_mode_id INTEGER NOT NULL,
    FOREIGN KEY (agent_card_id) REFERENCES agent_card (id) ON DELETE CASCADE,
    FOREIGN KEY (output_mode_id) REFERENCES output_mode (id) ON DELETE CASCADE,
    UNIQUE (agent_card_id, output_mode_id)
);

-- 创建mcp_server表
CREATE TABLE mcp_server (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user_config (id) ON DELETE CASCADE
);

-- 创建agent_card_and_mcp_server关联表（修复SERIAL拼写错误）
CREATE TABLE agent_card_and_mcp_server (
    id SERIAL PRIMARY KEY,
    agent_card_id INTEGER NOT NULL,
    mcp_server_id INTEGER NOT NULL,
    FOREIGN KEY (agent_card_id) REFERENCES agent_card (id) ON DELETE CASCADE,
    FOREIGN KEY (mcp_server_id) REFERENCES mcp_server (id) ON DELETE CASCADE,
    UNIQUE (agent_card_id, mcp_server_id)
);

-- 创建tool表
CREATE TABLE tool (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(255) NOT NULL
);

-- 创建mcp_server_and_tool关联表
CREATE TABLE mcp_server_and_tool (
    id SERIAL PRIMARY KEY,
    mcp_server_id INTEGER NOT NULL,
    tool_id INTEGER NOT NULL,
    FOREIGN KEY (mcp_server_id) REFERENCES mcp_server (id) ON DELETE CASCADE,
    FOREIGN KEY (tool_id) REFERENCES tool (id) ON DELETE CASCADE,
    UNIQUE (mcp_server_id, tool_id)
);
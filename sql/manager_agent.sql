-- Agent_card表
CREATE TABLE Agent_card (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    url VARCHAR(255),
    version VARCHAR(50),
    streaming BOOLEAN,
    examples JSONB
);

-- skills表
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tags JSONB,
    examples JSONB
);

-- inputModes表
CREATE TABLE inputModes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- outputModes表
CREATE TABLE outputModes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Agent_card_and_skill表（关联表）
CREATE TABLE Agent_card_and_skill (
    id SERIAL PRIMARY KEY,
    agent_card_id INT NOT NULL,
    skill_id INT NOT NULL,
    FOREIGN KEY (agent_card_id) REFERENCES Agent_card(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id)
);

-- Agent_card_and_inputModes表（关联表）
CREATE TABLE Agent_card_and_inputModes (
    id SERIAL PRIMARY KEY,
    agent_card_id INT NOT NULL,
    inputModes_id INT NOT NULL,
    FOREIGN KEY (agent_card_id) REFERENCES Agent_card(id),
    FOREIGN KEY (inputModes_id) REFERENCES inputModes(id)
);

-- Agent_card_and_outputModes表（关联表）
CREATE TABLE Agent_card_and_outputModes (
    id SERIAL PRIMARY KEY,
    agent_card_id INT NOT NULL,
    outputModes_id INT NOT NULL,
    FOREIGN KEY (agent_card_id) REFERENCES Agent_card(id),
    FOREIGN KEY (outputModes_id) REFERENCES outputModes(id)
);

-- mcp_server表
CREATE TABLE mcp_server (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(255) NOT NULL
);

-- agent_card_and_mcp_server表（关联表）
CREATE TABLE agent_card_and_mcp_server (
    id SERIAL PRIMARY KEY,
    agent_card_id INT NOT NULL,
    mcp_server_id INT NOT NULL,
    FOREIGN KEY (agent_card_id) REFERENCES Agent_card(id),
    FOREIGN KEY (mcp_server_id) REFERENCES mcp_server(id)
);

-- tool表
CREATE TABLE tool (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(255) NOT NULL
);

-- mcp_server_and_tool表（关联表）
CREATE TABLE mcp_server_and_tool (
    id SERIAL PRIMARY KEY,
    mcp_server_id INT NOT NULL,
    tool_id INT NOT NULL,
    FOREIGN KEY (mcp_server_id) REFERENCES mcp_server(id),
    FOREIGN KEY (tool_id) REFERENCES tool(id)
);
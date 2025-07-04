from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class UserConfig(Base):
    __tablename__ = 'user_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    core_llm_name = Column(String(255))
    core_llm_url = Column(String(255))
    core_llm_key = Column(String(255))

    # 关系定义
    llm_associations = relationship("UserAndLLM", back_populates="user_config")
    agent_cards = relationship("AgentCard", back_populates="user_config")

class LLMConfig(Base):
    __tablename__ = 'llm_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    key = Column(String(255), nullable=False)

    # 关系定义
    user_associations = relationship("UserAndLLM", back_populates="llm_config")

class UserAndLLM(Base):
    __tablename__ = 'user_config_and_llm_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user_config.id'), nullable=False)
    llm_id = Column(Integer, ForeignKey('llm_config.id'), nullable=False)

    # 关系定义
    user_config = relationship("UserConfig", back_populates="llm_associations")
    llm_config = relationship("LLMConfig", back_populates="user_associations")

class AgentCard(Base):
    __tablename__ = 'agent_card'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    url = Column(String(255))
    version = Column(String(50))
    streaming = Column(Boolean)
    examples = Column(JSONB)
    user_id = Column(Integer, ForeignKey('user_config.id'), nullable=False)

    llm_name = Column(String(255))
    llm_url = Column(String(255))
    llm_key = Column(String(255))

    # 关系定义
    user_config = relationship("UserConfig", back_populates="agent_cards")
    skills = relationship("AgentCardAndSkill", back_populates="agent_card")
    input_modes = relationship("AgentCardAndInputMode", back_populates="agent_card")
    output_modes = relationship("AgentCardAndOutputMode", back_populates="agent_card")
    mcp_servers = relationship("AgentCardAndMcpServer", back_populates="agent_card")

class Skill(Base):
    __tablename__ = 'skill'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    tags = Column(JSONB)
    examples = Column(JSONB)
    
    # 关系定义
    agent_cards = relationship("AgentCardAndSkill", back_populates="skill")

class InputMode(Base):
    __tablename__ = 'input_mode'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    
    # 关系定义
    agent_cards = relationship("AgentCardAndInputMode", back_populates="input_mode")

class OutputMode(Base):
    __tablename__ = 'output_mode'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    
    # 关系定义
    agent_cards = relationship("AgentCardAndOutputMode", back_populates="output_mode")

class AgentCardAndSkill(Base):
    __tablename__ = 'agent_card_and_skill'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_card_id = Column(Integer, ForeignKey('agent_card.id'), nullable=False)
    skill_id = Column(Integer, ForeignKey('skill.id'), nullable=False)
    
    # 关系定义
    agent_card = relationship("AgentCard", back_populates="skills")
    skill = relationship("Skill", back_populates="agent_cards")

class AgentCardAndInputMode(Base):
    __tablename__ = 'agent_card_and_input_mode'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_card_id = Column(Integer, ForeignKey('agent_card.id'), nullable=False)
    input_mode_id = Column(Integer, ForeignKey('input_mode.id'), nullable=False)
    
    # 关系定义
    agent_card = relationship("AgentCard", back_populates="input_modes")
    input_mode = relationship("InputMode", back_populates="agent_cards")

class AgentCardAndOutputMode(Base):
    __tablename__ = 'agent_card_and_output_mode'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_card_id = Column(Integer, ForeignKey('agent_card.id'), nullable=False)
    output_mode_id = Column(Integer, ForeignKey('output_mode.id'), nullable=False)
    
    # 关系定义
    agent_card = relationship("AgentCard", back_populates="output_modes")
    output_mode = relationship("OutputMode", back_populates="agent_cards")

class McpServer(Base):
    __tablename__ = 'mcp_server'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('user_config.id'), nullable=False)
    
    # 关系定义
    agent_cards = relationship("AgentCardAndMcpServer", back_populates="mcp_server")
    tools = relationship("McpServerAndTool", back_populates="mcp_server")

class AgentCardAndMcpServer(Base):
    __tablename__ = 'agent_card_and_mcp_server'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_card_id = Column(Integer, ForeignKey('agent_card.id'), nullable=False)
    mcp_server_id = Column(Integer, ForeignKey('mcp_server.id'), nullable=False)
    
    # 关系定义
    agent_card = relationship("AgentCard", back_populates="mcp_servers")
    mcp_server = relationship("McpServer", back_populates="agent_cards")

class Tool(Base):
    __tablename__ = 'tool'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(555), nullable=False)
    user_id = Column(Integer, ForeignKey('user_config.id'), nullable=False)

    # 关系定义
    mcp_servers = relationship("McpServerAndTool", back_populates="tool")

class McpServerAndTool(Base):
    __tablename__ = 'mcp_server_and_tool'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mcp_server_id = Column(Integer, ForeignKey('mcp_server.id'), nullable=False)
    tool_id = Column(Integer, ForeignKey('tool.id'), nullable=False)
    
    # 关系定义
    mcp_server = relationship("McpServer", back_populates="tools")
    tool = relationship("Tool", back_populates="mcp_servers")
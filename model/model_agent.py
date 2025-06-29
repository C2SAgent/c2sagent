from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class AgentCard(Base):
    """Agent_card 表模型"""
    __tablename__ = 'agent_card'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    url = Column(String(255))
    version = Column(String(50))
    streaming = Column(Boolean)
    examples = Column(JSONB)
    user_id = Column(String(255))
    
    # 定义关系
    skills = relationship("AgentCardAndSkill", back_populates="agent_card")
    input_modes = relationship("AgentCardAndInputModes", back_populates="agent_card")
    output_modes = relationship("AgentCardAndOutputModes", back_populates="agent_card")
    mcp_servers = relationship("AgentCardAndMcpServer", back_populates="agent_card")

class Skills(Base):
    """skills 表模型"""
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    tags = Column(JSONB)
    examples = Column(JSONB)
    
    agent_cards = relationship("AgentCardAndSkill", back_populates="skill")

class InputModes(Base):
    """inputModes 表模型"""
    __tablename__ = 'inputModes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    
    agent_cards = relationship("AgentCardAndInputModes", back_populates="input_mode")

class OutputModes(Base):
    """outputModes 表模型"""
    __tablename__ = 'outputModes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    
    agent_cards = relationship("AgentCardAndOutputModes", back_populates="output_mode")

class AgentCardAndSkill(Base):
    """Agent_card_and_skill 关联表模型"""
    __tablename__ = 'agent_card_and_skill'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_card_id = Column(Integer, ForeignKey('agent_card.id'), nullable=False)
    skill_id = Column(Integer, ForeignKey('skills.id'), nullable=False)
    
    # 定义关系
    agent_card = relationship("AgentCard", back_populates="skills")
    skill = relationship("Skills", back_populates="agent_cards")

class AgentCardAndInputModes(Base):
    """Agent_card_and_inputModes 关联表模型"""
    __tablename__ = 'agent_card_and_inputModes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_card_id = Column(Integer, ForeignKey('agent_card.id'), nullable=False)
    inputModes_id = Column(Integer, ForeignKey('inputModes.id'), nullable=False)
    
    # 定义关系
    agent_card = relationship("AgentCard", back_populates="input_modes")
    input_mode = relationship("InputModes", back_populates="agent_cards")

class AgentCardAndOutputModes(Base):
    """Agent_card_and_outputModes 关联表模型"""
    __tablename__ = 'agent_card_and_outputModes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_card_id = Column(Integer, ForeignKey('agent_card.id'), nullable=False)
    outputModes_id = Column(Integer, ForeignKey('outputModes.id'), nullable=False)
    
    # 定义关系
    agent_card = relationship("AgentCard", back_populates="output_modes")
    output_mode = relationship("OutputModes", back_populates="agent_cards")

class McpServer(Base):
    """mcp_server 表模型"""
    __tablename__ = 'mcp_server'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    
    agent_cards = relationship("AgentCardAndMcpServer", back_populates="mcp_server")
    tools = relationship("McpServerAndTool", back_populates="mcp_server")

class AgentCardAndMcpServer(Base):
    """agent_card_and_mcp_server 关联表模型"""
    __tablename__ = 'agent_card_and_mcp_server'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_card_id = Column(Integer, ForeignKey('agent_card.id'), nullable=False)
    mcp_server_id = Column(Integer, ForeignKey('mcp_server.id'), nullable=False)
    
    # 定义关系
    agent_card = relationship("AgentCard", back_populates="mcp_servers")
    mcp_server = relationship("McpServer", back_populates="agent_cards")

class Tool(Base):
    """tool 表模型"""
    __tablename__ = 'tool'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    
    mcp_servers = relationship("McpServerAndTool", back_populates="tool")

class McpServerAndTool(Base):
    """mcp_server_and_tool 关联表模型"""
    __tablename__ = 'mcp_server_and_tool'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mcp_server_id = Column(Integer, ForeignKey('mcp_server.id'), nullable=False)
    tool_id = Column(Integer, ForeignKey('tool.id'), nullable=False)
    
    # 定义关系
    mcp_server = relationship("McpServer", back_populates="tools")
    tool = relationship("Tool", back_populates="mcp_servers")


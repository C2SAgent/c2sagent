class UserConfig(Base):
    __tablename__ = 'user_config'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    password = Column(String(255))

    core_llm_name = Column(String(255))
    core_llm_url = Column(String(255))
    core_llm_key = Column(String(255))

    llm_configs = relationship("UserAndLLM", back_populates="user_config")
    agent_cards = relationship("AgentCard", back_populates="user_config")

class UserConfigAndLLMConfig(Base):
    __tablename__ = 'user_config_and_llm_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user_configs.id'), nullable=False)
    llm_id = Column(Integer, ForeignKey('llm_configs.id'), nullable=False)

    user_config = relationship("UserConfig", back_populates="llm_config")
    llm_config = relationship("LLMConfig", back_populates="user_config")


class LLMConfig(Base):
    __tablename__ = 'llm_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    url = Column(String(255))
    key = Column(String(255))

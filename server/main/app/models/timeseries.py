# models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()


class DataSource(Base):
    """数据源表，用于隔离不同数据源"""

    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, server_default="now()")
    params = Column(JSONB)  # 存储数据源特定的参数


class TimeSeriesData(Base):
    """时序数据表"""

    __tablename__ = "time_series_data"

    id = Column(Integer, primary_key=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default="now()")


class TrainedModel(Base):
    """训练好的模型记录表"""

    __tablename__ = "trained_models"

    id = Column(Integer, primary_key=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    status = Column(
        String(20), default="pending"
    )  # pending, training, completed, failed
    params = Column(JSONB)  # 模型参数
    metrics = Column(JSONB)  # 模型评估指标
    created_at = Column(DateTime, server_default="now()")
    updated_at = Column(DateTime, server_default="now()", onupdate="now()")

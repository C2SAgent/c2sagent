# base.py
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import Executable
import logging

Base = declarative_base()

class PostgreSQLCRUD:
    """PostgreSQL 基础 CRUD 操作类"""
    
    def __init__(self, db_url: str, pool_size: int = 5, max_overflow: int = 10):
        """
        初始化数据库连接
        
        :param db_url: 数据库连接字符串
                      格式: postgresql://username:password@host:port/database
        :param pool_size: 连接池大小
        :param max_overflow: 最大溢出连接数
        """
        try:
            self.engine = create_engine(
                db_url,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_pre_ping=True,  # 自动检测连接是否有效
                echo=False          # 设为True可查看SQL日志
            )
            self.Session = scoped_session(sessionmaker(bind=self.engine))
            logging.info("PostgreSQL connection established successfully")
        except exc.SQLAlchemyError as e:
            logging.error(f"Database connection failed: {e}")
            raise

    def get_session(self):
        """获取新的数据库会话"""
        return self.Session()

    def close_session(self):
        """关闭当前线程的会话"""
        self.Session.remove()

    def fetch_all(
        self, 
        model: Base, 
        filters: Optional[Dict] = None, 
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Base]:
        """
        查询多条记录
        
        :param model: SQLAlchemy 模型类
        :param filters: 过滤条件字典，如 {"name": "test"}
        :param order_by: 排序字段，如 "id desc"
        :param limit: 返回记录数限制
        :param offset: 偏移量
        :return: 模型实例列表
        """
        session = self.get_session()
        try:
            query = session.query(model)
            
            if filters:
                for key, value in filters.items():
                    if hasattr(model, key):
                        query = query.filter(getattr(model, key) == value)
            
            if order_by:
                if "desc" in order_by.lower():
                    field = order_by.split()[0]
                    query = query.order_by(getattr(model, field).desc())
                else:
                    query = query.order_by(getattr(model, order_by))
            
            if limit:
                query = query.limit(limit)
            
            if offset:
                query = query.offset(offset)
                
            return query.all()
        except exc.SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Fetch all error: {e}")
            raise
        finally:
            self.close_session()

    def fetch_one(
        self, 
        model: Base, 
        filters: Optional[Dict] = None
    ) -> Optional[Base]:
        """
        查询单条记录
        
        :param model: SQLAlchemy 模型类
        :param filters: 过滤条件字典
        :return: 模型实例或None
        """
        session = self.get_session()
        try:
            query = session.query(model)
            
            if filters:
                for key, value in filters.items():
                    if hasattr(model, key):
                        query = query.filter(getattr(model, key) == value)
            
            return query.first()
        except exc.SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Fetch one error: {e}")
            raise
        finally:
            self.close_session()

    def execute_raw_sql(
        self, 
        sql: str, 
        params: Optional[Dict] = None
    ) -> List[Dict]:
        """
        执行原始SQL查询
        
        :param sql: SQL语句
        :param params: 参数字典
        :return: 结果字典列表
        """
        session = self.get_session()
        try:
            result = session.execute(sql, params or {})
            return [dict(row) for row in result]
        except exc.SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Raw SQL error: {e}")
            raise
        finally:
            self.close_session()

    def insert(self, model: Base, data: Dict) -> Base:
        """
        插入单条记录
        
        :param model: SQLAlchemy 模型类
        :param data: 数据字典
        :return: 插入后的模型实例
        """
        session = self.get_session()
        try:
            instance = model(**data)
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance
        except exc.SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Insert error: {e}")
            raise
        finally:
            self.close_session()

    def bulk_insert(self, model: Base, data_list: List[Dict]) -> List[Base]:
        """
        批量插入记录
        
        :param model: SQLAlchemy 模型类
        :param data_list: 数据字典列表
        :return: 插入后的模型实例列表
        """
        session = self.get_session()
        try:
            instances = [model(**data) for data in data_list]
            session.bulk_save_objects(instances)
            session.commit()
            return instances
        except exc.SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Bulk insert error: {e}")
            raise
        finally:
            self.close_session()

    def update(
        self, 
        model: Base, 
        filters: Dict, 
        update_data: Dict
    ) -> int:
        """
        更新记录
        
        :param model: SQLAlchemy 模型类
        :param filters: 过滤条件字典
        :param update_data: 更新数据字典
        :return: 更新的记录数
        """
        session = self.get_session()
        try:
            query = session.query(model)
            
            for key, value in filters.items():
                if hasattr(model, key):
                    query = query.filter(getattr(model, key) == value)
            
            count = query.update(update_data, synchronize_session=False)
            session.commit()
            return count
        except exc.SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Update error: {e}")
            raise
        finally:
            self.close_session()

    def delete(self, model: Base, filters: Dict) -> int:
        """
        删除记录
        
        :param model: SQLAlchemy 模型类
        :param filters: 过滤条件字典
        :return: 删除的记录数
        """
        session = self.get_session()
        try:
            query = session.query(model)
            
            for key, value in filters.items():
                if hasattr(model, key):
                    query = query.filter(getattr(model, key) == value)
            
            count = query.delete(synchronize_session=False)
            session.commit()
            return count
        except exc.SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Delete error: {e}")
            raise
        finally:
            self.close_session()

    def __enter__(self):
        """支持上下文管理"""
        self.session = self.get_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动关闭会话"""
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()
        self.close_session()
from typing import List, Dict, Optional, Type, Any
from unittest.mock import Base
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
import logging



class DatabaseManager:
    """数据库操作封装类"""
    
    def __init__(self, db_url: str, pool_size: int = 5, max_overflow: int = 10):
        """
        初始化数据库连接
        
        :param db_url: 数据库连接字符串 (e.g. "postgresql://user:password@localhost/dbname")
        :param pool_size: 连接池大小
        :param max_overflow: 最大溢出连接数
        """
        self.engine = create_engine(
            db_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,
            echo=False  # 设为True可查看SQL日志
        )
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        logging.info("Database connection established")

    def get_session(self):
        """获取新的数据库会话"""
        return self.Session()

    def close_session(self):
        """关闭当前线程的会话"""
        self.Session.remove()

    def fetch_all(
        self, 
        model: Type[Base], 
        filters: Optional[Dict] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Base]:
        """
        查询多条记录
        
        :param model: SQLAlchemy 模型类
        :param filters: 过滤条件字典 (e.g. {"name": "test"})
        :param order_by: 排序字段 (e.g. "id desc")
        :param limit: 返回记录数限制
        :param offset: 偏移量
        :return: 模型实例列表
        """
        session = self.get_session()
        try:
            query = session.query(model)
            
            # 应用过滤条件
            if filters:
                for key, value in filters.items():
                    if hasattr(model, key):
                        query = query.filter(getattr(model, key) == value)
            
            # 应用排序
            if order_by:
                if "desc" in order_by.lower():
                    field = order_by.split()[0]
                    query = query.order_by(getattr(model, field).desc())
                else:
                    query = query.order_by(getattr(model, order_by))
            
            # 应用分页
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
                
            return query.all()
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Fetch all error: {e}")
            raise
        finally:
            self.close_session()

    def fetch_one(
        self, 
        model: Type[Base], 
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
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Fetch one error: {e}")
            raise
        finally:
            self.close_session()

    def insert(self, model: Type[Base], data: Dict) -> Base:
        """
        插入单条记录
        
        :param model: SQLAlchemy 模型类
        :param data: 数据字典 (需与模型字段匹配)
        :return: 插入后的模型实例
        """
        session = self.get_session()
        try:
            instance = model(**data)
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Insert error: {e}")
            raise
        finally:
            self.close_session()

    def bulk_insert(self, model: Type[Base], data_list: List[Dict]) -> List[Base]:
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
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Bulk insert error: {e}")
            raise
        finally:
            self.close_session()

    def update(
        self, 
        model: Type[Base], 
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
            
            # 应用过滤条件
            for key, value in filters.items():
                if hasattr(model, key):
                    query = query.filter(getattr(model, key) == value)
            
            count = query.update(update_data, synchronize_session=False)
            session.commit()
            return count
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Update error: {e}")
            raise
        finally:
            self.close_session()

    def delete(self, model: Type[Base], filters: Dict) -> int:
        """
        删除记录
        
        :param model: SQLAlchemy 模型类
        :param filters: 过滤条件字典
        :return: 删除的记录数
        """
        session = self.get_session()
        try:
            query = session.query(model)
            
            # 应用过滤条件
            for key, value in filters.items():
                if hasattr(model, key):
                    query = query.filter(getattr(model, key) == value)
            
            count = query.delete(synchronize_session=False)
            session.commit()
            return count
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Delete error: {e}")
            raise
        finally:
            self.close_session()

    def execute_raw_sql(self, sql: str, params: Optional[Dict] = None) -> List[Dict]:
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
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Raw SQL error: {e}")
            raise
        finally:
            self.close_session()

    def create_all_tables(self):
        """创建所有表结构"""
        Base.metadata.create_all(self.engine)

    def drop_all_tables(self):
        """删除所有表结构（谨慎使用）"""
        Base.metadata.drop_all(self.engine)

    def __enter__(self):
        """支持上下文管理"""
        self.session = self.get_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动关闭会话"""
        if exc_type is not None:
            self.session.rollback()
        self.close_session()
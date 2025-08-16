from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Type, Any, List, Optional, Dict, Union
from model.model_agent import Base  # 假设模型定义在models.py中


class DatabaseManager:
    """
    通用的数据库操作类，使用fetch前缀命名查询方法
    """

    def __init__(self, db_url: str, echo: bool = False):
        """
        初始化数据库操作类

        Args:
            db_url: 数据库连接URL，例如: 'postgresql://user:password@localhost/dbname'
            echo: 是否输出SQL日志，默认为False
        """
        self.engine = create_engine(db_url, echo=echo)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def _get_session(self):
        """获取一个新的数据库会话"""
        return self.Session()

    def _close_session(self, session):
        """关闭数据库会话"""
        if session:
            session.close()

    def fetch_one(self, model: Type[Base], **filters) -> Optional[Any]:
        """
        根据条件获取单个记录

        Args:
            model: SQLAlchemy模型类
            filters: 查询条件，例如 id=1, name='test'

        Returns:
            查询到的记录对象或None
        """
        session = self._get_session()
        try:
            return session.query(model).filter_by(**filters).first()
        finally:
            self._close_session(session)

    def fetch_all(
        self,
        model: Type[Base],
        filters: Optional[Dict] = None,
        order_by: Optional[Union[str, List[str]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Any]:
        """
        获取多个记录，支持分页和排序

        Args:
            model: SQLAlchemy模型类
            filters: 查询条件字典
            order_by: 排序字段，可以是字符串或字符串列表
            limit: 返回记录数限制
            offset: 偏移量

        Returns:
            查询到的记录列表
        """
        session = self._get_session()
        try:
            query = session.query(model)

            if filters:
                query = query.filter_by(**filters)

            if order_by:
                if isinstance(order_by, str):
                    query = query.order_by(order_by)
                else:
                    for field in order_by:
                        query = query.order_by(field)

            if limit:
                query = query.limit(limit)

            if offset:
                query = query.offset(offset)

            return query.all()
        finally:
            self._close_session(session)

    def fetch_complex(
        self,
        model: Type[Base],
        conditions: List[Any],
        order_by: Optional[Union[str, List[str]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Any]:
        """
        复杂查询，支持多条件组合

        Args:
            model: SQLAlchemy模型类
            conditions: 查询条件列表，可以使用and_、or_等组合
            order_by: 排序字段
            limit: 返回记录数限制
            offset: 偏移量

        Returns:
            查询到的记录列表
        """
        session = self._get_session()
        try:
            query = session.query(model)

            if conditions:
                query = query.filter(and_(*conditions))

            if order_by:
                if isinstance(order_by, str):
                    query = query.order_by(order_by)
                else:
                    for field in order_by:
                        query = query.order_by(field)

            if limit:
                query = query.limit(limit)

            if offset:
                query = query.offset(offset)

            return query.all()
        finally:
            self._close_session(session)

    def insert(self, model: Type[Base], data: Dict[str, Any]) -> Any:
        """
        插入一条新记录

        Args:
            model: SQLAlchemy模型类
            data: 要插入的数据字典

        Returns:
            插入后的记录对象
        """
        session = self._get_session()
        try:
            obj = model(**data)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            self._close_session(session)

    def bulk_insert(
        self, model: Type[Base], data_list: List[Dict[str, Any]]
    ) -> List[Any]:
        """
        批量插入记录

        Args:
            model: SQLAlchemy模型类
            data_list: 要插入的数据字典列表

        Returns:
            插入后的记录对象列表
        """
        session = self._get_session()
        try:
            objects = [model(**data) for data in data_list]
            session.bulk_save_objects(objects)
            session.commit()
            return objects
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            self._close_session(session)

    def update(
        self, model: Type[Base], filters: Dict[str, Any], update_data: Dict[str, Any]
    ) -> int:
        """
        更新记录

        Args:
            model: SQLAlchemy模型类
            filters: 筛选条件
            update_data: 要更新的数据

        Returns:
            更新的记录数
        """
        session = self._get_session()
        try:
            result = session.query(model).filter_by(**filters).update(update_data)
            session.commit()
            return result
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            self._close_session(session)

    def delete(self, model: Type[Base], **filters) -> int:
        """
        删除记录

        Args:
            model: SQLAlchemy模型类
            filters: 筛选条件

        Returns:
            删除的记录数
        """
        session = self._get_session()
        try:
            result = session.query(model).filter_by(**filters).delete()
            session.commit()
            return result
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            self._close_session(session)

    def fetch_or_insert(
        self,
        model: Type[Base],
        filters: Dict[str, Any],
        defaults: Optional[Dict[str, Any]] = None,
    ) -> tuple:
        """
        查询或插入记录

        Args:
            model: SQLAlchemy模型类
            filters: 查询条件
            defaults: 不存在时插入的默认值

        Returns:
            (object, created) 元组，object是查询或插入的对象，created表示是否是新插入的
        """
        session = self._get_session()
        try:
            obj = session.query(model).filter_by(**filters).first()
            if obj:
                return obj, False

            create_data = {**filters, **(defaults or {})}
            obj = model(**create_data)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj, True
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            self._close_session(session)

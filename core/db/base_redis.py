from redis import asyncio as aioredis
from typing import Optional, Union, Dict, List, Any
import json


class RedisManager:
    """
    基于官方redis-py的异步Redis操作类
    包含完整的增删改查功能
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0", **kwargs):
        """
        初始化Redis连接
        :param redis_url: Redis连接URL
        :param kwargs: 其他连接参数
        """
        self.redis_url = redis_url
        self.redis_pool = None
        self.connection_kwargs = kwargs

    async def init_redis_pool(self) -> aioredis.Redis:
        """初始化Redis连接池"""
        if not self.redis_pool:
            self.redis_pool = aioredis.from_url(
                self.redis_url, **self.connection_kwargs
            )
        return self.redis_pool

    async def close(self):
        """关闭Redis连接 (使用 aclose() 替代弃用的 close())"""
        if self.redis_pool:
            await self.redis_pool.aclose()

    async def set_value(
        self,
        key: str,
        value: Union[str, bytes, int, float, Dict, List],
        expire: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        """
        设置键值对
        :param key: 键名
        :param value: 值(支持字符串、数字、字典、列表等)
        :param expire: 过期时间(秒)
        :param nx: 仅当键不存在时设置
        :param xx: 仅当键存在时设置
        :return: 是否设置成功
        """
        redis = await self.init_redis_pool()
        if isinstance(value, (dict, list)):
            value = json.dumps(value)

        kwargs = {}
        if expire is not None:
            kwargs["ex"] = expire
        if nx:
            kwargs["nx"] = True
        if xx:
            kwargs["xx"] = True

        result = await redis.set(key, value, **kwargs)
        return bool(result)

    async def get_value(
        self, key: str, is_json: bool = False
    ) -> Optional[Union[str, Dict, List]]:
        """
        获取键值
        :param key: 键名
        :param is_json: 是否为JSON格式
        :return: 键值(如果是JSON会自动解析)
        """
        redis = await self.init_redis_pool()
        value = await redis.get(key)
        if value is None:
            return None

        value = value.decode() if isinstance(value, bytes) else value

        if is_json:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value

    async def delete_key(self, *keys: str) -> int:
        """
        删除一个或多个键
        :param keys: 要删除的键名
        :return: 成功删除的键数量
        """
        redis = await self.init_redis_pool()
        return await redis.delete(*keys)

    async def update_value(
        self,
        key: str,
        value: Union[str, bytes, int, float, Dict, List],
        expire: Optional[int] = None,
    ) -> bool:
        """
        更新键值(等同于set)
        :param key: 键名
        :param value: 新值
        :param expire: 过期时间(秒)
        :return: 是否更新成功
        """
        return await self.set_value(key, value, expire, xx=True)

    async def exists_key(self, key: str) -> bool:
        """
        检查键是否存在
        :param key: 键名
        :return: 是否存在
        """
        redis = await self.init_redis_pool()
        return bool(await redis.exists(key))

    async def expire_key(self, key: str, expire: int) -> bool:
        """
        设置键过期时间
        :param key: 键名
        :param expire: 过期时间(秒)
        :return: 是否设置成功
        """
        redis = await self.init_redis_pool()
        return bool(await redis.expire(key, expire))

    async def ttl_key(self, key: str) -> int:
        """
        获取键剩余生存时间
        :param key: 键名
        :return: 剩余时间(秒), -2表示键不存在, -1表示键存在但没有设置过期时间
        """
        redis = await self.init_redis_pool()
        return await redis.ttl(key)

    async def hset_dict(
        self, key: str, field: str, value: Union[str, bytes, int, float, Dict, List]
    ) -> bool:
        """
        设置哈希表中的字段值
        :param key: 键名
        :param field: 字段名
        :param value: 字段值
        :return: 是否设置成功(1=新字段, 0=更新字段)
        """
        redis = await self.init_redis_pool()
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return bool(await redis.hset(key, field, value))

    async def hget_dict(
        self, key: str, field: str, is_json: bool = False
    ) -> Optional[Union[str, Dict, List]]:
        """
        获取哈希表中的字段值
        :param key: 键名
        :param field: 字段名
        :param is_json: 是否为JSON格式
        :return: 字段值
        """
        redis = await self.init_redis_pool()
        value = await redis.hget(key, field)
        if value is None:
            return None

        value = value.decode() if isinstance(value, bytes) else value

        if is_json:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value

    async def hdel_field(self, key: str, *fields: str) -> int:
        """
        删除哈希表中的一个或多个字段
        :param key: 键名
        :param fields: 要删除的字段名
        :return: 成功删除的字段数量
        """
        redis = await self.init_redis_pool()
        return await redis.hdel(key, *fields)

    async def hgetall_dict(self, key: str) -> Dict[str, Any]:
        """
        获取哈希表中所有字段和值
        :param key: 键名
        :return: 字典形式的字段和值
        """
        redis = await self.init_redis_pool()
        result = await redis.hgetall(key)
        return {k.decode(): v.decode() for k, v in result.items()}

    async def increment(self, key: str, amount: int = 1) -> int:
        """
        自增操作
        :param key: 键名
        :param amount: 自增数量
        :return: 自增后的值
        """
        redis = await self.init_redis_pool()
        return await redis.incrby(key, amount)

    async def decrement(self, key: str, amount: int = 1) -> int:
        """
        自减操作
        :param key: 键名
        :param amount: 自减数量
        :return: 自减后的值
        """
        redis = await self.init_redis_pool()
        return await redis.decrby(key, amount)

    async def keys(self, pattern: str = "*") -> List[str]:
        """
        查找所有符合给定模式的键
        :param pattern: 匹配模式
        :return: 匹配的键列表
        """
        redis = await self.init_redis_pool()
        keys = await redis.keys(pattern)
        return [key.decode() if isinstance(key, bytes) else key for key in keys]

    async def flush_db(self) -> bool:
        """
        清空当前数据库
        :return: 是否成功
        """
        redis = await self.init_redis_pool()
        return bool(await redis.flushdb())

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.init_redis_pool()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()


async def example_usage():
    # 使用示例
    redis = BaseRedis()
    async with redis:
        # 字符串操作
        await redis.set_value("string_key", "hello world", expire=60)
        string_val = await redis.get_value("string_key")
        print(f"String value: {string_val}")

        # 字典操作
        await redis.set_value("dict_key", {"name": "Alice", "age": 30}, expire=60)
        dict_val = await redis.get_value("dict_key", is_json=True)
        print(f"Dict value: {dict_val}")

        # 哈希表操作
        await redis.hset_dict("user:1001", "profile", {"name": "Bob", "age": 25})
        profile = await redis.hget_dict("user:1001", "profile", is_json=True)
        print(f"User profile: {profile}")

        # 自增操作
        await redis.increment("counter")
        counter = await redis.get_value("counter")
        print(f"Counter: {counter}")

        # 删除操作
        await redis.delete_key("string_key")
        exists = await redis.exists_key("string_key")
        print(f"Key exists after deletion: {exists}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())

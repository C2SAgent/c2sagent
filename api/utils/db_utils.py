from sqlalchemy.ext.asyncio import AsyncEngine


def create_init_db(engine: AsyncEngine, base):
    """Factory to create an init_db coroutine for FastAPI on_startup."""

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)

    return init_db

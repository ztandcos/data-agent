import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker

from app.conf.app_config import DBConfig, app_config


class MysqlClientManager:
    def __init__(self, config: DBConfig):
        self.config = config
        self.session_factory = None
        self.engine: AsyncEngine | None = None

    def get_url(self) -> str:
        return (
            "mysql+asyncmy://"
            f"{self.config.user}:{self.config.password}"
            f"@{self.config.host}:{self.config.port}/{self.config.database}"
            "?charset=utf8mb4"
        )

    def init(self) -> None:
        self.engine = create_async_engine(
            self.get_url(),
            pool_size = 10,
            pool_pre_ping=True,
            echo=False,
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            autoflush=True,
            expire_on_commit=False,
        )

    async def close(self) -> None:
        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None

    async def ping(self) -> int:
        if self.engine is None:
            raise RuntimeError("MySQL engine is not initialized")

        # async with AsyncSession(self.engin,autoflush = True,expire_on_commit = False) as session:
        async with self.session_factory() as session:  # 这里在对象的后面加上()，实际上就是调用了session类中的__call__方法   
            result = await session.execute(text("SELECT 1"))
            # return int(result.scalar_one())
            rows = result.mappings().fetchall()
            return rows


meta_mysql_client_manager = MysqlClientManager(app_config.db_meta)
dw_mysql_client_manager = MysqlClientManager(app_config.db_dw)


if __name__ == "__main__":
    dw_mysql_client_manager.init()
    async def test():
        result = await dw_mysql_client_manager.ping()
        print(f"Connection successful! Ping result: {result}")

    asyncio.run(test())

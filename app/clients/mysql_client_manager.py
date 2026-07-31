"""
mysql 客户端管理
"""
import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker

from app.conf.app_config import DBConfig, app_config

# 单例engine
engine = None

class MysqlClientManager:
    def __init__(self,db_config:DBConfig):
        self.db_config = db_config
        self.engine:AsyncEngine | None = None
        self.session_factory = None

    def _get_url(self):
        return f"mysql+asyncmy://{self.db_config.user}:{self.db_config.password}@{self.db_config.host}:{self.db_config.port}/{self.db_config.database}?charset=utf8mb4"

    def init(self):
        self.engine = create_async_engine(self._get_url())
        self.session_factory = async_sessionmaker(dw_mysql_client_manager.engine,autoflush = True,expire_on_commint = False)
    async def close(self):
        await self.engine.dispose()

dw_mysql_client_manager = MysqlClientManager(app_config.db_dw)
meta_mysql_client_manager = MysqlClientManager(app_config.db_meta)

if __name__ == '__main__':
    dw_mysql_client_manager.init()

    async def test():
        async  with dw_mysql_client_manager.session_factory() as session:
            result = await session.execute(text("select * from fact_order limit 10"))
            rows = result.mappings().fetchall()
            print(rows[0]['order_id'])

    asyncio.run(test())
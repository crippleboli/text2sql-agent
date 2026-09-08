"""
mysql 客户端管理
"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from app.conf.app_config import DBConfig, app_config


class MysqlClientManager:
    """
        MySQL 客户端管理器类
        封装连接池创建、Session 生成器与连接销毁逻辑
    """
    def __init__(self,db_config:DBConfig):
        self.db_config = db_config
        self.engine:AsyncEngine | None = None       # 异步引擎类型
        self.session_factory = None                 # 会话工厂 用于创建同参 session

    def _get_url(self):
        return f"mysql+asyncmy://{self.db_config.user}:{self.db_config.password}@{self.db_config.host}:{self.db_config.port}/{self.db_config.database}?charset=utf8mb4"

    def init(self):
        self.engine = create_async_engine(url = self._get_url(),     # 根据 url 创建异步 engine
                                          pool_size = 10,            # 链接数量 default = 5
                                          pool_pre_ping=True,        # 测试链接 connection 是否成功
                                          )
        self.session_factory = async_sessionmaker(self.engine,
                                                  autoflush = True,
                                                  expire_on_commit = False,
                                                  autobegin = True
                                                  )

    async def close(self):
        await self.engine.dispose()

# 实例化业务数据仓库 (dw) 和元数据库 (meta) 的专属管理器
dw_mysql_client_manager = MysqlClientManager(app_config.db_dw)
meta_mysql_client_manager = MysqlClientManager(app_config.db_meta)

if __name__ == '__main__':
    # init 创建连接池和会话工厂
    dw_mysql_client_manager.init()

    async def test():
        async  with dw_mysql_client_manager.session_factory() as session:
            result = await session.execute(text("select * from fact_order limit 10"))
            # mappings()将结果转为 类似 dict的mapping类型
            rows = result.mappings().fetchall()
            print(rows[0]['order_id'])

    asyncio.run(test())
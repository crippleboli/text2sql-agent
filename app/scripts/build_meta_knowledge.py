import argparse
from pathlib import Path

from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import meta_mysql_client_manager, dw_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.repository.column_qdrant_repository import ColumnQdrantRepository
from app.repository.dw_mysql_repository import DWMySQLRepository
from app.repository.meta_mysql_repository import MetaMySQLRepository
from app.repository.value_es_repository import ValueESRepository
from app.service.meta_knowledge_service import MetaKnowledgeService
import asyncio


async def build(config_path:Path):
    meta_mysql_client_manager.init()
    dw_mysql_client_manager.init()
    qdrant_client_manager.init()
    embedding_client_manager.init()
    es_client_manager.init()

    # 创建两个 Session 分别操作 meta 和 dw 两个数据库
    async with meta_mysql_client_manager.session_factory() as meta_session, dw_mysql_client_manager.session_factory() as dw_session:
        meta_mysql_repository = MetaMySQLRepository(meta_session)
        dw_mysql_repository = DWMySQLRepository(dw_session)
        column_qdrant_repository = ColumnQdrantRepository(qdrant_client_manager.client)
        embedding_client = embedding_client_manager.client
        value_es_repository = ValueESRepository(es_client_manager.client)

        meta_knowledge_service = MetaKnowledgeService(meta_mysql_repository=meta_mysql_repository,
                                                      dw_mysql_repository=dw_mysql_repository,
                                                      column_qdrant_repository=column_qdrant_repository,
                                                      embedding_client=embedding_client,
                                                      value_es_repository=value_es_repository
                                                      )
        await meta_knowledge_service.build(config_path)

if __name__ == '__main__':
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser()

    # 添加 -c / --conf 参数 用于传入配置文件路径  python -m 模块 -c 配置文件
    parser.add_argument('-c', '--conf')

    # 解析命令行参数    获取 -c 参数传入的配置文件路径
    args = parser.parse_args()
    config_path = Path(args.conf)
    # 路径参数传入 build函数
    asyncio.run(build(config_path))
"""
qdrant 客户端管理
"""
import asyncio
import random
from typing import Optional
from qdrant_client import models
from qdrant_client import  AsyncQdrantClient
from app.conf.app_config import QdrantConfig, app_config


class QdrantClientManager:
    """
        Qdrant 异步客户端管理器
        持有异步连接实例，负责生命周期的解耦与资源释放
    """
    def __init__(self,qdrant_config:QdrantConfig):
        self.qdrant_config = qdrant_config
        self.client:Optional[AsyncQdrantClient] = None  # 异步 Qdrant 客户端实例，延迟到 init() 时创建

    def _get_url(self):
        return f"http://{self.qdrant_config.host}:{self.qdrant_config.port}"

    def init(self):
        self.client = AsyncQdrantClient(url = self._get_url())

    async def close(self):
        await self.client.close()

# 实例化 Qdrant 客户端管理器的全局单例
qdrant_client_manager = QdrantClientManager(app_config.qdrant)

if __name__ == '__main__':
    qdrant_client_manager.init()

    async def test():
        client = qdrant_client_manager.client
        # 创建集合
        if not await client.collection_exists('my_collection'):
            await client.create_collection(
                collection_name = 'my_collection',
                vectors_config=models.VectorParams(size=10,             # 向量维度 必须与配置的embedding模型输出维度相同
                                                   distance= models.Distance.COSINE    # 相似度计算算法
                                                   )
            )

        # 写入数据
        await client.upsert(
            collection_name = 'my_collection',
            points=[
                models.PointStruct(
                    id=i,
                    vector = [random.random() for _ in range(10)],
                )
                for i in range(100)
            ],
        )

        # 查询数据
        res = await client.query_points(
            collection_name = 'my_collection',
            query= [random.random() for _ in range(10)],
            limit = 10,
            score_threshold = 0.8,          # 相似度阈值
        )
        print(res)

    asyncio.run(test())
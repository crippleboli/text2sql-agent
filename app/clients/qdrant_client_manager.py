import asyncio
import random
from typing import Optional
from qdrant_client import models
from qdrant_client import  AsyncQdrantClient
from app.conf.app_config import QdrantConfig, app_config


class QdrantClientManager:
    def __init__(self,qdrant_config:QdrantConfig):
        self.qdrant_config = qdrant_config
        self.client:Optional[AsyncQdrantClient] = None

    def _get_url(self):
        return f"http://{self.qdrant_config.host}:{self.qdrant_config.port}"

    def init(self):
        self.client = AsyncQdrantClient(url = self._get_url())

    async def close(self):
        await self.client.close()

qdrant_client_manager = QdrantClientManager(app_config.qdrant)

if __name__ == '__main__':
    qdrant_client_manager.init()

    async def test():
        client = qdrant_client_manager.client
        # 创建集合
        if not await client.collection_exists('my_collection'):
            await client.create_collection(
                collection_name = 'my_collection',
                vectors_config=models.VectorParams(size=10,distance= models.Distance.COSINE)
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
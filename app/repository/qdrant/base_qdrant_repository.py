from typing import TypeVar, Generic
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from app.conf.app_config import app_config


T = TypeVar('T')

class BaseQdrantRepository(Generic[T]):
    collection_name: str

    def __init__(self, client: AsyncQdrantClient):
        self.client = client

    async def ensure_collection(self):
        """
        取保qdrant的collection存在 不存在时创建
        """
        if not await self.client.collection_exists(self.collection_name):
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=app_config.qdrant.embedding_size,
                    distance=Distance.COSINE,
                ),
            )

    async def upsert(self, ids: list[str], embeddings: list[list[float]], payloads: list[T],batch_size: int = 20):
        """
        批量向 Qdrant 集合中插入或更新向量数据，并按照指定批次大小分批写入 分批防止一次写入太多 Point

        :param ids: Point 的唯一 ID 列表
        :param embeddings: Point 的向量列表
        :param payloads: Point 的元数据列表
        :param batch_size: 每批写入 Qdrant 的 Point 数量，默认为 20
        """
        zipped = list(zip(ids, embeddings, payloads))

        for i in range(0, len(zipped), batch_size):
            batch = zipped[i:i + batch_size]
            batch_points = [PointStruct(id=id, vector=embedding, payload=payload) for id, embedding, payload in batch]
            await self.client.upsert(collection_name=self.collection_name, points=batch_points)

    async def search(self, embedding: list[float], score_threshold: float = 0.6, limit: int = 5) -> list[T]:
        """
        根据输入的向量在 Qdrant 集合中检索最相似的字段元数据列表
        :param embedding: 用户问题向量化的结果
        :param score_threshold: 相似度匹配得分阈值，默认为 0.6
        :param limit: 返回的最大匹配结果数量，默认为 5
        :return: 匹配到的字段元数据列表
        """

        result = await self.client.query_points(
            collection_name=self.collection_name,
            query=embedding,
            score_threshold=score_threshold,
            limit=limit,
        )

        return [point.payload for point in result.points]
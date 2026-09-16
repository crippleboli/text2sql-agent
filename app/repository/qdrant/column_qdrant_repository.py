from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from app.conf.app_config import app_config
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.repository.qdrant.base_qdrant_repository import BaseQdrantRepository


class  ColumnQdrantRepository(BaseQdrantRepository[ColumnInfoQdrant]):
    # 类属性 collection 相当于 mysql中的 table
    collection_name:str = 'data-agent-column'

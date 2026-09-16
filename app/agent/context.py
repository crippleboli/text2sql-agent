from typing import TypedDict
from langchain_openai import OpenAIEmbeddings

from app.repository.es.value_es_repository import ValueESRepository
from app.repository.mysql.meta_mysql_repository import MetaMySQLRepository
from app.repository.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repository.qdrant.metric_qdrant_repository import MetricQdrantRepository


class DataAgentContext(TypedDict):
    embedding_client: OpenAIEmbeddings
    column_qdrant_repository: ColumnQdrantRepository
    metric_qdrant_repository: MetricQdrantRepository
    value_es_repository: ValueESRepository
    meta_mysql_repository:MetaMySQLRepository
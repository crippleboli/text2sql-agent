from typing import TypedDict
from langchain_openai import OpenAIEmbeddings
from app.repository.qdrant.column_qdrant_repository import ColumnQdrantRepository

class DataAgentContext(TypedDict):
    embedding_client: OpenAIEmbeddings
    column_qdrant_repository: ColumnQdrantRepository
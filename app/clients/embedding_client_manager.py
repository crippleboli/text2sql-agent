"""
    embedding 客户端管理
"""
from typing import Optional
from app.conf.app_config import EmbeddingConfig, app_config
from langchain_openai import OpenAIEmbeddings


class EmbeddingClientManager:
    def __init__(self,config:EmbeddingConfig):
        self.client:  Optional[OpenAIEmbeddings]  = None
        self.config = config

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}/v1/"

    def init(self):
        self.client = OpenAIEmbeddings(
            model=self.config.model,
            base_url=self._get_url(),
            api_key="unused",
            check_embedding_ctx_length=False,
        )


embedding_client_manager = EmbeddingClientManager(app_config.embedding)

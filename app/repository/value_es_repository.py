from elasticsearch import AsyncElasticsearch


class ValueESRepository:

    index_name = 'data-agent-value'

    def __init__(self,client:AsyncElasticsearch):
        self.client = client

    async def ensure_index(self):
         self.client.indices.exists(self.index_name)


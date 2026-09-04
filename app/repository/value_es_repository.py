from elasticsearch import AsyncElasticsearch


class ValueESRepository:

    index_name = 'data-agent-value'
    index_mappings = {
        'dynamic': False,
        "properties": {
            "id": {"type": "keyword"},
            "value": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_max_word"}, # analyzer分词器 search_analyzer问题分词器
            "type": {"type": "keyword"},
            "column_id": {"type": "keyword"},
            "column_name": {"type": "keyword"},
            "table_id": {"type": "keyword"},
            "table_name": {"type": "keyword"},
        }
    }

    def __init__(self,client:AsyncElasticsearch):
        self.client = client

    async def ensure_index(self):
         if not  await self.client.indices.exists(self.index_name):
             await self.client.indices.create(index=self.index_name,mappings=self.index_mappings)

    async def index(self, value_infos, batch_size = 20):
        for i in range(0, len(value_infos), batch_size):
            batch = value_infos[i:i+batch_size]
            operations = []
            for value_info in batch:
                operations.append({"index": {"_index": self.index_name, "_id": value_info['id']}})
                operations.append(value_info)
            await self.client.bulk(operations)

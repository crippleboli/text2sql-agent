from elasticsearch import AsyncElasticsearch


class ValueESRepository:

    index_name = 'data-agent-value' # 类属性：es的index名称
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
         if not  await self.client.indices.exists(index=self.index_name):
             await self.client.indices.create(index=self.index_name,
                                              mappings=self.index_mappings
                                              )

    async def index(self, value_infos, batch_size = 20):
        for i in range(0, len(value_infos), batch_size):
            batch = value_infos[i:i+batch_size]
            operations = []
            for value_info in batch:
                # 凑出bulk所需数据operations
                operations.append({"index": {"_index": self.index_name, "_id": value_info['id']}})
                operations.append(value_info)
            await self.client.bulk(operations=operations)

        # bulk api 参数格式
        """
        resp = client.bulk(
            operations=[
                {
                    "index": {
                        "_index": "books"
                    }
                },
                {
                    "name": "Revelation Space",
                    "author": "Alastair Reynolds",
                    "release_date": "2000-03-15",
                    "page_count": 585
                },
                {
                    "index": {
                        "_index": "books"
                    }
                },
                {
                    "name": "1984",
                    "author": "George Orwell",
                    "release_date": "1985-06-01",
                    "page_count": 328
                },
                {
                    "index": {
                        "_index": "books"
                    }
                },
                {
                    "name": "Fahrenheit 451",
                    "author": "Ray Bradbury",
                    "release_date": "1953-10-15",
                    "page_count": 227
                },
                {
                    "index": {
                        "_index": "books"
                    }
                },
                {
                    "name": "Brave New World",
                    "author": "Aldous Huxley",
                    "release_date": "1932-06-01",
                    "page_count": 268
                },
                {
                    "index": {
                        "_index": "books"
                    }
                },
                {
                    "name": "The Handmaids Tale",
                    "author": "Margaret Atwood",
                    "release_date": "1985-06-01",
                    "page_count": 311
                }
            ],
        )
        """
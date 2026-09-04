import uuid
from pathlib import Path

from langchain_huggingface import HuggingFaceEndpointEmbeddings
from qdrant_client.http.models import PointStruct

from app.conf.config_loader import load_config
from app.conf.meta_config import MetaConfig
from app.models.es.value_info_es import ValueInfoES
from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.repository.column_qdrant_repository import ColumnQdrantRepository
from app.repository.dw_mysql_repository import DWMySQLRepository
from app.repository.meta_mysql_repository import MetaMySQLRepository
from app.repository.value_es_repository import ValueESRepository


class MetaKnowledgeService:
    def __init__(self,
                 meta_mysql_repository:MetaMySQLRepository,
                 dw_mysql_repository:DWMySQLRepository,
                 column_qdrant_repository:ColumnQdrantRepository,
                 embedding_client:HuggingFaceEndpointEmbeddings,
                 value_es_repository:ValueESRepository,
                 ):

        self.meta_mysql_repository = meta_mysql_repository
        self.dw_mysql_repository = dw_mysql_repository
        self.column_qdrant_repository = column_qdrant_repository
        self.embedding_client = embedding_client
        self.value_es_repository = value_es_repository

    def _convert_column_info_from_mysql_to_qdrant(self, column_info: ColumnInfoMySQL) -> ColumnInfoQdrant:
        return ColumnInfoQdrant(
            id=column_info.id,
            name=column_info.name,
            role=column_info.role,
            examples=column_info.examples,
            description=column_info.description,
            alias=column_info.alias,
            table_id=column_info.table_id
        )

    async def _save_tables_to_meta_db(self,meta_config:MetaConfig):
        table_infos: list[TableInfoMySQL] = []
        column_infos: list[ColumnInfoMySQL] = []


        for table in meta_config.tables:
            # table -> TableInfoMySQL
            table_info = TableInfoMySQL(
                id=table.name,
                name=table.name,
                role=table.role,
                description=table.description
            )
            table_infos.append(table_info)

            # 查询该表所有字段的字段类型
            column_types: dict[str, str] = await self.dw_mysql_repository.get_column_types(table.name)

            for column in table.columns:
                column_values: list = await self.dw_mysql_repository.get_column_values(table.name, column.name, 10)

                # column -> ColumnInfoMySQL
                column_info = ColumnInfoMySQL(
                    id=f'{table.name}.{column.name}',
                    name=column.name,
                    type=column_types[column.name],  # 单独获取
                    role=column.role,
                    examples=column_values,  # 单独获取
                    description=column.description,
                    alias=column.alias,
                    table_id=table.name
                )
                column_infos.append(column_info)

        async with self.meta_mysql_repository.session.begin():
            await self.meta_mysql_repository.save_table_infos(table_infos)
            await self.meta_mysql_repository.save_column_infos(column_infos)
        # await self.meta_mysql_repository.session.commit()

        return table_infos,column_infos

    async def _save_column_info_to_qdrant(self,column_infos:list[ColumnInfoMySQL]):
        # 确保collection已经存在
        await self.column_qdrant_repository.ensure_collection()

        points: list[dict] = []
        for column_info in column_infos:
            points.append({
                'id': uuid.uuid4(),
                'embedding_text': column_info.name,
                'payload': self._convert_column_info_from_mysql_to_qdrant(column_info)
            })

            points.append({
                'id': uuid.uuid4(),
                'embedding_text': column_info.description,
                'payload': self._convert_column_info_from_mysql_to_qdrant(column_info)
            })

            for alia in column_info.alias:
                points.append({
                    'id': uuid.uuid4(),
                    'embedding_text': alia,
                    'payload': self._convert_column_info_from_mysql_to_qdrant(column_info)
                })

        # 向量列表
        embedding_texts = [point['embedding_text'] for point in points]
        embedding_batch_size = 10
        embeddings = []
        for i in range(0, len(embedding_texts), embedding_batch_size):
            batch_embedding_texts = embedding_texts[i:i + embedding_batch_size]
            batch_embeddings = await self.embedding_client.aembed_documents(batch_embedding_texts)
            embeddings.extend(batch_embeddings)

        # id列表
        ids = [point['id'] for point in points]

        # payload列表
        payloads = [point['payload'] for point in points]

        await self.column_qdrant_repository.upsert(ids, embeddings, payloads)




    async def build(self,config_path:Path):
        # 1. 加载配置文件
        meta_config: MetaConfig = load_config(config_path,MetaConfig)
        # 2. 处理表信息
        if meta_config.tables:
            # 2.1 保存表信息到meta数据库
            table_infos,column_infos = await self._save_tables_to_meta_db(meta_config)

            # 2.2 为字段信息建立向量索引
            await self._save_column_info_to_qdrant(column_infos)


            # 2.3 为字段取值建立全文索引
            # 确保index存在
            await self.value_es_repository.ensure_index()

            column2sync: dict[str,bool]  = {}           # 字段名 是否需要同步
            for table in meta_config.tables:
                for column in table.columns:
                    column2sync[f'{table.name}.{column.name}'] = column.sync

            value_infos: list[ValueInfoES] = []
            for column_info in column_infos:
                sync = column2sync[column_info.id]
                if sync:
                    # 查询所有值
                    table_name = column_info.table_id
                    column_name = column_info.name
                    values = await self.dw_mysql_repository.get_column_values(table_name, column_name, 1000000) # 复用
                    current_value_infos = [ValueInfoES( id=f"{column_info.id}.{value}",
                                                value=value,
                                                type=column_info.type,
                                                column_id=column_info.id,
                                                column_name=column_info.name,
                                                table_id=column_info.table_id,
                                                table_name=column_info.table_id
                                                ) for value in values]
                    value_infos.extend(current_value_infos)


            await self.value_es_repository.index(value_infos)


        # 3. 处理指标信息
        if meta_config.metrics:
            pass
            # 3.1 保存指标信息到meta数据库
            # 3.2 为指标信息建立向量索引
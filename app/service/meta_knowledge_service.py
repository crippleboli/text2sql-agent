import uuid
from pathlib import Path
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from qdrant_client.models import PointStruct
from app.conf.config_loader import load_config
from app.conf.meta_config import MetaConfig
from app.core.log import logger
from app.models.es.value_info_es import ValueInfoES
from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.column_metric_mysql import ColumnMetricMySQL
from app.models.mysql.metric_info_mysql import MetricInfoMySQL
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
        """
            将 MySQL 格式的字段元数据对象转换为 Qdrant 向量数据库存储所需的 Payload 数据对象
        """
        return ColumnInfoQdrant(
            id=column_info.id,
            name=column_info.name,
            type=column_info.type,
            role=column_info.role,
            examples=column_info.examples,
            description=column_info.description,
            alias=column_info.alias,
            table_id=column_info.table_id
        )

    async def _save_tables_to_meta_db(self,meta_config:MetaConfig):
        """
           根据 YAML 配置和 DW 业务数据库信息，生成表级和字段级元数据，并保存到 Meta MySQL 数据库中

        :param meta_config: 由 YAML 配置文件加载得到的元数据配置对象
        :return: 包含表级元数据列表和字段级元数据列表的元组
        """
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
                # 查询该字段的 10 个不同值，作为 Meta 数据库中的 examples
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

        async with self.meta_mysql_repository.session.begin():  # 不用commit
            await self.meta_mysql_repository.save_table_infos(table_infos)
            await self.meta_mysql_repository.save_column_infos(column_infos)

        return table_infos,column_infos

    async def _save_column_info_to_qdrant(self,column_infos:list[ColumnInfoMySQL]):
        """
        将字段元数据转换为向量数据，并保存到 Qdrant 向量数据库中
        根据字段名称、字段描述和字段别名分别生成向量检索点，使用 Embedding 模型生成向量后，再批量写入 Qdrant

        :param column_infos: 从 Meta MySQL 数据库中生成的字段级元数据列表
        :return: None
        """
        # 确保collection已经存在
        await self.column_qdrant_repository.ensure_collection()

        points: list[dict] = []
        # 循环取出meta元数据表的所有真实数据 无关dw真实业务数据
        for column_info in column_infos:
            # 名称字段
            points.append({
                'id': uuid.uuid4(),
                'embedding_text': column_info.name,
                'payload': self._convert_column_info_from_mysql_to_qdrant(column_info)
            })
            # 描述字段
            points.append({
                'id': uuid.uuid4(),
                'embedding_text': column_info.description,
                'payload': self._convert_column_info_from_mysql_to_qdrant(column_info)
            })
            # 别名字段
            for alia in column_info.alias:
                points.append({
                    'id': uuid.uuid4(),
                    'embedding_text': alia,
                    'payload': self._convert_column_info_from_mysql_to_qdrant(column_info)
                })

        # 向量列表
        # 分批控制每次 Embedding 调用的输入数量和请求规模
        embedding_texts = [point['embedding_text'] for point in points]
        embedding_batch_size = 5
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


    async def _save_value_info_to_es(self,meta_config:MetaConfig,column_infos:list[ColumnInfoMySQL]):
        """
        将配置中需要同步的字段值保存到 Elasticsearch

        meta_config: 元数据配置，包含表、字段以及字段是否需要同步的配置
        column_infos: 从 MySQL 元数据表中读取的字段信息
        """

        # 确保index存在  相当于 MySQL的table 和 qdrant的collection
        await self.value_es_repository.ensure_index()

        # 是否需要对值同步到es的index中 配置在meta_config.yaml中 读取为meta_config
        column2sync: dict[str, bool] = {}
        for table in meta_config.tables:
            for column in table.columns:
                column2sync[f'{table.name}.{column.name}'] = column.sync

        value_infos: list[ValueInfoES] = []
        for column_info in column_infos:
            sync = column2sync[column_info.id]
            if sync:
                # 查询所有值
                table_name = column_info.table_id   # 取出表名
                column_name = column_info.name      # 取出列名
                values = await self.dw_mysql_repository.get_column_values(table_name, column_name, 1000000)  # 根据表名列名 确定字段后取出所有值
                current_value_infos = [ValueInfoES(id=f"{column_info.id}.{value}",
                                                   value=value,
                                                   type=column_info.type,
                                                   column_id=column_info.id,
                                                   column_name=column_info.name,
                                                   table_id=column_info.table_id,
                                                   table_name=column_info.table_id
                                                   ) for value in values]
                value_infos.extend(current_value_infos)

        await self.value_es_repository.index(value_infos)


    async def build(self,config_path:Path):
        # 1. 加载配置文件
        meta_config: MetaConfig = load_config(config_path,MetaConfig)
        logger.info('加载配置文件成功')
        # 2. 处理表信息
        if meta_config.tables:
            # 2.1 保存表信息到meta数据库
            table_infos,column_infos = await self._save_tables_to_meta_db(meta_config)
            logger.info('保存表信息到meta数据库')

            # 2.2 为字段信息建立向量索引qdrant
            await self._save_column_info_to_qdrant(column_infos)
            logger.info('为字段信息建立向量索引')

            # 2.3 为字段取值建立全文索引es
            await self._save_value_info_to_es(meta_config,column_infos)
            logger.info('为字段取值建立全文索引')


"""        # 3. 处理指标信息
        if meta_config.metrics:
            # 3.1 保存指标信息到meta数据库
            metric_infos:list[MetricInfoMySQL] = []
            column_metrics: list[ColumnMetricMySQL] = []
            for metric in meta_config.metrics:

            # 3.2 为指标信息建立向量索引"""


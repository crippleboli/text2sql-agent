from typing import TypedDict
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant
from app.repository.es.value_es_repository import ValueESRepository

class ColumnInfoState(TypedDict):
    name: str
    type: str
    role: str
    examples: list
    description: str
    alias: list[str]


class TableInfoState(TypedDict):
    name: str
    role: str
    description: str
    columns: list[ColumnInfoState]


class MetricInfoState(TypedDict):
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]


class DataAgentState(TypedDict):
    query:str                                        # 用户查询
    keywords:list[str]                               # 用户查询关键字
    retrieved_columns:list[ColumnInfoQdrant]         # 召回的字段信息
    retrieved_metrics:list[MetricInfoQdrant]         # 召回的指标信息
    retrieved_values:list[ValueESRepository]         # 召回的字段取值

    table_infos:list[TableInfoState]                 # 表信息
    metric_infos:list[MetricInfoState]               # 指标信息

    error:str                                        # 验证sql时的错误信息

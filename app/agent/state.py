from typing import TypedDict

from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant


class DataAgentState(TypedDict):
    query:str                                        # 用户查询
    keywords:list[str]                               # 用户查询关键字
    error:str                                        # 验证sql时的错误信息
    retrieved_columns:list[ColumnInfoQdrant]         # 召回的字段信息

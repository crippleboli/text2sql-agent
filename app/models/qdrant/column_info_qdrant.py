"""
    ColumnInfoQdrant 用于描述字段的基本信息
    作为 Qdrant 向量点的 payload 保存
"""
from typing import  TypedDict

class ColumnInfoQdrant(TypedDict):
    """字段名称固定、字段类型固定的 dict 结构"""
    id:str
    name:str
    type:str
    role:str
    examples:str
    description:str
    alias:list
    table_id:str
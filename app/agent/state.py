from typing import TypedDict


class DataAgentState(TypedDict):
    query:str                   # 用户查询
    keywords:list[str]          # 用户查询关键字
    error:str                   # 验证sql时的错误信息

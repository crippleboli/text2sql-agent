from typing import  TypedDict


class ColumnInfoQdrant(TypedDict):
    id:str
    name:str
    role:str
    examples:str
    description:str
    alias:list
    table_id:str
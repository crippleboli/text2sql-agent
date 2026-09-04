from typing  import TypedDict


class ValueInfoES(TypedDict):
    id:str          # id
    value:str       # 值
    type:str        # 值类型
    column_id:str   # 所属的字段id
    column_name:str # 所属的字段名称
    table_id:str    # 所属的表id
    table_name:str  # 所属的表名称

"""
Meta MySQL 数据访问层

负责将业务逻辑层生成的表级元数据和字段级元数据，添加到 Meta MySQL 数据库的当前 Session 中，供外层事务统一提交保存
本文件不负责生成元数据、查询 DW 业务数据库或提交事务
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL


class MetaMySQLRepository:
    def __init__(self,session:AsyncSession):
        self.session = session

    async def save_table_infos(self, table_infos:list[TableInfoMySQL]):
        self.session.add_all(table_infos)

    async def save_column_infos(self, column_infos:list[ColumnInfoMySQL]):
        self.session.add_all(column_infos)
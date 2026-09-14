from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

class DWMySQLRepository:
    def __init__(self,session:AsyncSession):
        self.session = session

    async def get_column_types(self, table_name:str)-> dict[str,str]:
        """
        查询 DW 数据库指定表的所有字段及其字段类型。

        :param table_name: 要查询的表名
        :return: 字段名与字段类型组成的字典
        """
        sql = f'show columns from {table_name}'
        result = await self.session.execute(text(sql))
        return {row.Field: row.Type for row in result.fetchall()}

    async def get_column_values(self, table_name:str, column_name:str, limit:int):
        """
        查询业务表指定字段的不重复示例值，用于补充字段元数据中的 examples

        :param table_name: 要查询的业务表名
        :param column_name: 要查询的字段名
        :param limit: 最多返回的示例值数量
        :return: 用于字段元数据 examples 的示例值列表
        """
        sql = f'select distinct {column_name} from {table_name} limit {limit}'
        result = await self.session.execute(text(sql))
        return result.scalars().fetchall()
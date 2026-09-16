from langgraph.runtime import Runtime
from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def execute_sql(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer('执行sql')

    sql = state["sql"]
    dw_mysql_repository = runtime.context["dw_mysql_repository"]
    result = await dw_mysql_repository.execute_sql(sql)

    logger.info(f"执行SQL结果：{result}")
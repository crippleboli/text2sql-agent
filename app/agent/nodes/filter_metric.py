from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime
from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt
import yaml


async def filter_metric(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer('过滤指标')

    query = state['query']
    metric_infos = state['metric_infos']

    # 用llm过滤指标信息
    prompt = PromptTemplate(
        template=load_prompt('filter_metric_info'),
        input_variables=['query', 'metric_infos'],
    )
    output_parser = JsonOutputParser()
    chain = prompt | llm | output_parser

    result = await chain.ainvoke({
        'query': query,
        'metric_infos': yaml.dump(metric_infos,allow_unicode=True,sort_keys=False),
    })

    for metric_info in metric_infos[:]:
        if metric_info["name"] not in result:
            metric_infos.remove(metric_info)


    logger.info(f"过滤后的指标信息: {[metric_info['name'] for metric_info in metric_infos]}")
    return {"metric_infos": metric_infos}
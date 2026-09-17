from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime
from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant
from app.prompt.prompt_loader import load_prompt


async def recall_metric(state:DataAgentState,runtime:Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    # 输出进度信息
    writer({"stage": "召回指标"})

    # 获取用户问题
    query = state['query']
    # 获取关键字列表
    keywords = state['keywords']
    # 获取embedding服务
    embedding_client = runtime.context['embedding_client']

    metric_qdrant_repository = runtime.context['metric_qdrant_repository']


    try:
        # 1. 扩展关键字
        prompt = PromptTemplate(
            template=load_prompt('extend_keywords_for_metric_recall'),
            input_variables=['query']
        )
        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser

        result = await chain.ainvoke({'query': query})


        # 2. 合并关键字
        keywords = list(set(keywords + result))

        # 3. 召回指标
        retrieved_metrics_map: dict[str, MetricInfoQdrant] = {}
        for keyword in keywords:
            embedding = await embedding_client.aembed_query(keyword)
            payloads:list[MetricInfoQdrant] = await metric_qdrant_repository.search(embedding)

            # 不同关键词可能召回同样的内容 根据payload中的id去重
            for payload in payloads:
                column_id = payload['id']
                if column_id not in retrieved_metrics_map:
                    retrieved_metrics_map[column_id] = payload

        retrieved_metrics = list(retrieved_metrics_map.values())  # 取出值部分
        logger.info(f'召回指标信息：{list(retrieved_metrics_map.keys())}')

        return {'retrieved_metrics': retrieved_metrics}
    except Exception as e:
        logger.error(f"召回指标信息失败: {str(e)}")
        raise
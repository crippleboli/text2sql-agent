text2sql-agent/
├── app/
│   ├── agent/
│   │   ├── nodes/
│   │   │   ├── __init__.py
│   │   │   ├── add_extra_context.py
│   │   │   ├── correct_sql.py
│   │   │   ├── execute_sql.py
│   │   │   ├── extract_keywords.py
│   │   │   ├── filter_metric.py
│   │   │   ├── filter_table.py
│   │   │   ├── generate_sql.py
│   │   │   ├── merge_retrieved_info.py
│   │   │   ├── recall_column.py
│   │   │   ├── recall_metric.py
│   │   │   ├── recall_value.py
│   │   │   └── validate_sql.py
│   │   ├── __init__.py
│   │   ├── context.py
│   │   ├── graph.py
│   │   ├── llm.py
│   │   └── state.py
│   ├── api/
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── query_router.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── query_schema.py
│   │   ├── __init__.py
│   │   └── dependencies.py
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── embedding_client_manager.py
│   │   ├── es_client_manager.py
│   │   ├── mysql_client_manager.py
│   │   └── qdrant_client_manager.py
│   ├── conf/
│   │   ├── __init__.py
│   │   ├── app_config.py
│   │   ├── config_loader.py
│   │   └── meta_config.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── context.py
│   │   ├── lifespan.py
│   │   └── log.py
│   ├── models/
│   │   ├── es/
│   │   │   ├── __init__.py
│   │   │   └── value_info_es.py
│   │   ├── mysql/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── column_info_mysql.py
│   │   │   ├── column_metric_mysql.py
│   │   │   ├── metric_info_mysql.py
│   │   │   └── table_info_mysql.py
│   │   ├── qdrant/
│   │   │   ├── __init__.py
│   │   │   ├── column_info_qdrant.py
│   │   │   └── metric_info_qdrant.py
│   │   └── __init__.py
│   ├── prompt/
│   │   ├── __init__.py
│   │   └── prompt_loader.py
│   ├── repository/
│   │   ├── es/
│   │   │   ├── __init__.py
│   │   │   └── value_es_repository.py
│   │   ├── mysql/
│   │   │   ├── __init__.py
│   │   │   ├── dw_mysql_repository.py
│   │   │   └── meta_mysql_repository.py
│   │   ├── qdrant/
│   │   │   ├── __init__.py
│   │   │   ├── base_qdrant_repository.py
│   │   │   ├── column_qdrant_repository.py
│   │   │   └── metric_qdrant_repository.py
│   │   └── __init__.py
│   ├── scripts/
│   │   ├── __init__.py
│   │   └── build_meta_knowledge.py
│   ├── service/
│   │   ├── __init__.py
│   │   ├── meta_knowledge_service.py
│   │   └── query_service.py
│   └── __init__.py
├── conf/
│   ├── app_config.yaml
│   └── meta_config.yaml
├── prompts/
│   ├── correct_sql.prompt
│   ├── extend_keywords_for_column_recall.prompt
│   ├── extend_keywords_for_metric_recall.prompt
│   ├── extend_keywords_for_value_recall.prompt
│   ├── filter_metric_info.prompt
│   ├── filter_table_info.prompt
│   ├── generate_sql.prompt
│   └── plan_sql.prompt
├── .gitignore
├── .python-version
├── README.md
├── gen_tree.py
├── graph.mmd
├── main.py
├── note.txt
├── pyproject.toml
└── uv.lock
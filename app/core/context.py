from contextvars import ContextVar

# 以init方法 传入上下文变量名 构造特殊全局变量
request_id_ctx_var = ContextVar('request_id')
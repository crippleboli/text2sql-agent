"""
请求上下文变量定义文件：声明基于 contextvars.ContextVar 的轻量级全局上下文变量，用于实现多协程并发场景下的数据隔离
"""
from contextvars import ContextVar

# 以init方法 传入上下文变量名 构造特殊全局变量
request_id_ctx_var = ContextVar('request_id')
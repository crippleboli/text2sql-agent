"""
日志系统配置文件
实现功能：
1. 配置 Loguru 日志的控制台输出与本地文件
2. 利用 contextvars + Loguru patch 机制，实现多协程并发场景下的 request_id 链路追踪与隔离
"""
import asyncio
import sys
import uuid
from pathlib import Path
from loguru import logger
from app.conf.app_config import app_config
from app.core.context import request_id_ctx_var


# 日志模板
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<magenta>request_id - {extra[request_id]}</magenta> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


def inject_request_id(record):
    try:
        request_id = request_id_ctx_var.get()   # 尝试获取协程任务 通常由 FastAPI 等中间件提前 set 配置好
    except Exception as e:
        request_id = uuid.uuid4()               # 获取不到 uuid兜底重新配置
    record["extra"]["request_id"] = request_id


# 移除初始配置
logger.remove()
# 添加自写函数
logger = logger.patch(inject_request_id)

# 终端输出
if app_config.logging.console.enable:
    logger.add(sink=sys.stdout,     # 标准输出到终端
               level=app_config.logging.console.level,  # 日志过滤的最低级别
               format=log_format)   # 日志的渲染格式

# 日志文件输出
if app_config.logging.file.enable:
    path = Path(app_config.logging.file.path)
    path.mkdir(parents=True, exist_ok=True)     # 确保路径存在
    logger.add(
        sink=path / "app.log",
        level=app_config.logging.file.level,
        format=log_format,          # 日志的渲染格式
        rotation=app_config.logging.file.rotation,
        retention=app_config.logging.file.retention,
        encoding="utf-8"
    )

if __name__ == '__main__':
    async def test1():
        # 接收请求
        request_id_ctx_var.set('request-1')

        # 模拟处理
        await asyncio.sleep(1)
        await graph('request-1')


    async def test2():
        # 接收请求
        request_id_ctx_var.set('request-2')

        # 模拟处理
        await asyncio.sleep(1)
        await graph('request-2')

    async def graph(request:str):
        # 打印日志
        logger.info(request)

    async def main():
        await asyncio.gather(test1(), test2())

    asyncio.run(main())
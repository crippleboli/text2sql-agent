from typing import TypeVar,Type
from omegaconf import OmegaConf
from pathlib import Path

# 通用类型 T
T = TypeVar('T')

def load_config(config_file:Path,schema_cls:Type[T])->T:
    """
        标准的OmegaConf解析步骤 参考官方文档 注意使用 TypeVar兼容两套配置
    :param config_file: 终端传入的 yaml 路径
    :param schema_cls:  app/conf/app_config.py(meta_config.py) 中定义的类结构 内存读取 不传路径
    :return: 定义的类结构中的 根对象实例：MetaConfig / AppConfig
    """
    # 解析终端传入路径下的yaml配置
    context = OmegaConf.load(config_file)
    # 结构化指定的 schema 结构：app 配置/meta 配置
    schema = OmegaConf.structured(schema_cls)
    # merge 后转为类
    config: T = OmegaConf.to_object(OmegaConf.merge(schema, context))
    return config
from typing import TypeVar,Type
from omegaconf import OmegaConf
from pathlib import Path

# 通用类型 T
T = TypeVar('T')

def load_config(config_file:Path,schema_cls:Type[T])->T:
    context = OmegaConf.load(config_file)
    schema = OmegaConf.structured(schema_cls)
    config: T = OmegaConf.to_object(OmegaConf.merge(schema, context))
    return config
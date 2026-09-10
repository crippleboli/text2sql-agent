from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from omegaconf import OmegaConf


@dataclass
class ColumnConfig:
    name: str
    role: str
    description: str
    alias: list[str]
    sync: bool


@dataclass
class TableConfig:
    name: str
    role: str
    description: str
    columns: list[ColumnConfig]


@dataclass
class MetricConfig:
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]


@dataclass
class MetaConfig:
    tables: Optional[list[TableConfig]] = None
    metrics: Optional[list[MetricConfig]] = None


config_file = Path(__file__).parents[2] / 'conf' / 'meta_config.yaml'

# 创建“结构化配置”
schema = OmegaConf.structured(MetaConfig)

# 加载 YAML
content = OmegaConf.load(config_file)

# 合并 + 校验
conf = OmegaConf.merge(schema, content)

meta_config: MetaConfig = OmegaConf.to_object(conf)

if __name__ == '__main__':
    print(meta_config.metrics[0].name)

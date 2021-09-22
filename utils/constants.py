import yaml
from enum import unique, Enum

"""
从配置文件中读取数据
"""

config_path = '../config/config.yaml'
with open(config_path, 'r') as f:
    config = yaml.load(f.read(), Loader=yaml.BaseLoader)


@unique
class Constants(Enum):
    # Java libraries path
    JARS_PATH = config['jars_path']

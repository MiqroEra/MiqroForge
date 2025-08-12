"""MiqroForge 命令行工具包"""

__version__ = "0.1.0"
__author__ = "MiqroForge Team"
__description__ = "MiqroForge 计算集群管理命令行工具"

# 导入主要模块
from . import managers
from . import config

__all__ = [
    "managers",
    "config",
]

"""MiqroForge 配置文件

管理各种服务的连接配置参数。
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path

# 配置文件路径
CONFIG_DIR = Path.home() / ".miqroforge"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
PROJECT_CONFIG_FILE = Path(__file__).parent.parent.parent / "config" / "config.json"

# 默认配置
DEFAULT_CONFIG = {
    "kubernetes": {
        "config_file": None,  # 使用默认kubeconfig
        "context": None,      # 使用默认context
    },
    "docker": {
        "host": None,         # 使用默认Docker socket
        "tls_verify": False,
        "cert_path": None,
    },
    "mysql": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "",
        "database": "miqroforge",
        "charset": "utf8mb4",
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": None,
    }
}


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        """初始化配置管理器"""
        self.config = DEFAULT_CONFIG.copy()
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        # 首先尝试加载项目配置文件
        if PROJECT_CONFIG_FILE.exists():
            try:
                import json
                with open(PROJECT_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    project_config = json.load(f)
                    if project_config:
                        self._merge_config(project_config)
                        print(f"已加载项目配置文件: {PROJECT_CONFIG_FILE}")
            except Exception as e:
                print(f"加载项目配置文件失败: {e}")
        
        # 然后尝试加载用户配置文件（会覆盖项目配置）
        if CONFIG_FILE.exists():
            try:
                import yaml
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        self._merge_config(user_config)
                        print(f"已加载用户配置文件: {CONFIG_FILE}")
            except Exception as e:
                print(f"加载用户配置文件失败: {e}")
    
    def _merge_config(self, user_config: Dict[str, Any]):
        """合并用户配置到默认配置"""
        for section, values in user_config.items():
            if section in self.config and isinstance(values, dict):
                self.config[section].update(values)
            else:
                self.config[section] = values
    
    def get(self, section: str, key: Optional[str] = None) -> Any:
        """获取配置值
        
        Args:
            section: 配置节名称
            key: 配置键名称，如果为None则返回整个节
            
        Returns:
            配置值
        """
        if section not in self.config:
            return None
        
        if key is None:
            return self.config[section]
        
        return self.config[section].get(key)
    
    def set(self, section: str, key: str, value: Any):
        """设置配置值
        
        Args:
            section: 配置节名称
            key: 配置键名称
            value: 配置值
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
    
    def save(self):
        """保存配置到文件"""
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            
            import yaml
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            print(f"配置已保存到: {CONFIG_FILE}")
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get_kubernetes_config(self) -> Dict[str, Any]:
        """获取Kubernetes配置
        
        Returns:
            Kubernetes配置字典
        """
        return self.get("kubernetes")
    
    def get_docker_config(self) -> Dict[str, Any]:
        """获取Docker配置
        
        Returns:
            Docker配置字典
        """
        return self.get("docker")
    
    def get_mysql_config(self) -> Dict[str, Any]:
        """获取MySQL配置
        
        Returns:
            MySQL配置字典
        """
        return self.get("mysql")
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置
        
        Returns:
            日志配置字典
        """
        return self.get("logging")
    
    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置
        
        Returns:
            所有配置的字典
        """
        return self.config.copy()


# 全局配置实例
config = ConfigManager()

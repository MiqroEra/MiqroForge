"""Kubernetes服务管理器

提供对Kubernetes集群的基本连接接口。
"""

from kubernetes import client, config
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class KubernetesManager:
    """Kubernetes集群管理器"""
    
    def __init__(self, config_file: Optional[str] = None, context: Optional[str] = None, 
                 config_manager=None):
        """初始化Kubernetes客户端
        
        Args:
            config_file: kubeconfig文件路径，如果为None则自动从配置管理器读取
            context: 集群上下文，如果为None则自动从配置管理器读取
            config_manager: 配置管理器实例，如果为None则使用默认配置
        """
        # 如果没有提供参数，从配置管理器读取
        if config_file is None or context is None:
            if config_manager is None:
                from ..config import config as default_config
                config_manager = default_config
            
            k8s_config = config_manager.get_kubernetes_config()
            if config_file is None:
                config_file = k8s_config.get("config_file")
            if context is None:
                context = k8s_config.get("context")
        
        try:
            if config_file:
                config.load_kube_config(config_file=config_file, context=context)
            else:
                config.load_incluster_config()  # 在集群内运行时使用
            
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.networking_v1 = client.NetworkingV1Api()
            logger.info(f"Kubernetes客户端初始化成功 (config: {config_file}, context: {context})")
        except Exception as e:
            logger.error(f"Kubernetes客户端初始化失败: {e}")
            raise
    
    def test_connection(self) -> bool:
        """测试连接是否正常
        
        Returns:
            连接是否正常
        """
        try:
            # 尝试获取命名空间列表来测试连接
            self.v1.list_namespace()
            return True
        except Exception as e:
            logger.error(f"Kubernetes连接测试失败: {e}")
            return False

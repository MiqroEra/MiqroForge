"""Docker服务管理器

提供对Docker容器的基本连接接口。
"""

import docker
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DockerManager:
    """Docker容器管理器"""
    
    def __init__(self, host: Optional[str] = None, tls_verify: bool = False, 
                 cert_path: Optional[str] = None, config_manager=None):
        """初始化Docker客户端
        
        Args:
            host: Docker守护进程地址，如果为None则自动从配置管理器读取
            tls_verify: 是否验证TLS证书，如果为None则自动从配置管理器读取
            cert_path: TLS证书路径，如果为None则自动从配置管理器读取
            config_manager: 配置管理器实例，如果为None则使用默认配置
        """
        # 如果没有提供参数，从配置管理器读取
        if host is None or cert_path is None:
            if config_manager is None:
                from ..config import config as default_config
                config_manager = default_config
            
            docker_config = config_manager.get_docker_config()
            if host is None:
                host = docker_config.get("host")
            if tls_verify is False:  # 默认False，所以需要特殊处理
                tls_verify = docker_config.get("tls_verify", False)
            if cert_path is None:
                cert_path = docker_config.get("cert_path")
        
        try:
            # 构建Docker客户端配置
            if host:
                # 如果指定了host，使用DockerClient
                if tls_verify and cert_path:
                    tls_config = docker.tls.TLSConfig(
                        ca_cert=cert_path,
                        verify=True
                    )
                    self.client = docker.DockerClient(base_url=host, tls=tls_config)
                else:
                    self.client = docker.DockerClient(base_url=host)
            else:
                # 使用默认配置
                self.client = docker.from_env()
            
            logger.info(f"Docker客户端连接成功 (host: {host}, tls_verify: {tls_verify})")
        except Exception as e:
            logger.error(f"Docker客户端连接失败: {e}")
            raise
    
    def test_connection(self) -> bool:
        """测试连接是否正常
        
        Returns:
            连接是否正常
        """
        try:
            # 尝试获取Docker信息来测试连接
            self.client.info()
            return True
        except Exception as e:
            logger.error(f"Docker连接测试失败: {e}")
            return False

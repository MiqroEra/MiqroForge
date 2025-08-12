"""综合服务管理器

提供对Kubernetes、Docker、MySQL等服务的统一管理接口。
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ServiceManager:
    """综合服务管理器"""
    
    def __init__(self, config_manager=None):
        """初始化服务管理器
        
        Args:
            config_manager: 配置管理器实例，如果为None则使用默认配置
        """
        self.config_manager = config_manager
        self.k8s = None
        self.docker = None
        self.mysql = None
        self.sqlalchemy = None
    
    def init_kubernetes(self, config_file: Optional[str] = None, 
                       context: Optional[str] = None) -> bool:
        """初始化Kubernetes客户端
        
        Args:
            config_file: kubeconfig文件路径，如果为None则自动从配置管理器读取
            context: 集群上下文，如果为None则自动从配置管理器读取
            
        Returns:
            是否初始化成功
        """
        try:
            from .k8s_manager import KubernetesManager
            self.k8s = KubernetesManager(config_file, context, self.config_manager)
            logger.info("Kubernetes客户端初始化成功")
            return True
        except ImportError:
            logger.error("请安装kubernetes库: pip install kubernetes")
            return False
        except Exception as e:
            logger.error(f"Kubernetes初始化失败: {e}")
            return False
    
    def init_docker(self, host: Optional[str] = None, tls_verify: bool = False,
                   cert_path: Optional[str] = None) -> bool:
        """初始化Docker客户端
        
        Args:
            host: Docker守护进程地址，如果为None则自动从配置管理器读取
            tls_verify: 是否验证TLS证书，如果为None则自动从配置管理器读取
            cert_path: TLS证书路径，如果为None则自动从配置管理器读取
            
        Returns:
            是否初始化成功
        """
        try:
            from .docker_manager import DockerManager
            self.docker = DockerManager(host, tls_verify, cert_path, self.config_manager)
            logger.info("Docker客户端初始化成功")
            return True
        except ImportError:
            logger.error("请安装docker库: pip install docker")
            return False
        except Exception as e:
            logger.error(f"Docker初始化失败: {e}")
            return False
    
    def init_mysql(self, host: Optional[str] = None, user: Optional[str] = None, 
                   password: Optional[str] = None, database: Optional[str] = None, 
                   port: Optional[int] = None) -> bool:
        """初始化MySQL连接
        
        Args:
            host: 数据库主机地址，如果为None则自动从配置管理器读取
            user: 用户名，如果为None则自动从配置管理器读取
            password: 密码，如果为None则自动从配置管理器读取
            database: 数据库名，如果为None则自动从配置管理器读取
            port: 端口号，如果为None则自动从配置管理器读取
            
        Returns:
            是否初始化成功
        """
        try:
            from .mysql_manager import MySQLManager
            self.mysql = MySQLManager(host, user, password, database, port, self.config_manager)
            if self.mysql.connect():
                logger.info("MySQL客户端初始化成功")
                return True
            else:
                self.mysql = None
                return False
        except ImportError:
            logger.error("请安装mysql-connector-python库: pip install mysql-connector-python")
            return False
        except Exception as e:
            logger.error(f"MySQL初始化失败: {e}")
            return False
    
    def init_sqlalchemy(self, connection_string: Optional[str] = None) -> bool:
        """初始化SQLAlchemy连接
        
        Args:
            connection_string: 数据库连接字符串，如果为None则自动从配置管理器生成
            
        Returns:
            是否初始化成功
        """
        try:
            from .mysql_manager import SQLAlchemyManager
            self.sqlalchemy = SQLAlchemyManager(connection_string, self.config_manager)
            if self.sqlalchemy.connect():
                logger.info("SQLAlchemy客户端初始化成功")
                return True
            else:
                self.sqlalchemy = None
                return False
        except ImportError:
            logger.error("请安装sqlalchemy库: pip install sqlalchemy")
            return False
        except Exception as e:
            logger.error(f"SQLAlchemy初始化失败: {e}")
            return False
    
    def init_all_services(self) -> bool:
        """初始化所有服务（使用默认配置）
        
        Returns:
            是否全部初始化成功
        """
        success_count = 0
        
        # 初始化Kubernetes
        if self.init_kubernetes():
            success_count += 1
        
        # 初始化Docker
        if self.init_docker():
            success_count += 1
        
        # 初始化MySQL
        if self.init_mysql():
            success_count += 1
        
        # 初始化SQLAlchemy
        if self.init_sqlalchemy():
            success_count += 1
        
        logger.info(f"服务初始化完成: {success_count}/4 个服务连接成功")
        return success_count == 4
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取各服务连接状态
        
        Returns:
            服务状态字典
        """
        status = {}
        
        # Kubernetes状态
        if self.k8s:
            status["kubernetes"] = "已连接"
        else:
            status["kubernetes"] = "未连接"
        
        # Docker状态
        if self.docker:
            status["docker"] = "已连接"
        else:
            status["docker"] = "未连接"
        
        # MySQL状态
        if self.mysql and self.mysql.is_connected():
            status["mysql"] = "已连接"
        elif self.mysql:
            status["mysql"] = "连接失败"
        else:
            status["mysql"] = "未连接"
        
        # SQLAlchemy状态
        if self.sqlalchemy and self.sqlalchemy.is_connected():
            status["sqlalchemy"] = "已连接"
        elif self.sqlalchemy:
            status["sqlalchemy"] = "连接失败"
        else:
            status["sqlalchemy"] = "未连接"
        
        return status
    
    def disconnect_all(self):
        """断开所有服务连接"""
        if self.mysql:
            self.mysql.disconnect()
            self.mysql = None
        
        if self.sqlalchemy:
            self.sqlalchemy = None
        
        self.k8s = None
        self.docker = None
        
        logger.info("所有服务连接已断开")

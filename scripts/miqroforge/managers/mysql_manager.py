"""MySQL服务管理器

提供对MySQL数据库的基本连接接口。
"""

import mysql.connector
from mysql.connector import Error
from typing import Optional
import logging
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class MySQLManager:
    """MySQL数据库管理器"""
    
    def __init__(self, host: Optional[str] = None, user: Optional[str] = None, 
                 password: Optional[str] = None, database: Optional[str] = None, 
                 port: Optional[int] = None, config_manager=None):
        """初始化MySQL连接参数
        
        Args:
            host: 数据库主机地址，如果为None则自动从配置管理器读取
            user: 用户名，如果为None则自动从配置管理器读取
            password: 密码，如果为None则自动从配置管理器读取
            database: 数据库名，如果为None则自动从配置管理器读取
            port: 端口号，如果为None则自动从配置管理器读取
            config_manager: 配置管理器实例，如果为None则使用默认配置
        """
        # 如果没有提供参数，从配置管理器读取
        if any(param is None for param in [host, user, password, database, port]):
            if config_manager is None:
                from ..config import config as default_config
                config_manager = default_config
            
            mysql_config = config_manager.get_mysql_config()
            if host is None:
                host = mysql_config.get("host", "localhost")
            if user is None:
                user = mysql_config.get("user", "root")
            if password is None:
                password = mysql_config.get("password", "")
            if database is None:
                database = mysql_config.get("database", "miqroforge")
            if port is None:
                port = mysql_config.get("port", 3306)
        
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """建立数据库连接
        
        Returns:
            连接是否成功
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            logger.info("MySQL连接成功")
            return True
        except Error as e:
            logger.error(f"MySQL连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("MySQL连接已断开")
    
    def is_connected(self) -> bool:
        """检查连接状态
        
        Returns:
            是否已连接
        """
        return self.connection is not None and self.connection.is_connected()


class SQLAlchemyManager:
    """SQLAlchemy数据库管理器"""
    
    def __init__(self, connection_string: Optional[str] = None, config_manager=None):
        """初始化SQLAlchemy连接
        
        Args:
            connection_string: 数据库连接字符串，如果为None则自动从配置管理器生成
            config_manager: 配置管理器实例，如果为None则使用默认配置
        """
        if connection_string is None:
            if config_manager is None:
                from ..config import config as default_config
                config_manager = default_config
            
            mysql_config = config_manager.get_mysql_config()
            host = mysql_config.get("host", "localhost")
            port = mysql_config.get("port", 3306)
            user = mysql_config.get("user", "root")
            password = mysql_config.get("password", "")
            database = mysql_config.get("database", "miqroforge")
            
            # 对密码进行URL编码，处理特殊字符
            encoded_password = quote_plus(password)
            
            connection_string = f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{database}"
        
        self.connection_string = connection_string
        self.engine = None
    
    def connect(self) -> bool:
        """建立数据库连接
        
        Returns:
            连接是否成功
        """
        try:
            from sqlalchemy import create_engine
            self.engine = create_engine(self.connection_string)
            # 测试连接
            from sqlalchemy import text
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("SQLAlchemy连接成功")
            return True
        except Exception as e:
            logger.error(f"SQLAlchemy连接失败: {e}")
            return False
    
    def is_connected(self) -> bool:
        """检查连接状态
        
        Returns:
            是否已连接
        """
        return self.engine is not None



"""Docker服务管理器

提供对Docker容器的基本连接接口。
"""

import docker
from typing import Optional, List
import logging
import json

from docker.api import container

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

    def list_images(self) -> List[str]:
        """列出所有镜像"""
        images = self.client.images.list()
        # print(images)
        image_names = []
        for image in images:
            if image.tags is not None and len(image.tags) > 0:
                image_names.extend(image.tags)

        return image_names

    def check_image_exists(self, image: str) -> bool:
        if ":" not in image:
            image = f"{image}:latest"
        # print(f"image: {image}")
        """检查镜像是否存在"""
        for image_name in self.list_images():
            # print(f"image_name: {image_name}")
            if image == image_name:
                return True
        return False
    
    def pull(self, image: str, show_progress: bool = True) -> bool:
        """拉取镜像
        
        Args:
            image: 镜像名称
            show_progress: 是否显示进度条，默认为True
            
        Returns:
            拉取是否成功
        """
        if self.check_image_exists(image):
            print(f"Image {image} already exists, skip pulling.")
            return True

        print(f"Pulling image: {image}")
        
        try:
            if show_progress:
                # 使用带进度显示的拉取方式，实现真正的进度条效果
                for line in self.client.api.pull(image, stream=True, decode=True):
                    if 'id' in line and 'status' in line:
                        if 'progress' in line:
                            # 显示下载进度，在同一行更新
                            progress = line.get('progress', '')
                            status = line.get('status', '')
                            layer_id = line.get('id', '')
                            # 使用 \r 回到行首，\033[K 清除当前行
                            print(f"\r{layer_id}: {status} {progress}", end='', flush=True)
                        # else:
                        #     # 显示状态信息，换行显示
                        #     status = line.get('status', '')
                        #     layer_id = line.get('id', '')
                        #     print(f"\n{layer_id}: {status}")
                
                # 拉取完成后换行
                print()
            else:
                # 静默拉取
                self.client.images.pull(image)
                
            print(f"Pull image success: {image}")
            return True
            
        except Exception as e:
            print(f"Pull image failed: {image}, error: {e}")
            logger.error(f"拉取镜像失败: {image}, 错误: {e}")
            return False
    
    def connect(self) -> bool:
        """连接Docker"""
        return self.test_connection()

    def get_node_description(self, image: str, app_path: str) -> str:
        """获取节点描述"""
        container = None
        try:
            container = self.client.containers.run(image, command=f"bash -c 'cd {app_path} && cat help.md'", detach=False, remove=True)
            description = container.decode('utf-8')
            print(f"description: \n{description}\n")
            return description
        except Exception as e:
            logger.error(f"get node description failed: {e}")
            self.remove_failed_containers()
            return ''

    def get_node_json(self, image: str, app_path: str) -> dict:
        """获取节点JSON"""
        container = None
        try:
            container = self.client.containers.run(image, command=f"bash -c 'cd {app_path} && cat node.json'", detach=False, remove=True)
            node_json_str = container.decode('utf-8')
            node_json = json.loads(node_json_str)
            node_json['description'] = self.get_node_description(image, app_path)
            return node_json
        except Exception as e:
            logger.error(f"read node.json failed: {e}")
            self.remove_failed_containers()
            return None

    def list_containers(self, all_containers: bool = True) -> List[dict]:
        """列出所有容器
        
        Args:
            all_containers: 是否包含停止的容器
            
        Returns:
            容器信息列表
        """
        try:
            containers = self.client.containers.list(all=all_containers)
            container_info = []
            for container in containers:
                container_info.append({
                    'id': container.id,
                    'name': container.name,
                    'status': container.status,
                    'image': container.image.tags[0] if container.image.tags else container.image.id,
                    'created': container.attrs['Created']
                })
            return container_info
        except Exception as e:
            logger.error(f"列出容器失败: {e}")
            return []

    def remove_container(self, container_id: str, force: bool = False) -> bool:
        """删除指定容器
        
        Args:
            container_id: 容器ID或名称
            force: 是否强制删除运行中的容器
            
        Returns:
            删除是否成功
        """
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
            logger.info(f"容器 {container_id} 删除成功")
            return True
        except Exception as e:
            logger.error(f"删除容器 {container_id} 失败: {e}")
            return False

    def remove_failed_containers(self, status_filter: str = "created") -> int:
        """删除指定状态的失败容器
        
        Args:
            status_filter: 要删除的容器状态，默认为"created"
            
        Returns:
            删除的容器数量
        """
        try:
            containers = self.client.containers.list(all=True)
            removed_count = 0
            
            for container in containers:
                if container.status.lower() == status_filter.lower():
                    try:
                        container.remove(force=True)
                        logger.info(f"删除失败容器: {container.name} (ID: {container.id})")
                        removed_count += 1
                    except Exception as e:
                        logger.error(f"删除容器 {container.name} 失败: {e}")
            
            logger.info(f"成功删除 {removed_count} 个状态为 '{status_filter}' 的容器")
            return removed_count
        except Exception as e:
            logger.error(f"清理失败容器时出错: {e}")
            return 0

    def cleanup_all_stopped_containers(self) -> int:
        """清理所有已停止的容器
        
        Returns:
            清理的容器数量
        """
        try:
            containers = self.client.containers.list(all=True)
            removed_count = 0
            
            for container in containers:
                if container.status in ['exited', 'created', 'dead']:
                    try:
                        container.remove(force=True)
                        logger.info(f"清理停止的容器: {container.name} (ID: {container.id})")
                        removed_count += 1
                    except Exception as e:
                        logger.error(f"清理容器 {container.name} 失败: {e}")
            
            logger.info(f"成功清理 {removed_count} 个已停止的容器")
            return removed_count
        except Exception as e:
            logger.error(f"清理已停止容器时出错: {e}")
            return 0

    def list_containers(self, all_containers: bool = True) -> List[dict]:
        """列出所有容器
        
        Args:
            all_containers: 是否包含停止的容器
            
        Returns:
            容器信息列表
        """
        try:
            containers = self.client.containers.list(all=all_containers)
            container_info = []
            for container in containers:
                container_info.append({
                    'id': container.id,
                    'name': container.name,
                    'status': container.status,
                    'image': container.image.tags[0] if container.image.tags else container.image.id,
                    'created': container.attrs['Created']
                })
            return container_info
        except Exception as e:
            logger.error(f"列出容器失败: {e}")
            return []

    def remove_container(self, container_id: str, force: bool = False) -> bool:
        """删除指定容器
        
        Args:
            container_id: 容器ID或名称
            force: 是否强制删除运行中的容器
            
        Returns:
            删除是否成功
        """
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
            logger.info(f"容器 {container_id} 删除成功")
            return True
        except Exception as e:
            logger.error(f"删除容器 {container_id} 失败: {e}")
            return False

    def remove_failed_containers(self, status_filter: str = "created") -> int:
        """删除指定状态的失败容器
        
        Args:
            status_filter: 要删除的容器状态，默认为"created"
            
        Returns:
            删除的容器数量
        """
        try:
            containers = self.client.containers.list(all=True)
            removed_count = 0
            
            for container in containers:
                if container.status.lower() == status_filter.lower():
                    try:
                        container.remove(force=True)
                        logger.info(f"删除失败容器: {container.name} (ID: {container.id})")
                        removed_count += 1
                    except Exception as e:
                        logger.error(f"删除容器 {container.name} 失败: {e}")
            
            logger.info(f"成功删除 {removed_count} 个状态为 '{status_filter}' 的容器")
            return removed_count
        except Exception as e:
            logger.error(f"清理失败容器时出错: {e}")
            return 0

    def cleanup_all_stopped_containers(self) -> int:
        """清理所有已停止的容器
        
        Returns:
            清理的容器数量
        """
        try:
            containers = self.client.containers.list(all=True)
            removed_count = 0
            
            for container in containers:
                if container.status in ['exited', 'created', 'dead']:
                    try:
                        container.remove(force=True)
                        logger.info(f"清理停止的容器: {container.name} (ID: {container.id})")
                        removed_count += 1
                    except Exception as e:
                        logger.error(f"清理容器 {container.name} 失败: {e}")
            
            logger.info(f"成功清理 {removed_count} 个已停止的容器")
            return removed_count
        except Exception as e:
            logger.error(f"清理已停止容器时出错: {e}")
            return 0

    def find_exposed_port(self, container_name: str, port: int) -> int:
        """查找指定容器的指定端口"""
        try:
            container = self.client.containers.get(container_name)
            return container.ports[f"{port}/tcp"][0]['HostPort']
        except Exception as e:
            logger.error(f"查找端口失败: {e}")
            return None
        
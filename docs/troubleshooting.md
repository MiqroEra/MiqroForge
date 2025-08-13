### 常见安装问题

#### 1. 权限不足错误
```bash
# 错误信息：Please run this script with sudo or root
# 解决方案：使用sudo运行脚本
sudo ./scripts/install_miqroforge.sh
```

#### 2. 系统版本不兼容
```bash
# 错误信息：This script only supports Ubuntu 20.04 or higher
# 解决方案：确保系统版本满足要求
lsb_release -a
# 或升级到支持的版本
```

#### 3. Docker安装失败
```bash
# 检查Docker服务状态
sudo systemctl status docker

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 检查Docker版本
docker --version
docker-compose --version
```

#### 4. NFS服务问题
```bash
# 检查NFS服务状态
sudo systemctl status nfs-kernel-server

# 重启NFS服务
sudo systemctl restart nfs-kernel-server

# 检查NFS导出配置
cat /etc/exports
sudo exportfs -a

# 检查NFS端口
sudo netstat -tulpn | grep :2049
```

#### 5. K3s安装失败
```bash
# 检查K3s服务状态
sudo systemctl status k3s

# 查看K3s日志
sudo journalctl -u k3s -f

# 重新安装K3s
sudo k3s-uninstall.sh
# 然后重新运行安装脚本
```

#### 6. 容器启动失败
```bash
# 查看容器状态
docker ps -a

# 查看容器日志
docker logs miqroforge-web
docker logs miqroforge-mysql
docker logs miqroforge-minio

# 重启服务
docker compose -f docker-compose.yaml restart

# 重新创建并启动服务
docker compose -f docker-compose.yaml up -d --force-recreate
```

#### 7. 端口冲突
```bash
# 检查端口占用
sudo netstat -tulpn | grep :30080
sudo netstat -tulpn | grep :3306
sudo netstat -tulpn | grep :9000

# 修改端口配置（编辑docker-compose.yaml）
# 将30080改为其他可用端口
```

#### 8. 磁盘空间不足
```bash
# 检查磁盘空间
df -h

# 清理Docker镜像和容器
docker system prune -a

# 清理日志文件
sudo find /var/log -name "*.log" -delete
```

#### 9. 网络连接问题
```bash
# 检查网络配置
ip addr show

# 检查防火墙设置
sudo ufw status

# 允许必要端口通过防火墙
sudo ufw allow 30080
sudo ufw allow 3306
sudo ufw allow 9000
sudo ufw allow 9001
```

#### 10. Python依赖问题
```bash
# 检查Python版本
python3 --version

# 重新安装依赖
pip install -e . --break-system-packages --force-reinstall

# 清理pip缓存
pip cache purge
```

### 日志查看

#### 系统日志
```bash
# 查看系统日志
sudo journalctl -f

# 查看特定服务日志
sudo journalctl -u docker -f
sudo journalctl -u nfs-kernel-server -f
sudo journalctl -u k3s -f
```

#### 应用日志
```bash
# 查看MiqroForge日志
tail -f ./data/miqroforge/backend/logs/*.log

# 查看Docker容器日志
docker logs -f miqroforge-web
```

### 重置环境

如果遇到严重问题需要重置环境：

```bash
# 停止所有服务
docker compose -f docker-compose.yaml down

# 卸载K3s
sudo k3s-uninstall.sh

# 清理数据目录
sudo rm -rf /data/miqroforge
sudo rm -rf ./data

# 重新运行安装脚本
sudo ./scripts/install_miqroforge.sh
```

### 获取帮助

如果以上解决方案无法解决问题：

1. 检查系统日志获取详细错误信息
2. 确认系统满足最低要求
3. 在GitHub Issues中搜索类似问题
4. 提交新的Issue并提供详细的错误信息和系统环境
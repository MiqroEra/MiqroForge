> [English](README.md) | 中文 

# MiqroForge 安装脚本

这是一个自动化安装脚本，用于在Linux系统上快速部署和配置MiqroForge微服务架构平台。脚本集成了完整的容器化运行环境，包括存储、数据库、Web服务等核心组件。

## 功能特性

- **一键部署**: 自动化安装Docker、Python、NFS、K3s等所有依赖组件
- **容器化架构**: 基于Docker Compose的微服务部署，支持快速启动和扩展
- **存储集成**: 内置MinIO对象存储和MySQL数据库，提供完整的数据存储解决方案
- **Kubernetes就绪**: 自动安装K3s轻量级Kubernetes集群，支持容器编排
- **网络服务**: 集成NFS文件共享服务，支持分布式文件系统
- **Web界面**: 提供基于Web的管理界面，支持通过浏览器访问和管理

## 系统要求

- Ubuntu >= 20.04 操作系统
- 具有root权限或sudo权限
- 网络连接（用于下载Docker、Python、NFS、K3s等所有依赖组件）
- 至少2GB内存和10GB磁盘空间

## 使用方法


### 克隆仓库后运行

```bash
# 克隆仓库
git clone https://github.com/MiqroEra/MiqroForge.git
cd MiqroForge

# 运行安装脚本
sudo ./scripts/install_miqroforge.sh
```

## 安装过程

脚本会自动执行以下步骤：
- 安装 Docker 和 Docker Compose
- 安装 Python >= 3.8 和依赖包
- 安装 NFS Server
- 安装 K3s (轻量级 Kubernetes 发行版)
- 基于 Docker Compose 安装 MiqroForge v1.0
    - [docker-compose.yaml](docker-compose.yaml)

## Kubernetes 安装

本脚本自动安装 K3s (轻量级 Kubernetes 发行版)，如需换成其他 Kubernetes 发行版，请先卸载K3s.
- 卸载命令：
```bash
sudo k3s-uninstall.sh
```

- 其他安装方式：
    - [kubekey 安装文档](https://github.com/kubesphere/kubekey/blob/master/README_zh-CN.md)
    - [Kubernetes 官方文档](https://kubernetes.io/zh/docs/setup/)

## 测试

详情请参考: [test.ipynb](tests/test_cases.ipynb)

## 故障排除
详情请参考: [troubleshooting.md](docs/troubleshooting_zh-CN.md)

## 文档
详情请参考: [MiqroForge 文档](https://miqroforge-docs.readthedocs.io/zh-cn/latest)
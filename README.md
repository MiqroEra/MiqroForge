# MiqroForge 安装脚本

这是一个自动化安装脚本，用于在Linux系统上安装和配置MiqroForge运行环境。

## 功能特性

- **Docker自动安装**: 支持Ubuntu >= 20.04 操作系统
- **跨平台支持**: 支持多种Linux发行版
- **轻量级**: 专注于Docker环境准备，Kubernetes需要手动安装

## 系统要求

- Linux操作系统（Ubuntu/Debian）
- 具有root权限或sudo权限
- 网络连接（用于下载Docker）
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

## 故障排除
详情请参考: [troubleshooting.md](docs/troubleshooting.md)

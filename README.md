# MiqroForge 安装脚本

这是一个自动化安装脚本，用于在Linux系统上安装和配置MiqroForge运行环境。

## 功能特性

- **Docker自动安装**: 支持Ubuntu/Debian、CentOS/RHEL、Alpine等主流Linux发行版
- **跨平台支持**: 支持多种Linux发行版
- **轻量级**: 专注于Docker环境准备，Kubernetes需要手动安装

## 系统要求

- Linux操作系统（Ubuntu/Debian、CentOS/RHEL、Alpine等）
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
- 安装Docker
- 安装Python 3.10
- 安装并运行MySQL
- 安装并运行Minio
- 安装MiqroForge
- 运行MiqroForge
- 运行MiqroForge的Web UI




## Kubernetes 安装

本脚本仅负责Docker环境的准备。如需安装Kubernetes，请选择以下方式之一：

### 方式一：使用K3s（推荐）

K3s是一个轻量级的Kubernetes发行版，适合开发和测试环境：

```bash
# 快速安装K3s v1.24.7
export LOCAL_IP=$(ip route get 1.1.1.1 | awk '/src/ {print $7}')
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="v1.24.7+k3s1" sh -s server --bind-address=$LOCAL_IP --node-ip=$LOCAL_IP --node-name=master
cp /etc/rancher/k3s/k3s.yaml ~/.kube/config

# 验证安装
kubectl get nodes
kubectl get pods -n kube-system
```

### 方式二：使用 KubeKey 安装Kubernetes v1.24.7

详情请见: [kubekey 安装文档](https://github.com/kubesphere/kubekey/blob/master/README_zh-CN.md)

## 故障排除

### 如果Docker安装失败

1. 检查系统包管理器是否正常工作
2. 确保有足够的磁盘空间
3. 检查网络连接

### 如果Kubernetes安装失败

1. 检查Docker是否正常运行
2. 确保系统有足够的资源
3. 检查防火墙设置
4. 查看kubelet日志：`journalctl -u kubelet`

## 卸载

### 卸载Docker

```bash
# Ubuntu/Debian
sudo apt-get purge docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd

# CentOS/RHEL
sudo yum remove docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd
```


## 注意事项

- 脚本需要root权限运行
- 安装过程中会重启相关服务
- 建议在安装前备份重要数据
- 某些操作可能需要重启系统才能生效
- K3s是推荐的Kubernetes发行版，适合轻量级部署

## 支持的版本

- **Docker**: 最新稳定版
- **Kubernetes**: 建议使用K3s `v1.24.7+k3s1` 或 kubekey 安装 Kubernetes `v1.24.7`

## 许可证

本项目采用MIT许可证。

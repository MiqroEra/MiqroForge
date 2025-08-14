#!/bin/bash

# 检查系统
check_os(){
    # 检查系统是否是 Ubuntu > 20.04，如果不是，则退出
    if [ "$(uname -s)" != "Linux" ] || [ "$(uname -r | cut -d'.' -f1)" -lt 5 ]; then
        echo "This script only supports Ubuntu 20.04 or higher"
        exit 1
    fi
}

check_sudo_or_root(){
    if [ "$(id -u)" -ne 0 ]; then
        echo "Please run this script with sudo or root"
        exit 1
    fi
}

# 安装docker
install_docker(){
    if ! command -v docker &> /dev/null; then
        echo "docker is not installed"
        echo "Installing docker..."
        apt install -y docker.io docker-compose-v2

        systemctl enable docker
        systemctl start docker
        systemctl status docker
    else
        echo "docker is already installed"
    fi 
}

install_python(){
    # 检查 python 是否安装
    if ! command -v python3 &> /dev/null; then
        echo "python is not installed"
        echo "Installing python..."
        apt install -y python3 python3-pip python3-venv python-is-python3
    else
        echo "python is already installed"
    fi
}

install_nfs_server(){
    # 检查 nfs-kernel-server 是否安装
    # 检查 NFS 内核服务器是否已安装
    check_nfs_installed() {
        # 方法1：检查包是否已安装
        if dpkg -l nfs-kernel-server >/dev/null 2>&1; then
            return 0
        fi
        
        # 方法3：检查服务是否存在
        if systemctl list-unit-files | grep -q nfs-kernel-server; then
            return 0
        fi
        
        return 1
    }

    # 检查服务状态
    check_nfs_status() {
        if systemctl is-active --quiet nfs-kernel-server 2>/dev/null; then
            echo "running"
        elif systemctl is-enabled nfs-kernel-server 2>/dev/null; then
            echo "installed"
        else
            echo "not_found"
        fi
    }

    if check_nfs_installed; then
        status=$(check_nfs_status)
        case $status in
            "running")
                echo "NFS Server is running"
                ;;
            "installed")
                echo "NFS Server is installed but not running"
                echo "Starting NFS kernel server..."
                systemctl start nfs-kernel-server
                systemctl enable nfs-kernel-server
                echo "NFS kernel server started"
                ;;
            *)
                echo "NFS Server is installed but in abnormal state"
                exit 1
                ;;
        esac
    else
        echo "NFS 内核服务器未安装"
        echo "Installing NFS kernel server..."
        apt install -y nfs-kernel-server
        echo "NFS kernel server installed"
        systemctl start nfs-kernel-server
        systemctl enable nfs-kernel-server
       
    fi

    # 判断 /etc/exports 是否配置 /data 共享，如果没有，则配置
    if ! grep -q "/data" /etc/exports; then
        echo "Configuring NFS..."
        mkdir -p /data/miqroforge
        chmod -R 777 /data/miqroforge
        echo "/data *(rw,fsid=0,sync,no_subtree_check,no_auth_nlm,insecure,no_root_squash)" >> /etc/exports
        exportfs -a
        systemctl restart nfs-kernel-server
        systemctl enable nfs-kernel-server
        echo "NFS configured"
    fi
}

install_k3s(){
    # 检查 k3s 是否安装
    if ! command -v k3s &> /dev/null; then
        echo "k3s is not installed"
        echo "Installing k3s..."
        export LOCAL_IP=$(ip route get 1.1.1.1 | awk '/src/ {print $7}')
        curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="v1.24.7+k3s1" sh -s server --bind-address=$LOCAL_IP --node-ip=$LOCAL_IP --node-name=master
        cp /etc/rancher/k3s/k3s.yaml ~/.kube/config

        # 验证安装
        echo "Verifying k3s installation..."
        sleep 10
        kubectl get nodes
        kubectl get pods -n kube-system
        echo "k3s installed successfully"
    else
        echo "k3s is already installed"
    fi
}

start_miqroforge_web(){
    export NFS_SERVER_IP=$(ip route get 1.1.1.1 | awk '/src/ {print $7}')
    export NFS_SERVER_EXPORT_PATH=/data/miqroforge
    export SERVER_PORT=30080
    docker compose -f docker-compose.yaml up -d
    echo "Miqroforge started successfully"
    echo "You can access Miqroforge at http://${NFS_SERVER_IP}:${SERVER_PORT}/miqroforge-frontend/"
}

install_miqroforge_cli(){
    # 判断命令 miqroforge 是否存在，不存在则安装
    if ! command -v miqroforge &> /dev/null; then
        echo "miqroforge is not installed"
        echo "Installing miqroforge..."
        pip install -e . --break-system-packages
    else
        echo "miqroforge is already installed"
    fi

    miqroforge --help
}


check_os
check_sudo_or_root
install_docker
install_python
install_nfs_server
install_k3s
start_miqroforge_web
install_miqroforge_cli

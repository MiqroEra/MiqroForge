#!/bin/bash

# 检查系统
check_os(){
    # 检查系统是否是 Ubuntu >= 20.04，如果不是，则退出
    source /etc/os-release
    # split VERSION_ID by .
    if [ "$ID" != "ubuntu" ] || [ "${VERSION_ID%.*}" -lt 20 ]; then
        echo "This script only supports Ubuntu >= 20.04 System"
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
    else
        echo "docker is already installed"
    fi 
}

install_python(){
    # 检查 python 是否安装
    echo "python is not installed"
    echo "Installing python..."
    apt install -y python3 python3-pip python3-venv python-is-python3
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
        

        # 验证安装
        echo "Verifying k3s installation..."

        # 检测 k3s 服务是否是 active
        if ! systemctl is-active --quiet k3s; then
            echo "k3s is not running"
            systemctl start k3s
            systemctl enable k3s
        fi
        echo "k3s started successfully"

        # 等待 node 状态为 ready
        while ! kubectl get nodes | grep -q "Ready"; do
            echo "Waiting for k3s to be ready..."
            sleep 10
        done
        echo "k3s is ready"

    else
        echo "k3s is already installed"
    fi

    mkdir -p ~/.kube
    cp /etc/rancher/k3s/k3s.yaml ~/.kube/config

}

start_miqroforge_web(){

    if ! grep -q "NFS_SERVER_IP" ~/.bashrc; then
        echo "export NFS_SERVER_IP=$(ip route get 1.1.1.1 | awk '/src/ {print $7}')" >> ~/.bashrc
    fi

    if ! grep -q "NFS_SERVER_EXPORT_PATH" ~/.bashrc; then
        echo "export NFS_SERVER_EXPORT_PATH=/data/miqroforge" >> ~/.bashrc
    fi

    if ! grep -q "SERVER_PORT" ~/.bashrc; then
        echo "export SERVER_PORT=30080" >> ~/.bashrc
    fi

    source ~/.bashrc
    docker compose -f docker-compose.yaml up -d
    echo "Miqroforge started successfully"
    
    # 循环判断 miqroforge-web 容器内的 8080 端口是否启动成功
    echo "Waiting for miqroforge-web container to be ready..."
    while true; do
        # 检查容器是否运行
        if docker ps | grep -q "miqroforge-web"; then
            # 检查容器内的 8080 端口是否可访问
            if docker exec miqroforge-web curl -s http://localhost:8080 > /dev/null 2>&1; then
                echo "miqroforge-web container is ready and port 8080 is accessible"
                break
            else
                echo "Waiting for port 8080 to be accessible in miqroforge-web container..."
                sleep 5
            fi
        else
            echo "Waiting for miqroforge-web container to start..."
            sleep 5
        fi
    done

    echo "You can access Miqroforge at http://${NFS_SERVER_IP}:${SERVER_PORT}/miqroforge-frontend/"
}

install_miqroforge_cli(){
    # 判断命令 miqroforge 是否存在，不存在则安装
    if ! command -v miqroforge &> /dev/null; then
        echo "miqroforge is not installed"
        echo "Installing miqroforge..."
        if [ "${VERSION_ID%.*}" -lt 22 ]; then
            pip install -e .
        else
            pip install -e . --break-system-packages
        fi
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

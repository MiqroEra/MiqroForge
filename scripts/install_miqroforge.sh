#!/bin/bash

# MiqroForge 自动化安装脚本
# 支持自动安装Docker环境

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR=$SCRIPT_DIR/../data
mkdir -p $DATA_DIR

# 配置文件
CONFIG_FILE=$SCRIPT_DIR/../config/config.json

# 默认配置
DEFAULT_MINIO_HOST=''
DEFAULT_MINIO_PORT=''
DEFAULT_MINIO_USER=''
DEFAULT_MINIO_PASSWORD=''

DEFAULT_MYSQL_HOST=''
DEFAULT_MYSQL_PORT=''
DEFAULT_MYSQL_USER=''
DEFAULT_MYSQL_PASSWORD=''
DEFAULT_MYSQL_DATABASE=''

# 读取配置文件
if [ -f $CONFIG_FILE ]; then    
    DEFAULT_USER=$(jq -r '.minio.user' $CONFIG_FILE)
    DEFAULT_PASSWORD=$(jq -r '.minio.password' $CONFIG_FILE)
    DEFAULT_MINIO_HOST=$(jq -r '.minio.host' $CONFIG_FILE)
    DEFAULT_MINIO_PORT=$(jq -r '.minio.port' $CONFIG_FILE)
    DEFAULT_MYSQL_USER=$(jq -r '.mysql.user' $CONFIG_FILE)
    DEFAULT_MYSQL_PASSWORD=$(jq -r '.mysql.password' $CONFIG_FILE)
    DEFAULT_MYSQL_DATABASE=$(jq -r '.mysql.database' $CONFIG_FILE)
fi

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "此脚本需要root权限运行"
        log_info "请使用: sudo $0"
        exit 1
    fi
}

# 检查网络连接
check_network() {
    log_info "检查网络连接..."
    if ! ping -c 1 8.8.8.8 > /dev/null 2>&1; then
        log_error "网络连接失败，请检查网络设置"
        exit 1
    fi
    log_success "网络连接正常"
}

# 检查是否已安装Docker
check_docker() {
    if command -v docker &> /dev/null; then
        log_success "Docker已安装: $(docker --version)"
        return 0
    else
        log_warning "Docker未安装，准备进行安装"
        return 1
    fi
}

# 检测操作系统类型
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VERSION=$VERSION_ID
    else
        OS=$(uname -s)
    fi
    log_info "检测到操作系统: $OS $VERSION"
}

# 在Ubuntu/Debian上安装Docker
install_docker_debian() {
    log_info "在Ubuntu/Debian上安装Docker..."
    
    # 安装必要的依赖
    apt-get update -y
    apt-get install -y apt-transport-https ca-certificates curl software-properties-common gnupg

    # 添加Docker的官方GPG密钥
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/$ID/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    # 设置Docker仓库
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$ID $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # 安装Docker
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # 启动Docker服务
    systemctl start docker
    systemctl enable docker
    
    log_success "Docker安装完成"
}

# 在CentOS/RHEL上安装Docker
install_docker_centos() {
    log_info "在CentOS/RHEL上安装Docker..."
    
    # 安装必要的依赖
    yum install -y yum-utils
    
    # 添加Docker仓库
    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

    # 安装Docker
    yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # 启动Docker服务
    systemctl start docker
    systemctl enable docker
    
    log_success "Docker安装完成"
}

# 在Alpine上安装Docker
install_docker_alpine() {
    log_info "在Alpine上安装Docker..."
    
    # 安装Docker
    apk add --update docker
    
    # 启动Docker服务
    rc-update add docker boot
    service docker start
    
    log_success "Docker安装完成"
}

# 安装Docker的主函数
install_docker() {
    detect_os
    case "$OS" in
        "Ubuntu"|"Debian GNU/Linux")
            install_docker_debian
            ;;
        "CentOS Linux"|"Red Hat Enterprise Linux"|"Fedora")
            install_docker_centos
            ;;
        "Alpine Linux")
            install_docker_alpine
            ;;
        *)
            log_error "不支持的操作系统: $OS"
            exit 1
            ;;
    esac
}



# 检查并安装 Python 3.10
check_python310() {
    if command -v python3.10 &> /dev/null; then
        log_success "已检测到 python3.10: $(python3.10 --version 2>&1)"
        return 0
    fi

    if command -v python3 &> /dev/null; then
        if python3 -c 'import sys; exit(0 if sys.version_info[:2] >= (3,10) else 1)'; then
            log_success "已检测到 python3≥3.10: $(python3 --version 2>&1)"
            return 0
        fi
    fi

    return 1
}

install_python310_debian() {
    log_info "在Ubuntu/Debian上安装 Python 3.10..."

    # 更新索引并安装基础工具
    apt-get update -y
    apt-get install -y software-properties-common curl ca-certificates gnupg

    # 先直接尝试安装（适用于较新版本的 Debian/Ubuntu）
    if apt-get install -y python3.10 python3.10-venv 2>/dev/null; then
        log_success "Python 3.10 安装完成"
    else
        # 对于旧版 Ubuntu，启用 deadsnakes PPA
        if [ "${ID:-}" = "ubuntu" ]; then
            log_warning "直接安装失败，尝试启用 deadsnakes PPA..."
            add-apt-repository -y ppa:deadsnakes/ppa
            apt-get update -y
            apt-get install -y python3.10 python3.10-venv || {
                log_error "通过 deadsnakes PPA 安装 Python 3.10 失败"
                exit 1
            }
        else
            log_error "当前 Debian 系列源中无 python3.10 包，请手动配置合适的软件源后重试"
            exit 1
        fi
    fi

    # 确保 pip 可用
    if ! python3.10 -m pip --version >/dev/null 2>&1; then
        log_info "为 Python 3.10 安装/升级 pip..."
        python3.10 -m ensurepip --upgrade || apt-get install -y python3-pip || true
    fi

    log_success "Python 3.10 安装完成: $(python3.10 --version 2>&1)"
}

install_python310_centos() {
    log_info "在CentOS/RHEL/Fedora上安装 Python 3.10..."

    pkg_mgr="yum"
    if command -v dnf >/dev/null 2>&1; then
        pkg_mgr="dnf"
    fi

    # 尝试启用 EPEL（在 RHEL/CentOS 上通常需要）
    ${pkg_mgr} install -y epel-release || true

    # 直接尝试安装
    if ${pkg_mgr} install -y python3.10 python3.10-devel python3.10-pip 2>/dev/null; then
        :
    else
        # 对于部分 EL 版本，可尝试 IUS 源
        if [ "${pkg_mgr}" = "yum" ] || [ "${pkg_mgr}" = "dnf" ]; then
            rhel_ver=$(rpm -E %rhel 2>/dev/null || echo "")
            if [ -n "$rhel_ver" ]; then
                log_warning "尝试启用 IUS 源以安装 Python 3.10..."
                ${pkg_mgr} install -y https://repo.ius.io/ius-release-el${rhel_ver}.rpm || true
                ${pkg_mgr} install -y python310 python310-devel python310-pip || {
                    log_error "在当前系统上无法通过仓库安装 Python 3.10"
                    exit 1
                }
                # IUS 包名为 python310，提供 python3.10 可执行链接
            else
                log_error "无法识别 RHEL 主版本号，安装 Python 3.10 失败"
                exit 1
            fi
        fi
    fi

    # 确保 pip 可用
    if command -v python3.10 >/dev/null 2>&1; then
        python3.10 -m ensurepip --upgrade || true
        log_success "Python 3.10 安装完成: $(python3.10 --version 2>&1)"
    else
        log_error "Python 3.10 安装失败"
        exit 1
    fi
}

install_python310_alpine() {
    log_info "在Alpine上安装 Python 3..."
    apk add --update python3 py3-pip
    if python3 -c 'import sys; exit(0 if sys.version_info[:2] == (3,10) else 1)'; then
        log_success "已安装 Python 3.10: $(python3 --version 2>&1)"
    else
        log_warning "Alpine 仓库当前提供的并非 3.10 版本: $(python3 --version 2>&1)"
    fi
}

install_python310() {
    detect_os
    log_info "检查 Python 3.10..."
    if check_python310; then
        return 0
    fi

    case "$OS" in
        "Ubuntu"|"Debian GNU/Linux")
            install_python310_debian
            ;;
        "CentOS Linux"|"Red Hat Enterprise Linux"|"Fedora")
            install_python310_centos
            ;;
        "Alpine Linux")
            install_python310_alpine
            ;;
        *)
            log_error "不支持的操作系统: $OS，无法自动安装 Python 3.10"
            exit 1
            ;;
    esac
}

run_mysql_container() {
    log_info "运行 MySQL 容器..."
    mkdir -p "$DATA_DIR/mysql"

    # 容器存在则不创建；存在但未运行则启动
    if docker ps -a --format '{{.Names}}' | grep -wq mysql; then
        log_info "检测到已有 MySQL 容器 'mysql'"
        if [ "$(docker inspect -f '{{.State.Running}}' mysql 2>/dev/null)" != "true" ]; then
            docker start mysql
            log_success "已启动已有 MySQL 容器"
        else
            log_info "MySQL 容器已在运行"
        fi
    else
        docker run -d \
          --name mysql \
          --restart=always \
          -p 3306:3306 \
          -e MYSQL_ROOT_PASSWORD=$DEFAULT_MYSQL_PASSWORD \
          -v "$DATA_DIR/mysql":/var/lib/mysql \
          mysql:8.0
        log_success "MySQL 容器运行成功"
    fi

    # 等待 MySQL 就绪，使用更可靠的检查方式
    log_info "等待 MySQL 就绪..."
    max_attempts=30
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if docker exec mysql sh -c 'mysqladmin ping -h"localhost" -P"3306" -u"root" -p"'$DEFAULT_PASSWORD'"' &>/dev/null; then
            log_success "MySQL 服务已就绪"
            break
        fi
        log_info "尝试 $attempt/$max_attempts: MySQL 还未就绪，等待..."
        sleep 2
        attempt=$((attempt + 1))
    done
    sleep 2

    if [ $attempt -gt $max_attempts ]; then
        log_error "MySQL 服务启动超时，请检查容器日志"
        return 1
    fi

    # 记录数据库是否在此次执行前已存在（用于决定是否导入）
    DB_EXISTS_BEFORE=$(docker exec mysql sh -c 'mysql -h"localhost" -P"3306" -u"root" -p"'$DEFAULT_MYSQL_PASSWORD'" -N -e "SELECT EXISTS(SELECT 1 FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='\''miqroforge'\'');"' || echo 0)

    # 记录用户是否在此次执行前已存在（用于决定是否创建与授权）
    USER_EXISTS_BEFORE=$(docker exec mysql sh -c 'mysql -h"localhost" -P"3306" -u"root" -p"'$DEFAULT_MYSQL_PASSWORD'" -N -e "SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user='\''miqroforge'\'' AND host='\''%'\'');"' || echo 0)

    # 幂等：创建数据库
    docker exec mysql sh -c 'mysql -h"localhost" -P"3306" -u"root" -p"'$DEFAULT_MYSQL_PASSWORD'" -e "CREATE DATABASE IF NOT EXISTS miqroforge;"'
    log_success "MySQL 数据库创建成功"

    # 仅当用户先前不存在时才创建用户并授权
    if [ "$USER_EXISTS_BEFORE" = "0" ]; then
        docker exec mysql sh -c 'mysql -h"localhost" -P"3306" -u"root" -p"'$DEFAULT_MYSQL_PASSWORD'" -e "CREATE USER IF NOT EXISTS '\''miqroforge'\''@'\''%'\'' IDENTIFIED BY '\''miqroforge@2025.'\'';"'
        log_success "MySQL 用户创建成功"
        docker exec mysql sh -c 'mysql -h"localhost" -P"3306" -u"root" -p"'$DEFAULT_MYSQL_PASSWORD'" -e "GRANT ALL PRIVILEGES ON miqroforge.* TO '\''miqroforge'\''@'\''%'\''; FLUSH PRIVILEGES;"'
        log_success "MySQL 权限授予成功"
    else
        log_info "检测到用户 'miqroforge'@'%' 已存在，跳过创建与授权"
    fi

    # 数据导入：仅当数据库在本次执行前不存在时才导入
    if [ "$DB_EXISTS_BEFORE" = "0" ]; then
        sql_file="$SCRIPT_DIR/../config/miqroforge.sql"
        if [ -f "$sql_file" ]; then
            log_info "导入 MySQL 数据..."
            docker exec -i mysql mysql -h"localhost" -P"3306" -u"root" -p"'$DEFAULT_MYSQL_PASSWORD'" miqroforge < "$sql_file"
            log_success "MySQL 数据导入成功"
        else
            log_info "未找到 SQL 文件：$sql_file，跳过导入"
        fi
    else
        log_info "数据库已存在，跳过数据导入"
    fi
}

run_minio_container() {
    log_info "运行 Minio 容器..."
    mkdir -p "$DATA_DIR/minio"

    # 如果容器存在则不创建；存在但未运行则启动
    if docker ps -a --format '{{.Names}}' | grep -wq minio; then
        log_info "检测到已有 Minio 容器 'minio'"
        if [ "$(docker inspect -f '{{.State.Running}}' minio 2>/dev/null)" != "true" ]; then
            docker start minio
            log_success "已启动已有 Minio 容器"
        else
            log_info "Minio 容器已在运行"
        fi
    else 
        docker run -d --name minio -p 9000:9000 -p 9001:9001 -e MINIO_ROOT_USER=$DEFAULT_MINIO_USER \
            -e MINIO_ROOT_PASSWORD=$DEFAULT_MINIO_PASSWORD \
            -e MINIO_USE_MULTIPLE_DISKS=1 \
            -e MINIO_DISK=/data \
            -v "$DATA_DIR/minio":/data \
            minio/minio:RELEASE.2022-06-11T19-55-32Z server /data --console-address ":9001" --address ":9000"

        log_success "Minio 容器运行成功"

        # 等待 Minio 就绪
        log_info "等待 Minio 就绪..."
        max_attempts=30
        attempt=1
        while [ $attempt -le $max_attempts ]; do
            if docker exec minio sh -c 'minio --version' &>/dev/null; then
                log_success "Minio 服务已就绪"
                break
            fi
            log_info "尝试 $attempt/$max_attempts: Minio 还未就绪，等待..."
            sleep 2
            attempt=$((attempt + 1))
        done
        sleep 2
        
        if [ $attempt -gt $max_attempts ]; then
            log_error "Minio 服务启动超时，请检查容器日志"
            return 1
        fi 
    fi

    log_success "Minio 服务就绪"

    # # 下载 mc 客户端
    # mkdir -p $SCRIPT_DIR/../bin
    
    # curl -L https://dl.min.io/client/mc/release/linux-amd64/mc -o $SCRIPT_DIR/../bin/mc
    # chmod +x $SCRIPT_DIR/../bin/mc
    # log_success "mc 客户端下载完成"

    # 配置 mc
    # 如果 minio 未配置，则配置
    if ! $SCRIPT_DIR/../bin/mc alias list | grep -q minio; then
        log_info "minio 未配置，配置 mc..."
        $SCRIPT_DIR/../bin/mc alias set minio http://$DEFAULT_MINIO_HOST:$DEFAULT_MINIO_PORT $DEFAULT_MINIO_USER $DEFAULT_MINIO_PASSWORD
        log_success "mc 配置完成"
    fi

    # 如果桶不存在，则创建桶
    if ! $SCRIPT_DIR/../bin/mc ls minio/miqroforge; then
        log_info "桶不存在，创建桶..."
        $SCRIPT_DIR/../bin/mc mb minio/miqroforge
        log_success "桶创建成功"
    else
        log_info "桶已存在，跳过创建"
    fi

    log_success "Minio 环境准备完成！"
}



# 主安装函数
install_miqroforge() {
    log_info "开始MiqroForge环境安装..."
    
    # 检查root权限
    check_root
    
    # 检查网络连接
    check_network
    
    # 检查Docker是否安装，如果没有则安装
    if ! check_docker; then
        log_info "安装Docker..."
        install_docker
    fi
    
    # 安装 Python 3.10（如未满足）
    if ! check_python310; then
        log_info "安装 Python 3.10..."
        install_python310
    fi      

    # 运行 MySQL 容器
    run_mysql_container

    # 运行 Minio 容器
    run_minio_container

    docker run -d --name miqroforge 


    log_success "MiqroForge环境准备完成！"
}

# 显示帮助信息
show_help() {
    echo "MiqroForge 自动化安装脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -v, --version  显示版本信息"
    echo ""
    echo "功能:"
    echo "  - 自动安装Docker（如果未安装）"
    echo "  - 自动安装 Python 3.10（如果未安装）"
    echo "  - 支持多种Linux发行版"
    echo ""
    echo "示例:"
    echo "  sudo $0          # 运行完整安装"
    echo "  sudo $0 --help   # 显示帮助信息"
}

# 显示版本信息
show_version() {
    echo "MiqroForge 安装脚本 v1.1.0"
    echo "支持 Docker 与 Python 3.10 自动安装"
}

# 主程序入口
main() {
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--version)
            show_version
            exit 0
            ;;
        "")
            install_miqroforge
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主程序
main "$@"

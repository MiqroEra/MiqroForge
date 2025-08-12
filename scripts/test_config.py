#!/usr/bin/env python3

from miqroforge.managers import ServiceManager
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_service_connection():
    """测试服务连接"""
    print("=== 测试服务连接 ===\n")
    
    manager = ServiceManager()
    
    # 测试Kubernetes连接
    print("测试Kubernetes连接...")
    if manager.init_kubernetes():
        if manager.k8s and manager.k8s.test_connection():
            print("  ✓ Kubernetes连接测试成功")
        else:
            print("  ✗ Kubernetes连接测试失败")
    else:
        print("  ✗ Kubernetes初始化失败")
    
    # 测试Docker连接
    print("\n测试Docker连接...")
    if manager.init_docker():
        if manager.docker and manager.docker.test_connection():
            print("  ✓ Docker连接测试成功")
        else:
            print("  ✗ Docker连接测试失败")
    else:
        print("  ✗ Docker初始化失败")
    
    # 测试MySQL连接
    print("\n测试MySQL连接...")
    if manager.init_mysql():
        if manager.mysql and manager.mysql.is_connected():
            print("  ✓ MySQL连接测试成功")
        else:
            print("  ✗ MySQL连接测试失败")
    else:
        print("  ✗ MySQL初始化失败")
    
    # 断开所有连接
    manager.disconnect_all()

def test_all_services_init():
    """测试一键初始化所有服务"""
    print("\n=== 测试一键初始化所有服务 ===\n")
    
    manager = ServiceManager()
    
    if manager.init_all_services():
        print("✓ 所有服务初始化成功")
    else:
        print("⚠ 部分服务初始化失败")
    
    # 显示服务状态
    print("\n服务状态:")
    status = manager.get_service_status()
    for service, state in status.items():
        print(f"  {service}: {state}")
    
    # 断开所有连接
    manager.disconnect_all()

if __name__ == "__main__":
    test_service_connection()
    test_all_services_init()

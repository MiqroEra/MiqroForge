from uuid import uuid4
from ..managers.mysql_manager import MySQLManager
from typing import List
from ..managers.docker_manager import DockerManager
import json

def handle_node_add(args) -> None:

    # args.add 现在是一个包含两个元素的列表
    if args.add is None or len(args.add) != 2:
        print("请提供两个参数: 镜像名称和项目路径")
        print("格式: miqroforge node --add <镜像名称> <项目路径>")
        print("例如: miqroforge node --add ubuntu:20.04 /opt/app")
        return
    
    image, app_path = args.add

    print(f"adding node:")
    print(f"  image: {image}")
    print(f"  app_path: {app_path}")

    docker_manager = DockerManager()
    if not docker_manager.connect():
        raise RuntimeError("无法连接到Docker")
    
    # 拉取镜像 如果镜像不存在, 则拉取
    docker_manager.pull(image)

    # 获取节点JSON
    node_json = docker_manager.get_node_json(image, app_path)

    if node_json is None:
        print(f"get node.json failed")
        return

    insert_node(node_json, image)

def insert_node(node_json: dict, image: str) -> None:
    mysql_manager = MySQLManager()
    try:
        if not mysql_manager.connect():
            raise RuntimeError("Failed to connect to database")
        
        # 获取节点ID
        node_id = node_json.get('id')
        if not node_id:
            raise ValueError("Node ID cannot be empty")

        node_input = node_json.get('input', {})
        node_output = node_json.get('output', {})
        
        if 'web' not in node_input:
            node_input['web'] = []
        if 'web' not in node_output:
            node_output['web'] = []
        if 'upstream' not in node_input:
            node_input['upstream'] = []
        if 'downstream' not in node_output:
            node_output['downstream'] = []

        print(f"Starting to process node, ID: {node_id}")
        
        # 先查询节点是否已存在
        print("Checking if node already exists...")
        check_sql = "SELECT id FROM node WHERE id = %s"
        mysql_manager.cursor.execute(check_sql, (node_id,))
        existing_node = mysql_manager.cursor.fetchone()
        
        if existing_node:
            print(f"Node {node_id} already exists, performing update operation...")
            
            # 更新现有节点
            update_sql = '''
            UPDATE node SET 
                type = %s,
                name = %s,
                description = %s,
                version = %s,
                color = %s,
                tag = %s,
                input = %s,
                output = %s,
                performance_config_path = %s,
                example_config_path = %s,
                contact = %s,
                image = %s,
                execution_command = %s
            WHERE id = %s
            '''
            
            # 准备更新参数
            update_params = (
                'C',
                json.dumps(node_json.get('name', ''), ensure_ascii=False),
                node_json.get('description', ''),
                node_json.get('version', ''),
                node_json.get('color', ''),
                node_json.get('tag', ''),
                json.dumps(node_json.get('input', {}), ensure_ascii=False),
                json.dumps(node_json.get('output', {}), ensure_ascii=False),
                node_json.get('performance_config_path', ''),
                node_json.get('example_config_path', ''),
                json.dumps(node_json.get('contact', {}), ensure_ascii=False),
                image,
                node_json.get('execution_command', ''),
                node_id
            )
            
            mysql_manager.cursor.execute(update_sql, update_params)
            mysql_manager.connection.commit()
            print(f"Node updated successfully, ID: {node_id}")
            
        else:
            print(f"Node {node_id} does not exist, performing insert operation...")
            
            # 插入新节点
            insert_sql = '''
            INSERT INTO node (
                id, 
                type, 
                name, 
                description, 
                version,
                color,
                tag,
                input,
                output,
                performance_config_path,
                example_config_path,
                contact,
                image,
                execution_command                
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            
            # 准备插入参数
            insert_params = (
                node_id,
                'C',
                json.dumps(node_json.get('name', ''), ensure_ascii=False),
                node_json.get('description', ''),
                node_json.get('version', ''),
                node_json.get('color', ''),
                node_json.get('tag', ''),
                json.dumps(node_json.get('input', {}), ensure_ascii=False),
                json.dumps(node_json.get('output', {}), ensure_ascii=False),
                node_json.get('performance_config_path', ''),
                node_json.get('example_config_path', ''),
                json.dumps(node_json.get('contact', {}), ensure_ascii=False),
                image,
                node_json.get('execution_command', ''),
            )
            
            mysql_manager.cursor.execute(insert_sql, insert_params)
            mysql_manager.connection.commit()
            print(f"Node inserted successfully, ID: {node_id}")
        
        print(f"Node processing completed, ID: {node_id}")
        
    except Exception as e:
        print(f"Failed to process node: {e}")
        if hasattr(mysql_manager, 'connection') and mysql_manager.connection:
            mysql_manager.connection.rollback()
        raise
    finally:
        if hasattr(mysql_manager, 'connection') and mysql_manager.connection:
            mysql_manager.connection.close()

def fetch_node(mysql_manager: MySQLManager) -> List:
    if mysql_manager.cursor is None:
        raise RuntimeError("数据库游标创建失败")

    query = "SELECT * FROM node ORDER BY created_time"
    mysql_manager.cursor.execute(query, ())
    return mysql_manager.cursor.fetchall()


def get_column_names(mysql_manager: MySQLManager) -> List[str]:
    """获取列名列表"""
    if mysql_manager.cursor is None:
        raise RuntimeError("数据库游标创建失败")
    
    # 获取列名信息
    if mysql_manager.cursor.description is None:
        raise RuntimeError("无法获取列名信息")
    
    column_names = [desc[0] for desc in mysql_manager.cursor.description]
    return column_names


def print_node_vertical(nodes: List, column_names: List[str]) -> None:
    """垂直打印节点数据，类似于MySQL的\\G命令"""
    if not nodes:
        print("没有找到节点数据")
        return
    
    for i, node in enumerate(nodes):
        print(f"节点 {i+1}")
        print(f"{'-'*50}")
        
        for j, (column_name, value) in enumerate(zip(column_names, node)):
            # 格式化显示，列名左对齐，值右对齐
            formatted_column = f"{column_name}:"
            formatted_value = str(value) if value is not None else "NULL"
            
            # 如果值太长，进行换行处理
            if len(formatted_value) > 80:
                lines = [formatted_value[i:i+80] for i in range(0, len(formatted_value), 80)]
                print(f"{formatted_column:<20} {lines[0]}")
                for line in lines[1:]:
                    print(f"{'':<20} {line}")
            else:
                print(f"{formatted_column:<20} {formatted_value}")
        
        print(f"{'='*50}")


def handle_node(args) -> None:
    
    mysql_manager = MySQLManager()
    try:
        if not mysql_manager.connect():
            raise RuntimeError("无法连接到数据库")

        if hasattr(args, 'add') and args.add is not None:
            handle_node_add(args)
        else:
            nodes = fetch_node(mysql_manager)
            # 获取列名信息
            column_names = get_column_names(mysql_manager)
            # 垂直打印节点数据，类似于MySQL的\G命令
            print_node_vertical(nodes, column_names)
    except Exception as e:
        print(f"error: {e}")
    finally:
        if hasattr(mysql_manager, 'connection') and mysql_manager.connection:
            mysql_manager.connection.close()


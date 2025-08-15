from typing import List
from ..managers.mysql_manager import MySQLManager
from ..managers.docker_manager import DockerManager
import json
import subprocess
import sys
import requests
import time

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
    # 插入节点
    insert_node(node_json, image)

    # 导入 k3s containerd 中
    import_node_to_k3s(image)

    restart_miqroforge()

def restart_miqroforge() -> None:
    print(f"Restarting miqroforge-web, please wait...")
    subprocess.run(["docker","restart","miqroforge-web"], check=True)
    
    docker_manager = DockerManager()
    if not docker_manager.connect():
        raise RuntimeError("无法连接到Docker")
    
    port = docker_manager.find_exposed_port('miqroforge-web',80)
    if port is None:
        print(f"Failed to find exposed port of miqroforge-web")
    else:
        url = f"http://127.0.0.1:{port}/api/doc.html"
        print(f"url: {url}")
        max_retry = 30
        retry = 0
        while True:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"miqroforge-web restarted successfully!")
                break

            time.sleep(1)
            retry += 1
            if retry > max_retry:
                print(f"Failed to restart miqroforge-web after {max_retry} retries")
                break

    # if result.returncode == 0:
    #     print(f"miqroforge-web restarted successfully!")
    # else:
    #     print(f"Failed to restart miqroforge-web")


def import_node_to_k3s(image: str) -> None:
    """导入镜像到 k3s containerd 中，并显示实时进度"""
    
    # 检查镜像是否已经在 k3s 中存在
    try:
        awk = "awk 'NR>1{print $1\":\"$2}'"
        result = subprocess.run(
            ["sh", "-c", f"crictl images | {awk} | grep '{image}'"], 
            capture_output=True, 
            text=True, 
            check=False
        )
        output = result.stdout.strip()
        print(f"check image {image} in k3s: {output}, returncode: {result.returncode}")
        if result.returncode == 0:
            print(f"Image {image} already exists in k3s, skip importing.")
            return
    except Exception as e:
        print(f"Warning: Failed to check existing images: {e}")
    
    print(f"Importing image to k3s: {image}")
    
    try:
        image_name = image.split("/")[-1].split(":")[0]
        subprocess.run(["docker","save","-o",f"/tmp/{image_name}.tar",image])
        subprocess.run(["k3s","ctr","images","import",f"/tmp/{image_name}.tar"],check=True)
        subprocess.run(["rm","-f",f"/tmp/{image_name}.tar"])
        
        print(f"\nImage {image} imported to k3s successfully!")
            
    except subprocess.CalledProcessError as e:
        print(f"\nFailed to import image {image} to k3s: {e}")
    except KeyboardInterrupt:
        print("\nImport interrupted by user")
    except Exception as e:
        print(f"\nError during import: {e}")

def fix_node_json(node_json: dict, key: str) -> None:
    if key not in node_json:
        node_json[key] = []
    elif not isinstance(node_json[key],list):
        node_json[key] = []
    fix_ui(node_json)

def fix_ui(items: dict) -> None:
    for item in items['web']:
        if 'ui' in item:
            if isinstance(item['ui'],str):
                item['ui'] = {item['ui']:''}
            elif not isinstance(item['ui'],dict):
                item['ui'] = {}


def insert_node(node_json: dict, image: str) -> None:
    mysql_manager = MySQLManager()
    try:
        if not mysql_manager.connect():
            raise RuntimeError("Failed to connect to database")
        
        # 获取节点ID
        node_id = node_json.get('id')
        if not node_id:
            raise ValueError("Node ID cannot be empty")

        if 'input' not in node_json:
            raise ValueError("Node input cannot be empty")
        if 'output' not in node_json:
            raise ValueError("Node output cannot be empty")

        fix_node_json(node_json['input'],'upstream')
        fix_node_json(node_json['output'],'downstream')

        print(f"node_json: {node_json}")
        print(f"Starting to process node, ID: {node_id}")
        
        # 先查询节点是否已存在
        print("Checking if node already exists...")
        check_sql = "SELECT id FROM node WHERE id = %s"
        mysql_manager.cursor.execute(check_sql, (node_id,))
        existing_node = mysql_manager.cursor.fetchone()
        
        if existing_node:
            user_input = input(f'Node {node_id} already exists, would you want to update? (y/n) ')
            if user_input.strip().lower() != 'y':
                print(f"Node {node_id} not updated. exit...")
                sys.exit(0)
            
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
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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


from ..managers.mysql_manager import MySQLManager
from typing import List




def handle_node_add(args) -> None:
    # TODO 添加节点
    print("Not implemented! Coming soon...")
    pass


def fetch_node(mysql_manager: MySQLManager) -> List:
    if mysql_manager.cursor is None:
        raise RuntimeError("数据库游标创建失败")

    query = "SELECT * FROM node"
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
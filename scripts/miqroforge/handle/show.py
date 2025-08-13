"""显示任务列表相关的处理函数"""

import sys
from typing import List, Dict, Any, Union, Optional, Tuple
from datetime import datetime
from decimal import Decimal
from tabulate import tabulate

from ..managers.mysql_manager import MySQLManager
from ..config import config

# 类型定义
RowItemType = Union[int, str, None]
TableRowType = List[RowItemType]
RowDictType = Dict[str, Any]

# 任务状态码到状态名称的映射
TASK_STATUS_MAP: Dict[int, str] = {
    1: "CREATED",
    2: "QUEUED",
    3: "RUNNING",
    4: "SUCCEED",
    5: "FAILED",
    6: "CANCELLED"
}

# 任务节点状态码到状态名称的映射
NODE_STATUS_MAP: Dict[int, str] = {
    1: "CREATED",
    2: "PENDING",
    3: "RUNNING",
    4: "SUCCEED",
    5: "FAILED",
    6: "CANCELLED"
}

# 任务表头中文映射
TASK_HEADERS_MAP: Dict[str, str] = {
    "id": "任务ID",
    "name": "任务名称",
    "status": "状态",
    "start_time": "开始时间",
    "end_time": "结束时间",
    "created_time": "创建时间",
    "error_message": "错误信息"
}

# 任务节点表头中文映射
NODE_HEADERS_MAP: Dict[str, str] = {
    "id": "节点ID",
    "task_id": "任务ID",
    "name_cn": "中文名称",
    "name_en": "英文名称",
    "status": "状态",
    "data_dir": "数据目录",
    "job_num": "作业数量",
    "created_time": "创建时间"
}

# 任务节点参数表头中文映射
NODE_PARAMS_HEADERS_MAP: Dict[str, str] = {
    "id": "参数ID",
    "task_id": "任务ID",
    "node_id": "节点ID",
    "type": "参数类型",
    "name_cn": "中文名称",
    "name_en": "英文名称",
    "param_code": "参数代码",
    "value": "参数值"
}

# 任务表要显示的字段列表
TASK_DISPLAY_FIELDS = ["id", "name", "status", "start_time", "end_time", "created_time", "error_message"]

# 任务节点表要显示的字段列表
NODE_DISPLAY_FIELDS = ["id", "task_id", "name_cn", "name_en", "status", "data_dir", "job_num", "created_time"]

# 任务节点参数表要显示的字段列表
NODE_PARAMS_DISPLAY_FIELDS = ["id", "task_id", "node_id", "type", "name_cn", "name_en", "param_code", "value"]

def safe_int(value: Any) -> int:
    """安全地将值转换为整数。"""
    if isinstance(value, (int, Decimal)):
        return int(value)
    return 0

def format_datetime(dt: Optional[datetime]) -> str:
    """格式化日期时间。"""
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "-"

def format_error_message(error_msg: Optional[str], max_length: int = 30) -> str:
    """格式化错误信息。"""
    if error_msg is None:
        return "-"
    if isinstance(error_msg, str) and len(error_msg) > max_length:
        return error_msg[:max_length-3] + "..."
    return str(error_msg)

def get_task_status_str(status_code: int) -> str:
    """获取任务状态字符串。"""
    return TASK_STATUS_MAP.get(status_code, "未知状态")

def get_node_status_str(status_code: int) -> str:
    """获取任务节点状态字符串。"""
    return NODE_STATUS_MAP.get(status_code, "未知状态")

def get_param_type_str(type_code: int) -> str:
    """获取参数类型字符串。"""
    param_type_map = {
        0: "输入参数",
        1: "输出参数"
    }
    return param_type_map.get(type_code, "未知类型")

def fetch_tasks(mysql_manager: MySQLManager, limit: int) -> List:
    """从数据库获取任务列表。"""
    if mysql_manager.cursor is None:
        raise RuntimeError("数据库游标创建失败")

    query = f"""
        SELECT {', '.join(TASK_DISPLAY_FIELDS)}
        FROM miqroforge.task 
        ORDER BY id DESC 
        LIMIT %s
    """
    mysql_manager.cursor.execute(query, (limit,))
    return mysql_manager.cursor.fetchall()

def fetch_task_nodes(mysql_manager: MySQLManager, task_id: int) -> List:
    """从数据库获取指定任务的节点列表。"""
    if mysql_manager.cursor is None:
        raise RuntimeError("数据库游标创建失败")

    query = f"""
        SELECT {', '.join(NODE_DISPLAY_FIELDS)}
        FROM miqroforge.task_node 
        WHERE task_id = %s
        ORDER BY id ASC
    """
    mysql_manager.cursor.execute(query, (task_id,))
    return mysql_manager.cursor.fetchall()

def fetch_node_params(mysql_manager: MySQLManager, node_id: int) -> List:
    """从数据库获取指定节点的参数列表。"""
    if mysql_manager.cursor is None:
        raise RuntimeError("数据库游标创建失败")

    query = f"""
        SELECT {', '.join(NODE_PARAMS_DISPLAY_FIELDS)}
        FROM miqroforge.task_node_params 
        WHERE node_id = %s
        ORDER BY id ASC
    """
    mysql_manager.cursor.execute(query, (node_id,))
    return mysql_manager.cursor.fetchall()

def format_task_row_data(row: Tuple) -> TableRowType:
    """格式化任务行数据。"""
    row_dict = dict(zip(TASK_DISPLAY_FIELDS, row))
    
    return [
        safe_int(row_dict["id"]),
        str(row_dict["name"] or ""),
        get_task_status_str(safe_int(row_dict["status"])),
        format_datetime(row_dict["start_time"]),
        format_datetime(row_dict["end_time"]),
        format_datetime(row_dict["created_time"]),
        format_error_message(row_dict["error_message"])
    ]

def format_node_row_data(row: Tuple) -> TableRowType:
    """格式化任务节点行数据。"""
    row_dict = dict(zip(NODE_DISPLAY_FIELDS, row))
    
    return [
        safe_int(row_dict["id"]),
        safe_int(row_dict["task_id"]),
        str(row_dict["name_cn"] or ""),
        str(row_dict["name_en"] or ""),
        get_node_status_str(safe_int(row_dict["status"])),
        str(row_dict["data_dir"] or ""),
        str(row_dict["job_num"] or ""),
        format_datetime(row_dict["created_time"])
    ]

def format_node_params_row_data(row: Tuple) -> TableRowType:
    """格式化任务节点参数行数据。"""
    row_dict = dict(zip(NODE_PARAMS_DISPLAY_FIELDS, row))
    
    return [
        safe_int(row_dict["id"]),
        safe_int(row_dict["task_id"]),
        safe_int(row_dict["node_id"]),
        get_param_type_str(safe_int(row_dict["type"])),
        str(row_dict["name_cn"] or ""),
        str(row_dict["name_en"] or ""),
        str(row_dict["param_code"] or ""),
        str(row_dict["value"] or "")
    ]

def print_task_table(table_data: List[TableRowType]) -> None:
    """打印任务表格。"""
    headers = [TASK_HEADERS_MAP[col] for col in TASK_DISPLAY_FIELDS]
    
    print("\n" + tabulate(
        table_data,
        headers=headers,
        tablefmt="grid",
        numalign="left",
        stralign="left"
    ))
    print(f"\n总计: {len(table_data)} 个任务")

def print_node_table(table_data: List[TableRowType]) -> None:
    """打印任务节点表格。"""
    headers = [NODE_HEADERS_MAP[col] for col in NODE_DISPLAY_FIELDS]
    
    print("\n" + tabulate(
        table_data,
        headers=headers,
        tablefmt="grid",
        numalign="left",
        stralign="left"
    ))
    print(f"\n总计: {len(table_data)} 个节点")

def print_node_params_table(table_data: List[TableRowType]) -> None:
    """打印任务节点参数表格。"""
    headers = [NODE_PARAMS_HEADERS_MAP[col] for col in NODE_PARAMS_DISPLAY_FIELDS]
    
    print("\n" + tabulate(
        table_data,
        headers=headers,
        tablefmt="grid",
        numalign="left",
        stralign="left"
    ))
    print(f"\n总计: {len(table_data)} 个参数")

def handle_show(args) -> None:
    """查看任务列表、指定任务的节点列表或指定节点的参数列表。"""
    mysql_manager = MySQLManager(config_manager=config)
    
    try:
        if not mysql_manager.connect():
            raise RuntimeError("无法连接到数据库")
        
        # 如果指定了节点ID，则显示该节点的参数列表
        if hasattr(args, 'node_id') and args.node_id is not None:
            node_id = safe_int(args.node_id)
            if node_id <= 0:
                raise ValueError("节点ID必须是正整数")
            
            # 获取节点参数数据
            rows = fetch_node_params(mysql_manager, node_id)
            
            if not rows:
                print(f"没有找到节点ID为 {node_id} 的参数")
                return

            # 格式化数据并显示
            table_data = [format_node_params_row_data(row) for row in rows]
            print(f"\n节点ID {node_id} 的参数列表:")
            print_node_params_table(table_data)
            
        # 如果指定了任务ID，则显示该任务的节点列表
        elif hasattr(args, 'id') and args.id is not None:
            task_id = safe_int(args.id)
            if task_id <= 0:
                raise ValueError("任务ID必须是正整数")
            
            # 获取任务节点数据
            rows = fetch_task_nodes(mysql_manager, task_id)
            
            if not rows:
                print(f"没有找到任务ID为 {task_id} 的节点")
                return

            # 格式化数据并显示
            table_data = [format_node_row_data(row) for row in rows]
            print(f"\n任务ID {task_id} 的节点列表:")
            print_node_table(table_data)
        else:
            # 获取任务列表数据
            rows = fetch_tasks(mysql_manager, args.limit)
            
            if not rows:
                print("没有找到任何任务")
                return

            # 格式化数据并显示
            table_data = [format_task_row_data(row) for row in rows]
            print_task_table(table_data)
            
    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)
    finally:
        mysql_manager.disconnect()

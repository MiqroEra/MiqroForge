#!/usr/bin/env python3

import argparse
import sys
from textwrap import dedent
from typing import List, Optional

# 导入 handle 函数
from miqroforge.handle import (
    handle_show,
    handle_node,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="miqroforge",
        description="MiqroForge 命令行工具",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    # miqroforge show
    show_parser = subparsers.add_parser(
        "task",
        help="查看计算任务",
        description="查看计算任务",
    )
    # 参数 -limit 参数
    show_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="查看指定数量的计算任务",
    )
    # 参数 --id 参数
    show_parser.add_argument("--id", type=int, help="查看指定ID的计算任务节点信息")
    # 添加 --node-id 参数
    show_parser.add_argument("--node-id", type=int, help="查看指定ID的计算节点参数信息")

    show_parser.set_defaults(func=handle_show)

    node_parser = subparsers.add_parser("node", help="查看节点模板信息")
    
    node_parser.add_argument("--add", nargs=2, metavar=('IMAGE', 'APP_PATH'), 
                        help="添加自定义节点，格式: --add <镜像名称> <项目路径>")
    
    node_parser.set_defaults(func=handle_node)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """主入口函数，供命令行工具调用"""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 2

    try:
        args.func(args)
    except NotImplementedError as exc:
        # 占位实现触发：输出提示并返回特定退出码
        sys.stderr.write(f"{exc}\n")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())

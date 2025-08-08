#!/usr/bin/env python3

import argparse
import sys


def handle_show(args: argparse.Namespace) -> None:
    """查看计算节点列表的占位实现。"""
    raise NotImplementedError("显示计算节点列表的实现待补充")


def handle_status(args: argparse.Namespace) -> None:
    """查看计算节点状态的占位实现。支持 --detail。"""
    raise NotImplementedError("显示计算节点状态的实现待补充")


def handle_resources(args: argparse.Namespace) -> None:
    """查看集群资源使用情况的占位实现。支持 --live。"""
    raise NotImplementedError("显示资源使用情况的实现待补充")


def handle_task_submit(args: argparse.Namespace) -> None:
    """提交计算任务的占位实现。接收任务描述文件路径。"""
    raise NotImplementedError("提交计算任务的实现待补充")


def handle_task_list(args: argparse.Namespace) -> None:
    """查看任务列表的占位实现。"""
    raise NotImplementedError("查看任务列表的实现待补充")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="miqroforge",
        description="MiqroForge 命令行工具",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    # miqroforge show
    show_parser = subparsers.add_parser(
        "show",
        help="查看计算节点",
        description="查看计算节点",
    )
    show_parser.set_defaults(func=handle_show)

    # miqroforge status --detail
    status_parser = subparsers.add_parser(
        "status",
        help="查看所有计算节点的状态",
        description="查看所有计算节点的状态（运行中、停止、离线等）",
    )
    status_parser.add_argument(
        "--detail",
        action="store_true",
        help="显示详细信息",
    )
    status_parser.set_defaults(func=handle_status)

    # miqroforge resources --live
    resources_parser = subparsers.add_parser(
        "resources",
        help="查看集群资源使用情况",
        description="查看集群资源使用情况",
    )
    resources_parser.add_argument(
        "--live",
        action="store_true",
        help="实时刷新显示",
    )
    resources_parser.set_defaults(func=handle_resources)

    # miqroforge task <submit|list>
    task_parser = subparsers.add_parser(
        "task",
        help="任务管理",
        description="任务管理相关子命令",
    )
    task_subparsers = task_parser.add_subparsers(dest="task_command", metavar="<task_command>")

    # miqroforge task submit simulation-job.yaml
    task_submit_parser = task_subparsers.add_parser(
        "submit",
        help="提交计算任务",
        description="提交计算任务，参数为任务描述文件（如 YAML）",
    )
    task_submit_parser.add_argument(
        "spec",
        help="任务描述文件路径（如 simulation-job.yaml）",
    )
    task_submit_parser.set_defaults(func=handle_task_submit)

    # miqroforge task list
    task_list_parser = task_subparsers.add_parser(
        "list",
        help="查看任务列表",
        description="查看任务列表",
    )
    task_list_parser.set_defaults(func=handle_task_list)

    return parser


def main(argv: list[str] | None = None) -> int:
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

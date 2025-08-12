#!/usr/bin/env python3
"""Task ORM和TaskMapper使用示例

展示如何使用Task ORM类和TaskMapper类进行任务数据操作。
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from miqroforge.models.task import Task
from miqroforge.mappers.task_mapper import TaskMapper


def main():
    """主函数 - 演示Task ORM和TaskMapper的使用"""
    
    print("=== Task ORM和TaskMapper使用示例 ===\n")
    
    # 1. 创建Task ORM对象
    print("1. 创建Task ORM对象:")
    task = Task(
        name="示例任务",
        status=1,  # Created状态
        created_by="example_user",
        priority=75,
        data_dir="/data/example"
    )
    print(f"   创建的Task对象: {task}")
    print(f"   Task对象字典表示: {task.to_dict()}")
    print()
    
    # 2. 创建TaskMapper实例
    print("2. 创建TaskMapper实例:")
    try:
        mapper = TaskMapper()
        print("   TaskMapper创建成功")
    except Exception as e:
        print(f"   TaskMapper创建失败: {e}")
        return
    print()
    
    # 3. 测试list方法
    print("3. 测试list方法:")
    try:
        tasks = mapper.list(limit=5)
        print(f"   查询到 {len(tasks)} 条任务记录:")
        for task in tasks:
            print(f"     - ID: {task.id}, 名称: {task.name}, 状态: {task.status}")
    except Exception as e:
        print(f"   查询失败: {e}")
    print()
    
    # 4. 测试创建任务
    print("4. 测试创建任务:")
    try:
        new_task = Task(
            name="Python示例任务",
            status=1,  # Created状态
            created_by="python_example",
            priority=80,
            data_dir="/data/python_example"
        )
        
        created_task = mapper.create(new_task)
        print(f"   成功创建任务，ID: {created_task.id}")
        print(f"   任务详情: {created_task}")
        
        # 验证创建结果
        retrieved_task = mapper.get_by_id(created_task.id)
        if retrieved_task:
            print(f"   验证成功，检索到的任务: {retrieved_task}")
        else:
            print("   验证失败，无法检索到刚创建的任务")
            
    except Exception as e:
        print(f"   创建任务失败: {e}")
    print()
    
    # 5. 测试更新任务
    print("5. 测试更新任务:")
    try:
        if 'created_task' in locals():
            task_to_update = mapper.get_by_id(created_task.id)
            if task_to_update:
                task_to_update.status = 3  # Running状态
                task_to_update.progress = 50
                
                if mapper.update(task_to_update):
                    print("   任务更新成功")
                    updated_task = mapper.get_by_id(created_task.id)
                    print(f"   更新后的任务: {updated_task}")
                else:
                    print("   任务更新失败")
            else:
                print("   未找到要更新的任务")
    except Exception as e:
        print(f"   更新任务失败: {e}")
    print()
    
    # 6. 测试删除任务
    print("6. 测试删除任务:")
    try:
        if 'created_task' in locals():
            if mapper.delete(created_task.id):
                print("   任务删除成功")
                
                # 验证删除结果
                deleted_task = mapper.get_by_id(created_task.id)
                if deleted_task:
                    print("   验证失败，删除后仍能检索到任务")
                else:
                    print("   验证成功，删除后无法检索到任务")
            else:
                print("   任务删除失败")
    except Exception as e:
        print(f"   删除任务失败: {e}")
    print()
    
    print("=== 示例完成 ===")


if __name__ == "__main__":
    main()

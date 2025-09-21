#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meraki Temporal Worker
支持所有Meraki网络管理工作流的Temporal Worker
"""

import asyncio
import logging
import sys
from typing import Optional

from temporalio.client import Client
from temporalio.worker import Worker

# 导入原有工作流
from translate import TranslateActivities
from greeting import GreetSomeone

# 导入示例工作流
from example_workflow import OrganizationInventoryWorkflow, DeviceDetailsWorkflow

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置常量
DEFAULT_TEMPORAL_HOST = "temporal:7233"  # 保持原有配置
DEFAULT_NAMESPACE = "avaca"  # 保持原有命名空间
MERAKI_TASK_QUEUE_NAME = "meraki-workflows-queue"
GREETING_TASK_QUEUE_NAME = "greeting-tasks-queue"


async def create_meraki_worker(
    client: Client,
    task_queue: str = MERAKI_TASK_QUEUE_NAME
) -> Worker:
    """
    创建Meraki工作流Worker
    
    Args:
        client: Temporal客户端
        task_queue: 任务队列名称
        
    Returns:
        配置好的Worker实例
    """
    # 所有Meraki工作流（使用重构后的示例工作流）
    meraki_workflows = [
        OrganizationInventoryWorkflow,
        DeviceDetailsWorkflow,
    ]
    
    # 导入重构后的MerakiActivities
    from meraki import MerakiActivities
    
    # 创建MerakiActivities实例（使用占位符API密钥）
    # 注意：在实际使用中，API密钥应该通过Temporal Secrets或环境变量传递
    meraki_activities = MerakiActivities("placeholder_api_key")
    
    # 获取所有Activity方法
    import inspect
    activity_methods = [
        getattr(meraki_activities, name) 
        for name, method in inspect.getmembers(meraki_activities, predicate=inspect.iscoroutinefunction)
        if hasattr(getattr(meraki_activities, name), '__temporal_activity_definition')
    ]
    
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=meraki_workflows,
        activities=activity_methods,  # 注册所有MerakiActivities
    )
    
    logger.info(f"创建Meraki Worker，支持 {len(meraki_workflows)} 个工作流和 {len(activity_methods)} 个Activity")
    for i, workflow in enumerate(meraki_workflows, 1):
        logger.info(f"  工作流 {i}. {workflow.__name__}")
    logger.info(f"  已注册 {len(activity_methods)} 个MerakiActivity方法")
    
    return worker


async def create_greeting_worker(
    client: Client,
    task_queue: str = GREETING_TASK_QUEUE_NAME
) -> Worker:
    """
    创建问候工作流Worker（保持向后兼容）
    
    Args:
        client: Temporal客户端
        task_queue: 任务队列名称
        
    Returns:
        配置好的Worker实例
    """
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        activities = TranslateActivities(session)
        
        worker = Worker(
            client,
            task_queue=task_queue,
            workflows=[GreetSomeone],
            activities=[activities.greet_in_spanish, activities.farewell_in_spanish],
        )
        
        logger.info("创建Greeting Worker（向后兼容）")
        return worker


async def run_meraki_worker(
    temporal_host: str = DEFAULT_TEMPORAL_HOST,
    namespace: str = DEFAULT_NAMESPACE,
    task_queue: str = MERAKI_TASK_QUEUE_NAME
):
    """
    运行Meraki工作流Worker
    
    Args:
        temporal_host: Temporal服务器地址
        namespace: 命名空间
        task_queue: 任务队列名称
    """
    try:
        logger.info(f"连接到Temporal服务器: {temporal_host}")
        logger.info(f"命名空间: {namespace}")
        logger.info(f"任务队列: {task_queue}")
        
        client = await Client.connect(temporal_host, namespace=namespace)
        logger.info("✅ 成功连接到Temporal服务器")
        
        worker = await create_meraki_worker(client, task_queue)
        
        logger.info("🚀 启动Meraki Temporal Worker...")
        logger.info("=" * 60)
        logger.info("Worker已准备就绪，等待工作流执行请求")
        logger.info("支持的工作流场景:")
        logger.info("  1. 设备状态查询")
        logger.info("  2. AP设备查询")
        logger.info("  3. 客户端统计")
        logger.info("  4. 固件版本汇总")
        logger.info("  5. 授权状态详情")
        logger.info("  6. 设备巡检报告")
        logger.info("  7. 楼层AP分布图")
        logger.info("  8. 设备点位图")
        logger.info("  9. 丢失设备追踪")
        logger.info("  10. 告警日志查询")
        logger.info("=" * 60)
        
        await worker.run()
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭Worker...")
    except Exception as e:
        logger.error(f"Worker运行失败: {str(e)}")
        raise


async def run_greeting_worker(
    temporal_host: str = DEFAULT_TEMPORAL_HOST,
    namespace: str = "avaca"  # 保持原有命名空间
):
    """
    运行问候工作流Worker（向后兼容）
    
    Args:
        temporal_host: Temporal服务器地址
        namespace: 命名空间
    """
    try:
        logger.info(f"连接到Temporal服务器: {temporal_host}")
        logger.info(f"命名空间: {namespace}")
        
        client = await Client.connect(temporal_host, namespace=namespace)
        logger.info("✅ 成功连接到Temporal服务器")
        
        worker = await create_greeting_worker(client)
        
        logger.info("🚀 启动Greeting Temporal Worker...")
        logger.info("Worker已准备就绪，等待问候工作流执行请求")
        
        await worker.run()
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭Worker...")
    except Exception as e:
        logger.error(f"Worker运行失败: {str(e)}")
        raise


async def run_all_workers(
    temporal_host: str = DEFAULT_TEMPORAL_HOST
):
    """
    同时运行所有Worker（并发模式）
    
    Args:
        temporal_host: Temporal服务器地址
    """
    logger.info("🚀 启动所有Temporal Workers...")
    
    try:
        # 并发运行两个Worker
        await asyncio.gather(
            run_meraki_worker(temporal_host, DEFAULT_NAMESPACE, MERAKI_TASK_QUEUE_NAME),
            run_greeting_worker(temporal_host, DEFAULT_NAMESPACE),
            return_exceptions=True
        )
    except Exception as e:
        logger.error(f"运行所有Workers失败: {str(e)}")
        raise


def print_usage():
    """打印使用说明"""
    print("🔧 Meraki Temporal Worker")
    print("=" * 50)
    print("用法:")
    print("  python worker.py                    # 运行Meraki工作流Worker")
    print("  python worker.py meraki             # 运行Meraki工作流Worker")
    print("  python worker.py greeting           # 运行问候工作流Worker（向后兼容）")
    print("  python worker.py all                # 同时运行所有Workers")
    print("  python worker.py --help             # 显示帮助信息")
    print()
    print("环境变量:")
    print("  TEMPORAL_HOST                       # Temporal服务器地址 (默认: temporal:7233)")
    print("  TEMPORAL_NAMESPACE                  # 命名空间 (默认: avaca)")
    print()
    print("示例:")
    print("  TEMPORAL_HOST=temporal:7233 python worker.py")
    print("  TEMPORAL_NAMESPACE=production python worker.py meraki")


async def main():
    """主函数"""
    import os
    
    # 从环境变量获取配置
    temporal_host = os.getenv("TEMPORAL_HOST", DEFAULT_TEMPORAL_HOST)
    namespace = os.getenv("TEMPORAL_NAMESPACE", DEFAULT_NAMESPACE)
    
    # 解析命令行参数
    mode = "meraki"  # 默认模式
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    
    if mode in ["--help", "-h", "help"]:
        print_usage()
        return
    
    try:
        if mode == "greeting":
            await run_greeting_worker(temporal_host, namespace)
        elif mode == "all":
            await run_all_workers(temporal_host)
        elif mode == "meraki":
            await run_meraki_worker(temporal_host, namespace)
        else:
            logger.error(f"未知模式: {mode}")
            print_usage()
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("👋 Worker已停止")
    except Exception as e:
        logger.error(f"❌ Worker启动失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

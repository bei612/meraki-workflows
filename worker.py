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

# 导入Concordia业务工作流 - ECharts图表版本
from concordia_workflows_echarts import (
    # 基础工作流 (10个)
    DeviceStatusWorkflow,
    APDeviceQueryWorkflow, 
    ClientCountWorkflow,
    FirmwareSummaryWorkflow,
    LicenseDetailsWorkflow,
    DeviceInspectionWorkflow,
    FloorplanAPWorkflow,
    DeviceLocationWorkflow,
    LostDeviceTraceWorkflow,
    AlertsLogWorkflow,
    # 复杂多Activity组合工作流 (4个)
    NetworkHealthAnalysisWorkflow,
    SecurityPostureWorkflow,
    TroubleshootingWorkflow,
    CapacityPlanningWorkflow
)

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
    # 所有Meraki工作流（Concordia业务场景 + 复杂多Activity组合场景）
    meraki_workflows = [
        # 基础工作流 - 对应testConcordia.py的10个场景
        DeviceStatusWorkflow,
        APDeviceQueryWorkflow,
        ClientCountWorkflow,
        FirmwareSummaryWorkflow,
        LicenseDetailsWorkflow,
        DeviceInspectionWorkflow,
        FloorplanAPWorkflow,
        DeviceLocationWorkflow,
        LostDeviceTraceWorkflow,
        AlertsLogWorkflow,
        # 复杂多Activity组合工作流 - 4个高级场景
        NetworkHealthAnalysisWorkflow,
        SecurityPostureWorkflow,
        TroubleshootingWorkflow,
        CapacityPlanningWorkflow,
    ]
    
    # 导入重构后的MerakiActivities
    from meraki import MerakiActivities
    
    # 创建MerakiActivities实例（merakiAPI.py 自己处理认证）
    meraki_activities = MerakiActivities()
    
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
        logger.info("📊 基础工作流 (10个):")
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
        logger.info("🚀 复杂多Activity组合工作流 (4个):")
        logger.info("  11. 网络健康全景分析")
        logger.info("  12. 安全态势感知分析")
        logger.info("  13. 运维故障诊断")
        logger.info("  14. 容量规划分析")
        logger.info("=" * 60)
        
        await worker.run()
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭Worker...")
    except Exception as e:
        logger.error(f"Worker运行失败: {str(e)}")
        raise


def print_usage():
    """打印使用说明"""
    print("🔧 Meraki Temporal Worker")
    print("=" * 50)
    print("用法:")
    print("  python worker.py                    # 运行Meraki工作流Worker")
    print("  python worker.py meraki             # 运行Meraki工作流Worker")
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
        if mode == "meraki":
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

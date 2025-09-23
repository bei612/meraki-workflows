#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整测试所有14个Meraki Temporal Workflow
合并了test_all_workflows.py、test_complex_workflows.py、test_concordia_workflows.py
一次性测试所有场景并输出完整的ECharts数据

用法：
  python test.py [org_id]

示例：
  python test.py 850617379619606726
  python test.py  # 使用默认org_id

注意：API Key 由 merakiAPI.py 自动从环境变量读取
"""

import asyncio
import sys
import json
import uuid
import os
from datetime import datetime
from temporalio.client import Client

sys.path.append('.')

from concordia_workflows_echarts import (
    # 基础工作流 (10个)
    DeviceStatusWorkflow, ConcordiaWorkflowInput,
    APDeviceQueryWorkflow, APDeviceQueryInput,
    ClientCountWorkflow,
    FirmwareSummaryWorkflow,
    LicenseDetailsWorkflow,
    DeviceInspectionWorkflow,
    FloorplanAPWorkflow, FloorplanAPInput,
    DeviceLocationWorkflow, DeviceLocationInput,
    LostDeviceTraceWorkflow, LostDeviceTraceInput,
    AlertsLogWorkflow,
    # 复杂工作流 (4个)
    NetworkHealthAnalysisWorkflow, NetworkHealthAnalysisInput,
    SecurityPostureWorkflow, SecurityPostureInput,
    TroubleshootingWorkflow, TroubleshootingInput,
    CapacityPlanningWorkflow, CapacityPlanningInput,
)

# 默认测试参数
DEFAULT_ORG_ID = "850617379619606726"  # Concordia组织ID
TEMPORAL_HOST = "temporal:7233"
TEMPORAL_NAMESPACE = "avaca"
TASK_QUEUE = "meraki-workflows-queue"

def print_separator(title: str, char: str = "=", width: int = 80):
    """打印分隔符"""
    print(f"\n{char * width}")
    print(f"{title:^{width}}")
    print(f"{char * width}")

def save_workflow_result(workflow_number: int, workflow_name: str, result, success: bool):
    """保存workflow结果到JSON文件"""
    try:
        # 创建结果目录
        os.makedirs("workflow_results", exist_ok=True)
        
        # 准备保存的数据
        save_data = {
            "workflow_number": workflow_number,
            "workflow_name": workflow_name,
            "execution_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "success": success,
            "result": None,
            "error": None
        }
        
        if success and result:
            # 将结果转换为字典格式
            if hasattr(result, '__dict__'):
                save_data["result"] = {
                    key: value for key, value in result.__dict__.items()
                    if not key.startswith('_')
                }
            else:
                save_data["result"] = result
        else:
            save_data["error"] = str(result) if result else "Unknown error"
        
        # 保存到文件
        filename = f"workflow_results/{workflow_number}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"   💾 结果已保存到: {filename}")
        
    except Exception as e:
        print(f"   ⚠️  保存结果失败: {str(e)}")

def print_workflow_result(result, workflow_name: str, workflow_number: int):
    """打印完整的工作流返回结果"""
    print_separator(f"🔍 Workflow {workflow_number}: {workflow_name} - 完整返回结果", "=", 100)
    
    # 将dataclass转换为字典
    if hasattr(result, '__dict__'):
        result_dict = {}
        for key, value in result.__dict__.items():
            result_dict[key] = value
    else:
        result_dict = result
    
    # 打印基本信息
    print(f"📊 工作流名称: {workflow_name}")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 判断成功状态：有success字段则用success字段，否则检查是否有echarts_data
    has_success_field = 'success' in result_dict
    is_success = result_dict.get('success', True) if has_success_field else bool(result_dict.get('echarts_data'))
    
    print(f"✅ 执行状态: {'成功' if is_success else '失败'}")
    
    if not is_success:
        print(f"❌ 错误信息: {result_dict.get('error_message', '未知错误')}")
        return
    
    # 打印业务数据
    print(f"\n📈 业务数据:")
    for key, value in result_dict.items():
        if key not in ['success', 'error_message', 'echarts_data']:
            if isinstance(value, (dict, list)):
                print(f"   {key}: {json.dumps(value, ensure_ascii=False, indent=2)[:200]}...")
            else:
                print(f"   {key}: {value}")
    
    # 打印ECharts数据
    echarts_data = result_dict.get('echarts_data', [])
    print(f"\n🎨 ECharts图表数据 ({len(echarts_data)}个图表):")
    
    if not echarts_data:
        print("   ⚠️  无ECharts数据")
        return
    
    for i, chart in enumerate(echarts_data, 1):
        print(f"\n   📊 图表 {i}:")
        if isinstance(chart, dict):
            # 提取图表基本信息
            chart_type = "未知"
            chart_title = "未命名图表"
            
            if 'series' in chart and chart['series']:
                series = chart['series'][0] if isinstance(chart['series'], list) else chart['series']
                if isinstance(series, dict):
                    chart_type = series.get('type', '未知')
            
            if 'title' in chart:
                if isinstance(chart['title'], dict):
                    chart_title = chart['title'].get('text', '未命名图表')
                else:
                    chart_title = str(chart['title'])
            
            print(f"      类型: {chart_type}")
            print(f"      标题: {chart_title}")
            
            # 打印完整的ECharts配置（格式化）
            print(f"      配置: {json.dumps(chart, ensure_ascii=False, indent=6)}")
        else:
            print(f"      数据: {json.dumps(chart, ensure_ascii=False, indent=6)}")
    
    print(f"\n{'=' * 100}")

async def test_basic_workflows(client: Client, org_id: str):
    """测试10个基础工作流"""
    print_separator("📊 基础工作流测试 (10个)", "=", 80)
    
    # 定义基础工作流测试用例
    basic_workflows = [
        {
            "name": "设备状态查询",
            "workflow": DeviceStatusWorkflow,
            "input": ConcordiaWorkflowInput(org_id=org_id),
            "description": "2个图表 (饼图+柱状图) - 已增强"
        },
        {
            "name": "AP设备搜索",
            "workflow": APDeviceQueryWorkflow,
            "input": APDeviceQueryInput(org_id=org_id, search_keyword="MR"),
            "description": "表格+地图散点图"
        },
        {
            "name": "客户端统计",
            "workflow": ClientCountWorkflow,
            "input": ConcordiaWorkflowInput(org_id=org_id),
            "description": "1个柱状图"
        },
        {
            "name": "固件版本汇总",
            "workflow": FirmwareSummaryWorkflow,
            "input": ConcordiaWorkflowInput(org_id=org_id),
            "description": "1个堆叠柱状图"
        },
        {
            "name": "许可证详情",
            "workflow": LicenseDetailsWorkflow,
            "input": ConcordiaWorkflowInput(org_id=org_id),
            "description": "1个仪表盘"
        },
        {
            "name": "设备巡检报告",
            "workflow": DeviceInspectionWorkflow,
            "input": ConcordiaWorkflowInput(org_id=org_id),
            "description": "1个雷达图"
        },
        {
            "name": "楼层AP分布",
            "workflow": FloorplanAPWorkflow,
            "input": FloorplanAPInput(org_id=org_id, floor_name="Floor"),
            "description": "1个树图"
        },
        {
            "name": "设备点位图",
            "workflow": DeviceLocationWorkflow,
            "input": DeviceLocationInput(org_id=org_id, search_keyword="MR44"),
            "description": "1个散点图"
        },
        {
            "name": "丢失设备追踪",
            "workflow": LostDeviceTraceWorkflow,
            "input": LostDeviceTraceInput(org_id=org_id, client_mac="d0:88:0c:69:5c:0f"),
            "description": "1个时间轴图"
        },
        {
            "name": "告警日志",
            "workflow": AlertsLogWorkflow,
            "input": ConcordiaWorkflowInput(org_id=org_id),
            "description": "1个热力图"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(basic_workflows, 1):
        print(f"\n🚀 执行基础工作流 {i}/10: {test_case['name']}")
        print(f"   📊 预期输出: {test_case['description']}")
        
        try:
            # 执行工作流
            workflow_id = f"test-basic-{i}-{uuid.uuid4().hex[:8]}"
            result = await client.execute_workflow(
                test_case['workflow'].run,
                test_case['input'],
                id=workflow_id,
                task_queue=TASK_QUEUE,
            )
            
            # 打印完整结果
            print_workflow_result(result, test_case['name'], i)
            
            # 保存结果到JSON文件
            save_workflow_result(i, test_case['name'], result, True)
            
            results.append({
                "workflow_number": i,
                "name": test_case['name'],
                "success": True,
                "echarts_count": len(result.echarts_data) if hasattr(result, 'echarts_data') and result.echarts_data else 0
            })
            
        except Exception as e:
            print(f"❌ 工作流 {i} 执行失败: {str(e)}")
            
            # 保存错误结果到JSON文件
            save_workflow_result(i, test_case['name'], str(e), False)
            
            results.append({
                "workflow_number": i,
                "name": test_case['name'],
                "success": False,
                "error": str(e)
            })
    
    return results

async def test_complex_workflows(client: Client, org_id: str):
    """测试4个复杂工作流"""
    print_separator("🚀 复杂多Activity组合工作流测试 (4个)", "=", 80)
    
    # 定义复杂工作流测试用例
    complex_workflows = [
        {
            "name": "网络健康全景分析",
            "workflow": NetworkHealthAnalysisWorkflow,
            "input": NetworkHealthAnalysisInput(org_id=org_id),
            "description": "4个图表 (饼图+柱状图+散点图+仪表盘)"
        },
        {
            "name": "安全态势感知分析",
            "workflow": SecurityPostureWorkflow,
            "input": SecurityPostureInput(org_id=org_id),
            "description": "4个图表 (树图+雷达图+热力图+柱状图)"
        },
        {
            "name": "运维故障诊断",
            "workflow": TroubleshootingWorkflow,
            "input": TroubleshootingInput(org_id=org_id),
            "description": "2个图表 (雷达图+时间轴图)"
        },
        {
            "name": "容量规划分析",
            "workflow": CapacityPlanningWorkflow,
            "input": CapacityPlanningInput(org_id=org_id, forecast_days=30),
            "description": "4个图表 (仪表盘+时间轴+堆叠柱状图+饼图)"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(complex_workflows, 11):
        print(f"\n🚀 执行复杂工作流 {i}/16: {test_case['name']}")
        print(f"   📊 预期输出: {test_case['description']}")
        print(f"   🔄 特性: 多Activity并发执行，高级数据分析")
        
        try:
            # 执行工作流
            workflow_id = f"test-complex-{i}-{uuid.uuid4().hex[:8]}"
            result = await client.execute_workflow(
                test_case['workflow'].run,
                test_case['input'],
                id=workflow_id,
                task_queue=TASK_QUEUE,
            )
            
            # 打印完整结果
            print_workflow_result(result, test_case['name'], i)
            
            # 保存结果到JSON文件
            save_workflow_result(i, test_case['name'], result, True)
            
            results.append({
                "workflow_number": i,
                "name": test_case['name'],
                "success": True,
                "echarts_count": len(result.echarts_data) if hasattr(result, 'echarts_data') and result.echarts_data else 0
            })
            
        except Exception as e:
            print(f"❌ 工作流 {i} 执行失败: {str(e)}")
            
            # 保存错误结果到JSON文件
            save_workflow_result(i, test_case['name'], str(e), False)
            
            results.append({
                "workflow_number": i,
                "name": test_case['name'],
                "success": False,
                "error": str(e)
            })
    
    return results

def print_final_statistics(basic_results: list, complex_results: list):
    """打印最终统计信息"""
    print_separator("📊 最终测试统计报告", "=", 100)
    
    all_results = basic_results + complex_results
    total_workflows = len(all_results)
    successful_workflows = len([r for r in all_results if r.get('success', False)])
    failed_workflows = total_workflows - successful_workflows
    
    print(f"\n🎯 **总体统计**:")
    print(f"   总工作流数量: {total_workflows}")
    print(f"   成功执行: {successful_workflows}")
    print(f"   执行失败: {failed_workflows}")
    print(f"   成功率: {(successful_workflows/total_workflows*100):.1f}%")
    
    print(f"\n📊 **基础工作流统计 (1-10)**:")
    basic_success = len([r for r in basic_results if r.get('success', False)])
    print(f"   成功: {basic_success}/10")
    print(f"   失败: {10-basic_success}/10")
    
    print(f"\n🚀 **复杂工作流统计 (11-14)**:")
    complex_success = len([r for r in complex_results if r.get('success', False)])
    print(f"   成功: {complex_success}/4")
    print(f"   失败: {4-complex_success}/4")
    
    print(f"\n🎨 **ECharts图表统计**:")
    total_charts = sum(r.get('echarts_count', 0) for r in all_results if r.get('success', False))
    print(f"   总图表数: {total_charts}")
    
    # 详细的工作流结果
    print(f"\n📋 **详细结果列表**:")
    print(f"{'序号':<4} {'工作流名称':<25} {'状态':<6} {'图表数':<8} {'类型':<8}")
    print("-" * 70)
    
    for result in all_results:
        status = "✅成功" if result.get('success', False) else "❌失败"
        charts = result.get('echarts_count', 0) if result.get('success', False) else 0
        wf_type = "基础" if result['workflow_number'] <= 10 else "复杂"
        
        print(f"{result['workflow_number']:<4} {result['name'][:24]:<25} {status:<6} {charts:<8} {wf_type:<8}")
    
    # 失败的工作流详情
    failed_results = [r for r in all_results if not r.get('success', False)]
    if failed_results:
        print(f"\n❌ **失败工作流详情**:")
        for result in failed_results:
            print(f"   {result['workflow_number']}. {result['name']}: {result.get('error', '未知错误')}")
    
    print(f"\n🏗️ **系统架构特性**:")
    print(f"   📊 基础工作流: 10个 (1-3个API调用，1-2个ECharts图表)")
    print(f"   🚀 复杂工作流: 4个 (4-5个API并发，2-4个ECharts图表)")
    print(f"   🎨 图表主题: 统一暗紫色主题")
    print(f"   🔧 API覆盖: 64个Meraki API方法")
    print(f"   📈 图表类型: 10+种ECharts图表类型")
    
    print(f"\n💼 **业务价值**:")
    print(f"   🏢 网络管理: 全方位网络设备和客户端管理")
    print(f"   🔒 安全监控: 多维度安全态势感知")
    print(f"   🔧 运维支持: 智能故障诊断和性能优化")
    print(f"   📊 决策支持: 容量规划和网络健康分析")
    print(f"   📈 数据可视化: 丰富的ECharts图表展示")
    
    if failed_workflows == 0:
        print(f"\n🎉 **所有14个工作流测试通过！系统已准备就绪！**")
    else:
        print(f"\n⚠️  **有{failed_workflows}个工作流测试失败，请检查相关配置**")
    
    return failed_workflows == 0

async def main():
    """主函数"""
    # 获取组织ID
    org_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ORG_ID
    
    print_separator("🚀 Meraki Temporal Workflow 完整测试系统", "=", 100)
    print(f"📋 测试组织ID: {org_id}")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Temporal服务: {TEMPORAL_HOST}")
    print(f"📦 命名空间: {TEMPORAL_NAMESPACE}")
    print(f"🎯 任务队列: {TASK_QUEUE}")
    print(f"💾 结果保存: workflow_results/1-14.json")
    
    try:
        # 连接Temporal服务
        print(f"\n🔌 连接Temporal服务...")
        client = await Client.connect(TEMPORAL_HOST, namespace=TEMPORAL_NAMESPACE)
        print(f"✅ 成功连接到Temporal服务")
        
        # 测试基础工作流
        basic_results = await test_basic_workflows(client, org_id)
        
        # 测试复杂工作流
        complex_results = await test_complex_workflows(client, org_id)
        
        # 打印最终统计
        success = print_final_statistics(basic_results, complex_results)
        
        # 退出
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ 测试执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

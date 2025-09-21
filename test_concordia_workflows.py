#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Concordia 业务场景的 Temporal Workflow

用法：
  python test_concordia_workflows.py <API_KEY> [workflow_number]

示例：
  python test_concordia_workflows.py 4fb1f6a6c032f662ab0d8315b8cf45268b615d66 1
  python test_concordia_workflows.py 4fb1f6a6c032f662ab0d8315b8cf45268b615d66 all
"""

import asyncio
import sys
import json
import uuid
from temporalio.client import Client
from concordia_workflows import (
    DeviceStatusWorkflow, ConcordiaWorkflowInput,
    APDeviceQueryWorkflow, APDeviceQueryInput,
    ClientCountWorkflow,
    FirmwareSummaryWorkflow,
    LicenseDetailsWorkflow,
    DeviceInspectionWorkflow,
    FloorplanAPWorkflow, FloorplanAPInput,
    DeviceLocationWorkflow, DeviceLocationInput,
    LostDeviceTraceWorkflow, LostDeviceTraceInput,
    AlertsLogWorkflow
)


CONCORDIA_ORG_ID = "850617379619606726"


def print_workflow_result(result, workflow_name: str):
    """打印完整的工作流返回结果"""
    print(f"\n🔍 {workflow_name} - 完整工作流返回结果:")
    print("=" * 80)
    
    # 将dataclass转换为字典
    if hasattr(result, '__dict__'):
        result_dict = {}
        for key, value in result.__dict__.items():
            result_dict[key] = value
    else:
        result_dict = result
    
    print(json.dumps(result_dict, indent=2, ensure_ascii=False, default=str))
    print("=" * 80)


async def test_workflow_1(client: Client, api_key: str):
    """测试工作流1: 告诉我整体设备运行状态"""
    print("\n" + "=" * 80)
    print("1. 测试设备状态工作流")
    print("-" * 80)
    
    input_data = ConcordiaWorkflowInput(
        api_key=api_key,
        org_id=CONCORDIA_ORG_ID
    )
    
    try:
        result = await client.execute_workflow(
            DeviceStatusWorkflow.run,
            input_data,
            id=f"test-device-status-{uuid.uuid4().hex[:8]}",
            task_queue="meraki-workflows-queue",
        )
        
        print("✅ 工作流执行成功")
        print(f"📊 设备总数: {result.device_status_overview.get('total_devices', 0)}")
        print(f"🟢 在线设备: {result.device_status_overview.get('online_devices', 0)}")
        print(f"🔴 离线设备: {result.device_status_overview.get('offline_devices', 0)}")
        print(f"⚠️  告警设备: {result.device_status_overview.get('alerting_devices', 0)}")
        print(f"💚 健康度: {result.health_metrics.get('online_percentage', 0)}%")
        
        print_workflow_result(result, "设备状态工作流")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")
        return False


async def test_workflow_2(client: Client, api_key: str):
    """测试工作流2: AP设备状态查询"""
    print("\n" + "=" * 80)
    print("2. 测试AP设备查询工作流")
    print("-" * 80)
    
    input_data = APDeviceQueryInput(
        api_key=api_key,
        org_id=CONCORDIA_ORG_ID,
        search_keyword="H330"
    )
    
    try:
        result = await client.execute_workflow(
            APDeviceQueryWorkflow.run,
            input_data,
            id="test-ap-query-concordia",
            task_queue="meraki-workflows-queue",
        )
        
        print("✅ 工作流执行成功")
        print(f"🔍 搜索关键词: {result.query_keyword}")
        print(f"📋 匹配设备数: {result.search_summary.get('total_matched', 0)}")
        print(f"📝 详情获取数: {result.search_summary.get('details_retrieved', 0)}")
        
        if result.matched_devices_list:
            print("🎯 匹配的设备:")
            for device in result.matched_devices_list[:3]:
                print(f"   - {device.get('name', '')} ({device.get('model', '')})")
        
        print_workflow_result(result, "AP设备查询工作流")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")
        return False


async def test_workflow_3(client: Client, api_key: str):
    """测试工作流3: 客户端数量统计"""
    print("\n" + "=" * 80)
    print("3. 测试客户端数量统计工作流")
    print("-" * 80)
    
    input_data = ConcordiaWorkflowInput(
        api_key=api_key,
        org_id=CONCORDIA_ORG_ID
    )
    
    try:
        result = await client.execute_workflow(
            ClientCountWorkflow.run,
            input_data,
            id="test-client-count-concordia",
            task_queue="meraki-workflows-queue",
        )
        
        print("✅ 工作流执行成功")
        print(f"👥 总客户端数: {result.query_summary.get('total_clients_in_org', 0)}")
        print(f"🌐 总网络数: {result.query_summary.get('total_networks', 0)}")
        print(f"🔥 重度使用客户端: {result.query_summary.get('total_heavy_usage_clients', 0)}")
        print(f"📊 最活跃网络: {result.client_distribution_analysis.get('most_active_network', 'N/A')}")
        
        print_workflow_result(result, "客户端数量统计工作流")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")
        return False


async def test_workflow_4(client: Client, api_key: str):
    """测试工作流4: 固件版本汇总"""
    print("\n" + "=" * 80)
    print("4. 测试固件版本汇总工作流")
    print("-" * 80)
    
    input_data = ConcordiaWorkflowInput(
        api_key=api_key,
        org_id=CONCORDIA_ORG_ID
    )
    
    try:
        result = await client.execute_workflow(
            FirmwareSummaryWorkflow.run,
            input_data,
            id="test-firmware-summary-concordia",
            task_queue="meraki-workflows-queue",
        )
        
        print("✅ 工作流执行成功")
        print(f"📱 总设备数: {result.firmware_summary.get('total_devices', 0)}")
        print(f"🏷️  总型号数: {result.firmware_summary.get('total_models', 0)}")
        print(f"✅ 固件一致型号: {result.firmware_summary.get('models_with_consistent_firmware', 0)}")
        print(f"⚠️  固件不一致型号: {result.firmware_summary.get('models_with_inconsistent_firmware', 0)}")
        print(f"🎯 整体一致性: {result.consistency_analysis.get('overall_consistency', False)}")
        
        print_workflow_result(result, "固件版本汇总工作流")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")
        return False


async def test_workflow_5(client: Client, api_key: str):
    """测试工作流5: 许可证详情"""
    print("\n" + "=" * 80)
    print("5. 测试许可证详情工作流")
    print("-" * 80)
    
    input_data = ConcordiaWorkflowInput(
        api_key=api_key,
        org_id=CONCORDIA_ORG_ID
    )
    
    try:
        result = await client.execute_workflow(
            LicenseDetailsWorkflow.run,
            input_data,
            id=f"test-license-details-{uuid.uuid4().hex[:8]}",
            task_queue="meraki-workflows-queue",
        )
        
        print("✅ 工作流执行成功")
        print(f"📄 许可证状态: {result.license_analysis.get('status', 'unknown')}")
        print(f"🏷️  许可证模式: {result.license_analysis.get('licensing_model', 'unknown')}")
        print(f"📱 无线许可证数: {result.license_analysis.get('total_wireless_licenses', 0)}")
        print(f"⏰ 到期时间: {result.license_analysis.get('expiration_date', 'unknown')}")
        
        if result.license_details:
            print("📋 许可证详情:")
            for license in result.license_details[:3]:
                print(f"   - {license.get('device_type', 'N/A')}: {license.get('license_count', 0)} 个许可证")
        
        print_workflow_result(result, "许可证详情工作流")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")
        return False


async def test_workflow_6(client: Client, api_key: str):
    """测试工作流6: 设备巡检报告"""
    print("\n" + "=" * 80)
    print("6. 测试设备巡检报告工作流")
    print("-" * 80)
    
    input_data = ConcordiaWorkflowInput(
        api_key=api_key,
        org_id=CONCORDIA_ORG_ID
    )
    
    try:
        result = await client.execute_workflow(
            DeviceInspectionWorkflow.run,
            input_data,
            id="test-device-inspection-concordia",
            task_queue="meraki-workflows-queue",
        )
        
        print("✅ 工作流执行成功")
        print(f"📊 设备健康度: {result.device_status_analysis.get('health_percentage', 0)}%")
        print(f"🚨 总告警数: {result.alerts_analysis.get('total_alerts', 0)}")
        print(f"🔴 严重告警数: {result.alerts_analysis.get('critical_alerts', 0)}")
        print(f"💚 整体健康: {result.health_assessment.get('overall_health', 'unknown')}")
        
        if result.recommendations.get('immediate_actions'):
            print("🔧 立即行动建议:")
            for action in result.recommendations['immediate_actions']:
                print(f"   - {action}")
        
        print_workflow_result(result, "设备巡检报告工作流")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")
        return False


async def test_workflow_7(client: Client, api_key: str):
    """测试工作流7: 楼层AP分布"""
    print("\n" + "=" * 80)
    print("7. 测试楼层AP分布工作流")
    print("-" * 80)
    
    input_data = FloorplanAPInput(
        api_key=api_key,
        org_id=CONCORDIA_ORG_ID,
        floor_name="一楼"
    )
    
    try:
        result = await client.execute_workflow(
            FloorplanAPWorkflow.run,
            input_data,
            id=f"test-floorplan-ap-{uuid.uuid4().hex[:8]}",
            task_queue="meraki-workflows-queue",
        )
        
        print("✅ 工作流执行成功")
        print(f"🏢 组织: {result.organization_name}")
        print(f"📋 可用楼层平面图: {len(result.available_floorplans)} 个")
        print(f"📡 选中楼层AP: {result.selected_floorplan.get('ap_count', 0)} 个")
        print(f"🌐 AP分布网络: {len(result.ap_distribution_by_network) if hasattr(result, 'ap_distribution_by_network') else 0} 个")
        
        if result.available_floorplans:
            print("📍 可用楼层:")
            for floorplan in result.available_floorplans[:3]:
                print(f"   - {floorplan.get('name', 'N/A')}")
        
        print_workflow_result(result, "楼层AP分布工作流")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")
        return False


async def test_workflow_8(client: Client, api_key: str):
    """测试工作流8: 设备点位图"""
    print("\n" + "=" * 80)
    print("8. 测试设备点位图工作流")
    print("-" * 80)
    
    input_data = DeviceLocationInput(
        api_key=api_key,
        org_id=CONCORDIA_ORG_ID,
        search_keyword="MR"
    )
    
    try:
        result = await client.execute_workflow(
            DeviceLocationWorkflow.run,
            input_data,
            id=f"test-device-location-{uuid.uuid4().hex[:8]}",
            task_queue="meraki-workflows-queue",
        )
        
        print("✅ 工作流执行成功")
        print(f"🔍 搜索关键词: {result.search_keyword}")
        print(f"📱 匹配设备数: {result.total_matched}")
        print(f"📍 设备详情: {len(result.matched_devices)} 个")
        print(f"🏢 位置信息: {len(result.selected_device_locations)} 个")
        
        if result.matched_devices:
            print("📍 匹配设备:")
            for device in result.matched_devices[:3]:
                print(f"   - {device.get('name', 'N/A')}: {device.get('model', 'N/A')}")
        
        print_workflow_result(result, "设备点位图工作流")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")
        return False


async def test_workflow_9(client: Client, api_key: str):
    """测试工作流9: 丢失设备追踪"""
    print("\n" + "=" * 80)
    print("9. 测试丢失设备追踪工作流")
    print("-" * 80)
    
    input_data = LostDeviceTraceInput(
        api_key=api_key,
        org_id=CONCORDIA_ORG_ID,
        client_mac=None,  # 空MAC地址，让工作流自动发现
        client_description="test"
    )
    
    try:
        result = await client.execute_workflow(
            LostDeviceTraceWorkflow.run,
            input_data,
            id=f"test-lost-device-trace-{uuid.uuid4().hex[:8]}",
            task_queue="meraki-workflows-queue",
        )
        
        print("✅ 工作流执行成功")
        print(f"🔍 搜索条件: {result.search_criteria}")
        print(f"👥 发现客户端: {len(result.discovered_clients)}")
        print(f"📊 连接历史: {len(result.connection_history)} 条记录")
        print(f"🎯 选中客户端: {result.selected_client_trace.get('description', 'N/A')}")
        
        if result.connection_history:
            print("🔗 连接历史:")
            for conn in result.connection_history[:3]:
                print(f"   - {conn.get('description', 'N/A')}")
        
        print_workflow_result(result, "丢失设备追踪工作流")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")
        return False


async def test_workflow_10(client: Client, api_key: str):
    """测试工作流10: 告警日志"""
    print("\n" + "=" * 80)
    print("10. 测试告警日志工作流")
    print("-" * 80)
    
    input_data = ConcordiaWorkflowInput(
        api_key=api_key,
        org_id=CONCORDIA_ORG_ID
    )
    
    try:
        result = await client.execute_workflow(
            AlertsLogWorkflow.run,
            input_data,
            id="test-alerts-log-concordia",
            task_queue="meraki-workflows-queue",
        )
        
        print("✅ 工作流执行成功")
        print(f"🚨 总告警数: {result.alerts_summary.get('total_alerts', 0)}")
        print(f"🔴 严重告警: {result.alerts_summary.get('critical_count', 0)}")
        print(f"🟡 警告告警: {result.alerts_summary.get('warning_count', 0)}")
        print(f"ℹ️  信息告警: {result.alerts_summary.get('info_count', 0)}")
        print(f"📋 告警类别: {', '.join(result.alert_categories)}")
        
        print_workflow_result(result, "告警日志工作流")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")
        return False


async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python test_concordia_workflows.py <API_KEY> [workflow_number]")
        print("示例: python test_concordia_workflows.py your_api_key 1")
        print("      python test_concordia_workflows.py your_api_key all")
        sys.exit(1)
    
    api_key = sys.argv[1]
    workflow_number = sys.argv[2] if len(sys.argv) > 2 else "all"
    
    print("🚀 开始测试 Concordia Temporal Workflows")
    print(f"🔑 API Key: {api_key[:10]}...")
    print(f"🎯 测试范围: {workflow_number}")
    
    # 连接到Temporal服务
    try:
        client = await Client.connect("temporal:7233", namespace="avaca")
        print("✅ 已连接到Temporal服务 (temporal:7233, namespace: avaca)")
    except Exception as e:
        print(f"❌ 无法连接到Temporal服务: {e}")
        print("💡 请确保Temporal服务正在运行: temporal server start-dev")
        sys.exit(1)
    
    # 测试工作流
    test_functions = {
        "1": test_workflow_1,
        "2": test_workflow_2,
        "3": test_workflow_3,
        "4": test_workflow_4,
        "5": test_workflow_5,
        "6": test_workflow_6,
        "7": test_workflow_7,
        "8": test_workflow_8,
        "9": test_workflow_9,
        "10": test_workflow_10,
    }
    
    success_count = 0
    total_count = 0
    
    if workflow_number == "all":
        # 测试所有工作流
        for num, test_func in test_functions.items():
            total_count += 1
            if await test_func(client, api_key):
                success_count += 1
    elif workflow_number in test_functions:
        # 测试指定工作流
        total_count = 1
        if await test_functions[workflow_number](client, api_key):
            success_count = 1
    else:
        print(f"❌ 不支持的工作流编号: {workflow_number}")
        print(f"💡 支持的编号: {', '.join(test_functions.keys())}, all")
        sys.exit(1)
    
    # 总结
    print("\n" + "=" * 80)
    print("🎯 测试总结")
    print("-" * 80)
    print(f"✅ 成功: {success_count}/{total_count}")
    print(f"❌ 失败: {total_count - success_count}/{total_count}")
    print(f"📊 成功率: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("🎉 所有测试都通过了！Temporal Workflows 工作正常！")
    else:
        print("⚠️  部分测试失败，请检查Worker是否正在运行")
        print("💡 启动Worker: python worker.py meraki")


if __name__ == "__main__":
    asyncio.run(main())


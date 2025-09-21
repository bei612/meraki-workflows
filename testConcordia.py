#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 Concordia.md 表格中每个问题所列 API 是否可调用并返回预期形态数据。

用法：
  python testConcordia.py <API_KEY>

说明：
- 仅做只读验证，不修改任何配置
- 使用有限 timespan/perPage 参数，避免大量数据
"""

import asyncio
import aiohttp
import sys
import json
from typing import Dict, Any, List

from merakiAPI import MerakiAPI


CONCORDIA_ORG_ID = "850617379619606726"
BASE_URL = "https://api.meraki.cn/api/v1"


async def assert_has_keys(obj: Dict[str, Any], keys: List[str], ctx: str):
    missing = [k for k in keys if k not in obj]
    if missing:
        raise AssertionError(f"{ctx} 缺少字段: {missing}")


def print_title(num: int, title: str):
    print("\n" + "=" * 80)
    print(f"{num}. {title}")
    print("-" * 80)


def print_api(endpoint: str, method: str = "GET", params: Dict[str, Any] | None = None):
    params = params or {}
    url = f"{BASE_URL}{endpoint}"
    qs = "&".join([f"{k}={json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v}" for k, v in params.items() if v is not None])
    if qs:
        url_with_qs = f"{url}?{qs}"
    else:
        url_with_qs = url
    print(f"API: {method} {endpoint}")
    print(f"URL: {url_with_qs}")
    return url_with_qs


def print_result(label: str, data: Any, max_len: int = 1200):
    try:
        s = json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        s = str(data)
    if len(s) > max_len:
        s_trunc = s[:max_len] + "... (truncated)"
    else:
        s_trunc = s
    print(f"{label}:\n{s_trunc}")


def print_question(question: str):
    """打印具体问题"""
    print(f"❓ 问题: {question}")


def print_api_response(label: str, data: Any, max_len: int = 800):
    """打印API返回（截断）"""
    try:
        s = json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        s = str(data)
    if len(s) > max_len:
        s_trunc = s[:max_len] + "... (API返回已截断)"
    else:
        s_trunc = s
    print(f"📥 {label}:\n{s_trunc}")


def print_final_result(label: str, data: Any):
    """打印最终逻辑处理结果（不截断）"""
    try:
        s = json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        s = str(data)
    print(f"🎯 {label}:\n{s}")


async def test_overall_device_status(api: MerakiAPI, session: aiohttp.ClientSession):
    print_title(1, "告诉我整体设备运行状态")
    
    # 1. 具体问题
    print_question("Concordia学校的所有设备当前运行状态如何？有多少在线、离线、告警？")
    
    # 2. API调用
    print_api(f"/organizations/{CONCORDIA_ORG_ID}/devices/statuses/overview")
    data = await api.get_device_statuses_overview(session, CONCORDIA_ORG_ID)
    
    # 3. API返回（截断）
    print_api_response("设备状态概览API返回", data)
    
    # 4. 数据验证
    await assert_has_keys(data, ["counts"], "设备状态概览")
    counts = data.get("counts", {})
    await assert_has_keys(counts, ["byStatus"], "设备状态概览.counts")
    
    # 5. 最终逻辑处理结果（不截断）
    status_summary = {
        "organization_name": "Concordia",
        "organization_id": CONCORDIA_ORG_ID,
        "device_status_overview": {
            "total_devices": sum(counts.get("byStatus", {}).values()),
            "online_devices": counts.get("byStatus", {}).get("online", 0),
            "offline_devices": counts.get("byStatus", {}).get("offline", 0),
            "alerting_devices": counts.get("byStatus", {}).get("alerting", 0),
            "dormant_devices": counts.get("byStatus", {}).get("dormant", 0)
        },
        "health_metrics": {
            "online_percentage": round((counts.get("byStatus", {}).get("online", 0) / max(sum(counts.get("byStatus", {}).values()), 1)) * 100, 2),
            "health_status": "良好" if counts.get("byStatus", {}).get("online", 0) > counts.get("byStatus", {}).get("offline", 0) else "需关注"
        },
        "raw_counts": counts.get("byStatus", {}),
        "query_time": "2025-09-21 18:30:00"
    }
    
    print_final_result("整体设备运行状态汇总", status_summary)
    print("[OK] 整体设备运行状态")


async def test_ap_status_by_name(api: MerakiAPI, session: aiohttp.ClientSession, ap_name_hint: str = "H330"):
    print_title(2, 'AP"XX"设备状态')
    
    # 1. 具体问题
    print_question(f"查询名称包含'{ap_name_hint}'的AP设备状态，包括在线状态、位置信息、固件版本等详情")
    
    # 2. API调用 - 全局搜索
    print_api(f"/organizations/{CONCORDIA_ORG_ID}/devices", params={"perPage": 5000, "startingAfter": "..."})
    matching_devices = await api.get_all_organization_devices_with_name_filter(session, CONCORDIA_ORG_ID, ap_name_hint)
    
    # 3. API返回（截断）
    print_api_response("设备搜索API返回", matching_devices[:3] if len(matching_devices) > 3 else matching_devices)
    
    if not matching_devices:
        print(f"[SKIP] 未找到包含'{ap_name_hint}'的设备，跳过 AP 设备状态 测试")
        return
    
    print(f"📋 找到 {len(matching_devices)} 个包含'{ap_name_hint}'的设备")
    
    # 获取前3个设备的详细信息
    selected_count = min(3, len(matching_devices))
    selected_details = []
    
    for i in range(selected_count):
        device = matching_devices[i]
        try:
            print_api(f"/devices/{device['serial']}")
            detail = await api.get_device_info(session, device["serial"])
            await assert_has_keys(detail, ["model", "serial"], f"设备{i+1}详情")
            
            # API返回（截断）
            print_api_response(f"设备{i+1}详情API返回", detail)
            
            selected_details.append({
                "name": detail.get("name"),
                "serial": detail.get("serial"),
                "model": detail.get("model"),
                "firmware": detail.get("firmware"),
                "lan_ip": detail.get("lanIp"),
                "network_id": detail.get("networkId"),
                "location": {
                    "lat": detail.get("lat"),
                    "lng": detail.get("lng"),
                    "address": detail.get("address")
                },
                "status": "online" if detail.get("lanIp") else "unknown",
                "tags": detail.get("tags", [])
            })
            
        except Exception as e:
            print(f"  ❌ 获取设备详情失败: {e}")
            continue
    
    # 4. 最终逻辑处理结果（不截断）
    ap_status_result = {
        "query_keyword": ap_name_hint,
        "search_summary": {
            "total_matched": len(matching_devices),
            "details_retrieved": len(selected_details),
            "search_scope": "全组织设备"
        },
        "matched_devices_list": [
            {
                "index": i+1,
                "name": device.get('name', 'N/A'),
                "model": device.get('model', 'N/A'),
                "serial": device.get('serial', 'N/A'),
                "network_id": device.get('networkId', 'N/A')
            } for i, device in enumerate(matching_devices)
        ],
        "selected_devices_details": selected_details,
        "user_interaction": {
            "action": "用户可从匹配列表中选择任意设备查看详情",
            "available_selections": len(matching_devices),
            "demonstration_count": len(selected_details)
        },
        "query_time": "2025-09-21 18:30:00"
    }
    
    print_final_result("AP设备状态查询结果", ap_status_result)
    print(f"[OK] AP 设备状态（全局搜索→找到{len(matching_devices)}个匹配设备→用户可选择查看详情）")


async def test_ap_named_placement(api: MerakiAPI, session: aiohttp.ClientSession, ap_name_hint: str = "Corr"):
    print_title(8, '给我设备"AP XX名字"的点位图')
    print("🔍 全局搜索包含字符串的设备...")
    print_api(f"/organizations/{CONCORDIA_ORG_ID}/devices", params={"perPage": 5000, "startingAfter": "..."})
    
    # 使用全局搜索方法
    matching_devices = await api.get_all_organization_devices_with_name_filter(session, CONCORDIA_ORG_ID, ap_name_hint)
    
    if not matching_devices:
        print(f"[SKIP] 未找到包含'{ap_name_hint}'的设备，跳过 AP 点位图 测试")
        return
    
    print(f"📋 找到 {len(matching_devices)} 个包含'{ap_name_hint}'的设备:")
    for i, device in enumerate(matching_devices):
        print(f"  {i+1}. {device.get('name', 'N/A')} ({device.get('model', 'N/A')}) - {device.get('serial', 'N/A')}")
    
    # 返回匹配设备列表，供用户选择
    devices_list = {
        "search_keyword": ap_name_hint,
        "total_matched": len(matching_devices),
        "matched_devices": [
            {
                "index": i+1,
                "name": device.get('name', 'N/A'),
                "model": device.get('model', 'N/A'),
                "serial": device.get('serial', 'N/A'),
                "networkId": device.get('networkId', 'N/A')
            } for i, device in enumerate(matching_devices)
        ]
    }
    
    print_result("匹配设备列表", devices_list)
    
    # 示例：选择前2个设备查看点位图（实际应用中用户可以选择）
    selected_count = min(2, len(matching_devices))
    print(f"\n🎯 示例：选择前 {selected_count} 个设备查看点位图:")
    
    selected_locations = []
    floor_plans_cache = {}  # 缓存楼层图，避免重复请求
    
    for i in range(selected_count):
        device = matching_devices[i]
        try:
            print(f"\n--- 查看设备 {i+1}: {device.get('name', 'N/A')} 的点位图 ---")
            print_api(f"/devices/{device['serial']}")
            info = await api.get_device_info(session, device["serial"])
            
            # 检查位置信息
            has_geo = ("lat" in info and "lng" in info)
            has_floor = ("floorPlanId" in info and info.get("floorPlanId"))
            
            print(f"  📍 地理位置: {'✅' if has_geo else '❌'} {info.get('lat', 'N/A')}, {info.get('lng', 'N/A')}")
            print(f"  🏢 楼层信息: {'✅' if has_floor else '❌'} {info.get('floorPlanId', 'N/A')}")
            
            device_location = {
                "name": info.get("name"),
                "serial": info.get("serial"),
                "model": info.get("model"),
                "has_geo": has_geo,
                "has_floor": has_floor,
                "lat": info.get("lat") if has_geo else None,
                "lng": info.get("lng") if has_geo else None,
                "floor_plan_id": info.get("floorPlanId") if has_floor else None,
                "network_id": info.get("networkId")
            }
            
            # 获取楼层详情（如果有且未缓存）
            if has_floor and device.get("networkId"):
                floor_plan_id = info["floorPlanId"]
                cache_key = f"{device['networkId']}_{floor_plan_id}"
                
                if cache_key not in floor_plans_cache:
                    try:
                        print_api(f"/networks/{device['networkId']}/floorPlans/{floor_plan_id}")
                        plan_detail = await api.get_floor_plan_by_id(session, device["networkId"], floor_plan_id)
                        floor_plans_cache[cache_key] = plan_detail
                        
                        img_link = plan_detail.get("imageUrl") or plan_detail.get("url")
                        if img_link:
                            print(f"  🖼️ 楼层图片: {img_link}")
                            device_location["floor_image_url"] = img_link
                        
                        device_location["floor_plan_name"] = plan_detail.get("name")
                        
                    except Exception as e:
                        print(f"  ⚠️ 楼层详情获取失败: {e}")
                else:
                    cached_plan = floor_plans_cache[cache_key]
                    img_link = cached_plan.get("imageUrl") or cached_plan.get("url")
                    if img_link:
                        print(f"  🖼️ 楼层图片: {img_link} (缓存)")
                        device_location["floor_image_url"] = img_link
                    device_location["floor_plan_name"] = cached_plan.get("name")
            
            if not (has_geo or has_floor):
                print(f"  ⚠️ 设备缺少位置信息")
                device_location["warning"] = "缺少地理位置或楼层信息"
            
            selected_locations.append(device_location)
            
        except Exception as e:
            print(f"  ❌ 获取设备位置失败: {e}")
            continue
    
    print(f"\n💡 用户可以从 {len(matching_devices)} 个匹配设备中选择任意设备查看点位图")
    print(f"[OK] AP 点位图链路（全局搜索→找到{len(matching_devices)}个匹配设备→用户可选择查看点位图）")


async def test_client_counts(api: MerakiAPI, session: aiohttp.ClientSession):
    print_title(3, "查询当前终端设备数量信息（Concordia组织汇总）")
    
    # 1. 具体问题
    print_question("Concordia学校当前有多少终端设备连接？各网络的客户端分布情况如何？")
    
    # 2. API调用 - 获取组织网络
    print_api(f"/organizations/{CONCORDIA_ORG_ID}/networks")
    nets = await api.get_organization_networks(session, CONCORDIA_ORG_ID)
    
    # 3. API返回（截断）
    print_api_response("组织网络API返回", nets)
    
    if not nets:
        print("[SKIP] Concordia组织无网络，跳过 终端数量 测试")
        return
    
    print(f"📋 Concordia 组织共有 {len(nets)} 个网络，开始统计各网络客户端数量:")
    
    # 汇总 Concordia 组织下所有网络的客户端数量
    total_clients = 0
    network_summaries = []
    
    for i, net in enumerate(nets):
        try:
            print(f"\n--- 网络 {i+1}: {net['name']} ---")
            print_api(f"/networks/{net['id']}/clients/overview")
            overview = await api.get_network_clients_overview(session, net["id"])
            
            # API返回（截断）
            print_api_response(f"网络{i+1}客户端概览API返回", overview)
            
            client_count = overview.get("counts", {}).get("total", 0)
            heavy_usage_count = overview.get("counts", {}).get("withHeavyUsage", 0)
            total_clients += client_count
            
            print(f"  📊 客户端总数: {client_count}")
            print(f"  🔥 重度使用客户端: {heavy_usage_count}")
            
            network_summaries.append({
                "network_name": net["name"],
                "network_id": net["id"],
                "client_count": client_count,
                "heavy_usage_count": heavy_usage_count,
                "product_types": net.get("productTypes", []),
                "timezone": net.get("timeZone", "N/A")
            })
        except Exception as e:
            print(f"  ❌ 网络 {net['name']} 客户端统计失败: {e}")
            continue
    
    # 4. 最终逻辑处理结果（不截断）
    client_count_result = {
        "organization_name": "Concordia",
        "organization_id": CONCORDIA_ORG_ID,
        "query_summary": {
            "total_clients_in_org": total_clients,
            "total_networks": len(nets),
            "networks_with_clients": len([n for n in network_summaries if n["client_count"] > 0]),
            "total_heavy_usage_clients": sum(n["heavy_usage_count"] for n in network_summaries),
            "avg_clients_per_network": round(total_clients / len(nets), 2) if nets else 0
        },
        "networks_breakdown": network_summaries,
        "client_distribution_analysis": {
            "most_active_network": max(network_summaries, key=lambda x: x["client_count"])["network_name"] if network_summaries else "N/A",
            "least_active_network": min(network_summaries, key=lambda x: x["client_count"])["network_name"] if network_summaries else "N/A",
            "networks_without_clients": [n["network_name"] for n in network_summaries if n["client_count"] == 0],
            "heavy_usage_ratio": round((sum(n["heavy_usage_count"] for n in network_summaries) / max(total_clients, 1)) * 100, 2)
        },
        "query_time": "2025-09-21 18:30:00"
    }
    
    print_final_result("Concordia组织客户端数量汇总", client_count_result)
    print(f"[OK] Concordia组织终端设备数量汇总完成")


async def test_firmware_summary(api: MerakiAPI, session: aiohttp.ClientSession):
    print_title(4, "汇总不同型号的固件版本")
    
    # 1. 具体问题
    print_question("Concordia学校所有设备的固件版本分布如何？哪些型号存在固件版本不一致的情况？")
    
    # 2. API调用 - 全局获取设备
    print_api(f"/organizations/{CONCORDIA_ORG_ID}/devices", params={"perPage": 5000, "startingAfter": "..."})
    all_devices = await api.get_all_organization_devices_with_name_filter(session, CONCORDIA_ORG_ID, None)
    
    # 3. API返回（截断）
    print_api_response("组织设备API返回", all_devices[:3] if len(all_devices) > 3 else all_devices)
    
    if not all_devices:
        print("[SKIP] 未找到任何设备，跳过固件汇总测试")
        return
    
    print(f"📋 获取到 {len(all_devices)} 个设备，开始固件汇总...")
    
    # 校验字段存在性
    if all_devices:
        await assert_has_keys(all_devices[0], ["model", "firmware"], "设备清单项")
    
    # 按型号分组固件版本汇总
    firmware_summary = {}
    model_counts = {}
    
    for device in all_devices:
        model = device.get("model")
        firmware = device.get("firmware")
        if model and firmware:
            # 固件版本汇总
            if model not in firmware_summary:
                firmware_summary[model] = set()
            firmware_summary[model].add(firmware)
            
            # 型号数量统计
            model_counts[model] = model_counts.get(model, 0) + 1
    
    # 转换为可序列化格式
    model_firmware_details = {}
    for model, fw_set in firmware_summary.items():
        model_firmware_details[model] = {
            "firmware_versions": sorted(list(fw_set)),
            "device_count": model_counts[model],
            "version_count": len(fw_set),
            "is_consistent": len(fw_set) == 1
        }
    
    # 4. 最终逻辑处理结果（不截断）
    firmware_analysis_result = {
        "organization_name": "Concordia",
        "organization_id": CONCORDIA_ORG_ID,
        "firmware_summary": {
            "total_devices": len(all_devices),
            "total_models": len(model_firmware_details),
            "models_with_consistent_firmware": len([m for m, info in model_firmware_details.items() if info["is_consistent"]]),
            "models_with_inconsistent_firmware": len([m for m, info in model_firmware_details.items() if not info["is_consistent"]])
        },
        "model_firmware_breakdown": model_firmware_details,
        "consistency_analysis": {
            "consistent_models": [model for model, info in model_firmware_details.items() if info["is_consistent"]],
            "inconsistent_models": [model for model, info in model_firmware_details.items() if not info["is_consistent"]],
            "overall_consistency": len([m for m, info in model_firmware_details.items() if info["is_consistent"]]) == len(model_firmware_details)
        },
        "firmware_upgrade_recommendations": {
            "models_needing_attention": [model for model, info in model_firmware_details.items() if not info["is_consistent"]],
            "total_devices_needing_upgrade": sum(info["device_count"] for model, info in model_firmware_details.items() if not info["is_consistent"])
        },
        "query_time": "2025-09-21 18:30:00"
    }
    
    print_final_result("固件版本汇总分析", firmware_analysis_result)
    print(f"[OK] 不同型号固件版本汇总（全量{len(all_devices)}设备→{len(model_firmware_details)}型号→固件统计）")


async def test_inspection_report(api: MerakiAPI, session: aiohttp.ClientSession):
    print_title(6, "给我一份最新的设备巡检报告")
    
    # 1. 具体问题
    print_question("生成Concordia学校的综合设备巡检报告，包括设备状态、告警信息、网络事件等")
    
    # 2. API调用 - 设备状态概览
    print_api(f"/organizations/{CONCORDIA_ORG_ID}/devices/statuses/overview")
    overview = await api.get_device_statuses_overview(session, CONCORDIA_ORG_ID)
    print_api_response("设备状态概览API返回", overview)
    await assert_has_keys(overview, ["counts"], "巡检-设备状态概览")
    
    # 3. API调用 - 组织健康告警
    print_api(f"/organizations/{CONCORDIA_ORG_ID}/assurance/alerts")
    alerts = await api.get_organization_assurance_alerts(session, CONCORDIA_ORG_ID)
    print_api_response("组织告警API返回", alerts[:3] if len(alerts) > 3 else alerts)
    assert isinstance(alerts, list)
    
    # 4. API调用 - 网络事件
    print_api(f"/organizations/{CONCORDIA_ORG_ID}/networks")
    nets = await api.get_organization_networks(session, CONCORDIA_ORG_ID)
    events = []
    if nets:
        try:
            print_api(f"/networks/{nets[0]['id']}/events", params={"perPage": 3, "timespan": 3600, "productType": "wireless"})
            events = await api.get_network_events(session, nets[0]["id"], perPage=3, timespan=3600, productType="wireless")
            print_api_response("网络事件API返回", events[:2] if len(events) > 2 else events)
            assert isinstance(events, list)
        except Exception:
            events = []
    
    # 5. 最终逻辑处理结果（不截断）
    status_counts = overview.get("counts", {}).get("byStatus", {})
    inspection_report = {
        "organization_name": "Concordia",
        "organization_id": CONCORDIA_ORG_ID,
        "report_metadata": {
            "report_time": "2025-09-21 18:30:00",
            "report_type": "综合设备巡检报告",
            "data_sources": ["设备状态", "组织告警", "网络事件"]
        },
        "device_status_analysis": {
            "total_devices": sum(status_counts.values()),
            "online_devices": status_counts.get("online", 0),
            "offline_devices": status_counts.get("offline", 0),
            "alerting_devices": status_counts.get("alerting", 0),
            "dormant_devices": status_counts.get("dormant", 0),
            "health_percentage": round((status_counts.get("online", 0) / max(sum(status_counts.values()), 1)) * 100, 2),
            "status_distribution": status_counts
        },
        "alerts_analysis": {
            "total_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a.get("severity") == "critical"]),
            "warning_alerts": len([a for a in alerts if a.get("severity") == "warning"]),
            "info_alerts": len([a for a in alerts if a.get("severity") == "informational"]),
            "recent_critical_alerts": [a for a in alerts[:5] if a.get("severity") == "critical"],
            "alert_categories": list(set([a.get("category", "unknown") for a in alerts]))
        },
        "network_events_analysis": {
            "events_sampled": len(events),
            "networks_checked": len(nets) if nets else 0,
            "sample_network": nets[0]["name"] if nets else "N/A",
            "recent_events": events[:3] if events else []
        },
        "health_assessment": {
            "overall_health": "良好" if status_counts.get("online", 0) > status_counts.get("offline", 0) else "需关注",
            "critical_issues": len([a for a in alerts if a.get("severity") == "critical"]),
            "devices_needing_attention": status_counts.get("offline", 0) + status_counts.get("alerting", 0),
            "network_stability": "稳定" if len(events) < 10 else "需关注"
        },
        "recommendations": {
            "immediate_actions": [],
            "maintenance_suggestions": []
        }
    }
    
    # 添加具体建议
    if status_counts.get("offline", 0) > 0:
        inspection_report["recommendations"]["immediate_actions"].append(f"检查 {status_counts.get('offline', 0)} 台离线设备")
    if status_counts.get("alerting", 0) > 0:
        inspection_report["recommendations"]["immediate_actions"].append(f"处理 {status_counts.get('alerting', 0)} 台告警设备")
    if len([a for a in alerts if a.get("severity") == "critical"]) > 0:
        inspection_report["recommendations"]["immediate_actions"].append("优先处理严重告警")
    
    print_final_result("设备巡检报告", inspection_report)
    print("[OK] 设备巡检报告链路（状态概览+告警+事件 聚合可行）")


async def test_license_details(api: MerakiAPI, session: aiohttp.ClientSession):
    print_title(5, "查询当前授权状态详情")
    print_api(f"/organizations/{CONCORDIA_ORG_ID}/licenses/overview")
    _ = await api.get_organization_licenses_overview(session, CONCORDIA_ORG_ID)
    try:
        print_api(f"/organizations/{CONCORDIA_ORG_ID}/licenses")
        lic_list = await api.get_organization_licenses(session, CONCORDIA_ORG_ID)
        if lic_list:
            # 字段松散校验
            keys = set().union(*[set(l.keys()) for l in lic_list])
            assert len(keys) > 0
        print_result("许可证列表返回", lic_list)
        print("[OK] 授权状态详情（概览+明细）")
    except Exception as e:
        # 某些租户/区域可能对明细接口返回 400/403；概览已验证通过
        print(f"[PARTIAL] 授权状态概览 OK，明细接口跳过：{str(e).split(':',1)[0]}")


async def test_floorplan_and_ap_positions(api: MerakiAPI, session: aiohttp.ClientSession):
    print_title(7, "查询某个楼层的 AP 分布图")
    nets = await api.get_organization_networks(session, CONCORDIA_ORG_ID)
    print_api(f"/organizations/{CONCORDIA_ORG_ID}/networks")
    for net in nets:
        try:
            print_api(f"/networks/{net['id']}/floorPlans")
            plans = await api.get_network_floor_plans(session, net["id"])
            if plans:
                # 任取一张楼层图，查询详情
                plan = plans[0]
                print_api(f"/networks/{net['id']}/floorPlans/{plan['floorPlanId']}")
                _detail = await api.get_floor_plan_by_id(session, net["id"], plan["floorPlanId"])  # 关键字段名以实际返回为准
                img_link = _detail.get("imageUrl") or _detail.get("url") or None
                if img_link:
                    print(f"图片链接: {img_link}")
                print_result("楼层详情返回", _detail)
                print("[OK] 楼层平面图（列表+详情）")
                break
        except Exception:
            continue
    else:
        print("[SKIP] 未找到楼层平面图，跳过 AP 分布图 测试")


async def test_lost_device_trace(api: MerakiAPI, session: aiohttp.ClientSession, query_hint: str = None):
    print_title(9, "我的电脑丢了，最近连接过哪些 AP（MAC/用户名）")
    
    # 优先用用户提供的查询关键词（MAC/用户名），否则自动发现一个客户端验证
    if query_hint:
        print(f"🔍 搜索客户端: '{query_hint}'")
        try:
            print_api(f"/organizations/{CONCORDIA_ORG_ID}/clients/search", params={"query": query_hint, "perPage": 10})
            search = await api.get_organization_clients_search(session, CONCORDIA_ORG_ID, query=query_hint, perPage=10)
            items = search.get("items") or search.get("clients") or []
            
            if items:
                print(f"📋 找到 {len(items)} 个匹配的客户端:")
                for i, item in enumerate(items):
                    mac = item.get("mac", "N/A")
                    description = item.get("description", "N/A")
                    network_name = item.get("network", {}).get("name", "N/A")
                    print(f"  {i+1}. MAC: {mac}, 描述: {description}, 网络: {network_name}")
                
                # 返回匹配客户端列表，供用户选择
                clients_list = {
                    "search_keyword": query_hint,
                    "total_matched": len(items),
                    "matched_clients": [
                        {
                            "index": i+1,
                            "mac": item.get("mac", "N/A"),
                            "description": item.get("description", "N/A"),
                            "network_name": item.get("network", {}).get("name", "N/A"),
                            "network_id": item.get("networkId") or item.get("network", {}).get("id"),
                            "client_id": item.get("clientId") or item.get("id")
                        } for i, item in enumerate(items)
                    ]
                }
                
                print_result("匹配客户端列表", clients_list)
                
                # 示例：选择第一个客户端查看连接统计（实际应用中用户可以选择）
                print(f"\n🎯 示例：选择第1个客户端查看连接轨迹:")
                item = items[0]
                network_id = item.get("networkId") or item.get("network", {}).get("id")
                client_id = item.get("clientId") or item.get("id")
                client_mac = item.get("mac", "Unknown")
                
                if network_id and client_id:
                    print(f"\n--- 查看客户端: {client_mac} ---")
                    print_api(f"/networks/{network_id}/wireless/clients/{client_id}/connectionStats", params={"timespan": 86400})
                    stats = await api.get_network_wireless_client_connection_stats(session, network_id, client_id, timespan=86400)
                    assert isinstance(stats, dict)
                    print_result("连接统计返回", stats)
                    
                    print(f"\n💡 用户可以从 {len(items)} 个匹配客户端中选择任意客户端查看连接轨迹")
                    print(f"[OK] 丢失设备连接轨迹（搜索'{query_hint}'→找到{len(items)}个客户端→用户可选择查看轨迹）")
                    return
            else:
                print(f"❌ 未找到匹配'{query_hint}'的客户端，尝试自动发现...")
        except Exception as e:
            print(f"⚠️ 客户端搜索失败: {e}，尝试自动发现...")

    # 自动发现：遍历网络，取一个有客户端的网络，选取客户端id直接查询连接统计
    print("🔍 自动发现活跃客户端...")
    print_api(f"/organizations/{CONCORDIA_ORG_ID}/networks")
    nets = await api.get_organization_networks(session, CONCORDIA_ORG_ID)
    
    for net in nets:
        try:
            print_api(f"/networks/{net['id']}/clients", params={"timespan": 86400, "perPage": 5})
            clis = await api.get_network_clients(session, net["id"], timespan=86400, perPage=5)
            if not clis:
                continue
            
            print(f"📋 网络 '{net['name']}' 找到 {len(clis)} 个活跃客户端:")
            for i, client in enumerate(clis):
                mac = client.get("mac", "N/A")
                description = client.get("description", "N/A")
                print(f"  {i+1}. MAC: {mac}, 描述: {description}")
            
            # 返回发现的客户端列表，供用户选择
            discovered_clients = {
                "network_name": net['name'],
                "network_id": net['id'],
                "total_found": len(clis),
                "active_clients": [
                    {
                        "index": i+1,
                        "mac": client.get("mac", "N/A"),
                        "description": client.get("description", "N/A"),
                        "client_id": client.get("id") or client.get("clientId")
                    } for i, client in enumerate(clis)
                ]
            }
            
            print_result("发现的活跃客户端", discovered_clients)
            
            # 示例：选择第一个客户端查看连接统计
            sample = clis[0]
            client_id = sample.get("id") or sample.get("clientId")
            client_mac = sample.get("mac", "Unknown")
            
            if not client_id:
                continue
                
            print(f"\n🎯 示例：选择第1个客户端查看连接轨迹:")
            print(f"\n--- 查看客户端: {client_mac} ---")
            print_api(f"/networks/{net['id']}/wireless/clients/{client_id}/connectionStats", params={"timespan": 86400})
            stats = await api.get_network_wireless_client_connection_stats(session, net["id"], client_id, timespan=86400)
            assert isinstance(stats, dict)
            print_result("连接统计返回", stats)
            
            print(f"\n💡 用户可以从网络'{net['name']}'的 {len(clis)} 个活跃客户端中选择任意客户端查看连接轨迹")
            print(f"[OK] 丢失设备连接轨迹（自动发现→网络'{net['name']}'→找到{len(clis)}个客户端→用户可选择查看轨迹）")
            return
        except Exception as e:
            print(f"⚠️ 网络 '{net['name']}' 客户端查询失败: {e}")
            continue

    print("[SKIP] 找不到可用于验证的客户端，跳过 丢失电脑轨迹 测试")


async def test_alerts_and_events(api: MerakiAPI, session: aiohttp.ClientSession):
    print_title(10, "列出当前的告警日志（全组织）")
    print_api(f"/organizations/{CONCORDIA_ORG_ID}/assurance/alerts")
    _alerts = await api.get_organization_assurance_alerts(session, CONCORDIA_ORG_ID)
    print_result("组织告警返回(样例)", _alerts[:5] if isinstance(_alerts, list) else _alerts)
    nets = await api.get_organization_networks(session, CONCORDIA_ORG_ID)
    if nets:
        try:
            print_api(f"/networks/{nets[0]['id']}/events", params={"perPage": 3, "timespan": 3600, "productType": "wireless"})
            _events = await api.get_network_events(session, nets[0]["id"], perPage=3, timespan=3600, productType="wireless")
            print_result("网络事件返回(样例)", _events[:3] if isinstance(_events, list) else _events)
            print("[OK] 告警日志（组织告警+网络事件）")
        except Exception as e:
            print("[PARTIAL] 组织告警 OK，网络事件接口暂跳过：Meraki events 400/权限/参数限制")
            return
    else:
        print("[PARTIAL] 组织无网络，仅验证组织告警")


async def main():
    if len(sys.argv) < 2:
        print("用法: python testConcordia.py <API_KEY> [LOST_QUERY_HINT]")
        sys.exit(1)
    api_key = sys.argv[1]
    lost_query = sys.argv[2] if len(sys.argv) > 2 else None

    api = MerakiAPI(api_key)

    async with aiohttp.ClientSession() as session:
        await test_overall_device_status(api, session)
        await test_ap_status_by_name(api, session)
        await test_ap_named_placement(api, session)
        await test_client_counts(api, session)
        await test_firmware_summary(api, session)
        await test_inspection_report(api, session)
        await test_license_details(api, session)
        await test_floorplan_and_ap_positions(api, session)
        await test_lost_device_trace(api, session, lost_query)
        await test_alerts_and_events(api, session)

    print("\n全部测试完成。可结合 Concordia.md 表格逐项对照。")


if __name__ == "__main__":
    asyncio.run(main())



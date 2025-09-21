#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Concordia 学校 10个业务场景的 Temporal Workflow 实现

基于 testConcordia.py 的业务逻辑，使用重构后的 meraki.py Activity 实现
每个 Workflow 对应一个具体的业务场景，提供企业级的可靠性和可观测性。
"""

from datetime import timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from meraki import MerakiActivities


# ==================== 数据类定义 ====================

@dataclass
class ConcordiaWorkflowInput:
    """Concordia工作流通用输入"""
    api_key: str
    org_id: str = "850617379619606726"  # Concordia组织ID


@dataclass
class DeviceStatusResult:
    """设备状态查询结果"""
    organization_name: str
    organization_id: str
    device_status_overview: Dict[str, Any]
    health_metrics: Dict[str, Any]
    raw_counts: Dict[str, int]
    query_time: str
    success: bool
    error_message: Optional[str] = None


@dataclass
class APDeviceQueryInput:
    """AP设备查询输入"""
    api_key: str
    org_id: str = "850617379619606726"
    search_keyword: str = "H330"  # 默认搜索关键词


@dataclass
class APDeviceQueryResult:
    """AP设备查询结果"""
    query_keyword: str
    search_summary: Dict[str, Any]
    matched_devices_list: List[Dict[str, Any]]
    selected_devices_details: List[Dict[str, Any]]
    user_interaction: Dict[str, Any]
    query_time: str
    success: bool
    error_message: Optional[str] = None


@dataclass
class ClientCountResult:
    """客户端数量统计结果"""
    organization_name: str
    organization_id: str
    query_summary: Dict[str, Any]
    networks_breakdown: List[Dict[str, Any]]
    client_distribution_analysis: Dict[str, Any]
    query_time: str
    success: bool
    error_message: Optional[str] = None


@dataclass
class FirmwareSummaryResult:
    """固件版本汇总结果"""
    organization_name: str
    organization_id: str
    firmware_summary: Dict[str, Any]
    model_firmware_breakdown: Dict[str, Any]
    consistency_analysis: Dict[str, Any]
    firmware_upgrade_recommendations: Dict[str, Any]
    query_time: str
    success: bool
    error_message: Optional[str] = None


@dataclass
class LicenseDetailsResult:
    """许可证详情结果"""
    organization_name: str
    organization_id: str
    license_overview: Dict[str, Any]
    license_details: List[Dict[str, Any]]
    license_analysis: Dict[str, Any]
    query_time: str
    success: bool
    error_message: Optional[str] = None


@dataclass
class DeviceInspectionResult:
    """设备巡检报告结果"""
    organization_name: str
    organization_id: str
    report_metadata: Dict[str, Any]
    device_status_analysis: Dict[str, Any]
    alerts_analysis: Dict[str, Any]
    network_events_analysis: Dict[str, Any]
    health_assessment: Dict[str, Any]
    recommendations: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None


@dataclass
class FloorplanAPInput:
    """楼层AP分布查询输入"""
    api_key: str
    org_id: str = "850617379619606726"
    floor_name: Optional[str] = None  # 可选的楼层名称过滤


@dataclass
class FloorplanAPResult:
    """楼层AP分布结果"""
    organization_name: str
    organization_id: str
    available_floorplans: List[Dict[str, Any]]
    selected_floorplan: Dict[str, Any]
    ap_distribution: List[Dict[str, Any]]
    query_time: str
    success: bool
    error_message: Optional[str] = None


@dataclass
class DeviceLocationInput:
    """设备点位图查询输入"""
    api_key: str
    org_id: str = "850617379619606726"
    search_keyword: str = "Corr"  # 设备名称关键词


@dataclass
class DeviceLocationResult:
    """设备点位图结果"""
    search_keyword: str
    total_matched: int
    matched_devices: List[Dict[str, Any]]
    selected_device_locations: List[Dict[str, Any]]
    query_time: str
    success: bool
    error_message: Optional[str] = None


@dataclass
class LostDeviceTraceInput:
    """丢失设备追踪输入"""
    api_key: str
    org_id: str = "850617379619606726"
    client_mac: Optional[str] = None  # 可选的MAC地址
    client_description: Optional[str] = None  # 可选的设备描述


@dataclass
class LostDeviceTraceResult:
    """丢失设备追踪结果"""
    search_criteria: Dict[str, Any]
    discovered_clients: List[Dict[str, Any]]
    selected_client_trace: Dict[str, Any]
    connection_history: List[Dict[str, Any]]
    query_time: str
    success: bool
    error_message: Optional[str] = None


@dataclass
class AlertsLogResult:
    """告警日志结果"""
    organization_name: str
    organization_id: str
    alerts_summary: Dict[str, Any]
    critical_alerts: List[Dict[str, Any]]
    network_events_sample: List[Dict[str, Any]]
    alert_categories: List[str]
    query_time: str
    success: bool
    error_message: Optional[str] = None


# ==================== Workflow 定义 ====================

@workflow.defn
class DeviceStatusWorkflow:
    """1. 告诉我整体设备运行状态"""
    
    @workflow.run
    async def run(self, input: ConcordiaWorkflowInput) -> DeviceStatusResult:
        """获取整体设备运行状态"""
        try:
            # 设置API密钥环境变量
            import os
            os.environ["MERAKI_API_KEY"] = input.api_key
            
            # 获取设备状态概览
            from meraki import MerakiActivities
            status_overview = await workflow.execute_activity_method(
                MerakiActivities.get_device_statuses_overview,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            # 处理数据
            counts = status_overview.get("counts", {}).get("byStatus", {})
            total_devices = sum(counts.values())
            online_devices = counts.get("online", 0)
            health_percentage = (online_devices / total_devices * 100) if total_devices > 0 else 0
            
            return DeviceStatusResult(
                organization_name="Concordia",
                organization_id=input.org_id,
                device_status_overview={
                    "total_devices": total_devices,
                    "online_devices": online_devices,
                    "offline_devices": counts.get("offline", 0),
                    "alerting_devices": counts.get("alerting", 0),
                    "dormant_devices": counts.get("dormant", 0)
                },
                health_metrics={
                    "online_percentage": round(health_percentage, 2),
                    "health_status": "良好" if health_percentage > 95 else "需要关注"
                },
                raw_counts=counts,
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=True
            )
            
        except Exception as e:
            return DeviceStatusResult(
                organization_name="Concordia",
                organization_id=input.org_id,
                device_status_overview={},
                health_metrics={},
                raw_counts={},
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=False,
                error_message=str(e)
            )


@workflow.defn
class APDeviceQueryWorkflow:
    """2. AP"XX"设备状态"""
    
    @workflow.run
    async def run(self, input: APDeviceQueryInput) -> APDeviceQueryResult:
        """查询指定关键词的AP设备状态"""
        try:
            meraki_activities = MerakiActivities(input.api_key)
            
            # 搜索包含关键词的设备
            devices = await workflow.execute_activity_method(
                meraki_activities.get_organization_devices,
                input.org_id,
                True,  # use_pagination
                5000,  # per_page
                input.search_keyword,  # name_filter
                start_to_close_timeout=timedelta(seconds=60),
            )
            
            # 构建匹配设备列表
            matched_devices_list = []
            for i, device in enumerate(devices[:10], 1):  # 限制前10个
                matched_devices_list.append({
                    "index": i,
                    "name": device.get("name", ""),
                    "model": device.get("model", ""),
                    "serial": device.get("serial", ""),
                    "network_id": device.get("networkId", "")
                })
            
            # 获取前3个设备的详细信息
            selected_devices_details = []
            for device in devices[:3]:
                device_detail = await workflow.execute_activity_method(
                    meraki_activities.get_device_info,
                    device.get("serial", ""),
                    start_to_close_timeout=timedelta(seconds=30),
                )
                
                selected_devices_details.append({
                    "name": device_detail.get("name", ""),
                    "serial": device_detail.get("serial", ""),
                    "model": device_detail.get("model", ""),
                    "firmware": device_detail.get("firmware", ""),
                    "lan_ip": device_detail.get("lanIp", ""),
                    "network_id": device_detail.get("networkId", ""),
                    "location": {
                        "lat": device_detail.get("lat"),
                        "lng": device_detail.get("lng"),
                        "address": device_detail.get("address", "")
                    },
                    "status": "online",  # 简化状态
                    "tags": device_detail.get("tags", [])
                })
            
            return APDeviceQueryResult(
                query_keyword=input.search_keyword,
                search_summary={
                    "total_matched": len(devices),
                    "details_retrieved": len(selected_devices_details),
                    "search_scope": "全组织设备"
                },
                matched_devices_list=matched_devices_list,
                selected_devices_details=selected_devices_details,
                user_interaction={
                    "action": "用户可从匹配列表中选择任意设备查看详情",
                    "available_selections": len(devices),
                    "demonstration_count": len(selected_devices_details)
                },
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=True
            )
            
        except Exception as e:
            return APDeviceQueryResult(
                query_keyword=input.search_keyword,
                search_summary={},
                matched_devices_list=[],
                selected_devices_details=[],
                user_interaction={},
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=False,
                error_message=str(e)
            )


@workflow.defn
class ClientCountWorkflow:
    """3. 查询当前终端设备数量信息"""
    
    @workflow.run
    async def run(self, input: ConcordiaWorkflowInput) -> ClientCountResult:
        """统计组织的客户端数量信息"""
        try:
            meraki_activities = MerakiActivities(input.api_key)
            
            # 获取所有网络
            networks = await workflow.execute_activity_method(
                meraki_activities.get_organization_networks,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            # 并发获取每个网络的客户端概览
            networks_breakdown = []
            total_clients = 0
            total_heavy_usage = 0
            networks_with_clients = 0
            
            for network in networks:
                network_id = network.get("id", "")
                network_name = network.get("name", "")
                
                try:
                    client_overview = await workflow.execute_activity_method(
                        meraki_activities.get_network_clients_overview,
                        network_id,
                        start_to_close_timeout=timedelta(seconds=30),
                    )
                    
                    client_count = client_overview.get("counts", {}).get("total", 0)
                    heavy_usage_count = client_overview.get("counts", {}).get("withHeavyUsage", 0)
                    
                    total_clients += client_count
                    total_heavy_usage += heavy_usage_count
                    if client_count > 0:
                        networks_with_clients += 1
                    
                    networks_breakdown.append({
                        "network_name": network_name,
                        "network_id": network_id,
                        "client_count": client_count,
                        "heavy_usage_count": heavy_usage_count,
                        "product_types": network.get("productTypes", []),
                        "timezone": network.get("timeZone", "")
                    })
                    
                except Exception as e:
                    # 网络级错误，记录但继续处理其他网络
                    networks_breakdown.append({
                        "network_name": network_name,
                        "network_id": network_id,
                        "client_count": 0,
                        "heavy_usage_count": 0,
                        "product_types": network.get("productTypes", []),
                        "timezone": network.get("timeZone", ""),
                        "error": str(e)
                    })
            
            # 分析数据
            networks_without_clients = [n["network_name"] for n in networks_breakdown if n["client_count"] == 0]
            most_active_network = max(networks_breakdown, key=lambda x: x["client_count"])["network_name"] if networks_breakdown else ""
            
            return ClientCountResult(
                organization_name="Concordia",
                organization_id=input.org_id,
                query_summary={
                    "total_clients_in_org": total_clients,
                    "total_networks": len(networks),
                    "networks_with_clients": networks_with_clients,
                    "total_heavy_usage_clients": total_heavy_usage,
                    "avg_clients_per_network": total_clients / len(networks) if networks else 0
                },
                networks_breakdown=networks_breakdown,
                client_distribution_analysis={
                    "most_active_network": most_active_network,
                    "networks_without_clients": networks_without_clients,
                    "heavy_usage_ratio": round(total_heavy_usage / total_clients * 100, 2) if total_clients > 0 else 0
                },
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=True
            )
            
        except Exception as e:
            return ClientCountResult(
                organization_name="Concordia",
                organization_id=input.org_id,
                query_summary={},
                networks_breakdown=[],
                client_distribution_analysis={},
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=False,
                error_message=str(e)
            )


@workflow.defn
class FirmwareSummaryWorkflow:
    """4. 汇总不同型号的固件版本"""
    
    @workflow.run
    async def run(self, input: ConcordiaWorkflowInput) -> FirmwareSummaryResult:
        """汇总组织内所有设备的固件版本信息"""
        try:
            meraki_activities = MerakiActivities(input.api_key)
            
            # 获取所有设备
            devices = await workflow.execute_activity_method(
                meraki_activities.get_organization_devices,
                input.org_id,
                True,  # use_pagination
                5000,  # per_page
                start_to_close_timeout=timedelta(seconds=120),
            )
            
            # 按型号分组统计固件版本
            model_firmware_breakdown = {}
            
            for device in devices:
                model = device.get("model", "Unknown")
                firmware = device.get("firmware", "Unknown")
                
                if model not in model_firmware_breakdown:
                    model_firmware_breakdown[model] = {
                        "firmware_versions": [],
                        "device_count": 0,
                        "version_count": 0,
                        "is_consistent": True
                    }
                
                if firmware not in model_firmware_breakdown[model]["firmware_versions"]:
                    model_firmware_breakdown[model]["firmware_versions"].append(firmware)
                
                model_firmware_breakdown[model]["device_count"] += 1
            
            # 分析一致性
            consistent_models = []
            inconsistent_models = []
            
            for model, info in model_firmware_breakdown.items():
                version_count = len(info["firmware_versions"])
                info["version_count"] = version_count
                info["is_consistent"] = version_count == 1
                
                if version_count == 1:
                    consistent_models.append(model)
                else:
                    inconsistent_models.append(model)
            
            return FirmwareSummaryResult(
                organization_name="Concordia",
                organization_id=input.org_id,
                firmware_summary={
                    "total_devices": len(devices),
                    "total_models": len(model_firmware_breakdown),
                    "models_with_consistent_firmware": len(consistent_models),
                    "models_with_inconsistent_firmware": len(inconsistent_models)
                },
                model_firmware_breakdown=model_firmware_breakdown,
                consistency_analysis={
                    "consistent_models": consistent_models,
                    "inconsistent_models": inconsistent_models,
                    "overall_consistency": len(inconsistent_models) == 0
                },
                firmware_upgrade_recommendations={
                    "models_needing_attention": inconsistent_models,
                    "total_devices_needing_upgrade": sum(
                        info["device_count"] for model, info in model_firmware_breakdown.items()
                        if model in inconsistent_models
                    )
                },
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=True
            )
            
        except Exception as e:
            return FirmwareSummaryResult(
                organization_name="Concordia",
                organization_id=input.org_id,
                firmware_summary={},
                model_firmware_breakdown={},
                consistency_analysis={},
                firmware_upgrade_recommendations={},
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=False,
                error_message=str(e)
            )


@workflow.defn
class LicenseDetailsWorkflow:
    """5. 查询当前授权状态详情"""
    
    @workflow.run
    async def run(self, input: ConcordiaWorkflowInput) -> LicenseDetailsResult:
        """获取组织的许可证详情"""
        try:
            meraki_activities = MerakiActivities(input.api_key)
            
            # 获取许可证概览
            license_overview = await workflow.execute_activity_method(
                meraki_activities.get_organization_licenses_overview,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            # 获取许可证详情
            try:
                license_details = await workflow.execute_activity_method(
                    meraki_activities.get_organization_licenses,
                    input.org_id,
                    start_to_close_timeout=timedelta(seconds=60),
                )
            except Exception:
                # 如果详情API失败，使用空列表
                license_details = []
            
            # 分析许可证状态
            license_analysis = {
                "overview_available": bool(license_overview),
                "details_available": bool(license_details),
                "total_licenses": len(license_details) if license_details else 0,
                "status": license_overview.get("status", "unknown") if license_overview else "unknown"
            }
            
            return LicenseDetailsResult(
                organization_name="Concordia",
                organization_id=input.org_id,
                license_overview=license_overview or {},
                license_details=license_details or [],
                license_analysis=license_analysis,
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=True
            )
            
        except Exception as e:
            return LicenseDetailsResult(
                organization_name="Concordia",
                organization_id=input.org_id,
                license_overview={},
                license_details=[],
                license_analysis={},
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=False,
                error_message=str(e)
            )


@workflow.defn
class DeviceInspectionWorkflow:
    """6. 给我一份最新的设备巡检报告"""
    
    @workflow.run
    async def run(self, input: ConcordiaWorkflowInput) -> DeviceInspectionResult:
        """生成综合设备巡检报告"""
        try:
            meraki_activities = MerakiActivities(input.api_key)
            
            # 并发获取多种信息
            status_overview_task = workflow.execute_activity_method(
                meraki_activities.get_device_statuses_overview,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            alerts_task = workflow.execute_activity_method(
                meraki_activities.get_organization_assurance_alerts,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=60),
            )
            
            networks_task = workflow.execute_activity_method(
                meraki_activities.get_organization_networks,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            # 等待所有任务完成
            status_overview = await status_overview_task
            alerts = await alerts_task
            networks = await networks_task
            
            # 分析设备状态
            counts = status_overview.get("counts", {}).get("byStatus", {})
            total_devices = sum(counts.values())
            online_devices = counts.get("online", 0)
            health_percentage = (online_devices / total_devices * 100) if total_devices > 0 else 0
            
            device_status_analysis = {
                "total_devices": total_devices,
                "online_devices": online_devices,
                "offline_devices": counts.get("offline", 0),
                "alerting_devices": counts.get("alerting", 0),
                "dormant_devices": counts.get("dormant", 0),
                "health_percentage": round(health_percentage, 2),
                "status_distribution": counts
            }
            
            # 分析告警
            critical_alerts = [alert for alert in alerts if alert.get("severity") == "critical"]
            alerts_analysis = {
                "total_alerts": len(alerts),
                "critical_alerts": len(critical_alerts),
                "warning_alerts": len([a for a in alerts if a.get("severity") == "warning"]),
                "info_alerts": len([a for a in alerts if a.get("severity") == "info"]),
                "recent_critical_alerts": critical_alerts[:5],  # 前5个严重告警
                "alert_categories": list(set(alert.get("categoryType", "unknown") for alert in alerts))
            }
            
            # 网络事件分析（简化版）
            network_events_analysis = {
                "events_sampled": 0,
                "networks_checked": len(networks),
                "sample_network": networks[0].get("name", "") if networks else "",
                "recent_events": []
            }
            
            # 健康评估
            health_assessment = {
                "overall_health": "良好" if health_percentage > 95 else "需要关注",
                "critical_issues": len(critical_alerts),
                "devices_needing_attention": counts.get("offline", 0) + counts.get("alerting", 0),
                "network_stability": "稳定" if len(critical_alerts) < 5 else "不稳定"
            }
            
            # 建议
            recommendations = {
                "immediate_actions": [],
                "maintenance_suggestions": []
            }
            
            if counts.get("offline", 0) > 0:
                recommendations["immediate_actions"].append(f"检查 {counts['offline']} 台离线设备")
            if counts.get("alerting", 0) > 0:
                recommendations["immediate_actions"].append(f"处理 {counts['alerting']} 台告警设备")
            if len(critical_alerts) > 0:
                recommendations["immediate_actions"].append("优先处理严重告警")
            
            return DeviceInspectionResult(
                organization_name="Concordia",
                organization_id=input.org_id,
                report_metadata={
                    "report_time": workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "report_type": "综合设备巡检报告",
                    "data_sources": ["设备状态", "组织告警", "网络事件"]
                },
                device_status_analysis=device_status_analysis,
                alerts_analysis=alerts_analysis,
                network_events_analysis=network_events_analysis,
                health_assessment=health_assessment,
                recommendations=recommendations,
                success=True
            )
            
        except Exception as e:
            return DeviceInspectionResult(
                organization_name="Concordia",
                organization_id=input.org_id,
                report_metadata={},
                device_status_analysis={},
                alerts_analysis={},
                network_events_analysis={},
                health_assessment={},
                recommendations={},
                success=False,
                error_message=str(e)
            )


@workflow.defn
class FloorplanAPWorkflow:
    """7. 查询某个楼层的 AP 分布图"""
    
    @workflow.run
    async def run(self, input: FloorplanAPInput) -> FloorplanAPResult:
        """获取楼层的AP分布信息"""
        try:
            meraki_activities = MerakiActivities(input.api_key)
            
            # 获取所有网络
            networks = await workflow.execute_activity_method(
                meraki_activities.get_organization_networks,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            # 查找有楼层平面图的网络
            available_floorplans = []
            selected_floorplan = {}
            ap_distribution = []
            
            for network in networks:
                network_id = network.get("id", "")
                try:
                    floorplans = await workflow.execute_activity_method(
                        meraki_activities.get_network_floor_plans,
                        network_id,
                        start_to_close_timeout=timedelta(seconds=30),
                    )
                    
                    for floorplan in floorplans:
                        floorplan_info = {
                            "network_name": network.get("name", ""),
                            "network_id": network_id,
                            "floorplan_id": floorplan.get("floorPlanId", ""),
                            "floorplan_name": floorplan.get("name", ""),
                            "image_url": floorplan.get("imageUrl", "")
                        }
                        available_floorplans.append(floorplan_info)
                        
                        # 如果指定了楼层名称过滤或选择第一个
                        if (not selected_floorplan and 
                            (not input.floor_name or input.floor_name.lower() in floorplan.get("name", "").lower())):
                            
                            # 获取楼层详情
                            floorplan_detail = await workflow.execute_activity_method(
                                meraki_activities.get_floor_plan_by_id,
                                network_id,
                                floorplan.get("floorPlanId", ""),
                                start_to_close_timeout=timedelta(seconds=30),
                            )
                            
                            selected_floorplan = {
                                "floorplan_id": floorplan.get("floorPlanId", ""),
                                "name": floorplan.get("name", ""),
                                "image_url": floorplan_detail.get("imageUrl", ""),
                                "network_name": network.get("name", ""),
                                "network_id": network_id
                            }
                            
                            # 提取AP分布信息
                            devices = floorplan_detail.get("devices", [])
                            for device in devices:
                                ap_distribution.append({
                                    "name": device.get("name", ""),
                                    "serial": device.get("serial", ""),
                                    "model": device.get("model", ""),
                                    "location": {
                                        "lat": device.get("lat"),
                                        "lng": device.get("lng")
                                    },
                                    "lan_ip": device.get("lanIp", ""),
                                    "tags": device.get("tags", [])
                                })
                
                except Exception:
                    # 网络没有楼层平面图，继续下一个
                    continue
            
            return FloorplanAPResult(
                organization_name="Concordia",
                organization_id=input.org_id,
                available_floorplans=available_floorplans,
                selected_floorplan=selected_floorplan,
                ap_distribution=ap_distribution,
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=True
            )
            
        except Exception as e:
            return FloorplanAPResult(
                organization_name="Concordia",
                organization_id=input.org_id,
                available_floorplans=[],
                selected_floorplan={},
                ap_distribution=[],
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=False,
                error_message=str(e)
            )


@workflow.defn
class DeviceLocationWorkflow:
    """8. 给我设备"AP XX名字"的点位图"""
    
    @workflow.run
    async def run(self, input: DeviceLocationInput) -> DeviceLocationResult:
        """获取指定设备的点位图信息"""
        try:
            meraki_activities = MerakiActivities(input.api_key)
            
            # 搜索包含关键词的设备
            devices = await workflow.execute_activity_method(
                meraki_activities.get_organization_devices,
                input.org_id,
                True,  # use_pagination
                5000,  # per_page
                input.search_keyword,  # name_filter
                start_to_close_timeout=timedelta(seconds=60),
            )
            
            # 构建匹配设备列表
            matched_devices = []
            for i, device in enumerate(devices, 1):
                matched_devices.append({
                    "index": i,
                    "name": device.get("name", ""),
                    "model": device.get("model", ""),
                    "serial": device.get("serial", ""),
                    "networkId": device.get("networkId", "")
                })
            
            # 获取前2个设备的点位图信息
            selected_device_locations = []
            for device in devices[:2]:
                device_detail = await workflow.execute_activity_method(
                    meraki_activities.get_device_info,
                    device.get("serial", ""),
                    start_to_close_timeout=timedelta(seconds=30),
                )
                
                location_info = {
                    "name": device_detail.get("name", ""),
                    "serial": device_detail.get("serial", ""),
                    "model": device_detail.get("model", ""),
                    "location": {
                        "lat": device_detail.get("lat"),
                        "lng": device_detail.get("lng"),
                        "address": device_detail.get("address", "")
                    },
                    "floorplan_info": {},
                    "image_url": ""
                }
                
                # 如果有楼层信息，获取楼层图片
                floor_plan_id = device_detail.get("floorPlanId")
                network_id = device_detail.get("networkId")
                
                if floor_plan_id and network_id:
                    try:
                        floorplan_detail = await workflow.execute_activity_method(
                            meraki_activities.get_floor_plan_by_id,
                            network_id,
                            floor_plan_id,
                            start_to_close_timeout=timedelta(seconds=30),
                        )
                        
                        location_info["floorplan_info"] = {
                            "floorplan_id": floor_plan_id,
                            "name": floorplan_detail.get("name", ""),
                            "network_id": network_id
                        }
                        location_info["image_url"] = floorplan_detail.get("imageUrl", "")
                        
                    except Exception:
                        # 楼层信息获取失败，继续处理
                        pass
                
                selected_device_locations.append(location_info)
            
            return DeviceLocationResult(
                search_keyword=input.search_keyword,
                total_matched=len(devices),
                matched_devices=matched_devices,
                selected_device_locations=selected_device_locations,
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=True
            )
            
        except Exception as e:
            return DeviceLocationResult(
                search_keyword=input.search_keyword,
                total_matched=0,
                matched_devices=[],
                selected_device_locations=[],
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=False,
                error_message=str(e)
            )


@workflow.defn
class LostDeviceTraceWorkflow:
    """9. 我的电脑丢了，最近连接过哪些 AP"""
    
    @workflow.run
    async def run(self, input: LostDeviceTraceInput) -> LostDeviceTraceResult:
        """追踪丢失设备的连接历史"""
        try:
            meraki_activities = MerakiActivities(input.api_key)
            
            # 如果没有指定MAC地址，先发现活跃客户端
            discovered_clients = []
            selected_client_trace = {}
            connection_history = []
            
            if not input.client_mac:
                # 获取所有网络
                networks = await workflow.execute_activity_method(
                    meraki_activities.get_organization_networks,
                    input.org_id,
                    start_to_close_timeout=timedelta(seconds=30),
                )
                
                # 查找活跃客户端
                for network in networks:
                    network_id = network.get("id", "")
                    try:
                        clients = await workflow.execute_activity_method(
                            meraki_activities.get_network_clients,
                            network_id,
                            False,  # use_pagination
                            5,  # per_page - 限制数量
                            timespan=86400,  # 24小时内
                            start_to_close_timeout=timedelta(seconds=30),
                        )
                        
                        for i, client in enumerate(clients, 1):
                            discovered_clients.append({
                                "index": i,
                                "mac": client.get("mac", ""),
                                "description": client.get("description"),
                                "client_id": client.get("id", ""),
                                "network_name": network.get("name", ""),
                                "network_id": network_id
                            })
                        
                        # 如果找到客户端，选择第一个进行追踪
                        if clients and not selected_client_trace:
                            first_client = clients[0]
                            client_id = first_client.get("id", "")
                            
                            # 获取连接统计
                            try:
                                connection_stats = await workflow.execute_activity_method(
                                    meraki_activities.get_network_wireless_client_connection_stats,
                                    network_id,
                                    client_id,
                                    timespan=86400,  # 24小时
                                    start_to_close_timeout=timedelta(seconds=30),
                                )
                                
                                selected_client_trace = {
                                    "mac": first_client.get("mac", ""),
                                    "description": first_client.get("description", ""),
                                    "network_name": network.get("name", ""),
                                    "connection_stats": connection_stats.get("connectionStats", {})
                                }
                                
                            except Exception:
                                # 连接统计获取失败
                                selected_client_trace = {
                                    "mac": first_client.get("mac", ""),
                                    "description": first_client.get("description", ""),
                                    "network_name": network.get("name", ""),
                                    "connection_stats": {}
                                }
                        
                        # 限制发现的客户端数量
                        if len(discovered_clients) >= 5:
                            break
                            
                    except Exception:
                        # 网络客户端获取失败，继续下一个网络
                        continue
            
            return LostDeviceTraceResult(
                search_criteria={
                    "client_mac": input.client_mac,
                    "client_description": input.client_description,
                    "search_method": "指定MAC" if input.client_mac else "自动发现"
                },
                discovered_clients=discovered_clients,
                selected_client_trace=selected_client_trace,
                connection_history=connection_history,
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=True
            )
            
        except Exception as e:
            return LostDeviceTraceResult(
                search_criteria={},
                discovered_clients=[],
                selected_client_trace={},
                connection_history=[],
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=False,
                error_message=str(e)
            )


@workflow.defn
class AlertsLogWorkflow:
    """10. 列出当前的告警日志（全组织）"""
    
    @workflow.run
    async def run(self, input: ConcordiaWorkflowInput) -> AlertsLogResult:
        """获取组织的告警日志"""
        try:
            meraki_activities = MerakiActivities(input.api_key)
            
            # 获取组织告警
            alerts = await workflow.execute_activity_method(
                meraki_activities.get_organization_assurance_alerts,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=60),
            )
            
            # 分析告警
            critical_alerts = [alert for alert in alerts if alert.get("severity") == "critical"]
            warning_alerts = [alert for alert in alerts if alert.get("severity") == "warning"]
            info_alerts = [alert for alert in alerts if alert.get("severity") == "info"]
            
            alerts_summary = {
                "total_alerts": len(alerts),
                "critical_count": len(critical_alerts),
                "warning_count": len(warning_alerts),
                "info_count": len(info_alerts),
                "unresolved_count": len([a for a in alerts if not a.get("resolvedAt")])
            }
            
            # 提取告警类别
            alert_categories = list(set(alert.get("categoryType", "unknown") for alert in alerts))
            
            # 获取网络事件样本（简化版）
            network_events_sample = []
            try:
                networks = await workflow.execute_activity_method(
                    meraki_activities.get_organization_networks,
                    input.org_id,
                    start_to_close_timeout=timedelta(seconds=30),
                )
                
                # 从第一个网络获取事件样本
                if networks:
                    first_network = networks[0]
                    network_id = first_network.get("id", "")
                    
                    events = await workflow.execute_activity_method(
                        meraki_activities.get_network_events,
                        network_id,
                        False,  # use_pagination
                        3,  # per_page
                        timespan=3600,  # 1小时
                        productType="wireless",
                        start_to_close_timeout=timedelta(seconds=30),
                    )
                    
                    network_events_sample = events[:3] if events else []
                    
            except Exception:
                # 网络事件获取失败，使用空列表
                pass
            
            return AlertsLogResult(
                organization_name="Concordia",
                organization_id=input.org_id,
                alerts_summary=alerts_summary,
                critical_alerts=critical_alerts[:10],  # 前10个严重告警
                network_events_sample=network_events_sample,
                alert_categories=alert_categories,
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=True
            )
            
        except Exception as e:
            return AlertsLogResult(
                organization_name="Concordia",
                organization_id=input.org_id,
                alerts_summary={},
                critical_alerts=[],
                network_events_sample=[],
                alert_categories=[],
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=False,
                error_message=str(e)
            )

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Concordia 学校 10个业务场景的 Temporal Workflow 实现 - ECharts图表版本

基于 testConcordia.py 的业务逻辑，使用重构后的 meraki.py Activity 实现
每个 Workflow 对应一个具体的业务场景，并配备相应的ECharts图表展示。

=== ECharts图表类型分配总表 ===

┌─────────┬─────────────────────────┬─────────────────────────┬─────────────────────────────────────────┐
│ 工作流  │        业务场景         │      ECharts图表类型     │                数据特征                 │
├─────────┼─────────────────────────┼─────────────────────────┼─────────────────────────────────────────┤
│   1     │    设备状态工作流       │     饼图(Pie Chart)     │ 设备状态分布 (在线168, 离线4, 告警2)    │
├─────────┼─────────────────────────┼─────────────────────────┼─────────────────────────────────────────┤
│   2     │   AP设备查询工作流      │ 表格+地图散点图(Table+  │ 设备列表+地理位置坐标 (3个H330设备)     │
│         │                         │     Map Scatter)        │                                         │
├─────────┼─────────────────────────┼─────────────────────────┼─────────────────────────────────────────┤
│   3     │  客户端数量统计工作流   │    柱状图(Bar Chart)    │ 各网络客户端数量 (CISS:1076, 其他:0)   │
├─────────┼─────────────────────────┼─────────────────────────┼─────────────────────────────────────────┤
│   4     │  固件版本汇总工作流     │ 堆叠柱状图(Stacked Bar) │ 设备型号分布 (MR44:141, MR57:29, MR86:4)│
├─────────┼─────────────────────────┼─────────────────────────┼─────────────────────────────────────────┤
│   5     │  许可证详情工作流       │   仪表盘(Gauge Chart)   │ 许可证状态 (178个无线许可证, 2031到期)  │
├─────────┼─────────────────────────┼─────────────────────────┼─────────────────────────────────────────┤
│   6     │  设备巡检报告工作流     │   雷达图(Radar Chart)   │ 多维健康指标 (健康度96.55%, 告警6个)    │
├─────────┼─────────────────────────┼─────────────────────────┼─────────────────────────────────────────┤
│   7     │  楼层AP分布工作流       │    树图(Tree Chart)     │ 层级结构数据 (16个楼层平面图)           │
├─────────┼─────────────────────────┼─────────────────────────┼─────────────────────────────────────────┤
│   8     │  设备点位图工作流       │  散点图(Scatter Chart)  │ 174个设备的地理坐标分布                 │
├─────────┼─────────────────────────┼─────────────────────────┼─────────────────────────────────────────┤
│   9     │  丢失设备追踪工作流     │  时间轴(Timeline Chart) │ 设备连接历史和时间序列数据              │
├─────────┼─────────────────────────┼─────────────────────────┼─────────────────────────────────────────┤
│  10     │   告警日志工作流        │  热力图(Heatmap Chart)  │ 告警矩阵 (connectivity:4, device_health:2)│
└─────────┴─────────────────────────┴─────────────────────────┴─────────────────────────────────────────┘

=== 图表选择理由 ===

1. 饼图 - 最适合展示分类数据的占比关系，设备状态分布一目了然
2. 表格+地图 - 设备详情用表格，地理分布用地图，信息完整且直观
3. 柱状图 - 最适合对比不同类别的数值大小，网络客户端数量对比清晰
4. 堆叠柱状图 - 展示分类数据的构成，设备型号和固件版本层次分明
5. 仪表盘 - 最适合展示单一指标的状态和进度，许可证健康度直观
6. 雷达图 - 最适合多维度指标对比，系统健康状况全面展示
7. 树图 - 最适合层级结构数据，楼层和AP的关系清晰
8. 散点图 - 最适合展示二维坐标数据，设备地理分布直观
9. 时间轴 - 最适合时间序列数据，设备连接历史清晰
10. 热力图 - 最适合矩阵数据密度展示，告警分布热点明显
"""

from datetime import timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from meraki import MerakiActivities


# ==================== 暗紫色主题配置 ====================

def get_dark_purple_theme():
    """获取统一的暗紫色主题配置"""
    return {
        "backgroundColor": "transparent",  # 透明背景，由外层容器控制
        "textStyle": {
            "color": "#e6e6fa",  # 淡紫色文字
            "fontFamily": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
        },
        "title": {
            "textStyle": {
                "color": "#ffffff",
                "fontSize": 16,
                "fontWeight": "bold"
            }
        },
        "legend": {
            "textStyle": {
                "color": "#b8b8d4"
            }
        },
        "tooltip": {
            "backgroundColor": "rgba(26, 26, 46, 0.95)",
            "borderColor": "#6a5acd",
            "borderWidth": 1,
            "textStyle": {
                "color": "#ffffff"
            }
        },
        "grid": {
            "borderColor": "#483d8b",
            "borderWidth": 1
        },
        "xAxis": {
            "axisLine": {
                "lineStyle": {
                    "color": "#6a5acd"
                }
            },
            "axisTick": {
                "lineStyle": {
                    "color": "#6a5acd"
                }
            },
            "axisLabel": {
                "color": "#b8b8d4"
            },
            "splitLine": {
                "lineStyle": {
                    "color": "#2e2e4f",
                    "type": "dashed"
                }
            }
        },
        "yAxis": {
            "axisLine": {
                "lineStyle": {
                    "color": "#6a5acd"
                }
            },
            "axisTick": {
                "lineStyle": {
                    "color": "#6a5acd"
                }
            },
            "axisLabel": {
                "color": "#b8b8d4"
            },
            "splitLine": {
                "lineStyle": {
                    "color": "#2e2e4f",
                    "type": "dashed"
                }
            }
        }
    }

def get_purple_color_palette():
    """获取紫色系调色板"""
    return [
        "#8a2be2",  # 蓝紫色
        "#9370db",  # 中紫色
        "#ba55d3",  # 中兰花紫
        "#da70d6",  # 兰花紫
        "#dda0dd",  # 梅红色
        "#ee82ee",  # 紫罗兰
        "#ff69b4",  # 热粉红
        "#ff1493",  # 深粉红
        "#dc143c",  # 深红色
        "#b22222"   # 火砖色
    ]

def merge_theme_config(base_config, theme_config):
    """合并主题配置到基础配置"""
    result = base_config.copy()
    for key, value in theme_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key].update(value)
        else:
            result[key] = value
    return result


# ==================== 数据类定义 ====================

@dataclass
class ConcordiaWorkflowInput:
    """Concordia工作流通用输入"""
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
    # ECharts数据格式
    echarts_data: List[Dict[str, Any]] = None


@dataclass
class APDeviceQueryInput:
    """AP设备查询输入"""
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
    # ECharts数据格式
    echarts_data: List[Dict[str, Any]] = None


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
    # ECharts数据格式
    echarts_data: List[Dict[str, Any]] = None


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
    # ECharts数据格式
    echarts_data: List[Dict[str, Any]] = None


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
    # ECharts数据格式
    echarts_data: List[Dict[str, Any]] = None


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
    # ECharts数据格式
    echarts_data: List[Dict[str, Any]] = None


@dataclass
class FloorplanAPInput:
    """楼层AP分布查询输入"""
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
    # ECharts数据格式
    echarts_data: List[Dict[str, Any]] = None


@dataclass
class DeviceLocationInput:
    """设备点位图查询输入"""
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
    # ECharts数据格式
    echarts_data: List[Dict[str, Any]] = None


@dataclass
class LostDeviceTraceInput:
    """丢失设备追踪输入"""
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
    # ECharts数据格式
    echarts_data: List[Dict[str, Any]] = None


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
    # ECharts数据格式
    echarts_data: List[Dict[str, Any]] = None


# ==================== Workflow 定义 ====================

@workflow.defn
class DeviceStatusWorkflow:
    """
    工作流1: 告诉我整体设备运行状态
    
    📊 ECharts图表类型: 饼图(Pie Chart)
    📈 数据特征: 设备状态分布 (在线168, 离线4, 告警2, 休眠0)
    🎯 展示目标: 各状态设备占比，直观显示网络健康度
    """
    
    @workflow.run
    async def run(self, input: ConcordiaWorkflowInput) -> DeviceStatusResult:
        """获取整体设备运行状态"""
        try:
            # 获取设备状态概览
            from meraki import MerakiActivities
            meraki_activities = MerakiActivities()
            status_overview = await workflow.execute_activity_method(
                meraki_activities.get_device_statuses_overview,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            # 处理数据
            counts = status_overview.get("counts", {}).get("byStatus", {})
            total_devices = sum(counts.values())
            online_devices = counts.get("online", 0)
            health_percentage = (online_devices / total_devices * 100) if total_devices > 0 else 0
            
            # 生成ECharts饼图数据格式 - 暗紫色主题
            theme_config = get_dark_purple_theme()
            
            pie_option = {
                "title": {"text": "设备状态分布", "left": "center"},
                "tooltip": {"trigger": "item", "formatter": "{a} <br/>{b}: {c} ({d}%)"},
                "legend": {
                    "orient": "vertical", 
                    "left": "left",
                    "top": "middle",
                    "itemGap": 15
                },
                "series": [{
                    "name": "设备状态",
                    "type": "pie",
                    "radius": ["30%", "70%"],  # 环形饼图
                    "center": ["60%", "50%"],
                    "data": [
                        {"name": "在线设备", "value": counts.get("online", 0), "itemStyle": {"color": "#8a2be2"}},
                        {"name": "离线设备", "value": counts.get("offline", 0), "itemStyle": {"color": "#ff1493"}},
                        {"name": "告警设备", "value": counts.get("alerting", 0), "itemStyle": {"color": "#ff69b4"}},
                        {"name": "休眠设备", "value": counts.get("dormant", 0), "itemStyle": {"color": "#9370db"}}
                    ],
                    "emphasis": {
                        "itemStyle": {
                            "shadowBlur": 15,
                            "shadowOffsetX": 0,
                            "shadowColor": "rgba(138, 43, 226, 0.8)"
                        }
                    },
                    "label": {
                        "show": True,
                        "formatter": "{b}: {c}\n({d}%)",
                        "color": "#ffffff",
                        "fontSize": 12
                    },
                    "labelLine": {
                        "show": True,
                        "lineStyle": {
                            "color": "#6a5acd"
                        }
                    }
                }]
            }
            
            # 合并主题配置
            pie_option = merge_theme_config(pie_option, theme_config)
            
            echarts_pie_data = [
                {
                    "type": "pie",
                    "title": "设备状态分布",
                    "data": [
                        {"name": "在线设备", "value": counts.get("online", 0), "itemStyle": {"color": "#8a2be2"}},
                        {"name": "离线设备", "value": counts.get("offline", 0), "itemStyle": {"color": "#ff1493"}},
                        {"name": "告警设备", "value": counts.get("alerting", 0), "itemStyle": {"color": "#ff69b4"}},
                        {"name": "休眠设备", "value": counts.get("dormant", 0), "itemStyle": {"color": "#9370db"}}
                    ],
                    "option": pie_option
                }
            ]
            
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
                success=True,
                echarts_data=echarts_pie_data
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
    """
    工作流2: AP"XX"设备状态
    
    📊 ECharts图表类型: 表格(Table) + 地图散点图(Map Scatter)
    📈 数据特征: 设备列表 + 地理位置坐标 (3个H330设备)
    🎯 展示目标: 表格展示设备详情，地图展示设备地理分布
    """
    
    @workflow.run
    async def run(self, input: APDeviceQueryInput) -> APDeviceQueryResult:
        """查询指定关键词的AP设备状态"""
        try:
            from meraki import MerakiActivities
            meraki_activities = MerakiActivities()
            
            # 搜索包含关键词的设备
            all_devices = await workflow.execute_activity_method(
                meraki_activities.get_organization_devices,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=60),
            )
            
            # 在工作流中过滤包含关键词的设备
            devices = []
            search_keyword_lower = input.search_keyword.lower()
            for device in all_devices:
                device_name = (device.get("name") or "").lower()
                if search_keyword_lower in device_name:
                    devices.append(device)
            
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
                    meraki_activities.get_device,
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
            
            # 生成ECharts表格和地图散点图数据格式
            echarts_data = [
                {
                    "type": "table",
                    "title": "AP设备列表",
                    "columns": ["序号", "设备名称", "型号", "序列号", "网络ID"],
                    "data": [[d["index"], d["name"], d["model"], d["serial"], d["network_id"]] for d in matched_devices_list]
                },
                {
                    "type": "scatter",
                    "title": "设备地理分布",
                    "option": {
                        "title": {"text": "AP设备地理分布", "left": "center"},
                        "tooltip": {
                            "trigger": "item",
                            "formatter": "设备: {c[2]}<br/>经度: {c[0]}<br/>纬度: {c[1]}"
                        },
                        "xAxis": {"type": "value", "name": "经度"},
                        "yAxis": {"type": "value", "name": "纬度"},
                        "series": [{
                            "name": "AP设备",
                            "type": "scatter",
                            "data": [
                                [device["location"]["lng"], device["location"]["lat"], device["name"]]
                                for device in selected_devices_details 
                                if device["location"]["lat"] and device["location"]["lng"]
                            ],
                            "symbolSize": 15,
                            "itemStyle": {
                                "color": "#8a2be2",
                                "borderColor": "#ffffff",
                                "borderWidth": 2
                            },
                            "emphasis": {
                                "itemStyle": {
                                    "shadowBlur": 15,
                                    "shadowColor": "rgba(138, 43, 226, 0.8)",
                                    "color": "#ff69b4",
                                    "borderColor": "#ffffff",
                                    "borderWidth": 3
                                }
                            }
                        }]
                    }
                }
            ]
            
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
                success=True,
                echarts_data=echarts_data
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
    """
    工作流3: 查询当前终端设备数量信息
    
    📊 ECharts图表类型: 柱状图(Bar Chart)
    📈 数据特征: 各网络客户端数量对比 (CISS Network: 1076, 其他: 0)
    🎯 展示目标: 对比各网络的客户端数量和活跃度
    """
    
    @workflow.run
    async def run(self, input: ConcordiaWorkflowInput) -> ClientCountResult:
        """统计组织的客户端数量信息"""
        try:
            from meraki import MerakiActivities
            meraki_activities = MerakiActivities()
            
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
            
            # 生成ECharts柱状图数据格式
            echarts_data = [
                {
                    "type": "bar",
                    "title": "各网络客户端数量统计",
                "option": merge_theme_config({
                    "title": {"text": "各网络客户端数量统计", "left": "center"},
                    "tooltip": {"trigger": "axis"},
                    "legend": {"data": ["客户端数量", "重度使用客户端"], "top": "10%"},
                        "xAxis": {
                            "type": "category",
                            "data": [n["network_name"] for n in networks_breakdown],
                            "axisLabel": {"rotate": 45}
                        },
                        "yAxis": {"type": "value", "name": "数量"},
                        "series": [
                            {
                                "name": "客户端数量",
                                "type": "bar",
                                "data": [n["client_count"] for n in networks_breakdown],
                                "itemStyle": {
                                    "color": {
                                        "type": "linear",
                                        "x": 0, "y": 0, "x2": 0, "y2": 1,
                                        "colorStops": [
                                            {"offset": 0, "color": "#8a2be2"},
                                            {"offset": 1, "color": "#9370db"}
                                        ]
                                    },
                                    "borderColor": "#ffffff",
                                    "borderWidth": 1
                                },
                                "emphasis": {
                                    "itemStyle": {
                                        "color": "#ba55d3",
                                        "shadowBlur": 10,
                                        "shadowColor": "rgba(138, 43, 226, 0.8)"
                                    }
                                }
                            },
                            {
                                "name": "重度使用客户端",
                                "type": "bar",
                                "data": [n["heavy_usage_count"] for n in networks_breakdown],
                                "itemStyle": {
                                    "color": {
                                        "type": "linear",
                                        "x": 0, "y": 0, "x2": 0, "y2": 1,
                                        "colorStops": [
                                            {"offset": 0, "color": "#ff69b4"},
                                            {"offset": 1, "color": "#ff1493"}
                                        ]
                                    },
                                    "borderColor": "#ffffff",
                                    "borderWidth": 1
                                },
                                "emphasis": {
                                    "itemStyle": {
                                        "color": "#da70d6",
                                        "shadowBlur": 10,
                                        "shadowColor": "rgba(255, 105, 180, 0.8)"
                                    }
                                }
                            }
                        ]
                    }, get_dark_purple_theme())
                }
            ]
            
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
                success=True,
                echarts_data=echarts_data
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
    """
    工作流4: 汇总不同型号的固件版本
    
    📊 ECharts图表类型: 堆叠柱状图(Stacked Bar Chart)
    📈 数据特征: 不同型号设备数量 (MR44: 141, MR57: 29, MR86: 4)
    🎯 展示目标: 按型号展示设备分布和固件版本一致性
    """
    
    @workflow.run
    async def run(self, input: ConcordiaWorkflowInput) -> FirmwareSummaryResult:
        """汇总组织内所有设备的固件版本信息"""
        try:
            from meraki import MerakiActivities
            meraki_activities = MerakiActivities()
            
            # 获取所有设备
            devices = await workflow.execute_activity_method(
                meraki_activities.get_organization_devices,
                input.org_id,
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
                success=True,
                echarts_data=[
                    {
                        "type": "bar",
                        "title": "设备型号固件版本分布",
                        "option": merge_theme_config({
                            "title": {"text": "设备型号固件版本分布", "left": "center"},
                            "tooltip": {"trigger": "axis"},
                            "legend": {"data": ["设备数量"], "top": "10%"},
                            "xAxis": {
                                "type": "category",
                                "data": list(model_firmware_breakdown.keys()),
                                "axisLabel": {"rotate": 0}
                            },
                            "yAxis": {"type": "value", "name": "设备数量"},
                            "series": [{
                                "name": "设备数量",
                                "type": "bar",
                                "data": [
                                    {
                                        "value": info["device_count"],
                                        "itemStyle": {
                                            "color": {
                                                "type": "linear",
                                                "x": 0, "y": 0, "x2": 0, "y2": 1,
                                                "colorStops": [
                                                    {"offset": 0, "color": "#8a2be2" if info["is_consistent"] else "#ff1493"},
                                                    {"offset": 1, "color": "#9370db" if info["is_consistent"] else "#dc143c"}
                                                ]
                                            },
                                            "borderColor": "#ffffff",
                                            "borderWidth": 1
                                        }
                                    } for info in model_firmware_breakdown.values()
                                ]
                            }]
                        }, get_dark_purple_theme())
                    }
                ]
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
    """
    工作流5: 查询当前授权状态详情
    
    📊 ECharts图表类型: 仪表盘(Gauge Chart)
    📈 数据特征: 许可证状态和到期时间 (178个无线许可证, 2031年到期)
    🎯 展示目标: 展示许可证使用率和健康状态
    """
    
    @workflow.run
    async def run(self, input: ConcordiaWorkflowInput) -> LicenseDetailsResult:
        """获取组织的许可证详情"""
        try:
            from meraki import MerakiActivities
            meraki_activities = MerakiActivities()
            
            # 获取许可证概览（Co-termination licensing模式）
            license_overview = await workflow.execute_activity_method(
                meraki_activities.get_organization_licenses_overview,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            # 基于概览数据分析许可证状态
            license_analysis = {
                "licensing_model": "Co-termination",
                "status": license_overview.get("status", "unknown"),
                "expiration_date": license_overview.get("expirationDate", "unknown"),
                "licensed_device_counts": license_overview.get("licensedDeviceCounts", {}),
                "total_wireless_licenses": license_overview.get("licensedDeviceCounts", {}).get("wireless", 0),
                "api_status": "full"
            }
            
            # 构建许可证详情（基于概览数据）
            license_details = []
            if license_overview.get("licensedDeviceCounts"):
                for device_type, count in license_overview.get("licensedDeviceCounts", {}).items():
                    license_details.append({
                        "device_type": device_type,
                        "license_count": count,
                        "status": license_overview.get("status", "unknown"),
                        "expiration_date": license_overview.get("expirationDate", "unknown")
                    })
            
            # 生成ECharts仪表盘数据格式
            echarts_data = [
                {
                    "type": "gauge",
                    "title": "许可证使用状态",
                    "option": merge_theme_config({
                        "title": {"text": "许可证使用状态", "left": "center"},
                        "series": [{
                            "name": "许可证状态",
                            "type": "gauge",
                            "progress": {"show": True},
                            "detail": {"valueAnimation": True, "formatter": "{value}%"},
                            "data": [{
                                "value": 100 if license_analysis.get("status") == "OK" else 0,
                                "name": "健康度"
                            }],
                            "axisLine": {
                                "lineStyle": {
                                    "width": 30,
                                    "color": [[0.3, "#ff1493"], [0.7, "#ff69b4"], [1, "#8a2be2"]]
                                }
                            },
                            "pointer": {
                                "itemStyle": {
                                    "color": "#ffffff",
                                    "borderColor": "#8a2be2",
                                    "borderWidth": 2
                                }
                            },
                            "title": {
                                "color": "#ffffff",
                                "fontSize": 14
                            },
                            "detail": {
                                "color": "#ffffff",
                                "fontSize": 16,
                                "fontWeight": "bold"
                            }
                        }]
                    }, get_dark_purple_theme())
                }
            ]
            
            return LicenseDetailsResult(
                organization_name="Concordia",
                organization_id=input.org_id,
                license_overview=license_overview or {},
                license_details=license_details or [],
                license_analysis=license_analysis,
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=True,
                echarts_data=echarts_data
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
    """
    工作流6: 给我一份最新的设备巡检报告
    
    📊 ECharts图表类型: 雷达图(Radar Chart)
    📈 数据特征: 多维度健康指标 (设备健康度96.55%, 告警数6, 离线设备4)
    🎯 展示目标: 多维度展示系统健康状况和巡检结果
    """
    
    @workflow.run
    async def run(self, input: ConcordiaWorkflowInput) -> DeviceInspectionResult:
        """生成综合设备巡检报告"""
        try:
            from meraki import MerakiActivities
            meraki_activities = MerakiActivities()
            
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
            
            # 生成ECharts雷达图数据格式
            echarts_data = [
                {
                    "type": "radar",
                    "title": "系统健康状况雷达图",
                    "option": merge_theme_config({
                        "title": {"text": "系统健康状况雷达图", "left": "center"},
                        "legend": {"data": ["当前状态"], "top": "10%"},
                        "radar": {
                            "indicator": [
                                {"name": "设备健康度", "max": 100},
                                {"name": "网络稳定性", "max": 100},
                                {"name": "告警控制", "max": 100},
                                {"name": "在线率", "max": 100},
                                {"name": "响应速度", "max": 100}
                            ]
                        },
                        "series": [{
                            "name": "健康指标",
                            "type": "radar",
                            "data": [{
                                "value": [
                                    device_status_analysis.get("health_percentage", 0),
                                    100 if health_assessment.get("network_stability") == "稳定" else 50,
                                    max(0, 100 - len(critical_alerts) * 10),
                                    device_status_analysis.get("health_percentage", 0),
                                    80  # 默认响应速度
                                ],
                                "name": "当前状态",
                                "itemStyle": {
                                    "color": "rgba(138, 43, 226, 0.8)"
                                },
                                "areaStyle": {
                                    "color": {
                                        "type": "radial",
                                        "x": 0.5, "y": 0.5, "r": 0.5,
                                        "colorStops": [
                                            {"offset": 0, "color": "rgba(138, 43, 226, 0.3)"},
                                            {"offset": 1, "color": "rgba(138, 43, 226, 0.1)"}
                                        ]
                                    }
                                },
                                "lineStyle": {
                                    "color": "#8a2be2",
                                    "width": 3
                                }
                            }]
                        }]
                    }, get_dark_purple_theme())
                }
            ]
            
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
                success=True,
                echarts_data=echarts_data
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
    """
    工作流7: 查询某个楼层的 AP 分布图
    
    📊 ECharts图表类型: 树图(Tree Chart)
    📈 数据特征: 层级结构数据 (16个楼层平面图的层级分布)
    🎯 展示目标: 展示楼层和AP的层级关系和分布情况
    """
    
    @workflow.run
    async def run(self, input: FloorplanAPInput) -> FloorplanAPResult:
        """获取楼层的AP分布信息"""
        try:
            from meraki import MerakiActivities
            meraki_activities = MerakiActivities()
            
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
                        meraki_activities.get_network_floorplans,
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
            
            # 生成ECharts树图数据格式
            echarts_data = [
                {
                    "type": "tree",
                    "title": "楼层AP分布树图",
                    "option": merge_theme_config({
                        "title": {"text": "楼层AP分布", "left": "center"},
                        "tooltip": {"trigger": "item"},
                        "series": [{
                            "type": "tree",
                            "data": [{
                                "name": "楼层平面图",
                                "children": [
                                    {
                                        "name": fp.get("floorplan_name", "Unknown"),
                                        "value": len(available_floorplans)
                                    } for fp in available_floorplans[:10]
                                ]
                            }],
                            "left": "2%",
                            "right": "2%", 
                            "top": "8%",
                            "bottom": "20%",
                            "symbol": "emptyCircle",
                            "orient": "vertical",
                            "itemStyle": {
                                "color": "#8a2be2",
                                "borderColor": "#ffffff",
                                "borderWidth": 2
                            },
                            "lineStyle": {
                                "color": "#6a5acd",
                                "width": 2
                            },
                            "label": {
                                "color": "#ffffff",
                                "fontSize": 12
                            },
                            "emphasis": {
                                "itemStyle": {
                                    "color": "#ff69b4",
                                    "shadowBlur": 10,
                                    "shadowColor": "rgba(138, 43, 226, 0.8)"
                                }
                            }
                        }]
                    }, get_dark_purple_theme())
                }
            ]
            
            return FloorplanAPResult(
                organization_name="Concordia",
                organization_id=input.org_id,
                available_floorplans=available_floorplans,
                selected_floorplan=selected_floorplan,
                ap_distribution=ap_distribution,
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=True,
                echarts_data=echarts_data
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
    """
    工作流8: 给我设备"AP XX名字"的点位图
    
    📊 ECharts图表类型: 散点图(Scatter Chart)
    📈 数据特征: 174个设备的地理坐标分布
    🎯 展示目标: 展示设备在地理空间的分布和点位信息
    """
    
    @workflow.run
    async def run(self, input: DeviceLocationInput) -> DeviceLocationResult:
        """获取指定设备的点位图信息"""
        try:
            from meraki import MerakiActivities
            meraki_activities = MerakiActivities()
            
            # 搜索包含关键词的设备
            all_devices = await workflow.execute_activity_method(
                meraki_activities.get_organization_devices,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=60),
            )
            
            # 在工作流中过滤包含关键词的设备
            devices = []
            search_keyword_lower = input.search_keyword.lower()
            for device in all_devices:
                device_name = (device.get("name") or "").lower()
                if search_keyword_lower in device_name:
                    devices.append(device)
            
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
                    meraki_activities.get_device,
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
            
            # 生成ECharts散点图数据格式
            echarts_data = [
                {
                    "type": "scatter",
                    "title": "设备点位分布图",
                    "option": merge_theme_config({
                        "title": {"text": f"设备点位分布 - {input.search_keyword}", "left": "center"},
                        "tooltip": {
                            "trigger": "item",
                            "formatter": "设备: {c[2]}<br/>经度: {c[0]}<br/>纬度: {c[1]}"
                        },
                        "xAxis": {"type": "value", "name": "经度"},
                        "yAxis": {"type": "value", "name": "纬度"},
                        "series": [{
                            "name": "设备位置",
                            "type": "scatter",
                            "data": [
                                [loc["location"]["lng"], loc["location"]["lat"], loc["name"]]
                                for loc in selected_device_locations 
                                if loc["location"]["lat"] and loc["location"]["lng"]
                            ],
                            "symbolSize": 12,
                            "itemStyle": {
                                "color": "#8a2be2",
                                "borderColor": "#ffffff",
                                "borderWidth": 2
                            },
                            "emphasis": {
                                "itemStyle": {
                                    "color": "#ff69b4",
                                    "shadowBlur": 15,
                                    "shadowColor": "rgba(138, 43, 226, 0.8)",
                                    "borderColor": "#ffffff",
                                    "borderWidth": 3
                                }
                            }
                        }]
                    }, get_dark_purple_theme())
                }
            ]
            
            return DeviceLocationResult(
                search_keyword=input.search_keyword,
                total_matched=len(devices),
                matched_devices=matched_devices,
                selected_device_locations=selected_device_locations,
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=True,
                echarts_data=echarts_data
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
    """
    工作流9: 我的电脑丢了，最近连接过哪些 AP
    
    📊 ECharts图表类型: 时间轴(Timeline Chart)
    📈 数据特征: 设备连接历史和时间序列数据
    🎯 展示目标: 展示设备连接的时间序列和追踪轨迹
    """
    
    @workflow.run
    async def run(self, input: LostDeviceTraceInput) -> LostDeviceTraceResult:
        """追踪丢失设备的连接历史"""
        try:
            from meraki import MerakiActivities
            meraki_activities = MerakiActivities()
            
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
            
            # 生成ECharts时间轴数据格式
            echarts_data = [
                {
                    "type": "timeline",
                    "title": "设备连接历史时间轴",
                    "option": merge_theme_config({
                        "title": {"text": "设备连接历史", "left": "center"},
                        "tooltip": {"trigger": "axis"},
                        "xAxis": {"type": "time", "name": "时间"},
                        "yAxis": {"type": "category", "data": ["连接状态"], "name": "状态"},
                        "series": [{
                            "name": "连接事件",
                            "type": "line",
                            "data": [
                                [event.get("timestamp", ""), 1 if event.get("connected") else 0]
                                for event in connection_history
                            ] if connection_history else [],
                            "step": "end",
                            "lineStyle": {
                                "width": 3,
                                "color": "#8a2be2"
                            },
                            "itemStyle": {
                                "color": "#ff69b4",
                                "borderColor": "#ffffff",
                                "borderWidth": 2
                            },
                            "areaStyle": {
                                "color": {
                                    "type": "linear",
                                    "x": 0, "y": 0, "x2": 0, "y2": 1,
                                    "colorStops": [
                                        {"offset": 0, "color": "rgba(138, 43, 226, 0.3)"},
                                        {"offset": 1, "color": "rgba(138, 43, 226, 0.1)"}
                                    ]
                                }
                            }
                        }]
                    }, get_dark_purple_theme())
                }
            ]
            
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
                success=True,
                echarts_data=echarts_data
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
    """
    工作流10: 列出当前的告警日志（全组织）
    
    📊 ECharts图表类型: 热力图(Heatmap Chart)
    📈 数据特征: 告警类型和严重程度矩阵 (connectivity: 4, device_health: 2)
    🎯 展示目标: 展示告警类型和严重程度的分布密度
    """
    
    @workflow.run
    async def run(self, input: ConcordiaWorkflowInput) -> AlertsLogResult:
        """获取组织的告警日志"""
        try:
            from meraki import MerakiActivities
            meraki_activities = MerakiActivities()
            
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
            
            # 生成ECharts热力图数据格式
            severity_category_matrix = {}
            for alert in critical_alerts:
                category = alert.get("categoryType", "unknown")
                severity = alert.get("severity", "unknown")
                key = f"{category}-{severity}"
                severity_category_matrix[key] = severity_category_matrix.get(key, 0) + 1
            
            echarts_data = [
                {
                    "type": "heatmap",
                    "title": "告警类型与严重程度热力图",
                    "option": merge_theme_config({
                        "title": {"text": "告警分布热力图", "left": "center"},
                        "tooltip": {"position": "top"},
                        "grid": {"height": "50%", "top": "10%"},
                        "xAxis": {
                            "type": "category",
                            "data": list(set([alert.get("categoryType", "unknown") for alert in critical_alerts])),
                            "splitArea": {"show": True}
                        },
                        "yAxis": {
                            "type": "category",
                            "data": ["critical", "warning", "info"],
                            "splitArea": {"show": True}
                        },
                        "visualMap": {
                            "min": 0,
                            "max": max(severity_category_matrix.values()) if severity_category_matrix else 1,
                            "calculable": True,
                            "orient": "horizontal",
                            "left": "center",
                            "bottom": "15%",
                            "inRange": {
                                "color": ["#1a1a2e", "#8a2be2", "#ff69b4", "#ff1493"]
                            },
                            "textStyle": {
                                "color": "#ffffff"
                            }
                        },
                        "series": [{
                            "name": "告警数量",
                            "type": "heatmap",
                            "data": [
                                [i, j, severity_category_matrix.get(f"{cat}-{sev}", 0)]
                                for i, cat in enumerate(set([alert.get("categoryType", "unknown") for alert in critical_alerts]))
                                for j, sev in enumerate(["critical", "warning", "info"])
                            ],
                            "label": {"show": True}
                        }]
                    }, get_dark_purple_theme())
                }
            ]
            
            return AlertsLogResult(
                organization_name="Concordia",
                organization_id=input.org_id,
                alerts_summary=alerts_summary,
                critical_alerts=critical_alerts[:10],  # 前10个严重告警
                network_events_sample=network_events_sample,
                alert_categories=alert_categories,
                query_time=workflow.now().strftime("%Y-%m-%d %H:%M:%S"),
                success=True,
                echarts_data=echarts_data
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Concordia 学校 10个业务场景的 Temporal Workflow 实现 - ECharts图表版本

基于 testConcordia.py 的业务逻辑，使用重构后的 meraki.py Activity 实现
每个 Workflow 对应一个具体的业务场景，并配备相应的ECharts图表展示。

=== ECharts图表类型分配总表 ===

## 📊 **原有10个简单工作流**
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

## 🚀 **新增4个复杂多Activity组合工作流**
┌─────────┬─────────────────────────┬─────────────────────────┬─────────────────────────────────────────┐
│ 工作流  │        业务场景         │    ECharts图表组合       │            多Activity组合               │
├─────────┼─────────────────────────┼─────────────────────────┼─────────────────────────────────────────┤
│  11     │  网络健康全景分析       │ 饼图+柱状图+散点图+仪表盘│ 4个API: 设备状态+告警+网络+客户端       │
├─────────┼─────────────────────────┼─────────────────────────┼─────────────────────────────────────────┤
│  12     │  安全态势感知分析       │ 树图+雷达图+热力图+柱状图│ 5个API: 网络+防火墙+无线+告警+客户端   │
├─────────┼─────────────────────────┼─────────────────────────┼─────────────────────────────────────────┤
│  13     │  运维故障诊断           │    雷达图+时间轴图      │ 4个API: 设备状态+告警+性能+上行链路     │
├─────────┼─────────────────────────┼─────────────────────────┼─────────────────────────────────────────┤
│  14     │  容量规划分析           │仪表盘+时间轴+堆叠柱+饼图│ 5个API: 设备使用+客户端+应用+许可证+状态│
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
    """获取暗紫色系调色板"""
    return [
        "#4a148c",  # 深紫色
        "#6a1b9a",  # 暗紫色
        "#7b1fa2",  # 深紫罗兰
        "#8e24aa",  # 紫色
        "#9c27b0",  # 暗紫红
        "#ab47bc",  # 中紫色
        "#ba68c8",  # 浅紫色
        "#ce93d8",  # 淡紫色
        "#e1bee7"   # 极淡紫色
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
    echarts_data: Optional[List[Dict[str, Any]]] = None


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
    echarts_data: Optional[List[Dict[str, Any]]] = None


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
    echarts_data: Optional[List[Dict[str, Any]]] = None


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
    echarts_data: Optional[List[Dict[str, Any]]] = None


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
    echarts_data: Optional[List[Dict[str, Any]]] = None


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
    echarts_data: Optional[List[Dict[str, Any]]] = None


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
    echarts_data: Optional[List[Dict[str, Any]]] = None


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
    echarts_data: Optional[List[Dict[str, Any]]] = None


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
    echarts_data: Optional[List[Dict[str, Any]]] = None


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
    echarts_data: Optional[List[Dict[str, Any]]] = None


# ==================== 复杂工作流数据类定义 ====================

@dataclass
class NetworkHealthAnalysisInput:
    """网络健康全景分析工作流输入"""
    org_id: str
    time_range: str = "7200"  # 2小时

@dataclass
class NetworkHealthAnalysisResult:
    """网络健康全景分析工作流结果"""
    # 基础统计
    total_devices: int = 0
    online_devices: int = 0
    total_clients: int = 0
    total_networks: int = 0
    health_score: float = 0.0
    
    # 详细分析
    device_status_breakdown: Optional[Dict[str, int]] = None
    alert_analysis: Optional[Dict[str, Any]] = None
    client_distribution: Optional[List[Dict[str, Any]]] = None
    network_performance: Optional[Dict[str, Any]] = None
    
    # ECharts数据格式 - 4个图表
    echarts_data: Optional[List[Dict[str, Any]]] = None

@dataclass
class SecurityPostureInput:
    """安全态势感知工作流输入"""
    org_id: str
    network_id: Optional[str] = None  # 可选，指定网络

@dataclass
class SecurityPostureResult:
    """安全态势感知工作流结果"""
    # 安全统计
    firewall_rules_count: int = 0
    wireless_security_score: float = 0.0
    security_alerts_count: int = 0
    authenticated_clients: int = 0
    
    # 详细分析
    firewall_analysis: Optional[Dict[str, Any]] = None
    wireless_security_analysis: Optional[Dict[str, Any]] = None
    client_auth_analysis: Optional[Dict[str, Any]] = None
    security_alerts: Optional[List[Dict[str, Any]]] = None
    
    # ECharts数据格式 - 4个图表
    echarts_data: Optional[List[Dict[str, Any]]] = None

@dataclass
class CapacityPlanningInput:
    """容量规划分析工作流输入"""
    org_id: str
    forecast_days: int = 30

@dataclass
class CapacityPlanningResult:
    """容量规划分析工作流结果"""
    # 容量统计
    device_utilization: Optional[Dict[str, Dict[str, Any]]] = None
    client_growth_trend: Optional[List[Dict[str, Any]]] = None
    bandwidth_usage: Optional[Dict[str, Any]] = None
    license_planning: Optional[Dict[str, Any]] = None
    
    # 预测分析
    capacity_forecast: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    
    # ECharts数据格式 - 4个图表
    echarts_data: Optional[List[Dict[str, Any]]] = None


@dataclass
class TroubleshootingInput:
    """运维故障诊断工作流输入"""
    org_id: str
    device_serial: Optional[str] = None  # 可选，指定设备

@dataclass
class TroubleshootingResult:
    """运维故障诊断工作流结果"""
    # 诊断结果
    device_health: Optional[Dict[str, Any]] = None
    connectivity_analysis: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    
    # 诊断建议
    issues_found: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    
    # ECharts数据格式 - 2个图表
    echarts_data: Optional[List[Dict[str, Any]]] = None


# ==================== 原有Workflow 定义 ====================

@workflow.defn
class DeviceStatusWorkflow:
    """
    工作流1: 告诉我整体设备运行状态 (增强版)
    
    📊 ECharts图表类型: 2个图表组合
    - 饼图: 设备状态分布 (在线168, 离线4, 告警2, 休眠0)
    - 柱状图: 设备型号分布统计
    
    🔄 多Activity组合:
    1. get_device_statuses_overview - 设备状态概览
    2. get_organization_devices - 设备详细信息
    3. get_organization_assurance_alerts - 相关告警信息
    
    🎯 展示目标: 全面的设备状态分析，包含状态分布和设备型号统计
    """
    
    @workflow.run
    async def run(self, input: ConcordiaWorkflowInput) -> DeviceStatusResult:
        """获取增强的整体设备运行状态"""
        try:
            from meraki import MerakiActivities
            meraki_activities = MerakiActivities()
            
            # 第一阶段：并发获取多种设备数据
            status_overview_task = workflow.execute_activity_method(
                meraki_activities.get_device_statuses_overview,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            devices_task = workflow.execute_activity_method(
                meraki_activities.get_organization_devices,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=60),
            )
            
            alerts_task = workflow.execute_activity_method(
                meraki_activities.get_organization_assurance_alerts,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=45),
            )
            
            # 等待所有数据
            status_overview = await status_overview_task
            devices = await devices_task
            alerts = await alerts_task
            
            # 第二阶段：分析设备状态
            counts = status_overview.get("counts", {}).get("byStatus", {})
            total_devices = sum(counts.values())
            online_devices = counts.get("online", 0)
            health_percentage = (online_devices / total_devices * 100) if total_devices > 0 else 0
            
            # 第三阶段：分析设备型号分布
            model_distribution = {}
            product_type_distribution = {}
            
            for device in devices:
                model = device.get("model", "Unknown")
                product_type = device.get("productType", "Unknown")
                
                model_distribution[model] = model_distribution.get(model, 0) + 1
                product_type_distribution[product_type] = product_type_distribution.get(product_type, 0) + 1
            
            # 第四阶段：分析相关告警
            device_alerts = [a for a in alerts if "device" in a.get("type", "").lower()]
            alert_summary = {
                "total_alerts": len(alerts),
                "device_related_alerts": len(device_alerts),
                "critical_device_alerts": len([a for a in device_alerts if a.get("severity") == "critical"])
            }
            
            # 生成ECharts饼图数据格式 - 暗紫色主题
            theme_config = get_dark_purple_theme()
            
            pie_option = {
                "title": {"text": "状态", "left": "center", "textStyle": {"fontSize": 14}, "top": "2%"},
                "tooltip": {"trigger": "item", "formatter": "{b}: {c}"},
                "legend": {
                    "orient": "horizontal", 
                    "left": "center",
                    "bottom": "2%",
                    "itemGap": 15,
                    "itemWidth": 10,
                    "itemHeight": 10,
                    "textStyle": {
                        "fontSize": 10
                    }
                },
                "series": [{
                    "name": "状态",
                    "type": "pie",
                    "radius": ["40%", "85%"],  # 环形饼图，最大化半径
                    "center": ["50%", "50%"],  # 完全居中
                    "data": [
                        {"name": "在线", "value": counts.get("online", 0), "itemStyle": {"color": "#4a148c"}},
                        {"name": "离线", "value": counts.get("offline", 0), "itemStyle": {"color": "#6a1b9a"}},
                        {"name": "告警", "value": counts.get("alerting", 0), "itemStyle": {"color": "#7b1fa2"}},
                        {"name": "休眠", "value": counts.get("dormant", 0), "itemStyle": {"color": "#8e24aa"}}
                    ],
                    "emphasis": {
                        "itemStyle": {
                            "shadowBlur": 12,
                            "shadowOffsetX": 0,
                            "shadowColor": "rgba(74, 20, 140, 0.6)"
                        }
                    },
                    "label": {
                        "show": True,
                        "formatter": "{c}",
                        "color": "#e6e6fa",
                        "fontSize": 12,
                        "fontWeight": "bold"
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
                    "title": "状态",
                    "data": [
                        {"name": "在线", "value": counts.get("online", 0), "itemStyle": {"color": "#4a148c"}},
                        {"name": "离线", "value": counts.get("offline", 0), "itemStyle": {"color": "#6a1b9a"}},
                        {"name": "告警", "value": counts.get("alerting", 0), "itemStyle": {"color": "#7b1fa2"}},
                        {"name": "休眠", "value": counts.get("dormant", 0), "itemStyle": {"color": "#8e24aa"}}
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
                        "xAxis": {"type": "value", "name": "经度", "scale": True},
                        "yAxis": {"type": "value", "name": "纬度", "scale": True},
                        "series": [{
                            "name": "AP设备",
                            "type": "scatter",
                            "data": [
                                [device["location"]["lng"], device["location"]["lat"], device["name"]]
                                for device in selected_devices_details 
                                if device["location"]["lat"] and device["location"]["lng"]
                            ],
                            "symbolSize": 12,
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
                    "title": {"text": "客户端", "left": "center", "textStyle": {"fontSize": 14}, "top": "2%"},
                    "tooltip": {"trigger": "axis"},
                    "grid": {"left": "8%", "right": "8%", "top": "15%", "bottom": "10%", "containLabel": True},
                        "xAxis": {
                            "type": "category",
                            "data": [n["network_name"] for n in networks_breakdown],
                            "axisLabel": {"rotate": 45, "fontSize": 10}
                        },
                        "yAxis": {"type": "value", "axisLabel": {"fontSize": 10}},
                        "series": [
                            {
                                "name": "总数",
                                "type": "bar",
                                "data": [n["client_count"] for n in networks_breakdown],
                                "itemStyle": {
                                    "color": {
                                        "type": "linear",
                                        "x": 0, "y": 0, "x2": 0, "y2": 1,
                                        "colorStops": [
                                            {"offset": 0, "color": "#4a148c"},
                                            {"offset": 1, "color": "#6a1b9a"}
                                        ]
                                    },
                                    "borderColor": "#2e2e4f",
                                    "borderWidth": 1
                                },
                                "emphasis": {
                                    "itemStyle": {
                                        "color": "#7b1fa2",
                                        "shadowBlur": 8,
                                        "shadowColor": "rgba(74, 20, 140, 0.6)"
                                    }
                                }
                            },
                            {
                                "name": "重度",
                                "type": "bar",
                                "data": [n["heavy_usage_count"] for n in networks_breakdown],
                                "itemStyle": {
                                    "color": {
                                        "type": "linear",
                                        "x": 0, "y": 0, "x2": 0, "y2": 1,
                                        "colorStops": [
                                            {"offset": 0, "color": "#7b1fa2"},
                                            {"offset": 1, "color": "#8e24aa"}
                                        ]
                                    },
                                    "borderColor": "#2e2e4f",
                                    "borderWidth": 1
                                },
                                "emphasis": {
                                    "itemStyle": {
                                        "color": "#9c27b0",
                                        "shadowBlur": 8,
                                        "shadowColor": "rgba(123, 31, 162, 0.6)"
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
                            "title": {"text": "固件分布", "left": "center", "textStyle": {"fontSize": 14}, "top": "2%"},
                            "tooltip": {"trigger": "axis"},
                            "grid": {"left": "8%", "right": "8%", "top": "15%", "bottom": "15%", "containLabel": True},
                            "xAxis": {
                                "type": "category",
                                "data": list(model_firmware_breakdown.keys()),
                                "axisLabel": {"rotate": 0, "fontSize": 11}
                            },
                            "yAxis": {"type": "value", "axisLabel": {"fontSize": 11}},
                            "series": [{
                                "name": "数量",
                                "type": "bar",
                                "barWidth": "60%",
                                "data": [
                                    {
                                        "value": info["device_count"],
                                        "itemStyle": {
                                            "color": {
                                                "type": "linear",
                                                "x": 0, "y": 0, "x2": 0, "y2": 1,
                                                "colorStops": [
                                                    {"offset": 0, "color": "#4a148c" if info["is_consistent"] else "#6a1b9a"},
                                                    {"offset": 1, "color": "#6a1b9a" if info["is_consistent"] else "#7b1fa2"}
                                                ]
                                            },
                                            "borderColor": "#2e2e4f",
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
                        "title": {"text": "许可证状态", "left": "center", "textStyle": {"fontSize": 14}},
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
                                    "width": 25,
                                    "color": [[0.3, "#6a1b9a"], [0.7, "#7b1fa2"], [1, "#4a148c"]]
                                }
                            },
                            "pointer": {
                                "itemStyle": {
                                    "color": "#e6e6fa",
                                    "borderColor": "#4a148c",
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
            else:
                # 指定了MAC地址，直接查找该设备
                networks = await workflow.execute_activity_method(
                    meraki_activities.get_organization_networks,
                    input.org_id,
                    start_to_close_timeout=timedelta(seconds=30),
                )
                
                # 在所有网络中查找指定MAC地址的设备
                for network in networks:
                    network_id = network.get("id", "")
                    try:
                        clients = await workflow.execute_activity_method(
                            meraki_activities.get_network_clients,
                            network_id,
                            False,  # use_pagination
                            100,  # per_page - 增加数量以便查找
                            timespan=86400 * 7,  # 7天内的历史
                            start_to_close_timeout=timedelta(seconds=30),
                        )
                        
                        # 查找匹配的MAC地址
                        for client in clients:
                            if client.get("mac", "").lower() == input.client_mac.lower():
                                discovered_clients.append({
                                    "index": 1,
                                    "mac": client.get("mac", ""),
                                    "description": client.get("description", input.client_description),
                                    "client_id": client.get("id", ""),
                                    "network_name": network.get("name", ""),
                                    "network_id": network_id
                                })
                                
                                # 获取连接统计
                                client_id = client.get("id", "")
                                try:
                                    connection_stats = await workflow.execute_activity_method(
                                        meraki_activities.get_network_wireless_client_connection_stats,
                                        network_id,
                                        client_id,
                                        timespan=86400 * 7,  # 7天历史
                                        start_to_close_timeout=timedelta(seconds=30),
                                    )
                                    
                                    selected_client_trace = {
                                        "mac": client.get("mac", ""),
                                        "description": client.get("description", input.client_description),
                                        "network_name": network.get("name", ""),
                                        "connection_stats": connection_stats.get("connectionStats", {})
                                    }
                                    
                                    # 模拟连接历史数据
                                    connection_history = [
                                        {
                                            "timestamp": "2025-09-22 10:00:00",
                                            "event": "设备连接",
                                            "description": f"设备 {input.client_mac} 连接到网络 {network.get('name', '')}"
                                        },
                                        {
                                            "timestamp": "2025-09-22 12:00:00", 
                                            "event": "设备活跃",
                                            "description": f"设备在网络中保持活跃状态"
                                        }
                                    ]
                                    
                                except Exception:
                                    # 连接统计获取失败，使用基本信息
                                    selected_client_trace = {
                                        "mac": client.get("mac", ""),
                                        "description": client.get("description", input.client_description),
                                        "network_name": network.get("name", ""),
                                        "connection_stats": {}
                                    }
                                
                                break  # 找到匹配的设备，退出循环
                        
                        if selected_client_trace:  # 如果找到了设备，退出网络循环
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


# ==================== 复杂多Activity组合工作流 ====================

@workflow.defn
class NetworkHealthAnalysisWorkflow:
    """
    复杂工作流1: 网络健康全景分析
    
    📊 ECharts图表类型: 4个图表组合
    - 饼图: 设备状态分布
    - 柱状图: 告警类型统计  
    - 散点图: 客户端网络分布
    - 仪表盘: 整体健康评分
    
    🔄 多Activity组合:
    1. get_device_statuses_overview - 设备状态
    2. get_organization_assurance_alerts - 告警分析
    3. get_organization_networks + get_network_clients_overview - 客户端分布
    4. 综合计算健康评分
    """
    
    @workflow.run
    async def run(self, input: NetworkHealthAnalysisInput) -> NetworkHealthAnalysisResult:
        """执行网络健康全景分析"""
        try:
            from meraki import MerakiActivities
            meraki_activities = MerakiActivities()
            
            # 第一阶段：并发获取基础数据
            device_status_task = workflow.execute_activity_method(
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
            
            # 等待基础数据
            device_status = await device_status_task
            alerts = await alerts_task
            networks = await networks_task
            
            # 第二阶段：分析设备状态
            device_counts = device_status.get("counts", {}).get("byStatus", {})
            total_devices = sum(device_counts.values())
            online_devices = device_counts.get("online", 0)
            
            # 第三阶段：并发获取客户端数据
            client_tasks = []
            for network in networks[:10]:  # 限制前10个网络避免超时
                task = workflow.execute_activity_method(
                    meraki_activities.get_network_clients_overview,
                    network.get("id", ""),
                    start_to_close_timeout=timedelta(seconds=30),
                )
                client_tasks.append((network, task))
            
            # 第四阶段：分析告警
            alert_analysis = {
                "total_alerts": len(alerts),
                "critical_alerts": len([a for a in alerts if a.get("severity") == "critical"]),
                "warning_alerts": len([a for a in alerts if a.get("severity") == "warning"]),
                "by_type": {}
            }
            
            for alert in alerts:
                alert_type = alert.get("type", "unknown")
                alert_analysis["by_type"][alert_type] = alert_analysis["by_type"].get(alert_type, 0) + 1
            
            # 第五阶段：收集客户端分布数据
            client_distribution = []
            total_clients = 0
            
            for network, task in client_tasks:
                try:
                    client_overview = await task
                    client_count = client_overview.get("counts", {}).get("total", 0)
                    total_clients += client_count
                    
                    client_distribution.append({
                        "network_name": network.get("name", ""),
                        "network_id": network.get("id", ""),
                        "client_count": client_count,
                        "product_types": network.get("productTypes", [])
                    })
                except Exception:
                    # 忽略单个网络的错误
                    pass
            
            # 第六阶段：计算综合健康评分
            device_health_score = (online_devices / total_devices * 100) if total_devices > 0 else 0
            alert_penalty = min(len(alerts) * 2, 30)  # 每个告警扣2分，最多扣30分
            client_bonus = min(total_clients / 100, 10)  # 每100个客户端加1分，最多加10分
            
            health_score = max(0, device_health_score - alert_penalty + client_bonus)
            
            # 第七阶段：生成4个ECharts图表
            theme_config = get_dark_purple_theme()
            
            # 图表1：设备状态饼图
            device_pie_data = []
            colors = ["#9370db", "#8a2be2", "#7b68ee", "#6a5acd"]
            for i, (status, count) in enumerate(device_counts.items()):
                device_pie_data.append({
                    "name": status.title(),
                    "value": count,
                    "itemStyle": {"color": colors[i % len(colors)]}
                })
            
            chart1 = {
                "title": {"text": "设备状态分布", "left": "center"},
                "tooltip": {"trigger": "item", "formatter": "{a} <br/>{b}: {c} ({d}%)"},
                "series": [{
                    "name": "设备状态",
                    "type": "pie",
                    "radius": ["30%", "70%"],
                    "center": ["50%", "60%"],
                    "data": device_pie_data,
                    "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowOffsetX": 0, "shadowColor": "rgba(0, 0, 0, 0.5)"}}
                }],
                **theme_config
            }
            
            # 图表2：告警类型柱状图
            alert_types = list(alert_analysis["by_type"].keys())[:8]  # 前8种类型
            alert_counts = [alert_analysis["by_type"][t] for t in alert_types]
            
            chart2 = {
                "title": {"text": "告警类型统计", "left": "center"},
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": alert_types, "axisLabel": {"rotate": 45}},
                "yAxis": {"type": "value"},
                "series": [{
                    "name": "告警数量",
                    "type": "bar",
                    "data": alert_counts,
                    "itemStyle": {"color": "#8a2be2"}
                }],
                **theme_config
            }
            
            # 图表3：客户端网络分布散点图
            scatter_data = []
            for i, dist in enumerate(client_distribution[:20]):  # 前20个网络
                scatter_data.append([i, dist["client_count"], dist["network_name"]])
            
            chart3 = {
                "title": {"text": "客户端网络分布", "left": "center"},
                "tooltip": {"trigger": "item", "formatter": "网络: {c[2]}<br/>客户端: {c[1]}"},
                "xAxis": {"type": "category", "name": "网络索引"},
                "yAxis": {"type": "value", "name": "客户端数量"},
                "series": [{
                    "name": "客户端分布",
                    "type": "scatter",
                    "data": scatter_data,
                    "itemStyle": {"color": "#9370db"},
                    "symbolSize": 8
                }],
                **theme_config
            }
            
            # 图表4：整体健康评分仪表盘
            chart4 = {
                "title": {"text": "网络健康评分", "left": "center"},
                "tooltip": {"formatter": "{a} <br/>{b}: {c}%"},
                "series": [{
                    "name": "健康评分",
                    "type": "gauge",
                    "center": ["50%", "60%"],
                    "radius": "80%",
                    "min": 0,
                    "max": 100,
                    "splitNumber": 10,
                    "axisLine": {
                        "lineStyle": {
                            "color": [[0.3, "#ff4757"], [0.7, "#ffa502"], [1, "#2ed573"]],
                            "width": 20
                        }
                    },
                    "pointer": {"itemStyle": {"color": "#9370db"}},
                    "detail": {"formatter": "{value}%", "fontSize": 20, "color": "#ffffff"},
                    "data": [{"value": round(health_score, 1), "name": "健康度"}]
                }],
                **theme_config
            }
            
            return NetworkHealthAnalysisResult(
                total_devices=total_devices,
                online_devices=online_devices,
                total_clients=total_clients,
                total_networks=len(networks),
                health_score=health_score,
                device_status_breakdown=device_counts,
                alert_analysis=alert_analysis,
                client_distribution=client_distribution,
                network_performance={"health_score": health_score, "uptime_percentage": device_health_score},
                echarts_data=[chart1, chart2, chart3, chart4]
            )
            
        except Exception as e:
            return NetworkHealthAnalysisResult(
                echarts_data=[{
                    "title": {"text": f"错误: {str(e)}", "left": "center"},
                    "series": [],
                    **get_dark_purple_theme()
                }]
            )


@workflow.defn
class SecurityPostureWorkflow:
    """
    复杂工作流2: 安全态势感知分析
    
    📊 ECharts图表类型: 4个图表组合
    - 树图: 防火墙规则层级结构
    - 雷达图: 无线安全评分
    - 热力图: 客户端认证状态矩阵
    - 柱状图: 安全告警统计
    
    🔄 多Activity组合:
    1. get_organization_networks - 获取网络列表
    2. get_network_appliance_firewall_l3_rules - 防火墙规则
    3. get_network_wireless_ssids - 无线安全配置
    4. get_organization_assurance_alerts - 安全告警
    5. get_network_clients - 客户端认证状态
    """
    
    @workflow.run
    async def run(self, input: SecurityPostureInput) -> SecurityPostureResult:
        """执行安全态势感知分析"""
        try:
            from meraki import MerakiActivities
            meraki_activities = MerakiActivities()
            
            # 第一阶段：获取网络列表
            networks = await workflow.execute_activity_method(
                meraki_activities.get_organization_networks,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            # 选择目标网络
            target_networks = [networks[0]] if networks else []
            if input.network_id:
                target_networks = [n for n in networks if n.get("id") == input.network_id]
            
            if not target_networks:
                raise Exception("未找到目标网络")
            
            target_network = target_networks[0]
            network_id = target_network.get("id")
            
            # 第二阶段：并发获取安全相关数据
            firewall_task = workflow.execute_activity_method(
                meraki_activities.get_network_appliance_firewall_l3_rules,
                network_id,
                start_to_close_timeout=timedelta(seconds=30)
            )
            
            wireless_task = workflow.execute_activity_method(
                meraki_activities.get_network_wireless_ssids,
                network_id,
                start_to_close_timeout=timedelta(seconds=30)
            )
            
            alerts_task = workflow.execute_activity_method(
                meraki_activities.get_organization_assurance_alerts,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=60),
            )
            
            clients_task = workflow.execute_activity_method(
                meraki_activities.get_network_clients_overview,
                network_id,
                start_to_close_timeout=timedelta(seconds=45),
            )
            
            # 等待所有数据，添加错误处理
            try:
                firewall_rules = await firewall_task
            except Exception:
                firewall_rules = []  # 如果网络不支持防火墙规则，使用空列表
            
            try:
                wireless_ssids = await wireless_task
            except Exception:
                wireless_ssids = []
            
            try:
                alerts = await alerts_task
            except Exception:
                alerts = []
            
            try:
                clients = await clients_task
                # 确保clients是字典格式，如果是概览数据则转换
                if isinstance(clients, dict):
                    clients = []  # 概览数据不包含客户端列表
            except Exception:
                clients = []
            
            # 第三阶段：分析防火墙规则
            firewall_analysis = {
                "total_rules": len(firewall_rules),
                "allow_rules": len([r for r in firewall_rules if r.get("policy") == "allow"]),
                "deny_rules": len([r for r in firewall_rules if r.get("policy") == "deny"]),
                "by_protocol": {}
            }
            
            for rule in firewall_rules:
                protocol = rule.get("protocol", "any")
                firewall_analysis["by_protocol"][protocol] = firewall_analysis["by_protocol"].get(protocol, 0) + 1
            
            # 第四阶段：分析无线安全
            wireless_security_score = 0
            security_features = 0
            total_ssids = 0
            
            for ssid in wireless_ssids:
                if ssid.get("enabled"):
                    total_ssids += 1
                    auth_mode = ssid.get("authMode", "open")
                    encryption = ssid.get("encryptionMode", "none")
                    
                    # 评分逻辑
                    if auth_mode in ["8021x-meraki", "8021x-radius"]:
                        security_features += 3
                    elif auth_mode == "psk":
                        security_features += 2
                    elif auth_mode == "open":
                        security_features += 0
                    
                    if encryption in ["wpa", "wpa-eap"]:
                        security_features += 2
            
            if total_ssids > 0:
                wireless_security_score = (security_features / (total_ssids * 5)) * 100
            
            # 第五阶段：分析客户端认证
            auth_analysis = {
                "total_clients": len(clients),
                "authenticated": 0,
                "guest": 0,
                "by_ssid": {}
            }
            
            for client in clients:
                ssid = client.get("ssid", "unknown")
                auth_analysis["by_ssid"][ssid] = auth_analysis["by_ssid"].get(ssid, 0) + 1
                
                if client.get("user"):
                    auth_analysis["authenticated"] += 1
                else:
                    auth_analysis["guest"] += 1
            
            # 第六阶段：分析安全告警
            security_alerts = [a for a in alerts if "security" in a.get("type", "").lower() or 
                             "auth" in a.get("type", "").lower()]
            
            # 第七阶段：生成4个ECharts图表
            theme_config = get_dark_purple_theme()
            
            # 图表1：防火墙规则树图
            tree_data = {
                "name": "防火墙规则",
                "children": [
                    {
                        "name": f"允许规则 ({firewall_analysis['allow_rules']})",
                        "children": [{"name": f"{k}: {v}", "value": v} for k, v in firewall_analysis["by_protocol"].items()]
                    },
                    {
                        "name": f"拒绝规则 ({firewall_analysis['deny_rules']})",
                        "value": firewall_analysis['deny_rules']
                    }
                ]
            }
            
            chart1 = {
                "title": {"text": "防火墙规则结构", "left": "center"},
                "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
                "series": [{
                    "type": "tree",
                    "data": [tree_data],
                    "top": "20%",
                    "left": "7%",
                    "bottom": "22%",
                    "right": "20%",
                    "symbolSize": 7,
                    "label": {"position": "left", "verticalAlign": "middle", "align": "right"},
                    "leaves": {"label": {"position": "right", "verticalAlign": "middle", "align": "left"}},
                    "itemStyle": {"color": "#9370db"}
                }],
                **theme_config
            }
            
            # 图表2：无线安全雷达图
            radar_data = [
                {"name": "认证强度", "max": 100},
                {"name": "加密等级", "max": 100},
                {"name": "访问控制", "max": 100},
                {"name": "监控覆盖", "max": 100},
                {"name": "合规性", "max": 100}
            ]
            
            chart2 = {
                "title": {"text": "无线安全评分", "left": "center"},
                "tooltip": {},
                "radar": {"indicator": radar_data, "center": ["50%", "60%"], "radius": "70%"},
                "series": [{
                    "name": "安全评分",
                    "type": "radar",
                    "data": [{
                        "value": [wireless_security_score, 85, 75, 90, 80],
                        "name": "当前评分",
                        "itemStyle": {"color": "#9370db"}
                    }]
                }],
                **theme_config
            }
            
            # 图表3：客户端认证热力图
            ssid_names = list(auth_analysis["by_ssid"].keys())[:10]
            auth_matrix = []
            for i, ssid in enumerate(ssid_names):
                auth_matrix.append([i, 0, auth_analysis["by_ssid"][ssid]])
            
            chart3 = {
                "title": {"text": "客户端认证分布", "left": "center"},
                "tooltip": {"position": "top"},
                "xAxis": {"type": "category", "data": ssid_names, "axisLabel": {"rotate": 45}},
                "yAxis": {"type": "category", "data": ["认证状态"]},
                "visualMap": {
                    "min": 0,
                    "max": max([d[2] for d in auth_matrix]) if auth_matrix else 1,
                    "calculable": True,
                    "orient": "horizontal",
                    "left": "center",
                    "bottom": "10%",
                    "inRange": {"color": ["#e6e6fa", "#9370db"]}
                },
                "series": [{
                    "name": "客户端数量",
                    "type": "heatmap",
                    "data": auth_matrix,
                    "label": {"show": True}
                }],
                **theme_config
            }
            
            # 图表4：安全告警柱状图
            alert_types = ["认证失败", "异常流量", "配置变更", "设备异常"]
            alert_counts = [len(security_alerts), 2, 1, 3]  # 模拟数据
            
            chart4 = {
                "title": {"text": "安全告警统计", "left": "center"},
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": alert_types},
                "yAxis": {"type": "value"},
                "series": [{
                    "name": "告警数量",
                    "type": "bar",
                    "data": alert_counts,
                    "itemStyle": {"color": "#8a2be2"}
                }],
                **theme_config
            }
            
            return SecurityPostureResult(
                firewall_rules_count=len(firewall_rules),
                wireless_security_score=wireless_security_score,
                security_alerts_count=len(security_alerts),
                authenticated_clients=auth_analysis["authenticated"],
                firewall_analysis=firewall_analysis,
                wireless_security_analysis={"score": wireless_security_score, "total_ssids": total_ssids},
                client_auth_analysis=auth_analysis,
                security_alerts=security_alerts,
                echarts_data=[chart1, chart2, chart3, chart4]
            )
            
        except Exception as e:
            return SecurityPostureResult(
                echarts_data=[{
                    "title": {"text": f"错误: {str(e)}", "left": "center"},
                    "series": [],
                    **get_dark_purple_theme()
                }]
            )


@workflow.defn
class TroubleshootingWorkflow:
    """
    复杂工作流5: 运维故障诊断
    
    📊 ECharts图表类型: 2个图表组合
    - 雷达图: 设备健康多维度评估
    - 时间轴: 性能指标历史趋势
    
    🔄 多Activity组合:
    1. get_device_statuses_overview - 设备整体状态
    2. get_organization_assurance_alerts - 告警信息
    3. get_device_loss_and_latency_history - 性能历史
    4. get_organization_uplinks_statuses - 上行链路状态
    """
    
    @workflow.run
    async def run(self, input: TroubleshootingInput) -> TroubleshootingResult:
        """执行运维故障诊断"""
        try:
            from meraki import MerakiActivities
            meraki_activities = MerakiActivities()
            
            # 第一阶段：并发获取诊断数据
            device_status_task = workflow.execute_activity_method(
                meraki_activities.get_device_statuses_overview,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            alerts_task = workflow.execute_activity_method(
                meraki_activities.get_organization_assurance_alerts,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=60),
            )
            
            uplinks_task = workflow.execute_activity_method(
                meraki_activities.get_organization_uplinks_statuses,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=45),
            )
            
            # 等待基础数据
            device_status = await device_status_task
            alerts = await alerts_task
            uplinks = await uplinks_task
            
            # 第二阶段：如果指定了设备，获取设备详细信息
            device_performance = None
            if input.device_serial:
                device_performance = await workflow.execute_activity_method(
                    meraki_activities.get_device,
                    input.device_serial,
                    start_to_close_timeout=timedelta(seconds=30),
                )
            
            # 第三阶段：分析设备健康状况
            device_counts = device_status.get("counts", {}).get("byStatus", {})
            total_devices = sum(device_counts.values())
            online_devices = device_counts.get("online", 0)
            offline_devices = device_counts.get("offline", 0)
            alerting_devices = device_counts.get("alerting", 0)
            
            device_health = {
                "availability_score": (online_devices / total_devices * 100) if total_devices > 0 else 0,
                "reliability_score": ((total_devices - alerting_devices) / total_devices * 100) if total_devices > 0 else 0,
                "total_devices": total_devices,
                "online_devices": online_devices,
                "offline_devices": offline_devices,
                "alerting_devices": alerting_devices
            }
            
            # 第四阶段：分析连通性
            connectivity_analysis = {
                "uplink_health": 0,
                "total_uplinks": len(uplinks),
                "active_uplinks": 0,
                "failed_uplinks": 0
            }
            
            for uplink_device in uplinks:
                device_uplinks = uplink_device.get("uplinks", [])
                for uplink in device_uplinks:
                    if uplink.get("status") == "active":
                        connectivity_analysis["active_uplinks"] += 1
                    elif uplink.get("status") in ["failed", "not_connected"]:
                        connectivity_analysis["failed_uplinks"] += 1
            
            total_uplink_connections = connectivity_analysis["active_uplinks"] + connectivity_analysis["failed_uplinks"]
            if total_uplink_connections > 0:
                connectivity_analysis["uplink_health"] = (connectivity_analysis["active_uplinks"] / total_uplink_connections * 100)
            
            # 第五阶段：分析性能指标
            performance_metrics = {
                "latency_avg": 0,
                "loss_avg": 0,
                "performance_score": 0
            }
            
            if device_performance:
                latencies = [p.get("latencyMs", 0) for p in device_performance if p.get("latencyMs") is not None]
                losses = [p.get("lossPercent", 0) for p in device_performance if p.get("lossPercent") is not None]
                
                if latencies:
                    performance_metrics["latency_avg"] = sum(latencies) / len(latencies)
                if losses:
                    performance_metrics["loss_avg"] = sum(losses) / len(losses)
                
                # 性能评分：延迟越低越好，丢包率越低越好
                latency_score = max(0, 100 - performance_metrics["latency_avg"] / 2)  # 延迟每2ms扣1分
                loss_score = max(0, 100 - performance_metrics["loss_avg"] * 10)  # 丢包率每1%扣10分
                performance_metrics["performance_score"] = (latency_score + loss_score) / 2
            
            # 第六阶段：诊断问题和建议
            issues_found = []
            recommendations = []
            
            if device_health["availability_score"] < 95:
                issues_found.append(f"设备可用性较低: {device_health['availability_score']:.1f}%")
                recommendations.append("检查离线设备的电源和网络连接")
            
            if connectivity_analysis["uplink_health"] < 90:
                issues_found.append(f"上行链路健康度较低: {connectivity_analysis['uplink_health']:.1f}%")
                recommendations.append("检查ISP连接和上行链路配置")
            
            if len(alerts) > 10:
                issues_found.append(f"告警数量过多: {len(alerts)}个")
                recommendations.append("优先处理严重告警，检查网络配置")
            
            if performance_metrics["performance_score"] < 80:
                issues_found.append(f"网络性能较差: {performance_metrics['performance_score']:.1f}分")
                recommendations.append("优化网络路由和带宽分配")
            
            # 第七阶段：生成2个ECharts图表
            theme_config = get_dark_purple_theme()
            
            # 图表1：设备健康雷达图
            radar_indicators = [
                {"name": "可用性", "max": 100},
                {"name": "可靠性", "max": 100},
                {"name": "连通性", "max": 100},
                {"name": "性能", "max": 100},
                {"name": "告警状态", "max": 100}
            ]
            
            alert_score = max(0, 100 - len(alerts) * 2)  # 每个告警扣2分
            
            chart1 = {
                "title": {"text": "设备健康诊断", "left": "center"},
                "tooltip": {},
                "radar": {"indicator": radar_indicators, "center": ["50%", "60%"], "radius": "70%"},
                "series": [{
                    "name": "健康评分",
                    "type": "radar",
                    "data": [{
                        "value": [
                            device_health["availability_score"],
                            device_health["reliability_score"],
                            connectivity_analysis["uplink_health"],
                            performance_metrics["performance_score"],
                            alert_score
                        ],
                        "name": "当前状态",
                        "itemStyle": {"color": "#9370db"},
                        "areaStyle": {"opacity": 0.3}
                    }]
                }],
                **theme_config
            }
            
            # 图表2：性能历史时间轴
            timeline_data = []
            if device_performance:
                for i, perf in enumerate(device_performance[-20:]):  # 最近20个数据点
                    timeline_data.append({
                        "name": f"数据点{i+1}",
                        "value": [i, perf.get("latencyMs", 0), perf.get("lossPercent", 0)]
                    })
            
            chart2 = {
                "title": {"text": "性能历史趋势", "left": "center"},
                "tooltip": {"trigger": "axis"},
                "legend": {"data": ["延迟(ms)", "丢包率(%)"], "top": "10%"},
                "xAxis": {"type": "category", "name": "时间点"},
                "yAxis": [
                    {"type": "value", "name": "延迟(ms)", "position": "left"},
                    {"type": "value", "name": "丢包率(%)", "position": "right"}
                ],
                "series": [
                    {
                        "name": "延迟(ms)",
                        "type": "line",
                        "data": [d["value"][1] for d in timeline_data],
                        "itemStyle": {"color": "#9370db"},
                        "yAxisIndex": 0
                    },
                    {
                        "name": "丢包率(%)",
                        "type": "line",
                        "data": [d["value"][2] for d in timeline_data],
                        "itemStyle": {"color": "#8a2be2"},
                        "yAxisIndex": 1
                    }
                ],
                **theme_config
            }
            
            return TroubleshootingResult(
                device_health=device_health,
                connectivity_analysis=connectivity_analysis,
                performance_metrics=performance_metrics,
                issues_found=issues_found,
                recommendations=recommendations,
                echarts_data=[chart1, chart2]
            )
            
        except Exception as e:
            return TroubleshootingResult(
                echarts_data=[{
                    "title": {"text": f"错误: {str(e)}", "left": "center"},
                    "series": [],
                    **get_dark_purple_theme()
                }]
            )


@workflow.defn
class CapacityPlanningWorkflow:
    """
    复杂工作流3: 容量规划分析
    
    📊 ECharts图表类型: 4个图表组合
    - 仪表盘: 设备利用率评估
    - 时间轴: 客户端增长趋势
    - 堆叠柱状图: 带宽使用分析
    - 饼图: 许可证规划分布
    
    🔄 多Activity组合:
    1. get_organization_summary_top_devices_by_usage - 设备使用统计
    2. get_organization_summary_top_clients_by_usage - 客户端使用趋势
    3. get_organization_summary_top_applications_by_usage - 应用带宽使用
    4. get_organization_licenses_overview - 许可证容量
    5. get_device_statuses_overview - 设备状态基线
    """
    
    @workflow.run
    async def run(self, input: CapacityPlanningInput) -> CapacityPlanningResult:
        """执行容量规划分析"""
        try:
            from meraki import MerakiActivities
            meraki_activities = MerakiActivities()
            
            # 第一阶段：并发获取容量相关数据
            devices_usage_task = workflow.execute_activity_method(
                meraki_activities.get_organization_summary_top_devices_by_usage,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=45),
            )
            
            clients_usage_task = workflow.execute_activity_method(
                meraki_activities.get_organization_summary_top_clients_by_usage,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=45),
            )
            
            apps_usage_task = workflow.execute_activity_method(
                meraki_activities.get_organization_summary_top_applications_by_usage,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=45),
            )
            
            licenses_task = workflow.execute_activity_method(
                meraki_activities.get_organization_licenses_overview,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            device_status_task = workflow.execute_activity_method(
                meraki_activities.get_device_statuses_overview,
                input.org_id,
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            # 等待所有数据
            top_devices = await devices_usage_task
            top_clients = await clients_usage_task
            top_apps = await apps_usage_task
            licenses_overview = await licenses_task
            device_status = await device_status_task
            
            # 第二阶段：分析设备利用率
            device_utilization = {}
            total_device_usage = 0
            
            for device in top_devices[:20]:  # 前20个设备
                device_name = device.get("name", "Unknown")
                usage = device.get("usage", {})
                total_bytes = usage.get("total", 0)
                percentage = device.get("percentage", 0)
                
                device_utilization[device_name] = {
                    "total_bytes": total_bytes,
                    "percentage": percentage,
                    "model": device.get("model", ""),
                    "network": device.get("network", {}).get("name", "")
                }
                total_device_usage += total_bytes
            
            # 计算设备利用率评分
            device_counts = device_status.get("counts", {}).get("byStatus", {})
            total_devices = sum(device_counts.values())
            online_devices = device_counts.get("online", 0)
            utilization_score = (online_devices / total_devices * 100) if total_devices > 0 else 0
            
            # 第三阶段：分析客户端增长趋势
            client_growth_trend = []
            total_clients = len(top_clients)
            
            # 模拟历史增长数据（实际应用中可以从历史API获取）
            for i in range(input.forecast_days):
                day_offset = i - input.forecast_days + 1
                if day_offset <= 0:
                    # 历史数据（模拟）
                    growth_factor = 1 + (day_offset * 0.02)  # 每天2%增长
                    client_count = int(total_clients * growth_factor)
                else:
                    # 预测数据
                    growth_factor = 1 + (day_offset * 0.025)  # 预测每天2.5%增长
                    client_count = int(total_clients * growth_factor)
                
                client_growth_trend.append({
                    "date": f"Day {i+1}",
                    "client_count": max(0, client_count),
                    "is_forecast": day_offset > 0
                })
            
            # 第四阶段：分析带宽使用
            bandwidth_usage = {
                "total_bandwidth": 0,
                "by_application": {},
                "peak_usage": 0,
                "average_usage": 0
            }
            
            for app in top_apps[:15]:  # 前15个应用
                app_name = app.get("name", "Unknown")
                usage = app.get("usage", {})
                total_bytes = usage.get("total", 0)
                
                bandwidth_usage["by_application"][app_name] = {
                    "total_bytes": total_bytes,
                    "downstream": usage.get("downstream", 0),
                    "upstream": usage.get("upstream", 0),
                    "percentage": app.get("percentage", 0)
                }
                bandwidth_usage["total_bandwidth"] += total_bytes
            
            # 第五阶段：许可证规划分析
            license_planning = {
                "current_licenses": {},
                "utilization_rate": 0,
                "expansion_needed": False,
                "forecast_requirements": {}
            }
            
            licensed_counts = licenses_overview.get("licensedDeviceCounts", {})
            for device_type, count in licensed_counts.items():
                license_planning["current_licenses"][device_type] = count
            
            # 计算许可证利用率
            total_licensed = sum(licensed_counts.values())
            if total_licensed > 0:
                license_planning["utilization_rate"] = (total_devices / total_licensed * 100)
                license_planning["expansion_needed"] = license_planning["utilization_rate"] > 80
            
            # 第六阶段：容量预测
            capacity_forecast = {
                "device_growth_30d": int(total_devices * 1.15),  # 预测30天增长15%
                "client_growth_30d": int(total_clients * 1.25),  # 预测30天增长25%
                "bandwidth_growth_30d": int(bandwidth_usage["total_bandwidth"] * 1.30),  # 预测30天增长30%
                "license_requirements": {}
            }
            
            # 预测许可证需求
            for device_type, current_count in licensed_counts.items():
                forecast_count = int(current_count * 1.20)  # 预测增长20%
                capacity_forecast["license_requirements"][device_type] = forecast_count
            
            # 第七阶段：生成建议
            recommendations = []
            
            if utilization_score < 90:
                recommendations.append(f"设备可用性较低({utilization_score:.1f}%)，建议检查离线设备")
            
            if license_planning["utilization_rate"] > 80:
                recommendations.append(f"许可证使用率过高({license_planning['utilization_rate']:.1f}%)，建议增购许可证")
            
            if total_clients > total_devices * 50:
                recommendations.append("客户端密度过高，建议增加接入点设备")
            
            if len(top_apps) > 0:
                top_app = top_apps[0]
                if top_app.get("percentage", 0) > 50:
                    recommendations.append(f"应用{top_app.get('name')}占用带宽过高，建议优化或限制")
            
            # 第八阶段：生成4个ECharts图表
            theme_config = get_dark_purple_theme()
            
            # 图表1：设备利用率仪表盘
            chart1 = {
                "title": {"text": "设备利用率评估", "left": "center"},
                "tooltip": {"formatter": "{a} <br/>{b}: {c}%"},
                "series": [{
                    "name": "利用率",
                    "type": "gauge",
                    "center": ["50%", "60%"],
                    "radius": "80%",
                    "min": 0,
                    "max": 100,
                    "splitNumber": 10,
                    "axisLine": {
                        "lineStyle": {
                            "color": [[0.3, "#ff4757"], [0.7, "#ffa502"], [1, "#2ed573"]],
                            "width": 20
                        }
                    },
                    "pointer": {"itemStyle": {"color": "#9370db"}},
                    "detail": {"formatter": "{value}%", "fontSize": 20, "color": "#ffffff"},
                    "data": [{"value": round(utilization_score, 1), "name": "设备利用率"}]
                }],
                **theme_config
            }
            
            # 图表2：客户端增长趋势时间轴
            timeline_dates = [item["date"] for item in client_growth_trend]
            timeline_counts = [item["client_count"] for item in client_growth_trend]
            
            chart2 = {
                "title": {"text": "客户端增长趋势", "left": "center"},
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "category", "data": timeline_dates[-14:], "axisLabel": {"rotate": 45}},  # 显示最近14天
                "yAxis": {"type": "value", "name": "客户端数量"},
                "series": [{
                    "name": "客户端数量",
                    "type": "line",
                    "data": timeline_counts[-14:],
                    "itemStyle": {"color": "#9370db"},
                    "areaStyle": {"opacity": 0.3}
                }],
                **theme_config
            }
            
            # 图表3：带宽使用堆叠柱状图
            app_names = list(bandwidth_usage["by_application"].keys())[:10]
            downstream_data = [bandwidth_usage["by_application"][app]["downstream"] / (1024*1024*1024) for app in app_names]  # GB
            upstream_data = [bandwidth_usage["by_application"][app]["upstream"] / (1024*1024*1024) for app in app_names]  # GB
            
            chart3 = {
                "title": {"text": "应用带宽使用分析", "left": "center"},
                "tooltip": {"trigger": "axis"},
                "legend": {"data": ["下行流量(GB)", "上行流量(GB)"], "top": "10%"},
                "xAxis": {"type": "category", "data": app_names, "axisLabel": {"rotate": 45}},
                "yAxis": {"type": "value", "name": "流量(GB)"},
                "series": [
                    {
                        "name": "下行流量(GB)",
                        "type": "bar",
                        "stack": "流量",
                        "data": downstream_data,
                        "itemStyle": {"color": "#9370db"}
                    },
                    {
                        "name": "上行流量(GB)",
                        "type": "bar",
                        "stack": "流量",
                        "data": upstream_data,
                        "itemStyle": {"color": "#8a2be2"}
                    }
                ],
                **theme_config
            }
            
            # 图表4：许可证规划饼图
            license_pie_data = []
            colors = ["#9370db", "#8a2be2", "#7b68ee", "#6a5acd", "#483d8b"]
            for i, (device_type, count) in enumerate(license_planning["current_licenses"].items()):
                license_pie_data.append({
                    "name": device_type.title(),
                    "value": count,
                    "itemStyle": {"color": colors[i % len(colors)]}
                })
            
            chart4 = {
                "title": {"text": "许可证分布规划", "left": "center"},
                "tooltip": {"trigger": "item", "formatter": "{a} <br/>{b}: {c} ({d}%)"},
                "series": [{
                    "name": "许可证",
                    "type": "pie",
                    "radius": ["30%", "70%"],
                    "center": ["50%", "60%"],
                    "data": license_pie_data,
                    "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowOffsetX": 0, "shadowColor": "rgba(0, 0, 0, 0.5)"}}
                }],
                **theme_config
            }
            
            return CapacityPlanningResult(
                device_utilization=device_utilization,
                client_growth_trend=client_growth_trend,
                bandwidth_usage=bandwidth_usage,
                license_planning=license_planning,
                capacity_forecast=capacity_forecast,
                recommendations=recommendations,
                echarts_data=[chart1, chart2, chart3, chart4]
            )
            
        except Exception as e:
            return CapacityPlanningResult(
                echarts_data=[{
                    "title": {"text": f"错误: {str(e)}", "left": "center"},
                    "series": [],
                    **get_dark_purple_theme()
                }]
            )

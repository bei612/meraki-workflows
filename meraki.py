#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meraki API Activities for Temporal Workflows

本文件包含所有 Meraki API 调用的 Temporal Activity 实现
直接使用 merakiAPI.py 进行API调用，merakiAPI.py 负责所有认证和请求逻辑
"""

import aiohttp
from typing import Dict, List, Optional, Any
from temporalio import activity
from merakiAPI import MerakiAPI


class MerakiActivities:
    """Meraki API Activities 类 - 用于 Temporal Workflow"""

    # ==================== 组织级 API ====================
    
    @activity.defn
    async def get_organizations(self) -> List[Dict]:
        """获取用户有权限访问的组织列表"""
        api = MerakiAPI()  # merakiAPI.py 自己处理认证
        async with aiohttp.ClientSession() as session:
            return await api.get_organizations(session)

    @activity.defn
    async def get_organization_networks(self, org_id: str) -> List[Dict]:
        """获取组织的网络列表"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_networks(session, org_id)

    @activity.defn
    async def get_organization_devices(self, org_id: str) -> List[Dict]:
        """获取组织的设备列表"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_devices(session, org_id)

    @activity.defn
    async def get_organization_licenses(self, org_id: str) -> List[Dict]:
        """获取组织的许可证列表"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_licenses(session, org_id)

    @activity.defn
    async def get_organization_assurance_alerts(self, org_id: str) -> List[Dict]:
        """获取组织的保障告警"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_assurance_alerts(session, org_id)

    @activity.defn
    async def get_device_statuses_overview(self, org_id: str) -> Dict:
        """获取设备状态概览"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_device_statuses_overview(session, org_id)

    @activity.defn
    async def get_organization_devices_provisioning_statuses(self, org_id: str) -> List[Dict]:
        """获取组织设备的配置状态"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_devices_provisioning_statuses(session, org_id)

    @activity.defn
    async def get_organization_inventory_devices(self, org_id: str) -> List[Dict]:
        """获取组织库存设备"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_inventory_devices(session, org_id)

    @activity.defn
    async def get_organization_clients_search(self, org_id: str, mac: str) -> List[Dict]:
        """搜索组织中的客户端"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_clients_search(session, org_id, mac)

    @activity.defn
    async def get_organization_uplinks_statuses(self, org_id: str) -> List[Dict]:
        """获取组织上行链路状态"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_uplinks_statuses(session, org_id)

    # ==================== 网络级 API ====================

    @activity.defn
    async def get_network_clients(self, network_id: str) -> List[Dict]:
        """获取网络客户端列表"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_clients(session, network_id)

    @activity.defn
    async def get_network_events(self, network_id: str) -> List[Dict]:
        """获取网络事件"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_events(session, network_id)

    @activity.defn
    async def get_network_clients_usage_histories(self, network_id: str) -> List[Dict]:
        """获取网络客户端使用历史"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_clients_usage_histories(session, network_id)

    @activity.defn
    async def get_network_clients_application_usage(self, network_id: str) -> List[Dict]:
        """获取网络客户端应用使用情况"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_clients_application_usage(session, network_id)

    @activity.defn
    async def get_network_devices(self, network_id: str) -> List[Dict]:
        """获取网络设备列表"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_devices(session, network_id)

    @activity.defn
    async def get_network_floorplans(self, network_id: str) -> List[Dict]:
        """获取网络楼层平面图"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_floorplans(session, network_id)

    # ==================== 设备级 API ====================

    @activity.defn
    async def get_device(self, serial: str) -> Dict:
        """获取设备信息"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_device(session, serial)

    @activity.defn
    async def get_device_appliance_uplinks_settings(self, serial: str) -> Dict:
        """获取设备安全网关上行链路设置"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_device_appliance_uplinks_settings(session, serial)

    @activity.defn
    async def get_device_clients(self, serial: str) -> List[Dict]:
        """获取设备客户端"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_device_clients(session, serial)

    @activity.defn
    async def get_device_lldp_cdp(self, serial: str) -> Dict:
        """获取设备LLDP/CDP信息"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_device_lldp_cdp(session, serial)

    @activity.defn
    async def get_device_loss_and_latency_history(self, serial: str) -> List[Dict]:
        """获取设备丢包和延迟历史"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_device_loss_and_latency_history(session, serial)

    # ==================== 无线 API ====================

    @activity.defn
    async def get_network_wireless_ssids(self, network_id: str) -> List[Dict]:
        """获取网络无线SSID"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_wireless_ssids(session, network_id)

    @activity.defn
    async def get_network_wireless_settings(self, network_id: str) -> Dict:
        """获取网络无线设置"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_wireless_settings(session, network_id)

    @activity.defn
    async def get_network_wireless_clients_connection_stats(self, network_id: str) -> List[Dict]:
        """获取网络无线客户端连接统计"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_wireless_clients_connection_stats(session, network_id)

    @activity.defn
    async def get_network_wireless_air_marshal(self, network_id: str) -> List[Dict]:
        """获取网络无线Air Marshal检测"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_wireless_air_marshal(session, network_id)

    # ==================== 安全网关 API ====================

    @activity.defn
    async def get_network_appliance_settings(self, network_id: str) -> Dict:
        """获取网络安全网关设置"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_appliance_settings(session, network_id)

    @activity.defn
    async def get_network_appliance_firewall_l3_rules(self, network_id: str) -> List[Dict]:
        """获取网络安全网关L3防火墙规则"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_appliance_firewall_l3_rules(session, network_id)

    @activity.defn
    async def get_network_appliance_firewall_l7_rules(self, network_id: str) -> List[Dict]:
        """获取网络安全网关L7防火墙规则"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_appliance_firewall_l7_rules(session, network_id)

    @activity.defn
    async def get_network_appliance_content_filtering(self, network_id: str) -> Dict:
        """获取网络安全网关内容过滤"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_appliance_content_filtering(session, network_id)

    @activity.defn
    async def get_network_appliance_firewall_firewalled_services(self, network_id: str) -> List[Dict]:
        """获取网络安全网关防火墙服务"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_appliance_firewall_firewalled_services(session, network_id)

    @activity.defn
    async def get_network_appliance_vlans(self, network_id: str) -> List[Dict]:
        """获取网络安全网关VLAN配置"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_appliance_vlans(session, network_id)

    # ==================== 交换机 API ====================

    @activity.defn
    async def get_network_switch_settings(self, network_id: str) -> Dict:
        """获取网络交换机设置"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_switch_settings(session, network_id)

    @activity.defn
    async def get_network_switch_access_control_lists(self, network_id: str) -> List[Dict]:
        """获取网络交换机访问控制列表"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_switch_access_control_lists(session, network_id)

    @activity.defn
    async def get_network_switch_access_policies(self, network_id: str) -> List[Dict]:
        """获取网络交换机访问策略"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_switch_access_policies(session, network_id)

    @activity.defn
    async def get_network_switch_dhcp_server_policy(self, network_id: str) -> Dict:
        """获取网络交换机DHCP服务器策略"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_switch_dhcp_server_policy(session, network_id)

    @activity.defn
    async def get_network_switch_ports(self, serial: str) -> List[Dict]:
        """获取交换机端口配置"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_switch_ports(session, serial)

    # ==================== 传感器 API ====================

    @activity.defn
    async def get_network_sensor_alerts_profiles(self, network_id: str) -> List[Dict]:
        """获取网络传感器告警配置"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_sensor_alerts_profiles(session, network_id)

    @activity.defn
    async def get_network_sensor_alerts_current_overview_by_metric(self, network_id: str) -> List[Dict]:
        """获取网络传感器当前告警概览"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_sensor_alerts_current_overview_by_metric(session, network_id)

    # ==================== 摄像头 API ====================

    @activity.defn
    async def get_network_camera_quality_retention_profiles(self, network_id: str) -> List[Dict]:
        """获取网络摄像头画质保留配置"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_camera_quality_retention_profiles(session, network_id)

    @activity.defn
    async def get_network_camera_schedules(self, network_id: str) -> List[Dict]:
        """获取网络摄像头录制计划"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_camera_schedules(session, network_id)

    # ==================== 统计 API ====================

    @activity.defn
    async def get_organization_summary_top_applications_by_usage(self, org_id: str) -> List[Dict]:
        """获取组织顶级应用使用量"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_summary_top_applications_by_usage(session, org_id)

    @activity.defn
    async def get_organization_summary_top_clients_by_usage(self, org_id: str) -> List[Dict]:
        """获取组织顶级客户端使用量"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_summary_top_clients_by_usage(session, org_id)

    @activity.defn
    async def get_organization_summary_top_devices_by_usage(self, org_id: str) -> List[Dict]:
        """获取组织顶级设备使用量"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_summary_top_devices_by_usage(session, org_id)

    @activity.defn
    async def get_organization_summary_top_appliances_by_utilization(self, org_id: str) -> List[Dict]:
        """获取组织安全网关利用率"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_summary_top_appliances_by_utilization(session, org_id)

    # ==================== 特殊功能 API ====================

    @activity.defn
    async def get_all_organization_devices_with_name_filter(self, org_id: str, name_filter: str) -> List[Dict]:
        """获取组织中包含指定名称关键词的所有设备"""
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            devices = await api.get_organization_devices(session, org_id)
            
            # 应用名称过滤器
            name_filter_lower = name_filter.lower()
            filtered_devices = []
            for device in devices:
                device_name = (device.get("name") or device.get("hostname") or "").lower()
                if name_filter_lower in device_name:
                    filtered_devices.append(device)
            
            return filtered_devices
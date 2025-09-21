#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meraki API 客户端类

API端点说明：
- 全球版本: https://api.meraki.com/api/v1
- 中国地区: https://api.meraki.cn/api/v1 (默认使用)
- 加拿大: https://api.meraki.ca/api/v1
- 印度: https://api.meraki.in/api/v1
- 美国联邦: https://api.gov-meraki.com/api/v1
"""

import aiohttp
import json
from typing import Dict, List, Optional, Any
from temporalio import activity


class MerakiAPI:
    """Meraki API 客户端类 - 适用于 Temporal Workflow"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.meraki.cn/api/v1"):
        """
        初始化Meraki API客户端
        
        Args:
            api_key: Meraki API密钥
            base_url: API基础URL（默认为中国地区版本）
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    async def _make_request(self, session: aiohttp.ClientSession, endpoint: str, 
                           params: Optional[Dict] = None, method: str = 'GET') -> Dict:
        """
        发送异步API请求
        
        Args:
            session: aiohttp客户端会话
            endpoint: API端点
            params: 查询参数
            method: HTTP方法
            
        Returns:
            API响应数据
            
        Raises:
            Exception: 当API请求失败时
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.request(method, url, headers=self.headers, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            error_msg = f"Meraki API请求失败: {e}"
            if hasattr(e, 'status'):
                error_msg += f" (状态码: {e.status})"
            raise Exception(error_msg)
    
    @activity.defn
    async def get_organizations(self, session: aiohttp.ClientSession) -> List[Dict]:
        """
        获取用户有权限访问的组织列表
        
        Args:
            session: aiohttp客户端会话
            
        Returns:
            组织列表
        """
        return await self._make_request(session, "/organizations")
    
    @activity.defn
    async def get_organization_networks(self, session: aiohttp.ClientSession, org_id: str) -> List[Dict]:
        """
        获取组织的网络列表
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            
        Returns:
            网络列表
        """
        return await self._make_request(session, f"/organizations/{org_id}/networks")
    
    @activity.defn
    async def get_organization_devices(self, session: aiohttp.ClientSession, org_id: str, **params) -> List[Dict]:
        """
        获取组织的设备列表
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            **params: 查询参数（如 perPage, startingAfter, name, serial 等）
            
        Returns:
            设备列表
        """
        return await self._make_request(session, f"/organizations/{org_id}/devices", params)
    
    @activity.defn
    async def get_all_organization_devices_with_name_filter(self, session: aiohttp.ClientSession, 
                                                          org_id: str, name_filter: str = None) -> List[Dict]:
        """
        获取组织所有设备列表（支持分页和名称过滤）
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            name_filter: 名称过滤字符串（包含匹配）
            
        Returns:
            过滤后的设备列表
        """
        all_devices = []
        per_page = 5000  # 官方文档最大值：3-5000，默认1000
        starting_after = None
        
        while True:
            params = {"perPage": per_page}
            if starting_after:
                params["startingAfter"] = starting_after
                
            try:
                devices = await self._make_request(session, f"/organizations/{org_id}/devices", params)
                
                if not devices:  # 空列表，说明没有更多数据
                    break
                    
                all_devices.extend(devices)
                
                # 检查是否还有更多页面
                if len(devices) < per_page:
                    # 返回的设备数少于请求数，说明这是最后一页
                    break
                else:
                    # 设置下一页的起始点
                    starting_after = devices[-1].get("serial") or devices[-1].get("id")
                    if not starting_after:
                        break  # 无法获取分页标识，退出
                        
            except Exception as e:
                print(f"获取设备列表失败: {e}")
                break
        
        # 如果指定了名称过滤，进行字符串包含匹配
        if name_filter:
            name_filter_lower = name_filter.lower()
            filtered_devices = []
            for device in all_devices:
                device_name = device.get("name", "").lower()
                if name_filter_lower in device_name:
                    filtered_devices.append(device)
            return filtered_devices
        
        return all_devices
    
    @activity.defn
    async def get_device_uplinks(self, session: aiohttp.ClientSession, org_id: str, 
                                serials: List[str]) -> List[Dict]:
        """
        获取指定设备的上行链路地址
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            serials: 设备序列号列表
            
        Returns:
            设备上行链路信息
        """
        params = {'serials[]': serials}
        return await self._make_request(session, f"/organizations/{org_id}/devices/uplinks/addresses/byDevice", params)
    
    @activity.defn
    async def get_device_statuses_overview(self, session: aiohttp.ClientSession, org_id: str) -> Dict:
        """
        获取设备状态概览
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            
        Returns:
            设备状态概览信息
        """
        return await self._make_request(session, f"/organizations/{org_id}/devices/statuses/overview")
    
    @activity.defn
    async def get_device_loss_and_latency_history(self, session: aiohttp.ClientSession, 
                                                  serial: str, **params) -> List[Dict]:
        """
        获取设备的丢包率和延迟历史
        
        Args:
            session: aiohttp客户端会话
            serial: 设备序列号
            **params: 查询参数（如 t0, t1, timespan 等）
            
        Returns:
            丢包率和延迟历史数据
        """
        return await self._make_request(session, f"/devices/{serial}/lossAndLatencyHistory", params)
    
    @activity.defn
    async def get_network_clients(self, session: aiohttp.ClientSession, network_id: str, 
                                 **params) -> List[Dict]:
        """
        获取网络客户端列表
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            **params: 查询参数（如 timespan, perPage 等）
            
        Returns:
            网络客户端列表
        """
        return await self._make_request(session, f"/networks/{network_id}/clients", params)
    
    @activity.defn
    async def get_device_clients(self, session: aiohttp.ClientSession, serial: str, 
                                **params) -> List[Dict]:
        """
        获取设备客户端列表
        
        Args:
            session: aiohttp客户端会话
            serial: 设备序列号
            **params: 查询参数（如 timespan 等）
            
        Returns:
            设备客户端列表
        """
        return await self._make_request(session, f"/devices/{serial}/clients", params)
    
    @activity.defn
    async def get_organization_licenses_overview(self, session: aiohttp.ClientSession, 
                                               org_id: str) -> Dict:
        """
        获取组织许可证概览
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            
        Returns:
            许可证概览信息
        """
        return await self._make_request(session, f"/organizations/{org_id}/licenses/overview")
    
    @activity.defn
    async def get_organization_licenses(self, session: aiohttp.ClientSession, org_id: str, 
                                      **params) -> List[Dict]:
        """
        获取组织许可证列表
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            **params: 查询参数
            
        Returns:
            许可证列表
        """
        return await self._make_request(session, f"/organizations/{org_id}/licenses", params)
    
    @activity.defn
    async def get_organization_assurance_alerts(self, session: aiohttp.ClientSession, 
                                              org_id: str, **params) -> List[Dict]:
        """
        获取组织健康警报
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            **params: 查询参数
            
        Returns:
            健康警报列表
        """
        return await self._make_request(session, f"/organizations/{org_id}/assurance/alerts", params)
    
    @activity.defn
    async def get_organization_assurance_alerts_overview(self, session: aiohttp.ClientSession, 
                                                       org_id: str) -> Dict:
        """
        获取组织健康警报概览
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            
        Returns:
            健康警报概览信息
        """
        return await self._make_request(session, f"/organizations/{org_id}/assurance/alerts/overview")
    
    @activity.defn
    async def get_network_events(self, session: aiohttp.ClientSession, network_id: str, 
                                **params) -> List[Dict]:
        """
        获取网络事件列表
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            **params: 查询参数
            
        Returns:
            网络事件列表
        """
        return await self._make_request(session, f"/networks/{network_id}/events", params)
    
    @activity.defn
    async def get_device_info(self, session: aiohttp.ClientSession, serial: str) -> Dict:
        """
        获取单个设备信息（包含经纬度和楼层平面图ID）
        
        Args:
            session: aiohttp客户端会话
            serial: 设备序列号
            
        Returns:
            设备详细信息
        """
        return await self._make_request(session, f"/devices/{serial}")
    
    @activity.defn
    async def get_network_floor_plans(self, session: aiohttp.ClientSession, network_id: str) -> List[Dict]:
        """
        获取网络楼层平面图列表
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            楼层平面图列表
        """
        return await self._make_request(session, f"/networks/{network_id}/floorPlans")
    
    @activity.defn
    async def get_floor_plan_by_id(self, session: aiohttp.ClientSession, network_id: str, 
                                  floor_plan_id: str) -> Dict:
        """
        根据ID获取楼层平面图详情
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            floor_plan_id: 楼层平面图ID
            
        Returns:
            楼层平面图详细信息
        """
        return await self._make_request(session, f"/networks/{network_id}/floorPlans/{floor_plan_id}")
    
    @activity.defn
    async def get_network_client_by_id(self, session: aiohttp.ClientSession, network_id: str, 
                                      client_id: str) -> Dict:
        """
        根据ID获取网络客户端详情
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            client_id: 客户端ID
            
        Returns:
            客户端详细信息
        """
        return await self._make_request(session, f"/networks/{network_id}/clients/{client_id}")
    
    # ========== 补充缺失的 API 方法 ==========
    
    @activity.defn
    async def get_device_appliance_performance(self, session: aiohttp.ClientSession, 
                                             serial: str, **params) -> Dict:
        """
        获取MX设备的性能得分
        
        Args:
            session: aiohttp客户端会话
            serial: 设备序列号
            **params: 查询参数
            
        Returns:
            MX设备性能得分
        """
        return await self._make_request(session, f"/devices/{serial}/appliance/performance", params)
    
    @activity.defn
    async def get_network_clients_overview(self, session: aiohttp.ClientSession, 
                                         network_id: str, **params) -> Dict:
        """
        获取网络客户端概览统计信息
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            **params: 查询参数
            
        Returns:
            网络客户端概览统计信息
        """
        return await self._make_request(session, f"/networks/{network_id}/clients/overview", params)
    
    @activity.defn
    async def get_network_clients_usage_histories(self, session: aiohttp.ClientSession, 
                                                 network_id: str, **params) -> List[Dict]:
        """
        获取客户端使用历史记录
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            **params: 查询参数
            
        Returns:
            客户端使用历史记录
        """
        return await self._make_request(session, f"/networks/{network_id}/clients/usageHistories", params)
    
    @activity.defn
    async def get_network_clients_application_usage(self, session: aiohttp.ClientSession, 
                                                   network_id: str, **params) -> List[Dict]:
        """
        获取客户端应用程序使用数据
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            **params: 查询参数
            
        Returns:
            客户端应用程序使用数据
        """
        return await self._make_request(session, f"/networks/{network_id}/clients/applicationUsage", params)
    
    @activity.defn
    async def get_organization_summary_top_networks_by_status(self, session: aiohttp.ClientSession, 
                                                            org_id: str, **params) -> List[Dict]:
        """
        获取组织中网络的客户端和状态概览信息
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            **params: 查询参数
            
        Returns:
            网络客户端和状态概览信息
        """
        return await self._make_request(session, f"/organizations/{org_id}/summary/top/networks/byStatus", params)
    
    @activity.defn
    async def get_organization_devices_statuses(self, session: aiohttp.ClientSession, 
                                              org_id: str, **params) -> List[Dict]:
        """
        获取组织中每个Meraki设备的状态（已弃用但仍可用）
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            **params: 查询参数
            
        Returns:
            设备状态列表
        """
        return await self._make_request(session, f"/organizations/{org_id}/devices/statuses", params)
    
    # ========== 扩展的只读 API 方法 ==========
    
    @activity.defn
    async def get_network_wireless_ssids(self, session: aiohttp.ClientSession, 
                                       network_id: str) -> List[Dict]:
        """
        获取网络无线SSID列表
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            SSID列表
        """
        return await self._make_request(session, f"/networks/{network_id}/wireless/ssids")
    
    @activity.defn
    async def get_network_wireless_settings(self, session: aiohttp.ClientSession, 
                                          network_id: str) -> Dict:
        """
        获取网络无线设置
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            无线网络设置
        """
        return await self._make_request(session, f"/networks/{network_id}/wireless/settings")
    
    @activity.defn
    async def get_network_appliance_settings(self, session: aiohttp.ClientSession, 
                                           network_id: str) -> Dict:
        """
        获取网络安全网关设置
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            安全网关设置
        """
        return await self._make_request(session, f"/networks/{network_id}/appliance/settings")
    
    @activity.defn
    async def get_network_switch_settings(self, session: aiohttp.ClientSession, 
                                        network_id: str) -> Dict:
        """
        获取网络交换机设置
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            交换机设置
        """
        return await self._make_request(session, f"/networks/{network_id}/switch/settings")
    
    @activity.defn
    async def get_network_appliance_firewall_l3_rules(self, session: aiohttp.ClientSession, 
                                                     network_id: str) -> List[Dict]:
        """
        获取L3防火墙规则
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            L3防火墙规则列表
        """
        return await self._make_request(session, f"/networks/{network_id}/appliance/firewall/l3FirewallRules")
    
    @activity.defn
    async def get_network_appliance_firewall_l7_rules(self, session: aiohttp.ClientSession, 
                                                     network_id: str) -> List[Dict]:
        """
        获取L7防火墙规则
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            L7防火墙规则列表
        """
        return await self._make_request(session, f"/networks/{network_id}/appliance/firewall/l7FirewallRules")
    
    @activity.defn
    async def get_network_appliance_vlans(self, session: aiohttp.ClientSession, 
                                        network_id: str) -> List[Dict]:
        """
        获取网络VLAN配置
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            VLAN配置列表
        """
        return await self._make_request(session, f"/networks/{network_id}/appliance/vlans")
    
    @activity.defn
    async def get_network_switch_ports(self, session: aiohttp.ClientSession, 
                                     serial: str) -> List[Dict]:
        """
        获取交换机端口配置
        
        Args:
            session: aiohttp客户端会话
            serial: 设备序列号
            
        Returns:
            端口配置列表
        """
        return await self._make_request(session, f"/devices/{serial}/switch/ports")
    
    @activity.defn
    async def get_organization_inventory_devices(self, session: aiohttp.ClientSession, 
                                               org_id: str, **params) -> List[Dict]:
        """
        获取组织设备库存
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            **params: 查询参数
            
        Returns:
            设备库存列表
        """
        return await self._make_request(session, f"/organizations/{org_id}/inventory/devices", params)
    
    @activity.defn
    async def get_network_alerts_settings(self, session: aiohttp.ClientSession, 
                                        network_id: str) -> Dict:
        """
        获取网络告警设置
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            告警设置
        """
        return await self._make_request(session, f"/networks/{network_id}/alerts/settings")
    
    @activity.defn
    async def get_network_traffic_analysis(self, session: aiohttp.ClientSession, 
                                         network_id: str, **params) -> Dict:
        """
        获取网络流量分析
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            **params: 查询参数（如 timespan）
            
        Returns:
            流量分析数据
        """
        return await self._make_request(session, f"/networks/{network_id}/traffic", params)
    
    @activity.defn
    async def get_organization_admins(self, session: aiohttp.ClientSession, 
                                    org_id: str) -> List[Dict]:
        """
        获取组织管理员列表
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            
        Returns:
            管理员列表
        """
        return await self._make_request(session, f"/organizations/{org_id}/admins")
    
    @activity.defn
    async def get_organization_config_templates(self, session: aiohttp.ClientSession, 
                                              org_id: str) -> List[Dict]:
        """
        获取组织配置模板
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            
        Returns:
            配置模板列表
        """
        return await self._make_request(session, f"/organizations/{org_id}/configTemplates")
    
    @activity.defn
    async def get_network_webhooks_http_servers(self, session: aiohttp.ClientSession, 
                                              network_id: str) -> List[Dict]:
        """
        获取网络Webhook HTTP服务器配置
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            HTTP服务器配置列表
        """
        return await self._make_request(session, f"/networks/{network_id}/webhooks/httpServers")
    
    @activity.defn
    async def get_organization_api_requests_overview(self, session: aiohttp.ClientSession, 
                                                   org_id: str, **params) -> Dict:
        """
        获取组织API请求概览
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            **params: 查询参数
            
        Returns:
            API请求概览
        """
        return await self._make_request(session, f"/organizations/{org_id}/apiRequests/overview", params)
    
    # ========== 无线网络扩展API ==========
    
    @activity.defn
    async def get_network_wireless_clients_connection_stats(self, session: aiohttp.ClientSession, 
                                                          network_id: str, **params) -> List[Dict]:
        """
        获取无线客户端连接统计
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            **params: 查询参数
            
        Returns:
            无线客户端连接统计
        """
        return await self._make_request(session, f"/networks/{network_id}/wireless/clients/connectionStats", params)
    
    @activity.defn
    async def get_network_wireless_client_connection_stats(self, session: aiohttp.ClientSession,
                                                          network_id: str, client_id: str, **params) -> Dict:
        """
        获取单个客户端的无线连接统计
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            client_id: 客户端ID（可由MAC/用户名搜索获得）
            **params: 查询参数（如 timespan）
            
        Returns:
            客户端连接统计数据
        """
        return await self._make_request(session, f"/networks/{network_id}/wireless/clients/{client_id}/connectionStats", params)

    @activity.defn
    async def get_network_wireless_channel_utilization_history(self, session: aiohttp.ClientSession, 
                                                             network_id: str, **params) -> List[Dict]:
        """
        获取无线信道利用率历史
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            **params: 查询参数
            
        Returns:
            信道利用率历史数据
        """
        return await self._make_request(session, f"/networks/{network_id}/wireless/channelUtilizationHistory", params)
    
    @activity.defn
    async def get_network_wireless_client_count_history(self, session: aiohttp.ClientSession, 
                                                      network_id: str, **params) -> List[Dict]:
        """
        获取无线客户端数量历史
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            **params: 查询参数
            
        Returns:
            客户端数量历史数据
        """
        return await self._make_request(session, f"/networks/{network_id}/wireless/clientCountHistory", params)
    
    @activity.defn
    async def get_network_wireless_air_marshal(self, session: aiohttp.ClientSession, 
                                             network_id: str, **params) -> List[Dict]:
        """
        获取无线Air Marshal检测结果
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            **params: 查询参数
            
        Returns:
            Air Marshal检测结果
        """
        return await self._make_request(session, f"/networks/{network_id}/wireless/airMarshal", params)
    
    # ========== 安全网关扩展API ==========
    
    @activity.defn
    async def get_network_appliance_content_filtering(self, session: aiohttp.ClientSession, 
                                                    network_id: str) -> Dict:
        """
        获取内容过滤设置
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            内容过滤设置
        """
        return await self._make_request(session, f"/networks/{network_id}/appliance/contentFiltering")
    
    @activity.defn
    async def get_network_appliance_content_filtering_categories(self, session: aiohttp.ClientSession, 
                                                               network_id: str) -> List[Dict]:
        """
        获取内容过滤分类
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            内容过滤分类列表
        """
        return await self._make_request(session, f"/networks/{network_id}/appliance/contentFiltering/categories")
    
    @activity.defn
    async def get_network_appliance_connectivity_monitoring_destinations(self, session: aiohttp.ClientSession, 
                                                                       network_id: str) -> List[Dict]:
        """
        获取连接监控目标
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            连接监控目标列表
        """
        return await self._make_request(session, f"/networks/{network_id}/appliance/connectivityMonitoringDestinations")
    
    @activity.defn
    async def get_network_appliance_firewall_firewalled_services(self, session: aiohttp.ClientSession, 
                                                               network_id: str) -> List[Dict]:
        """
        获取防火墙服务配置
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            防火墙服务配置列表
        """
        return await self._make_request(session, f"/networks/{network_id}/appliance/firewall/firewalledServices")
    
    # ========== 交换机扩展API ==========
    
    @activity.defn
    async def get_network_switch_access_control_lists(self, session: aiohttp.ClientSession, 
                                                     network_id: str) -> List[Dict]:
        """
        获取交换机访问控制列表
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            访问控制列表
        """
        return await self._make_request(session, f"/networks/{network_id}/switch/accessControlLists")
    
    @activity.defn
    async def get_network_switch_access_policies(self, session: aiohttp.ClientSession, 
                                               network_id: str) -> List[Dict]:
        """
        获取交换机访问策略
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            访问策略列表
        """
        return await self._make_request(session, f"/networks/{network_id}/switch/accessPolicies")
    
    @activity.defn
    async def get_network_switch_dhcp_server_policy(self, session: aiohttp.ClientSession, 
                                                   network_id: str) -> Dict:
        """
        获取交换机DHCP服务器策略
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            DHCP服务器策略
        """
        return await self._make_request(session, f"/networks/{network_id}/switch/dhcpServerPolicy")
    
    @activity.defn
    async def get_network_switch_port_schedules(self, session: aiohttp.ClientSession, 
                                              network_id: str) -> List[Dict]:
        """
        获取交换机端口计划
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            端口计划列表
        """
        return await self._make_request(session, f"/networks/{network_id}/switch/portSchedules")
    
    # ========== 摄像头API ==========
    
    @activity.defn
    async def get_network_camera_quality_retention_profiles(self, session: aiohttp.ClientSession, 
                                                          network_id: str) -> List[Dict]:
        """
        获取摄像头画质保留配置
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            画质保留配置列表
        """
        return await self._make_request(session, f"/networks/{network_id}/camera/qualityRetentionProfiles")
    
    @activity.defn
    async def get_network_camera_schedules(self, session: aiohttp.ClientSession, 
                                         network_id: str) -> List[Dict]:
        """
        获取摄像头录制计划
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            录制计划列表
        """
        return await self._make_request(session, f"/networks/{network_id}/camera/schedules")
    
    # ========== 传感器API ==========
    
    @activity.defn
    async def get_network_sensor_alerts_profiles(self, session: aiohttp.ClientSession, 
                                               network_id: str) -> List[Dict]:
        """
        获取传感器告警配置
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            传感器告警配置列表
        """
        return await self._make_request(session, f"/networks/{network_id}/sensor/alerts/profiles")
    
    @activity.defn
    async def get_network_sensor_alerts_current_overview_by_metric(self, session: aiohttp.ClientSession, 
                                                                 network_id: str) -> List[Dict]:
        """
        获取传感器当前告警概览（按指标）
        
        Args:
            session: aiohttp客户端会话
            network_id: 网络ID
            
        Returns:
            当前告警概览
        """
        return await self._make_request(session, f"/networks/{network_id}/sensor/alerts/current/overview/byMetric")
    
    # ========== 组织级统计API ==========
    
    @activity.defn
    async def get_organization_summary_top_appliances_by_utilization(self, session: aiohttp.ClientSession, 
                                                                   org_id: str, **params) -> List[Dict]:
        """
        获取组织中按利用率排序的顶级安全网关
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            **params: 查询参数
            
        Returns:
            安全网关利用率排行
        """
        return await self._make_request(session, f"/organizations/{org_id}/summary/top/appliances/byUtilization", params)
    
    @activity.defn
    async def get_organization_summary_top_applications_by_usage(self, session: aiohttp.ClientSession, 
                                                               org_id: str, **params) -> List[Dict]:
        """
        获取组织中按使用量排序的顶级应用
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            **params: 查询参数
            
        Returns:
            应用使用量排行
        """
        return await self._make_request(session, f"/organizations/{org_id}/summary/top/applications/byUsage", params)
    
    @activity.defn
    async def get_organization_summary_top_clients_by_usage(self, session: aiohttp.ClientSession, 
                                                          org_id: str, **params) -> List[Dict]:
        """
        获取组织中按使用量排序的顶级客户端
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            **params: 查询参数
            
        Returns:
            客户端使用量排行
        """
        return await self._make_request(session, f"/organizations/{org_id}/summary/top/clients/byUsage", params)
    
    @activity.defn
    async def get_organization_summary_top_devices_by_usage(self, session: aiohttp.ClientSession, 
                                                          org_id: str, **params) -> List[Dict]:
        """
        获取组织中按使用量排序的顶级设备
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            **params: 查询参数
            
        Returns:
            设备使用量排行
        """
        return await self._make_request(session, f"/organizations/{org_id}/summary/top/devices/byUsage", params)

    @activity.defn
    async def get_organization_clients_search(self, session: aiohttp.ClientSession,
                                              org_id: str, **params) -> Dict:
        """
        按关键词搜索组织内的客户端（支持MAC、IP、主机名、用户名等）
        
        Args:
            session: aiohttp客户端会话
            org_id: 组织ID
            **params: 查询参数（如 query, perPage, startingAfter 等）
        Returns:
            搜索结果
        """
        return await self._make_request(session, f"/organizations/{org_id}/clients/search", params)

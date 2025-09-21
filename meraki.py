#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meraki API Activities for Temporal Workflows (重构版本)

这个文件包含了所有 Meraki API 调用的独立 Activity 定义，
符合 Temporal Activity 最佳实践：
- Activity 参数完全可序列化
- 内部管理 HTTP 会话
- 自包含且幂等

从 merakiAPI.py 转换而来，包含61个API方法。
"""

import aiohttp
import json
from typing import Dict, List, Optional, Any
from temporalio import activity


class MerakiActivities:
    """Meraki API Activities 类 - 用于 Temporal Workflow"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.meraki.cn/api/v1"):
        """
        初始化Meraki Activities
        
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
        发送异步API请求的工具方法
        
        Args:
            session: aiohttp客户端会话
            endpoint: API端点
            params: 查询参数
            method: HTTP方法
            
        Returns:
            API响应数据
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
    
    async def _paginated_request(self, session: aiohttp.ClientSession, endpoint: str, 
                                params: Optional[Dict] = None, per_page: int = 1000,
                                name_filter: Optional[str] = None) -> List[Dict]:
        """
        通用的分页请求处理方法
        
        Args:
            session: aiohttp客户端会话
            endpoint: API端点
            params: 基础查询参数
            per_page: 每页数量（默认1000，最大5000）
            name_filter: 可选的名称过滤器
            
        Returns:
            所有分页数据的合并列表
        """
        all_items = []
        starting_after = None
        request_params = params.copy() if params else {}
        
        while True:
            # 设置分页参数
            request_params["perPage"] = per_page
            if starting_after:
                request_params["startingAfter"] = starting_after
                
            try:
                items = await self._make_request(session, endpoint, request_params)
                
                # 处理不同的响应格式
                if isinstance(items, dict):
                    # 对于搜索API，数据可能在 'items' 或其他字段中
                    if 'items' in items:
                        items = items['items']
                    elif 'results' in items:
                        items = items['results']
                    else:
                        # 如果是单个对象而不是列表，直接返回
                        return [items] if items else []
                
                if not items:  # 空列表，说明没有更多数据
                    break
                    
                all_items.extend(items)
                
                # 检查是否还有更多页面
                if len(items) < per_page:
                    # 返回的项目数少于请求数，说明这是最后一页
                    break
                else:
                    # 设置下一页的起始点
                    # 不同的API可能使用不同的标识符
                    starting_after = (items[-1].get("id") or 
                                    items[-1].get("serial") or 
                                    items[-1].get("networkId") or
                                    items[-1].get("alertId") or
                                    items[-1].get("licenseId") or
                                    items[-1].get("mac") or
                                    items[-1].get("clientId"))
                    if not starting_after:
                        break  # 无法获取分页标识，退出
                        
            except Exception as e:
                print(f"分页请求失败: {e}")
                break
        
        # 如果指定了名称过滤，进行字符串包含匹配
        if name_filter:
            name_filter_lower = name_filter.lower()
            filtered_items = []
            for item in all_items:
                # 尝试多个可能的名称字段
                item_name = (item.get("name") or 
                           item.get("hostname") or 
                           item.get("description") or "").lower()
                if name_filter_lower in item_name:
                    filtered_items.append(item)
            return filtered_items
        
        return all_items

    # ==================== 组织级 API ====================
    
    @activity.defn
    async def get_organizations(self, use_pagination: bool = True, per_page: int = 1000) -> List[Dict]:
        """
        获取用户有权限访问的组织列表
        
        Args:
            use_pagination: 是否使用自动分页（默认True）
            per_page: 每页数量（仅在use_pagination=True时有效）
            
        Returns:
            组织列表
        """
        async with aiohttp.ClientSession() as session:
            if use_pagination:
                return await self._paginated_request(session, "/organizations", per_page=per_page)
            else:
                return await self._make_request(session, "/organizations")
    
    @activity.defn
    async def get_organization_networks(self, org_id: str, use_pagination: bool = True, 
                                       per_page: int = 1000, name_filter: Optional[str] = None) -> List[Dict]:
        """
        获取组织的网络列表
        
        Args:
            org_id: 组织ID
            use_pagination: 是否使用自动分页（默认True）
            per_page: 每页数量（仅在use_pagination=True时有效）
            name_filter: 名称过滤器（仅在use_pagination=True时有效）
            
        Returns:
            网络列表
        """
        async with aiohttp.ClientSession() as session:
            if use_pagination:
                return await self._paginated_request(
                    session, f"/organizations/{org_id}/networks", 
                    per_page=per_page, name_filter=name_filter
                )
            else:
                return await self._make_request(session, f"/organizations/{org_id}/networks")
    
    @activity.defn
    async def get_organization_devices(self, org_id: str, use_pagination: bool = True, 
                                      per_page: int = 1000, name_filter: Optional[str] = None, 
                                      **params) -> List[Dict]:
        """
        获取组织的设备列表
        
        Args:
            org_id: 组织ID
            use_pagination: 是否使用自动分页（默认True）
            per_page: 每页数量（仅在use_pagination=True时有效）
            name_filter: 名称过滤器（仅在use_pagination=True时有效）
            **params: 其他查询参数
            
        Returns:
            设备列表
        """
        async with aiohttp.ClientSession() as session:
            if use_pagination:
                return await self._paginated_request(
                    session, f"/organizations/{org_id}/devices", 
                    params=params, per_page=per_page, name_filter=name_filter
                )
            else:
                return await self._make_request(session, f"/organizations/{org_id}/devices", params)
    
    
    @activity.defn
    async def get_device_appliance_uplinks_settings(self, serial: str) -> Dict:
        """获取设备安全网关上行链路设置"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/devices/{serial}/appliance/uplinks/settings")
    
    @activity.defn
    async def get_organization_uplinks_statuses(self, org_id: str, use_pagination: bool = True, 
                                               per_page: int = 1000, **params) -> List[Dict]:
        """
        获取组织上行链路状态列表
        
        Args:
            org_id: 组织ID
            use_pagination: 是否使用自动分页（默认True）
            per_page: 每页数量（仅在use_pagination=True时有效）
            **params: 其他查询参数
            
        Returns:
            上行链路状态列表
        """
        async with aiohttp.ClientSession() as session:
            if use_pagination:
                return await self._paginated_request(
                    session, f"/organizations/{org_id}/uplinks/statuses", 
                    params=params, per_page=per_page
                )
            else:
                return await self._make_request(session, f"/organizations/{org_id}/uplinks/statuses", params)
    
    @activity.defn
    async def get_device_statuses_overview(self, org_id: str, **params) -> Dict:
        """获取组织设备状态概览"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/organizations/{org_id}/devices/statuses/overview", params)
    
    @activity.defn
    async def get_organization_licenses_overview(self, org_id: str) -> Dict:
        """获取组织许可证概览"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/organizations/{org_id}/licenses/overview")
    
    @activity.defn
    async def get_organization_licenses(self, org_id: str, use_pagination: bool = True, 
                                       per_page: int = 1000, **params) -> List[Dict]:
        """
        获取组织许可证列表
        
        Args:
            org_id: 组织ID
            use_pagination: 是否使用自动分页（默认True）
            per_page: 每页数量（仅在use_pagination=True时有效）
            **params: 其他查询参数
            
        Returns:
            许可证列表
        """
        async with aiohttp.ClientSession() as session:
            if use_pagination:
                return await self._paginated_request(
                    session, f"/organizations/{org_id}/licenses", 
                    params=params, per_page=per_page
                )
            else:
                return await self._make_request(session, f"/organizations/{org_id}/licenses", params)
    
    @activity.defn
    async def get_organization_assurance_alerts(self, org_id: str, use_pagination: bool = True, 
                                               per_page: int = 1000, **params) -> List[Dict]:
        """
        获取组织健康告警
        
        Args:
            org_id: 组织ID
            use_pagination: 是否使用自动分页（默认True）
            per_page: 每页数量（仅在use_pagination=True时有效）
            **params: 其他查询参数
            
        Returns:
            健康告警列表
        """
        async with aiohttp.ClientSession() as session:
            if use_pagination:
                return await self._paginated_request(
                    session, f"/organizations/{org_id}/assurance/alerts", 
                    params=params, per_page=per_page
                )
            else:
                return await self._make_request(session, f"/organizations/{org_id}/assurance/alerts", params)
    
    @activity.defn
    async def get_organization_assurance_alerts_overview(self, org_id: str, **params) -> Dict:
        """获取组织健康告警概览"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/organizations/{org_id}/assurance/alerts/overview", params)
    
    @activity.defn
    async def get_organization_summary_top_networks_by_status(self, org_id: str, **params) -> List[Dict]:
        """获取按状态排序的顶级网络"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/organizations/{org_id}/summary/top/networks/byStatus", params)
    
    @activity.defn
    async def get_organization_devices_provisioning_statuses(self, org_id: str, use_pagination: bool = True, 
                                                            per_page: int = 1000, **params) -> List[Dict]:
        """
        获取组织设备配置状态列表（替代已弃用的devices/statuses）
        
        Args:
            org_id: 组织ID
            use_pagination: 是否使用自动分页（默认True）
            per_page: 每页数量（仅在use_pagination=True时有效）
            **params: 其他查询参数
            
        Returns:
            设备配置状态列表
        """
        async with aiohttp.ClientSession() as session:
            if use_pagination:
                return await self._paginated_request(
                    session, f"/organizations/{org_id}/devices/provisioning/statuses", 
                    params=params, per_page=per_page
                )
            else:
                return await self._make_request(session, f"/organizations/{org_id}/devices/provisioning/statuses", params)
    
    @activity.defn
    async def get_organization_inventory_devices(self, org_id: str, use_pagination: bool = True, 
                                                per_page: int = 1000, **params) -> List[Dict]:
        """
        获取组织设备库存
        
        Args:
            org_id: 组织ID
            use_pagination: 是否使用自动分页（默认True）
            per_page: 每页数量（仅在use_pagination=True时有效）
            **params: 其他查询参数
            
        Returns:
            设备库存列表
        """
        async with aiohttp.ClientSession() as session:
            if use_pagination:
                return await self._paginated_request(
                    session, f"/organizations/{org_id}/inventory/devices", 
                    params=params, per_page=per_page
                )
            else:
                return await self._make_request(session, f"/organizations/{org_id}/inventory/devices", params)
    
    @activity.defn
    async def get_organization_admins(self, org_id: str) -> List[Dict]:
        """获取组织管理员列表"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/organizations/{org_id}/admins")
    
    @activity.defn
    async def get_organization_config_templates(self, org_id: str) -> List[Dict]:
        """获取组织配置模板列表"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/organizations/{org_id}/configTemplates")
    
    @activity.defn
    async def get_organization_api_requests_overview(self, org_id: str, **params) -> Dict:
        """获取组织API请求概览"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/organizations/{org_id}/apiRequests/overview", params)
    
    @activity.defn
    async def get_organization_summary_top_appliances_by_utilization(self, org_id: str, **params) -> List[Dict]:
        """获取按利用率排序的顶级安全网关"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/organizations/{org_id}/summary/top/appliances/byUtilization", params)
    
    @activity.defn
    async def get_organization_summary_top_applications_by_usage(self, org_id: str, **params) -> List[Dict]:
        """获取按使用量排序的顶级应用"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/organizations/{org_id}/summary/top/applications/byUsage", params)
    
    @activity.defn
    async def get_organization_summary_top_clients_by_usage(self, org_id: str, **params) -> List[Dict]:
        """获取按使用量排序的顶级客户端"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/organizations/{org_id}/summary/top/clients/byUsage", params)
    
    @activity.defn
    async def get_organization_summary_top_devices_by_usage(self, org_id: str, **params) -> List[Dict]:
        """获取按使用量排序的顶级设备"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/organizations/{org_id}/summary/top/devices/byUsage", params)
    
    @activity.defn
    async def get_organization_clients_search(self, org_id: str, use_pagination: bool = True, 
                                             per_page: int = 1000, **params) -> Dict:
        """
        搜索组织客户端
        
        Args:
            org_id: 组织ID
            use_pagination: 是否使用自动分页（默认True）
            per_page: 每页数量（仅在use_pagination=True时有效）
            **params: 其他查询参数（如query等）
            
        Returns:
            客户端搜索结果
        """
        async with aiohttp.ClientSession() as session:
            if use_pagination:
                result = await self._paginated_request(
                    session, f"/organizations/{org_id}/clients/search", 
                    params=params, per_page=per_page
                )
                # 搜索API可能返回特殊格式，需要包装成字典
                return {"items": result} if isinstance(result, list) else result
            else:
                return await self._make_request(session, f"/organizations/{org_id}/clients/search", params)

    # ==================== 设备级 API ====================
    
    @activity.defn
    async def get_device_loss_and_latency_history(self, serial: str, **params) -> List[Dict]:
        """获取设备丢包和延迟历史"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/devices/{serial}/lossAndLatencyHistory", params)
    
    @activity.defn
    async def get_device_clients(self, serial: str, **params) -> List[Dict]:
        """获取设备客户端列表"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/devices/{serial}/clients", params)
    
    @activity.defn
    async def get_device_info(self, serial: str) -> Dict:
        """获取设备详细信息"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/devices/{serial}")
    
    @activity.defn
    async def get_device_appliance_performance(self, serial: str, **params) -> Dict:
        """获取安全网关性能数据"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/devices/{serial}/appliance/performance", params)

    # ==================== 网络级 API ====================
    
    @activity.defn
    async def get_network_clients(self, network_id: str, use_pagination: bool = True, 
                                 per_page: int = 1000, **params) -> List[Dict]:
        """
        获取网络客户端列表
        
        Args:
            network_id: 网络 ID
            use_pagination: 是否使用自动分页（默认True）
            per_page: 每页数量（仅在use_pagination=True时有效）
            **params: 其他查询参数（如timespan等）
            
        Returns:
            网络客户端列表
        """
        async with aiohttp.ClientSession() as session:
            if use_pagination:
                return await self._paginated_request(
                    session, f"/networks/{network_id}/clients", 
                    params=params, per_page=per_page
                )
            else:
                return await self._make_request(session, f"/networks/{network_id}/clients", params)
    
    @activity.defn
    async def get_network_events(self, network_id: str, use_pagination: bool = True, 
                                per_page: int = 1000, **params) -> List[Dict]:
        """
        获取网络事件
        
        Args:
            network_id: 网络 ID
            use_pagination: 是否使用自动分页（默认True）
            per_page: 每页数量（仅在use_pagination=True时有效）
            **params: 其他查询参数（如timespan、productType等）
            
        Returns:
            网络事件列表
        """
        async with aiohttp.ClientSession() as session:
            if use_pagination:
                return await self._paginated_request(
                    session, f"/networks/{network_id}/events", 
                    params=params, per_page=per_page
                )
            else:
                return await self._make_request(session, f"/networks/{network_id}/events", params)
    
    @activity.defn
    async def get_network_floor_plans(self, network_id: str) -> List[Dict]:
        """获取网络楼层平面图列表"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/floorPlans")
    
    @activity.defn
    async def get_floor_plan_by_id(self, network_id: str, floor_plan_id: str) -> Dict:
        """获取指定楼层平面图详情"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/floorPlans/{floor_plan_id}")
    
    @activity.defn
    async def get_network_client_by_id(self, network_id: str, client_id: str, **params) -> Dict:
        """获取网络中指定客户端详情"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/clients/{client_id}", params)
    
    @activity.defn
    async def get_network_clients_overview(self, network_id: str, **params) -> Dict:
        """获取网络客户端概览"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/clients/overview", params)
    
    @activity.defn
    async def get_network_clients_usage_histories(self, network_id: str, use_pagination: bool = True, 
                                                  per_page: int = 1000, **params) -> List[Dict]:
        """
        获取网络客户端使用历史
        
        Args:
            network_id: 网络 ID
            use_pagination: 是否使用自动分页（默认True）
            per_page: 每页数量（仅在use_pagination=True时有效）
            **params: 其他查询参数
            
        Returns:
            客户端使用历史列表
        """
        async with aiohttp.ClientSession() as session:
            if use_pagination:
                return await self._paginated_request(
                    session, f"/networks/{network_id}/clients/usageHistories", 
                    params=params, per_page=per_page
                )
            else:
                return await self._make_request(session, f"/networks/{network_id}/clients/usageHistories", params)
    
    @activity.defn
    async def get_network_clients_application_usage(self, network_id: str, use_pagination: bool = True, 
                                                    per_page: int = 1000, **params) -> List[Dict]:
        """
        获取网络客户端应用使用数据
        
        Args:
            network_id: 网络 ID
            use_pagination: 是否使用自动分页（默认True）
            per_page: 每页数量（仅在use_pagination=True时有效）
            **params: 其他查询参数
            
        Returns:
            客户端应用使用数据列表
        """
        async with aiohttp.ClientSession() as session:
            if use_pagination:
                return await self._paginated_request(
                    session, f"/networks/{network_id}/clients/applicationUsage", 
                    params=params, per_page=per_page
                )
            else:
                return await self._make_request(session, f"/networks/{network_id}/clients/applicationUsage", params)
    
    @activity.defn
    async def get_network_alerts_settings(self, network_id: str) -> Dict:
        """获取网络告警设置"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/alerts/settings")
    
    @activity.defn
    async def get_network_traffic_analysis(self, network_id: str, **params) -> Dict:
        """获取网络流量分析"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/trafficAnalysis", params)
    
    @activity.defn
    async def get_network_webhooks_http_servers(self, network_id: str) -> List[Dict]:
        """获取网络Webhook HTTP服务器列表"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/webhooks/httpServers")

    # ==================== 无线网络 API ====================
    
    @activity.defn
    async def get_network_wireless_ssids(self, network_id: str) -> List[Dict]:
        """获取无线网络SSID列表"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/wireless/ssids")
    
    @activity.defn
    async def get_network_wireless_settings(self, network_id: str) -> Dict:
        """获取无线网络设置"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/wireless/settings")
    
    @activity.defn
    async def get_network_wireless_clients_connection_stats(self, network_id: str, **params) -> List[Dict]:
        """获取无线客户端连接统计"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/wireless/clients/connectionStats", params)
    
    @activity.defn
    async def get_network_wireless_client_connection_stats(self, network_id: str, client_id: str, **params) -> Dict:
        """获取指定无线客户端连接统计"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/wireless/clients/{client_id}/connectionStats", params)
    
    @activity.defn
    async def get_network_wireless_channel_utilization_history(self, network_id: str, **params) -> List[Dict]:
        """获取无线信道利用率历史"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/wireless/channelUtilizationHistory", params)
    
    @activity.defn
    async def get_network_wireless_client_count_history(self, network_id: str, **params) -> List[Dict]:
        """获取无线客户端数量历史"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/wireless/clientCountHistory", params)
    
    @activity.defn
    async def get_network_wireless_air_marshal(self, network_id: str, **params) -> List[Dict]:
        """获取无线空中监管信息"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/wireless/airMarshal", params)

    # ==================== 安全网关 API ====================
    
    @activity.defn
    async def get_network_appliance_settings(self, network_id: str) -> Dict:
        """获取安全网关设置"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/appliance/settings")
    
    @activity.defn
    async def get_network_appliance_firewall_l3_firewall_rules(self, network_id: str) -> List[Dict]:
        """获取L3防火墙规则"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/appliance/firewall/l3FirewallRules")
    
    @activity.defn
    async def get_network_appliance_firewall_l7_firewall_rules(self, network_id: str) -> List[Dict]:
        """获取L7防火墙规则"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/appliance/firewall/l7FirewallRules")
    
    @activity.defn
    async def get_network_appliance_vlans(self, network_id: str) -> List[Dict]:
        """获取VLAN列表"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/appliance/vlans")
    
    @activity.defn
    async def get_network_appliance_content_filtering(self, network_id: str) -> Dict:
        """获取内容过滤设置"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/appliance/contentFiltering")
    
    @activity.defn
    async def get_network_appliance_content_filtering_categories(self, network_id: str) -> List[Dict]:
        """获取内容过滤类别"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/appliance/contentFiltering/categories")
    
    @activity.defn
    async def get_network_appliance_connectivity_monitoring_destinations(self, network_id: str) -> List[Dict]:
        """获取连接监控目标"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/appliance/connectivityMonitoringDestinations")
    
    @activity.defn
    async def get_network_appliance_firewall_firewalled_services(self, network_id: str) -> List[Dict]:
        """获取防火墙服务"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/appliance/firewall/firewalledServices")

    # ==================== 交换机 API ====================
    
    @activity.defn
    async def get_network_switch_settings(self, network_id: str) -> Dict:
        """获取交换机设置"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/switch/settings")
    
    @activity.defn
    async def get_network_switch_ports(self, serial: str) -> List[Dict]:
        """获取交换机端口列表"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/devices/{serial}/switch/ports")
    
    @activity.defn
    async def get_network_switch_access_control_lists(self, network_id: str) -> List[Dict]:
        """获取交换机访问控制列表"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/switch/accessControlLists")
    
    @activity.defn
    async def get_network_switch_access_policies(self, network_id: str) -> List[Dict]:
        """获取交换机访问策略"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/switch/accessPolicies")
    
    @activity.defn
    async def get_network_switch_dhcp_server_policy(self, network_id: str) -> Dict:
        """获取交换机DHCP服务器策略"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/switch/dhcpServerPolicy")
    
    @activity.defn
    async def get_network_switch_port_schedules(self, network_id: str) -> List[Dict]:
        """获取交换机端口调度"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/switch/portSchedules")

    # ==================== 摄像头 API ====================
    
    @activity.defn
    async def get_network_camera_quality_retention_profiles(self, network_id: str) -> List[Dict]:
        """获取摄像头质量保留配置文件"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/camera/qualityRetentionProfiles")
    
    @activity.defn
    async def get_network_camera_schedules(self, network_id: str) -> List[Dict]:
        """获取摄像头调度"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/camera/schedules")

    # ==================== 传感器 API ====================
    
    @activity.defn
    async def get_network_sensor_alerts_profiles(self, network_id: str) -> List[Dict]:
        """获取传感器告警配置文件"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/sensor/alerts/profiles")
    
    @activity.defn
    async def get_network_sensor_alerts_current_overview_by_metric(self, network_id: str) -> Dict:
        """获取传感器当前告警概览（按指标）"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(session, f"/networks/{network_id}/sensor/alerts/current/overview/byMetric")

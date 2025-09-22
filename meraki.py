#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meraki API Activities for Temporal Workflows

本文件包含所有 Meraki API 调用的 Temporal Activity 实现
每个Activity都是对 merakiAPI.py 中对应方法的薄包装层
merakiAPI.py 负责所有认证、请求逻辑和错误处理

Activity设计原则:
1. 每个Activity对应一个具体的Meraki API端点
2. 参数类型明确，返回值结构清晰
3. 不处理API密钥，由merakiAPI.py统一管理
4. 支持Temporal的重试和超时机制
"""

import aiohttp
from typing import Dict, List, Optional, Any
from temporalio import activity
from merakiAPI import MerakiAPI


class MerakiActivities:
    """
    Meraki API Activities 类 - 用于 Temporal Workflow
    
    包含61个Meraki Dashboard API的Activity封装
    按功能分组：组织级、网络级、设备级、客户端级、许可证、告警等
    """

    # ==================== 组织级 API ====================
    
    @activity.defn
    async def get_organizations(self) -> List[Dict]:
        """
        获取用户有权限访问的组织列表
        
        API端点: GET /organizations
        用途: 列出当前API密钥有权限访问的所有组织
        
        Returns:
            List[Dict]: 组织列表，每个组织包含:
                - id (str): 组织ID
                - name (str): 组织名称
                - url (str): 组织URL
                - api (dict): API访问设置
                - licensing (dict): 许可证信息
                - cloud (dict): 云设置
        
        使用场景: 
            - 多租户环境中选择目标组织
            - 权限验证和组织发现
        """
        api = MerakiAPI()  # merakiAPI.py 自己处理认证
        async with aiohttp.ClientSession() as session:
            return await api.get_organizations(session)

    @activity.defn
    async def get_organization_networks(self, org_id: str) -> List[Dict]:
        """
        获取组织的网络列表
        
        API端点: GET /organizations/{organizationId}/networks
        用途: 获取指定组织下的所有网络
        
        Args:
            org_id (str): 组织ID
            
        Returns:
            List[Dict]: 网络列表，每个网络包含:
                - id (str): 网络ID
                - organizationId (str): 所属组织ID
                - name (str): 网络名称
                - productTypes (list): 产品类型 [wireless, appliance, switch, camera, cellularGateway]
                - timeZone (str): 时区
                - tags (list): 标签列表
                - enrollmentString (str): 注册字符串
                - url (str): 网络URL
                - notes (str): 备注
        
        使用场景:
            - 网络管理和监控
            - 设备部署前的网络选择
            - 网络拓扑分析
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_networks(session, org_id)

    @activity.defn
    async def get_organization_devices(self, org_id: str) -> List[Dict]:
        """
        获取组织的设备列表
        
        API端点: GET /organizations/{organizationId}/devices
        用途: 获取指定组织下的所有网络设备
        
        Args:
            org_id (str): 组织ID
            
        Returns:
            List[Dict]: 设备列表，每个设备包含:
                - serial (str): 设备序列号
                - mac (str): 设备MAC地址
                - name (str): 设备名称
                - model (str): 设备型号 (如 MR44, MS220-8P, MX68)
                - networkId (str): 所属网络ID
                - productType (str): 产品类型 (wireless, switch, appliance, camera)
                - firmware (str): 固件版本
                - lanIp (str): LAN IP地址
                - lat (float): 纬度
                - lng (float): 经度
                - address (str): 物理地址
                - notes (str): 设备备注
                - tags (list): 设备标签
        
        使用场景:
            - 设备清单管理
            - 固件版本统计
            - 设备地理位置分析
            - 设备健康状态监控
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_devices(session, org_id)

    @activity.defn
    async def get_organization_licenses(self, org_id: str) -> List[Dict]:
        """
        获取组织的许可证列表 (Per-device licensing)
        
        API端点: GET /organizations/{organizationId}/licenses
        用途: 获取按设备许可的许可证信息
        
        Args:
            org_id (str): 组织ID
            
        Returns:
            List[Dict]: 许可证列表，每个许可证包含:
                - licenseKey (str): 许可证密钥
                - licenseType (str): 许可证类型
                - orderNumber (str): 订单号
                - deviceSerial (str): 绑定的设备序列号
                - networkId (str): 所属网络ID
                - state (str): 许可证状态 (active, expired, unused)
                - seatLimit (int): 座位限制
                - totalDurationInDays (int): 总有效天数
                - durationInDays (int): 剩余天数
                - permanentlyQueuedLicenses (list): 永久排队的许可证
        
        注意:
            - 仅适用于Per-device licensing模式
            - Co-termination licensing使用 get_organization_licenses_overview
        
        使用场景:
            - 许可证合规性检查
            - 许可证到期提醒
            - 许可证分配管理
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_licenses(session, org_id)

    @activity.defn
    async def get_organization_assurance_alerts(self, org_id: str) -> List[Dict]:
        """
        获取组织的保障告警
        
        API端点: GET /organizations/{organizationId}/assurance/alerts
        用途: 获取网络保障系统生成的告警信息
        
        Args:
            org_id (str): 组织ID
            
        Returns:
            List[Dict]: 告警列表，每个告警包含:
                - id (str): 告警ID
                - type (str): 告警类型 (connectivity, performance, configuration)
                - severity (str): 严重程度 (critical, warning, informational)
                - scope (dict): 影响范围 (networkIds, deviceSerials, deviceTypes)
                - category (str): 告警类别
                - description (str): 告警描述
                - startedAt (str): 开始时间 (ISO 8601)
                - dismissedAt (str): 解除时间
                - resolvedAt (str): 解决时间
                - alertData (dict): 告警详细数据
        
        使用场景:
            - 网络健康监控
            - 故障预警和响应
            - SLA监控和报告
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_assurance_alerts(session, org_id)

    @activity.defn
    async def get_device_statuses_overview(self, org_id: str) -> Dict:
        """
        获取设备状态概览
        
        API端点: GET /organizations/{organizationId}/devices/statuses/overview
        用途: 获取组织内所有设备的状态统计概览
        
        Args:
            org_id (str): 组织ID
            
        Returns:
            Dict: 设备状态概览，包含:
                - counts (dict): 设备数量统计
                    - byStatus (dict): 按状态分组的数量
                        - online (int): 在线设备数
                        - offline (int): 离线设备数
                        - alerting (int): 告警设备数
                        - dormant (int): 休眠设备数
        
        使用场景:
            - 网络健康仪表板
            - 设备状态监控
            - 运维报告生成
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_device_statuses_overview(session, org_id)

    # 注意：get_organization_devices_provisioning_statuses 在merakiAPI.py中不存在，已删除

    @activity.defn
    async def get_organization_inventory_devices(self, org_id: str) -> List[Dict]:
        """
        获取组织库存设备
        
        API端点: GET /organizations/{organizationId}/inventory/devices
        用途: 获取组织库存中的所有设备（包括未分配到网络的设备）
        
        Args:
            org_id (str): 组织ID
            
        Returns:
            List[Dict]: 库存设备列表，每个设备包含:
                - serial (str): 设备序列号
                - mac (str): 设备MAC地址
                - model (str): 设备型号
                - claimedAt (str): 认领时间
                - networkId (str): 所属网络ID（如果已分配）
                - orderNumber (str): 订单号
                - licenseExpirationDate (str): 许可证到期日期
        
        使用场景:
            - 设备资产管理
            - 库存盘点
            - 设备分配规划
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_inventory_devices(session, org_id)

    @activity.defn
    async def get_organization_clients_search(self, org_id: str, mac: str) -> List[Dict]:
        """
        搜索组织中的客户端
        
        API端点: GET /organizations/{organizationId}/clients/search
        用途: 在整个组织范围内搜索指定MAC地址的客户端设备
        
        Args:
            org_id (str): 组织ID
            mac (str): 客户端MAC地址
            
        Returns:
            List[Dict]: 客户端搜索结果，每个客户端包含:
                - id (str): 客户端ID
                - mac (str): 客户端MAC地址
                - description (str): 客户端描述
                - ip (str): IP地址
                - ip6 (str): IPv6地址
                - user (str): 用户名
                - firstSeen (str): 首次发现时间
                - lastSeen (str): 最后发现时间
                - manufacturer (str): 制造商
                - os (str): 操作系统
                - recentDeviceSerial (str): 最近连接的设备序列号
                - recentDeviceName (str): 最近连接的设备名称
                - recentDeviceMac (str): 最近连接的设备MAC
                - ssid (str): 连接的SSID
                - vlan (int): VLAN ID
                - switchport (str): 交换机端口
                - usage (dict): 流量使用统计
                - status (str): 连接状态
        
        使用场景:
            - 客户端设备追踪
            - 网络安全调查
            - 设备位置定位
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_clients_search(session, org_id, mac)

    @activity.defn
    async def get_organization_uplinks_statuses(self, org_id: str) -> List[Dict]:
        """
        获取组织上行链路状态
        
        API端点: GET /organizations/{organizationId}/uplinks/statuses
        用途: 获取组织内所有设备的上行链路连接状态
        
        Args:
            org_id (str): 组织ID
            
        Returns:
            List[Dict]: 上行链路状态列表，每个设备包含:
                - serial (str): 设备序列号
                - model (str): 设备型号
                - networkId (str): 所属网络ID
                - lastReportedAt (str): 最后报告时间
                - uplinks (list): 上行链路列表
                    - interface (str): 接口名称
                    - status (str): 连接状态 (active, ready, connecting, not_connected, failed)
                    - ip (str): IP地址
                    - gateway (str): 网关地址
                    - publicIp (str): 公网IP
                    - dns (list): DNS服务器
                    - usingStaticIp (bool): 是否使用静态IP
                    - provider (str): ISP提供商
        
        使用场景:
            - 网络连接监控
            - 上行链路故障诊断
            - 网络冗余检查
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_uplinks_statuses(session, org_id)

    # ==================== 网络级 API ====================

    @activity.defn
    async def get_network_clients(self, network_id: str, use_pagination: bool = True, per_page: int = 100, **kwargs) -> List[Dict]:
        """
        获取网络客户端列表
        
        API端点: GET /networks/{networkId}/clients
        用途: 获取指定网络中的所有客户端设备
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: 客户端列表，每个客户端包含:
                - id (str): 客户端ID
                - mac (str): 客户端MAC地址
                - description (str): 客户端描述
                - ip (str): IP地址
                - ip6 (str): IPv6地址
                - user (str): 用户名
                - firstSeen (str): 首次发现时间
                - lastSeen (str): 最后发现时间
                - manufacturer (str): 制造商
                - os (str): 操作系统
                - recentDeviceSerial (str): 最近连接的设备序列号
                - recentDeviceName (str): 最近连接的设备名称
                - recentDeviceConnection (str): 最近连接类型 (Wired, Wireless)
                - ssid (str): 连接的SSID（无线客户端）
                - vlan (int): VLAN ID
                - switchport (str): 交换机端口（有线客户端）
                - usage (dict): 流量使用统计
                    - sent (int): 发送字节数
                    - recv (int): 接收字节数
                - status (str): 连接状态 (Online, Offline)
        
        使用场景:
            - 网络客户端监控
            - 用户行为分析
            - 网络容量规划
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            # 构建查询参数
            params = {}
            if 'timespan' in kwargs:
                params['timespan'] = kwargs['timespan']
            if not use_pagination:
                params['perPage'] = per_page
            return await api.get_network_clients(session, network_id, **params)

    @activity.defn
    async def get_network_events(self, network_id: str) -> List[Dict]:
        """
        获取网络事件日志
        
        API端点: GET /networks/{networkId}/events
        用途: 获取网络中的事件日志，包括连接、断开、认证等事件
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: 事件列表，每个事件包含:
                - occurredAt (str): 事件发生时间 (ISO 8601)
                - networkId (str): 网络ID
                - type (str): 事件类型 (association, disassociation, authentication, etc.)
                - description (str): 事件描述
                - clientId (str): 客户端ID
                - clientMac (str): 客户端MAC地址
                - clientDescription (str): 客户端描述
                - deviceSerial (str): 设备序列号
                - deviceName (str): 设备名称
                - ssidNumber (int): SSID编号
                - eventData (dict): 事件详细数据
        
        使用场景:
            - 网络故障排查
            - 安全事件监控
            - 用户连接分析
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_events(session, network_id)

    @activity.defn
    async def get_network_clients_usage_histories(self, network_id: str) -> List[Dict]:
        """
        获取网络客户端使用历史
        
        API端点: GET /networks/{networkId}/clients/usageHistories
        用途: 获取网络中客户端的流量使用历史统计
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: 客户端使用历史列表，每个记录包含:
                - clientId (str): 客户端ID
                - clientMac (str): 客户端MAC地址
                - clientName (str): 客户端名称
                - usage (list): 使用历史数据点
                    - ts (str): 时间戳
                    - sent (int): 发送字节数
                    - recv (int): 接收字节数
                - total (dict): 总计统计
                    - sent (int): 总发送字节数
                    - recv (int): 总接收字节数
        
        使用场景:
            - 流量分析和计费
            - 网络使用趋势分析
            - 带宽规划
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_clients_usage_histories(session, network_id)

    @activity.defn
    async def get_network_clients_application_usage(self, network_id: str) -> List[Dict]:
        """
        获取网络客户端应用使用情况
        
        API端点: GET /networks/{networkId}/clients/applicationUsage
        用途: 获取网络中客户端的应用层流量使用统计
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: 客户端应用使用列表，每个记录包含:
                - clientId (str): 客户端ID
                - clientMac (str): 客户端MAC地址
                - clientName (str): 客户端名称
                - applicationUsage (list): 应用使用统计
                    - application (str): 应用名称
                    - sent (int): 发送字节数
                    - recv (int): 接收字节数
        
        使用场景:
            - 应用层流量分析
            - 网络使用优化
            - 带宽管理策略制定
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_clients_application_usage(session, network_id)

    @activity.defn
    async def get_network_devices(self, network_id: str) -> List[Dict]:
        """
        获取网络设备列表
        
        API端点: GET /networks/{networkId}/devices
        用途: 获取指定网络中的所有设备
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: 网络设备列表，每个设备包含:
                - serial (str): 设备序列号
                - mac (str): 设备MAC地址
                - name (str): 设备名称
                - model (str): 设备型号
                - networkId (str): 所属网络ID
                - productType (str): 产品类型 (wireless, switch, appliance, camera)
                - firmware (str): 固件版本
                - lanIp (str): LAN IP地址
                - lat (float): 纬度坐标
                - lng (float): 经度坐标
                - address (str): 物理地址
                - notes (str): 设备备注
                - tags (list): 设备标签
                - beaconIdParams (dict): 信标ID参数（适用于无线设备）
                - floorPlanId (str): 楼层平面图ID
        
        使用场景:
            - 网络设备管理
            - 设备拓扑分析
            - 设备配置批量操作
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_devices(session, network_id)

    @activity.defn
    async def get_network_floorplans(self, network_id: str) -> List[Dict]:
        """
        获取网络楼层平面图列表
        
        API端点: GET /networks/{networkId}/floorPlans
        用途: 获取网络中的所有楼层平面图
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: 楼层平面图列表，每个平面图包含:
                - floorPlanId (str): 楼层平面图ID
                - name (str): 楼层平面图名称
                - center (dict): 中心坐标
                    - lat (float): 纬度
                    - lng (float): 经度
                - bottomLeftCorner (dict): 左下角坐标
                    - lat (float): 纬度
                    - lng (float): 经度
                - bottomRightCorner (dict): 右下角坐标
                    - lat (float): 纬度
                    - lng (float): 经度
                - topLeftCorner (dict): 左上角坐标
                    - lat (float): 纬度
                    - lng (float): 经度
                - topRightCorner (dict): 右上角坐标
                    - lat (float): 纬度
                    - lng (float): 经度
                - imageUrl (str): 平面图图片URL
                - imageUrlExpiresAt (str): 图片URL过期时间
                - imageExtension (str): 图片文件扩展名
                - width (float): 宽度（米）
                - height (float): 高度（米）
        
        使用场景:
            - 室内定位系统
            - 设备位置可视化
            - 楼层管理
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_floor_plans(session, network_id)

    @activity.defn
    async def get_network_clients_overview(self, network_id: str) -> Dict:
        """
        获取网络客户端概览统计
        
        API端点: GET /networks/{networkId}/clients/overview
        用途: 获取网络中客户端的统计概览信息
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            Dict: 客户端概览统计，包含:
                - counts (dict): 客户端数量统计
                    - total (int): 总客户端数
                    - withHeavyUsage (int): 高使用量客户端数
                - usage (dict): 流量使用统计
                    - average (int): 平均使用量（字节）
                    - withHeavyUsage (int): 高使用量阈值（字节）
        
        使用场景:
            - 网络容量规划
            - 客户端使用分析
            - 网络性能监控
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_clients_overview(session, network_id)

    @activity.defn
    async def get_organization_licenses_overview(self, org_id: str) -> Dict:
        """
        获取组织许可证概览 (Co-termination licensing)
        
        API端点: GET /organizations/{organizationId}/licenses/overview
        用途: 获取Co-termination许可模式下的许可证概览信息
        
        Args:
            org_id (str): 组织ID
            
        Returns:
            Dict: 许可证概览，包含:
                - status (str): 许可证状态 (Co-termination licensing only)
                - expirationDate (str): 许可证到期日期 (Co-termination licensing only)
                - licensedDeviceCounts (dict): 已许可设备数量统计 (Co-termination licensing only)
                    - wireless (int): 无线设备数
                    - appliance (int): 安全网关设备数
                    - switch (int): 交换机设备数
                    - camera (int): 摄像头设备数
                    - cellularGateway (int): 蜂窝网关设备数
                - licenseCount (int): 许可证总数 (Per-device licensing only)
                - states (dict): 许可证状态统计 (Per-device licensing only)
                    - active (dict): 活跃许可证统计
        
        注意:
            - 适用于Co-termination licensing模式
            - Per-device licensing使用 get_organization_licenses
        
        使用场景:
            - 许可证合规性监控
            - 许可证到期提醒
            - 设备许可规划
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_licenses_overview(session, org_id)

    @activity.defn
    async def get_floor_plan_by_id(self, network_id: str, floor_plan_id: str) -> Dict:
        """
        获取指定楼层平面图详情
        
        API端点: GET /networks/{networkId}/floorPlans/{floorPlanId}
        用途: 获取特定楼层平面图的详细信息，包括设备位置
        
        Args:
            network_id (str): 网络ID
            floor_plan_id (str): 楼层平面图ID
            
        Returns:
            Dict: 楼层平面图详情，包含:
                - floorPlanId (str): 楼层平面图ID
                - name (str): 楼层平面图名称
                - center (dict): 中心坐标
                    - lat (float): 纬度
                    - lng (float): 经度
                - bottomLeftCorner (dict): 左下角坐标
                - bottomRightCorner (dict): 右下角坐标
                - topLeftCorner (dict): 左上角坐标
                - topRightCorner (dict): 右上角坐标
                - imageUrl (str): 平面图图片URL
                - imageUrlExpiresAt (str): 图片URL过期时间
                - imageExtension (str): 图片文件扩展名
                - width (float): 宽度（米）
                - height (float): 高度（米）
                - devices (list): 设备位置列表
                    - serial (str): 设备序列号
                    - lat (float): 设备纬度
                    - lng (float): 设备经度
        
        使用场景:
            - 设备位置可视化
            - 室内导航系统
            - 设备部署规划
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_floor_plan_by_id(session, network_id, floor_plan_id)

    @activity.defn
    async def get_network_wireless_client_connection_stats(self, network_id: str, client_id: str) -> Dict:
        """
        获取指定无线客户端连接统计
        
        API端点: GET /networks/{networkId}/wireless/clients/{clientId}/connectionStats
        用途: 获取特定无线客户端的连接质量和统计信息
        
        Args:
            network_id (str): 网络ID
            client_id (str): 客户端ID
            
        Returns:
            Dict: 无线客户端连接统计，包含:
                - connectionStats (dict): 连接统计信息
                    - assoc (int): 关联次数
                    - auth (int): 认证次数
                    - dhcp (int): DHCP请求次数
                    - dns (int): DNS请求次数
                - speeds (dict): 连接速度统计
                    - downstream (int): 下行速度 (Mbps)
                    - upstream (int): 上行速度 (Mbps)
                - vlan (int): VLAN ID
                - apMac (str): 接入点MAC地址
                - channel (int): 无线信道
                - rssi (int): 信号强度 (dBm)
                - snr (int): 信噪比 (dB)
        
        使用场景:
            - 无线连接质量分析
            - 客户端故障诊断
            - 网络优化
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_wireless_client_connection_stats(session, network_id, client_id)

    # ==================== 设备级 API ====================

    @activity.defn
    async def get_device(self, serial: str) -> Dict:
        """
        获取设备详细信息
        
        API端点: GET /devices/{serial}
        用途: 获取指定设备的详细配置和状态信息
        
        Args:
            serial (str): 设备序列号
            
        Returns:
            Dict: 设备详细信息，包含:
                - serial (str): 设备序列号
                - mac (str): 设备MAC地址
                - name (str): 设备名称
                - model (str): 设备型号
                - networkId (str): 所属网络ID
                - productType (str): 产品类型 (wireless, switch, appliance, camera)
                - firmware (str): 固件版本
                - lanIp (str): LAN IP地址
                - lat (float): 纬度坐标
                - lng (float): 经度坐标
                - address (str): 物理地址
                - notes (str): 设备备注
                - tags (list): 设备标签
                - configurationUpdatedAt (str): 配置更新时间
                - url (str): 设备管理URL
                - beaconIdParams (dict): 信标ID参数（适用于无线设备）
                - floorPlanId (str): 楼层平面图ID
        
        使用场景:
            - 设备详情查看
            - 设备配置管理
            - 故障诊断
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_device_info(session, serial)

    @activity.defn
    async def get_device_appliance_uplinks_settings(self, serial: str) -> Dict:
        """
        获取设备安全网关上行链路设置
        
        API端点: GET /devices/{serial}/appliance/uplinks/settings
        用途: 获取MX安全网关设备的上行链路配置设置
        
        Args:
            serial (str): 设备序列号（必须是MX系列安全网关）
            
        Returns:
            Dict: 上行链路设置，包含:
                - interfaces (dict): 接口配置
                    - wan1 (dict): WAN1接口设置
                        - enabled (bool): 是否启用
                        - vlanTagging (dict): VLAN标记设置
                        - svis (dict): SVI配置
                        - pppoe (dict): PPPoE配置
                    - wan2 (dict): WAN2接口设置
                    - cellular (dict): 蜂窝接口设置
        
        使用场景:
            - 网关配置管理
            - 上行链路故障排查
            - 网络连接配置
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_device_appliance_uplinks_settings(session, serial)

    @activity.defn
    async def get_device_clients(self, serial: str) -> List[Dict]:
        """
        获取设备客户端列表
        
        API端点: GET /devices/{serial}/clients
        用途: 获取连接到指定设备的所有客户端
        
        Args:
            serial (str): 设备序列号
            
        Returns:
            List[Dict]: 设备客户端列表，每个客户端包含:
                - id (str): 客户端ID
                - mac (str): 客户端MAC地址
                - description (str): 客户端描述
                - ip (str): IP地址
                - user (str): 用户名
                - vlan (int): VLAN ID
                - switchport (str): 交换机端口（有线客户端）
                - usage (dict): 流量使用统计
                - status (str): 连接状态
        
        使用场景:
            - 设备级客户端监控
            - 端口使用分析
            - 客户端故障排查
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_device_clients(session, serial)

    @activity.defn
    async def get_device_lldp_cdp(self, serial: str) -> Dict:
        """
        获取设备LLDP/CDP邻居发现信息
        
        API端点: GET /devices/{serial}/lldp_cdp
        用途: 获取设备通过LLDP和CDP协议发现的邻居设备信息
        
        Args:
            serial (str): 设备序列号
            
        Returns:
            Dict: LLDP/CDP信息，包含:
                - sourceMac (str): 源设备MAC地址
                - ports (dict): 端口邻居信息
                    - {portId} (dict): 端口ID对应的邻居信息
                        - lldp (dict): LLDP发现的邻居
                            - systemName (str): 系统名称
                            - portId (str): 端口ID
                            - portDescription (str): 端口描述
                            - systemDescription (str): 系统描述
                            - systemCapabilities (list): 系统能力
                            - managementAddress (str): 管理地址
                        - cdp (dict): CDP发现的邻居
                            - deviceId (str): 设备ID
                            - portId (str): 端口ID
                            - address (str): 设备地址
                            - sourcePort (str): 源端口
        
        使用场景:
            - 网络拓扑发现
            - 设备连接验证
            - 网络故障排查
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_device_lldp_cdp(session, serial)

    @activity.defn
    async def get_device_loss_and_latency_history(self, serial: str) -> List[Dict]:
        """
        获取设备丢包和延迟历史
        
        API端点: GET /devices/{serial}/lossAndLatencyHistory
        用途: 获取设备的网络质量历史数据，包括丢包率和延迟
        
        Args:
            serial (str): 设备序列号
            
        Returns:
            List[Dict]: 丢包和延迟历史数据，每个数据点包含:
                - startTs (str): 开始时间戳
                - endTs (str): 结束时间戳
                - lossPercent (float): 丢包率百分比
                - latencyMs (float): 延迟毫秒数
                - jitterMs (float): 抖动毫秒数
        
        使用场景:
            - 网络质量监控
            - 性能趋势分析
            - SLA监控
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_device_loss_and_latency_history(session, serial)

    # ==================== 无线 API ====================

    @activity.defn
    async def get_network_wireless_ssids(self, network_id: str) -> List[Dict]:
        """
        获取网络无线SSID配置列表
        
        API端点: GET /networks/{networkId}/wireless/ssids
        用途: 获取网络中所有无线SSID的配置信息
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: SSID配置列表，每个SSID包含:
                - number (int): SSID编号 (0-14)
                - name (str): SSID名称
                - enabled (bool): 是否启用
                - splashPage (str): 欢迎页面类型
                - ssidAdminAccessible (bool): 管理员是否可访问
                - authMode (str): 认证模式 (open, psk, 8021x-meraki, etc.)
                - encryptionMode (str): 加密模式 (wpa, wpa-eap, etc.)
                - wpaEncryptionMode (str): WPA加密模式
                - radiusServers (list): RADIUS服务器配置
                - radiusAccountingServers (list): RADIUS计费服务器
                - radiusAttributeForGroupPolicies (str): 组策略RADIUS属性
                - ipAssignmentMode (str): IP分配模式
                - useVlanTagging (bool): 是否使用VLAN标记
                - concentratorNetworkId (str): 集中器网络ID
                - vlanId (int): VLAN ID
                - walledGardenEnabled (bool): 是否启用围墙花园
                - walledGardenRanges (list): 围墙花园范围
                - minBitrate (int): 最小比特率
                - bandSelection (str): 频段选择
                - perClientBandwidthLimitUp (int): 每客户端上行带宽限制
                - perClientBandwidthLimitDown (int): 每客户端下行带宽限制
        
        使用场景:
            - 无线网络配置管理
            - SSID安全策略审计
            - 无线网络规划
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_wireless_ssids(session, network_id)

    @activity.defn
    async def get_network_wireless_settings(self, network_id: str) -> Dict:
        """
        获取网络无线全局设置
        
        API端点: GET /networks/{networkId}/wireless/settings
        用途: 获取网络的无线全局配置设置
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            Dict: 无线设置，包含:
                - meshingEnabled (bool): 是否启用Mesh组网
                - ipv6BridgeEnabled (bool): 是否启用IPv6桥接
                - locationAnalyticsEnabled (bool): 是否启用位置分析
                - upgradeStrategy (str): 升级策略
                - ledLightsOn (bool): LED指示灯是否开启
                - regulatoryDomain (dict): 监管域设置
                    - name (str): 监管域名称
                    - countryCode (str): 国家代码
        
        使用场景:
            - 无线网络全局配置
            - 合规性设置管理
            - 网络优化配置
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_wireless_settings(session, network_id)

    @activity.defn
    async def get_network_wireless_clients_connection_stats(self, network_id: str) -> List[Dict]:
        """
        获取网络无线客户端连接统计
        
        API端点: GET /networks/{networkId}/wireless/clients/connectionStats
        用途: 获取网络中所有无线客户端的连接质量统计信息
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: 无线客户端连接统计列表，每个客户端包含:
                - mac (str): 客户端MAC地址
                - connectionStats (dict): 连接统计
                    - assoc (int): 关联次数
                    - auth (int): 认证次数
                    - dhcp (int): DHCP请求次数
                    - dns (int): DNS请求次数
                - speeds (dict): 连接速度
                    - downstream (int): 下行速度 (Mbps)
                    - upstream (int): 上行速度 (Mbps)
                - vlan (int): VLAN ID
                - apMac (str): 接入点MAC地址
                - channel (int): 无线信道
                - rssi (int): 信号强度 (dBm)
                - snr (int): 信噪比 (dB)
        
        使用场景:
            - 无线网络性能监控
            - 客户端连接质量分析
            - 网络优化决策
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_wireless_clients_connection_stats(session, network_id)

    @activity.defn
    async def get_network_wireless_air_marshal(self, network_id: str) -> List[Dict]:
        """
        获取网络无线Air Marshal安全检测
        
        API端点: GET /networks/{networkId}/wireless/airMarshal
        用途: 获取Air Marshal检测到的恶意或未授权无线设备
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: Air Marshal检测结果，每个检测项包含:
                - bssid (str): 检测到的BSSID
                - ssid (str): 检测到的SSID
                - channels (list): 使用的信道列表
                - firstSeen (str): 首次发现时间
                - lastSeen (str): 最后发现时间
                - wiredMacs (list): 关联的有线MAC地址
                - type (str): 检测类型 (rogue, neighbor, other)
                - subType (str): 子类型
                - severity (str): 严重程度 (high, medium, low)
        
        使用场景:
            - 无线安全监控
            - 恶意AP检测
            - 网络安全审计
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_wireless_air_marshal(session, network_id)

    # ==================== 安全网关 API ====================

    @activity.defn
    async def get_network_appliance_settings(self, network_id: str) -> Dict:
        """
        获取网络安全网关全局设置
        
        API端点: GET /networks/{networkId}/appliance/settings
        用途: 获取MX安全网关的全局配置设置
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            Dict: 安全网关设置，包含:
                - clientTrackingMethod (str): 客户端跟踪方法
                - deploymentMode (str): 部署模式 (routed, passthrough)
                - dynamicDns (dict): 动态DNS设置
                    - enabled (bool): 是否启用
                    - prefix (str): 前缀
                    - url (str): 动态DNS URL
        
        使用场景:
            - 安全网关配置管理
            - 网络部署模式设置
            - 动态DNS配置
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_appliance_settings(session, network_id)

    @activity.defn
    async def get_network_appliance_firewall_l3_rules(self, network_id: str) -> List[Dict]:
        """
        获取网络安全网关L3防火墙规则
        
        API端点: GET /networks/{networkId}/appliance/firewall/l3FirewallRules
        用途: 获取MX安全网关的三层防火墙规则配置
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: L3防火墙规则列表，每个规则包含:
                - comment (str): 规则注释
                - policy (str): 策略 (allow, deny)
                - protocol (str): 协议 (tcp, udp, icmp, any)
                - srcPort (str): 源端口
                - srcCidr (str): 源CIDR
                - destPort (str): 目标端口
                - destCidr (str): 目标CIDR
                - syslogEnabled (bool): 是否启用系统日志
        
        使用场景:
            - 网络安全策略管理
            - 防火墙规则审计
            - 访问控制配置
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_appliance_firewall_l3_rules(session, network_id)

    @activity.defn
    async def get_network_appliance_firewall_l7_rules(self, network_id: str) -> List[Dict]:
        """
        获取网络安全网关L7应用层防火墙规则
        
        API端点: GET /networks/{networkId}/appliance/firewall/l7FirewallRules
        用途: 获取MX安全网关的七层应用防火墙规则配置
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: L7防火墙规则列表，每个规则包含:
                - policy (str): 策略 (deny)
                - type (str): 规则类型 (application, applicationCategory, host, port, ipRange)
                - value (str): 规则值
                    - 应用名称 (如 "Facebook", "YouTube")
                    - 应用类别 (如 "Social Networking", "Video & Music")
                    - 主机名 (如 "google.com")
                    - 端口范围 (如 "80", "443", "1000-2000")
                    - IP范围 (如 "192.168.1.0/24")
        
        使用场景:
            - 应用层访问控制
            - 内容过滤策略
            - 带宽管理
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_appliance_firewall_l7_rules(session, network_id)

    @activity.defn
    async def get_network_appliance_content_filtering(self, network_id: str) -> Dict:
        """
        获取网络安全网关内容过滤设置
        
        API端点: GET /networks/{networkId}/appliance/contentFiltering
        用途: 获取MX安全网关的内容过滤和URL过滤配置
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            Dict: 内容过滤设置，包含:
                - allowedUrlPatterns (list): 允许的URL模式列表
                - blockedUrlPatterns (list): 阻止的URL模式列表
                - blockedUrlCategories (list): 阻止的URL类别
                    - id (str): 类别ID
                    - name (str): 类别名称
                - urlCategoryListSize (str): URL类别列表大小 (topSites, fullList)
        
        使用场景:
            - 网络内容安全管理
            - URL访问控制
            - 企业上网策略
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_appliance_content_filtering(session, network_id)

    @activity.defn
    async def get_network_appliance_firewall_firewalled_services(self, network_id: str) -> List[Dict]:
        """
        获取网络安全网关防火墙服务配置
        
        API端点: GET /networks/{networkId}/appliance/firewall/firewalledServices
        用途: 获取MX安全网关对特定服务的防火墙访问控制配置
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: 防火墙服务列表，每个服务包含:
                - service (str): 服务名称 (ICMP, SNMP, web, SSH)
                - access (str): 访问策略 (blocked, restricted, unrestricted)
                - allowedIps (list): 允许访问的IP地址列表（当access为restricted时）
        
        使用场景:
            - 管理服务访问控制
            - 网络安全策略配置
            - 远程管理权限设置
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_appliance_firewall_firewalled_services(session, network_id)

    @activity.defn
    async def get_network_appliance_vlans(self, network_id: str) -> List[Dict]:
        """
        获取网络安全网关VLAN配置
        
        API端点: GET /networks/{networkId}/appliance/vlans
        用途: 获取MX安全网关的VLAN配置信息
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: VLAN配置列表，每个VLAN包含:
                - id (str): VLAN ID
                - name (str): VLAN名称
                - applianceIp (str): 网关IP地址
                - subnet (str): 子网CIDR
                - groupPolicyId (str): 组策略ID
                - templateVlanType (str): 模板VLAN类型
                - cidr (str): CIDR表示法
                - mask (int): 子网掩码位数
                - dhcpHandling (str): DHCP处理方式
                - dhcpLeaseTime (str): DHCP租期
                - dhcpBootOptionsEnabled (bool): 是否启用DHCP启动选项
                - dhcpOptions (list): DHCP选项配置
                - reservedIpRanges (list): 保留IP范围
                - dnsNameservers (str): DNS服务器
                - dhcpRelayServerIps (list): DHCP中继服务器IP
        
        使用场景:
            - VLAN网络规划
            - 子网配置管理
            - DHCP服务配置
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_appliance_vlans(session, network_id)

    # ==================== 交换机 API ====================

    @activity.defn
    async def get_network_switch_settings(self, network_id: str) -> Dict:
        """
        获取网络交换机全局设置
        
        API端点: GET /networks/{networkId}/switch/settings
        用途: 获取MS交换机的全局配置设置
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            Dict: 交换机设置，包含:
                - vlan (int): 默认VLAN ID
                - useCombinedPower (bool): 是否使用组合供电
                - powerExceptions (list): 供电异常配置
                    - serial (str): 设备序列号
                    - powerType (str): 供电类型
        
        使用场景:
            - 交换机全局配置管理
            - VLAN默认设置
            - 供电策略配置
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_switch_settings(session, network_id)

    @activity.defn
    async def get_network_switch_access_control_lists(self, network_id: str) -> List[Dict]:
        """
        获取网络交换机访问控制列表(ACL)
        
        API端点: GET /networks/{networkId}/switch/accessControlLists
        用途: 获取MS交换机的访问控制列表配置
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: ACL规则列表，每个规则包含:
                - comment (str): 规则注释
                - policy (str): 策略 (allow, deny)
                - ipVersion (str): IP版本 (ipv4, ipv6, any)
                - protocol (str): 协议 (tcp, udp, any)
                - srcCidr (str): 源CIDR
                - srcPort (str): 源端口
                - dstCidr (str): 目标CIDR
                - dstPort (str): 目标端口
                - vlan (str): VLAN范围
        
        使用场景:
            - 交换机安全策略配置
            - 网络访问控制
            - 流量过滤规则管理
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_switch_access_control_lists(session, network_id)

    @activity.defn
    async def get_network_switch_access_policies(self, network_id: str) -> List[Dict]:
        """
        获取网络交换机访问策略
        
        API端点: GET /networks/{networkId}/switch/accessPolicies
        用途: 获取MS交换机的端口访问策略配置
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: 访问策略列表，每个策略包含:
                - name (str): 策略名称
                - radiusServers (list): RADIUS服务器配置
                - radiusTestingEnabled (bool): 是否启用RADIUS测试
                - hostMode (str): 主机模式 (single, multiple)
                - accessPolicyType (str): 访问策略类型
                - guestVlanId (int): 访客VLAN ID
                - dot1xControlDirection (str): 802.1X控制方向
        
        使用场景:
            - 端口安全策略管理
            - 802.1X认证配置
            - 访客网络策略
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_switch_access_policies(session, network_id)

    @activity.defn
    async def get_network_switch_dhcp_server_policy(self, network_id: str) -> Dict:
        """
        获取网络交换机DHCP服务器策略
        
        API端点: GET /networks/{networkId}/switch/dhcpServerPolicy
        用途: 获取MS交换机的DHCP服务器策略配置
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            Dict: DHCP服务器策略，包含:
                - defaultPolicy (str): 默认策略 (allow, block)
                - allowedServers (list): 允许的DHCP服务器IP列表
                - blockedServers (list): 阻止的DHCP服务器IP列表
                - arpInspectionEnabled (bool): 是否启用ARP检查
        
        使用场景:
            - DHCP安全策略配置
            - 防止恶意DHCP服务器
            - ARP欺骗防护
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_switch_dhcp_server_policy(session, network_id)

    @activity.defn
    async def get_network_switch_ports(self, serial: str) -> List[Dict]:
        """
        获取交换机端口配置
        
        API端点: GET /devices/{serial}/switch/ports
        用途: 获取MS交换机设备的所有端口配置信息
        
        Args:
            serial (str): 交换机设备序列号
            
        Returns:
            List[Dict]: 端口配置列表，每个端口包含:
                - portId (str): 端口ID
                - name (str): 端口名称
                - tags (list): 端口标签
                - enabled (bool): 是否启用
                - type (str): 端口类型 (access, trunk)
                - vlan (int): 访问VLAN ID
                - allowedVlans (str): 允许的VLAN列表
                - poeEnabled (bool): 是否启用PoE供电
                - isolationEnabled (bool): 是否启用端口隔离
                - rstpEnabled (bool): 是否启用RSTP
                - stpGuard (str): STP保护类型
                - linkNegotiation (str): 链路协商模式
                - portScheduleId (str): 端口调度ID
                - udld (str): UDLD配置
                - accessPolicyType (str): 访问策略类型
                - accessPolicyNumber (int): 访问策略编号
                - macAllowList (list): MAC地址白名单
                - stickyMacAllowList (list): 粘性MAC白名单
                - stickyMacAllowListLimit (int): 粘性MAC限制数量
                - stormControlEnabled (bool): 是否启用风暴控制
        
        使用场景:
            - 交换机端口管理
            - VLAN配置
            - PoE供电管理
            - 端口安全策略
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_switch_ports(session, serial)

    # ==================== 传感器 API ====================

    @activity.defn
    async def get_network_sensor_alerts_profiles(self, network_id: str) -> List[Dict]:
        """
        获取网络传感器告警配置文件
        
        API端点: GET /networks/{networkId}/sensor/alerts/profiles
        用途: 获取MT传感器的告警配置文件和阈值设置
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: 传感器告警配置列表，每个配置包含:
                - profileId (str): 配置文件ID
                - name (str): 配置文件名称
                - conditions (list): 告警条件列表
                    - metric (str): 监控指标 (temperature, humidity, tvoc, etc.)
                    - threshold (dict): 阈值设置
                        - temperature (dict): 温度阈值
                            - celsius (float): 摄氏度
                            - fahrenheit (float): 华氏度
                            - quality (str): 质量等级
                        - humidity (dict): 湿度阈值
                            - relativePercentage (int): 相对湿度百分比
                            - quality (str): 质量等级
                    - direction (str): 触发方向 (above, below)
                - recipients (list): 告警接收者
                    - emails (list): 邮件地址列表
                    - smsNumbers (list): 短信号码列表
                    - httpServerIds (list): HTTP服务器ID列表
        
        使用场景:
            - 环境监控告警配置
            - 传感器阈值管理
            - 告警通知设置
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_sensor_alerts_profiles(session, network_id)

    @activity.defn
    async def get_network_sensor_alerts_current_overview_by_metric(self, network_id: str) -> List[Dict]:
        """
        获取网络传感器当前告警概览（按指标分组）
        
        API端点: GET /networks/{networkId}/sensor/alerts/current/overview/byMetric
        用途: 获取MT传感器当前活跃告警的概览统计，按监控指标分组
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: 按指标分组的告警概览，每个指标包含:
                - metric (str): 监控指标名称 (temperature, humidity, tvoc, pm25, noise, etc.)
                - count (int): 该指标的告警数量
                - conditions (list): 告警条件详情
                    - serial (str): 传感器设备序列号
                    - scope (str): 告警范围
                    - condition (dict): 具体告警条件
                        - threshold (dict): 阈值信息
                        - direction (str): 触发方向
        
        使用场景:
            - 传感器告警监控仪表板
            - 环境异常快速识别
            - 告警统计分析
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_sensor_alerts_current_overview_by_metric(session, network_id)

    # ==================== 摄像头 API ====================

    @activity.defn
    async def get_network_camera_quality_retention_profiles(self, network_id: str) -> List[Dict]:
        """
        获取网络摄像头画质保留配置文件
        
        API端点: GET /networks/{networkId}/camera/qualityRetentionProfiles
        用途: 获取MV摄像头的视频画质和保留时间配置文件
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: 画质保留配置列表，每个配置包含:
                - id (str): 配置文件ID
                - name (str): 配置文件名称
                - motionBasedRetentionEnabled (bool): 是否启用基于运动的保留
                - restrictedBandwidthModeEnabled (bool): 是否启用受限带宽模式
                - audioRecordingEnabled (bool): 是否启用音频录制
                - cloudArchiveEnabled (bool): 是否启用云存档
                - maxRetentionDays (int): 最大保留天数
                - videoSettings (dict): 视频设置
                    - MV21/MV71 (dict): 不同型号的设置
                        - quality (str): 画质 (Standard, Enhanced, High)
                        - resolution (str): 分辨率
        
        使用场景:
            - 摄像头录制策略配置
            - 存储空间管理
            - 视频质量优化
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_camera_quality_retention_profiles(session, network_id)

    @activity.defn
    async def get_network_camera_schedules(self, network_id: str) -> List[Dict]:
        """
        获取网络摄像头录制计划
        
        API端点: GET /networks/{networkId}/camera/schedules
        用途: 获取MV摄像头的录制时间计划配置
        
        Args:
            network_id (str): 网络ID
            
        Returns:
            List[Dict]: 录制计划列表，每个计划包含:
                - id (str): 计划ID
                - name (str): 计划名称
                - schedule (dict): 计划详情
                    - monday (list): 周一录制时间段
                        - from (str): 开始时间 (HH:MM格式)
                        - to (str): 结束时间 (HH:MM格式)
                    - tuesday (list): 周二录制时间段
                    - wednesday (list): 周三录制时间段
                    - thursday (list): 周四录制时间段
                    - friday (list): 周五录制时间段
                    - saturday (list): 周六录制时间段
                    - sunday (list): 周日录制时间段
        
        使用场景:
            - 摄像头录制时间管理
            - 存储资源优化
            - 安全监控计划配置
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_network_camera_schedules(session, network_id)

    # ==================== 统计 API ====================

    @activity.defn
    async def get_organization_summary_top_applications_by_usage(self, org_id: str) -> List[Dict]:
        """
        获取组织顶级应用使用量统计
        
        API端点: GET /organizations/{organizationId}/summary/top/applications/byUsage
        用途: 获取组织内流量使用量最高的应用程序排行榜
        
        Args:
            org_id (str): 组织ID
            
        Returns:
            List[Dict]: 应用使用量排行，每个应用包含:
                - name (str): 应用名称 (如 "HTTP", "HTTPS", "Facebook", "YouTube")
                - usage (dict): 使用量统计
                    - total (int): 总流量字节数
                    - downstream (int): 下行流量字节数
                    - upstream (int): 上行流量字节数
                - percentage (float): 占总流量的百分比
        
        使用场景:
            - 网络流量分析和优化
            - 带宽使用策略制定
            - 应用访问控制决策
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_summary_top_applications_by_usage(session, org_id)

    @activity.defn
    async def get_organization_summary_top_clients_by_usage(self, org_id: str) -> List[Dict]:
        """
        获取组织顶级客户端使用量统计
        
        API端点: GET /organizations/{organizationId}/summary/top/clients/byUsage
        用途: 获取组织内流量使用量最高的客户端设备排行榜
        
        Args:
            org_id (str): 组织ID
            
        Returns:
            List[Dict]: 客户端使用量排行，每个客户端包含:
                - name (str): 客户端名称或描述
                - mac (str): 客户端MAC地址
                - usage (dict): 使用量统计
                    - total (int): 总流量字节数
                    - downstream (int): 下行流量字节数
                    - upstream (int): 上行流量字节数
                - percentage (float): 占总流量的百分比
                - network (dict): 所属网络信息
                    - id (str): 网络ID
                    - name (str): 网络名称
        
        使用场景:
            - 用户流量监控和分析
            - 网络资源分配优化
            - 异常流量检测和调查
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_summary_top_clients_by_usage(session, org_id)

    @activity.defn
    async def get_organization_summary_top_devices_by_usage(self, org_id: str) -> List[Dict]:
        """
        获取组织顶级设备使用量统计
        
        API端点: GET /organizations/{organizationId}/summary/top/devices/byUsage
        用途: 获取组织内流量使用量最高的网络设备排行榜
        
        Args:
            org_id (str): 组织ID
            
        Returns:
            List[Dict]: 设备使用量排行，每个设备包含:
                - name (str): 设备名称
                - model (str): 设备型号 (如 "MR44", "MS220-8P", "MX68")
                - serial (str): 设备序列号
                - usage (dict): 使用量统计
                    - total (int): 总流量字节数
                    - downstream (int): 下行流量字节数
                    - upstream (int): 上行流量字节数
                - percentage (float): 占总流量的百分比
                - network (dict): 所属网络信息
                    - id (str): 网络ID
                    - name (str): 网络名称
                - productType (str): 产品类型 (wireless, switch, appliance)
        
        使用场景:
            - 设备性能监控和分析
            - 网络负载均衡优化
            - 设备容量规划和升级
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_summary_top_devices_by_usage(session, org_id)

    @activity.defn
    async def get_organization_summary_top_appliances_by_utilization(self, org_id: str) -> List[Dict]:
        """
        获取组织安全网关利用率统计
        
        API端点: GET /organizations/{organizationId}/summary/top/appliances/byUtilization
        用途: 获取组织内利用率最高的MX安全网关设备排行榜
        
        Args:
            org_id (str): 组织ID
            
        Returns:
            List[Dict]: 安全网关利用率排行，每个设备包含:
                - name (str): 设备名称
                - model (str): 设备型号 (如 "MX68", "MX84", "MX100")
                - serial (str): 设备序列号
                - utilization (dict): 利用率统计
                    - average (float): 平均利用率百分比
                    - byUplink (list): 按上行链路统计
                        - interface (str): 接口名称 (wan1, wan2, cellular)
                        - sent (int): 发送字节数
                        - received (int): 接收字节数
                        - utilization (float): 该接口利用率
                - network (dict): 所属网络信息
                    - id (str): 网络ID
                    - name (str): 网络名称
        
        使用场景:
            - 安全网关性能监控
            - 上行链路容量规划
            - 网络瓶颈识别和优化
        """
        api = MerakiAPI()
        async with aiohttp.ClientSession() as session:
            return await api.get_organization_summary_top_appliances_by_utilization(session, org_id)

    # ==================== 特殊功能 API ====================

    @activity.defn
    async def get_all_organization_devices_with_name_filter(self, org_id: str, name_filter: str) -> List[Dict]:
        """
        获取组织中包含指定名称关键词的所有设备
        
        API端点: 基于 GET /organizations/{organizationId}/devices 的扩展功能
        用途: 在组织的所有设备中搜索包含指定关键词的设备
        
        Args:
            org_id (str): 组织ID
            name_filter (str): 设备名称过滤关键词
            
        Returns:
            List[Dict]: 匹配的设备列表，每个设备包含:
                - serial (str): 设备序列号
                - mac (str): 设备MAC地址
                - name (str): 设备名称
                - model (str): 设备型号
                - networkId (str): 所属网络ID
                - productType (str): 产品类型
                - firmware (str): 固件版本
                - lanIp (str): LAN IP地址
                - lat (float): 纬度坐标
                - lng (float): 经度坐标
                - address (str): 物理地址
                - notes (str): 设备备注
                - tags (list): 设备标签
        
        使用场景:
            - 设备快速搜索和定位
            - 批量设备管理
            - 设备清单筛选
        """
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
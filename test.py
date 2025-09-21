#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meraki 资源摸底测试脚本
用于发现用户 API Key 下有哪些 Meraki 资源被纳管

使用方法：
python test.py <API_KEY>
"""

import asyncio
import aiohttp
import json
import sys
from collections import defaultdict
from typing import Dict, List, Set
from merakiAPI import MerakiAPI


class MerakiDiscovery:
    """Meraki 资源发现类"""
    
    def __init__(self, api_key: str):
        self.api = MerakiAPI(api_key)
        self.discovery_results = {
            'organizations': [],
            'networks': [],
            'devices': [],
            'device_types': set(),
            'network_types': set(),
            'summary': {}
        }
    
    async def discover_all(self, session: aiohttp.ClientSession) -> Dict:
        """
        完整的资源发现流程
        
        Args:
            session: aiohttp客户端会话
            
        Returns:
            发现结果字典
        """
        print("🔍 开始 Meraki 资源发现...")
        
        try:
            # 1. 发现组织
            await self._discover_organizations(session)
            
            # 2. 发现网络
            await self._discover_networks(session)
            
            # 3. 发现设备
            await self._discover_devices(session)
            
            # 4. 深度探测各类型资源
            await self._deep_discovery(session)
            
            # 5. 生成摘要
            self._generate_summary()
            
            print("✅ 资源发现完成！")
            return self.discovery_results
            
        except Exception as e:
            print(f"❌ 资源发现失败: {e}")
            raise
    
    async def _discover_organizations(self, session: aiohttp.ClientSession):
        """发现组织"""
        print("\n📋 发现组织...")
        
        try:
            orgs = await self.api.get_organizations(session)
            self.discovery_results['organizations'] = orgs
            
            print(f"  找到 {len(orgs)} 个组织:")
            for org in orgs:
                print(f"    - {org['name']} (ID: {org['id']})")
                
        except Exception as e:
            print(f"  ⚠️  获取组织失败: {e}")
            self.discovery_results['organizations'] = []
    
    async def _discover_networks(self, session: aiohttp.ClientSession):
        """发现网络"""
        print("\n🌐 发现网络...")
        
        all_networks = []
        network_types = set()
        
        for org in self.discovery_results['organizations']:
            org_id = org['id']
            org_name = org['name']
            
            try:
                networks = await self.api.get_organization_networks(session, org_id)
                
                print(f"  组织 '{org_name}' 有 {len(networks)} 个网络:")
                for network in networks:
                    network_types.update(network.get('productTypes', []))
                    print(f"    - {network['name']} (类型: {network.get('productTypes', 'unknown')})")
                
                all_networks.extend(networks)
                
            except Exception as e:
                print(f"  ⚠️  获取组织 {org_name} 的网络失败: {e}")
        
        self.discovery_results['networks'] = all_networks
        self.discovery_results['network_types'] = network_types
        print(f"  📊 发现的网络类型: {sorted(network_types)}")
    
    async def _discover_devices(self, session: aiohttp.ClientSession):
        """发现设备"""
        print("\n📱 发现设备...")
        
        all_devices = []
        device_types = set()
        device_models = set()
        
        for org in self.discovery_results['organizations']:
            org_id = org['id']
            org_name = org['name']
            
            try:
                devices = await self.api.get_organization_devices(session, org_id)
                
                print(f"  组织 '{org_name}' 有 {len(devices)} 个设备:")
                
                # 按设备类型分组统计
                type_count = defaultdict(int)
                model_count = defaultdict(int)
                
                for device in devices:
                    product_type = device.get('productType', 'unknown')
                    model = device.get('model', 'unknown')
                    
                    device_types.add(product_type)
                    device_models.add(model)
                    type_count[product_type] += 1
                    model_count[model] += 1
                
                # 显示统计信息
                for device_type, count in type_count.items():
                    print(f"    - {device_type}: {count} 台")
                
                all_devices.extend(devices)
                
            except Exception as e:
                print(f"  ⚠️  获取组织 {org_name} 的设备失败: {e}")
        
        self.discovery_results['devices'] = all_devices
        self.discovery_results['device_types'] = device_types
        self.discovery_results['device_models'] = device_models
        print(f"  📊 发现的设备类型: {sorted(device_types)}")
        print(f"  📊 发现的设备型号: {sorted(device_models)}")
    
    async def _deep_discovery(self, session: aiohttp.ClientSession):
        """深度探测各类型资源"""
        print("\n🔬 深度资源探测...")
        
        device_types = self.discovery_results['device_types']
        networks = self.discovery_results['networks']
        
        # 为每种设备类型探测相应的配置 - 顺序执行避免输出混乱
        for network in networks[:3]:  # 限制前3个网络避免过多请求
            network_id = network['id']
            network_name = network['name']
            network_product_types = network.get('productTypes', [])
            
            print(f"  探测网络: {network_name}")
            
            # 根据网络支持的产品类型进行探测 - 顺序执行
            if 'wireless' in network_product_types:
                await self._discover_wireless_resources(session, network_id, network_name)
            
            if 'appliance' in network_product_types:
                await self._discover_appliance_resources(session, network_id, network_name)
            
            if 'switch' in network_product_types:
                await self._discover_switch_resources(session, network_id, network_name)
            
            if 'sensor' in network_product_types:
                await self._discover_sensor_resources(session, network_id, network_name)
            
            if 'camera' in network_product_types:
                await self._discover_camera_resources(session, network_id, network_name)
        
        # 测试组织级统计API
        await self._discover_organization_statistics(session)
    
    async def _discover_wireless_resources(self, session: aiohttp.ClientSession, 
                                         network_id: str, network_name: str):
        """探测无线资源"""
        print(f"    📡 探测无线资源 ({network_name})...")
        
        try:
            # 获取 SSID 信息
            ssids = await self.api.get_network_wireless_ssids(session, network_id)
            enabled_ssids = [ssid for ssid in ssids if ssid.get('enabled', False)]
            print(f"      - SSID: {len(ssids)} 个 (启用: {len(enabled_ssids)} 个)")
            
            # 获取无线设置
            try:
                wireless_settings = await self.api.get_network_wireless_settings(session, network_id)
                print(f"      - 无线设置: ✅")
            except:
                print(f"      - 无线设置: ❌")
            
            # 获取无线客户端连接统计
            try:
                connection_stats = await self.api.get_network_wireless_clients_connection_stats(session, network_id)
                print(f"      - 客户端连接统计: {len(connection_stats)} 条记录")
            except:
                print(f"      - 客户端连接统计: ❌")
            
            # 获取Air Marshal检测
            try:
                air_marshal = await self.api.get_network_wireless_air_marshal(session, network_id)
                print(f"      - Air Marshal检测: {len(air_marshal)} 个威胁")
            except:
                print(f"      - Air Marshal检测: ❌")
            
        except Exception as e:
            print(f"      ⚠️  无线资源探测失败: {e}")
    
    async def _discover_appliance_resources(self, session: aiohttp.ClientSession, 
                                          network_id: str, network_name: str):
        """探测安全网关资源"""
        print(f"    🛡️  探测安全网关资源 ({network_name})...")
        
        try:
            # 获取安全网关设置
            try:
                appliance_settings = await self.api.get_network_appliance_settings(session, network_id)
                print(f"      - 安全网关设置: ✅")
            except:
                print(f"      - 安全网关设置: ❌")
            
            # 获取防火墙规则
            try:
                l3_rules = await self.api.get_network_appliance_firewall_l3_rules(session, network_id)
                print(f"      - L3防火墙规则: {len(l3_rules)} 条")
            except:
                print(f"      - L3防火墙规则: ❌")
            
            try:
                l7_rules = await self.api.get_network_appliance_firewall_l7_rules(session, network_id)
                print(f"      - L7防火墙规则: {len(l7_rules)} 条")
            except:
                print(f"      - L7防火墙规则: ❌")
            
            # 获取内容过滤
            try:
                content_filtering = await self.api.get_network_appliance_content_filtering(session, network_id)
                print(f"      - 内容过滤: ✅")
            except:
                print(f"      - 内容过滤: ❌")
            
            # 获取防火墙服务
            try:
                firewalled_services = await self.api.get_network_appliance_firewall_firewalled_services(session, network_id)
                print(f"      - 防火墙服务: {len(firewalled_services)} 个")
            except:
                print(f"      - 防火墙服务: ❌")
            
            # 获取 VLAN 配置
            try:
                vlans = await self.api.get_network_appliance_vlans(session, network_id)
                print(f"      - VLAN配置: {len(vlans)} 个")
            except:
                print(f"      - VLAN配置: ❌")
                
        except Exception as e:
            print(f"      ⚠️  安全网关资源探测失败: {e}")
    
    async def _discover_switch_resources(self, session: aiohttp.ClientSession, 
                                       network_id: str, network_name: str):
        """探测交换机资源"""
        print(f"    🔌 探测交换机资源 ({network_name})...")
        
        try:
            # 获取交换机设置
            try:
                switch_settings = await self.api.get_network_switch_settings(session, network_id)
                print(f"      - 交换机设置: ✅")
            except:
                print(f"      - 交换机设置: ❌")
            
            # 获取访问控制列表
            try:
                acls = await self.api.get_network_switch_access_control_lists(session, network_id)
                print(f"      - 访问控制列表: {len(acls)} 个")
            except:
                print(f"      - 访问控制列表: ❌")
            
            # 获取访问策略
            try:
                access_policies = await self.api.get_network_switch_access_policies(session, network_id)
                print(f"      - 访问策略: {len(access_policies)} 个")
            except:
                print(f"      - 访问策略: ❌")
            
            # 获取DHCP服务器策略
            try:
                dhcp_policy = await self.api.get_network_switch_dhcp_server_policy(session, network_id)
                print(f"      - DHCP服务器策略: ✅")
            except:
                print(f"      - DHCP服务器策略: ❌")
            
            # 获取交换机设备的端口信息
            switch_devices = [d for d in self.discovery_results['devices'] 
                            if d.get('productType') == 'switch' and d.get('networkId') == network_id]
            
            if switch_devices:
                switch_serial = switch_devices[0]['serial']
                try:
                    ports = await self.api.get_network_switch_ports(session, switch_serial)
                    print(f"      - 交换机端口: {len(ports)} 个")
                except:
                    print(f"      - 交换机端口: ❌")
            
        except Exception as e:
            print(f"      ⚠️  交换机资源探测失败: {e}")
    
    async def _discover_sensor_resources(self, session: aiohttp.ClientSession, 
                                       network_id: str, network_name: str):
        """探测传感器资源"""
        print(f"    🌡️  探测传感器资源 ({network_name})...")
        
        try:
            # 获取传感器告警配置
            try:
                alert_profiles = await self.api.get_network_sensor_alerts_profiles(session, network_id)
                print(f"      - 告警配置: {len(alert_profiles)} 个")
            except:
                print(f"      - 告警配置: ❌")
            
            # 获取当前告警概览
            try:
                current_alerts = await self.api.get_network_sensor_alerts_current_overview_by_metric(session, network_id)
                print(f"      - 当前告警: {len(current_alerts)} 个")
            except:
                print(f"      - 当前告警: ❌")
                
        except Exception as e:
            print(f"      ⚠️  传感器资源探测失败: {e}")
    
    async def _discover_camera_resources(self, session: aiohttp.ClientSession, 
                                       network_id: str, network_name: str):
        """探测摄像头资源"""
        print(f"    📹 探测摄像头资源 ({network_name})...")
        
        try:
            # 获取画质保留配置
            try:
                quality_profiles = await self.api.get_network_camera_quality_retention_profiles(session, network_id)
                print(f"      - 画质配置: {len(quality_profiles)} 个")
            except:
                print(f"      - 画质配置: ❌")
            
            # 获取录制计划
            try:
                schedules = await self.api.get_network_camera_schedules(session, network_id)
                print(f"      - 录制计划: {len(schedules)} 个")
            except:
                print(f"      - 录制计划: ❌")
                
        except Exception as e:
            print(f"      ⚠️  摄像头资源探测失败: {e}")
    
    async def _discover_organization_statistics(self, session: aiohttp.ClientSession):
        """探测组织级统计信息"""
        print(f"\n📊 探测组织级统计...")
        
        for org in self.discovery_results['organizations'][:2]:  # 限制前2个组织
            org_id = org['id']
            org_name = org['name']
            
            print(f"  组织: {org_name}")
            
            try:
                # 获取顶级应用使用量
                try:
                    top_apps = await self.api.get_organization_summary_top_applications_by_usage(session, org_id)
                    print(f"    - 顶级应用: {len(top_apps)} 个")
                except:
                    print(f"    - 顶级应用: ❌")
                
                # 获取顶级客户端使用量
                try:
                    top_clients = await self.api.get_organization_summary_top_clients_by_usage(session, org_id)
                    print(f"    - 顶级客户端: {len(top_clients)} 个")
                except:
                    print(f"    - 顶级客户端: ❌")
                
                # 获取顶级设备使用量
                try:
                    top_devices = await self.api.get_organization_summary_top_devices_by_usage(session, org_id)
                    print(f"    - 顶级设备: {len(top_devices)} 个")
                except:
                    print(f"    - 顶级设备: ❌")
                
                # 获取安全网关利用率
                try:
                    top_appliances = await self.api.get_organization_summary_top_appliances_by_utilization(session, org_id)
                    print(f"    - 安全网关利用率: {len(top_appliances)} 个")
                except:
                    print(f"    - 安全网关利用率: ❌")
                    
            except Exception as e:
                print(f"    ⚠️  组织统计探测失败: {e}")
    
    def _generate_summary(self):
        """生成摘要信息"""
        orgs = self.discovery_results['organizations']
        networks = self.discovery_results['networks']
        devices = self.discovery_results['devices']
        device_types = self.discovery_results['device_types']
        
        # 设备类型统计
        device_type_count = defaultdict(int)
        for device in devices:
            device_type_count[device.get('productType', 'unknown')] += 1
        
        # 网络类型统计
        network_product_types = defaultdict(int)
        for network in networks:
            for product_type in network.get('productTypes', []):
                network_product_types[product_type] += 1
        
        summary = {
            'total_organizations': len(orgs),
            'total_networks': len(networks),
            'total_devices': len(devices),
            'device_types_found': sorted(device_types),
            'device_type_counts': dict(device_type_count),
            'network_product_types': dict(network_product_types),
            'api_capabilities': self._assess_api_capabilities()
        }
        
        self.discovery_results['summary'] = summary
    
    def _assess_api_capabilities(self) -> Dict[str, bool]:
        """评估 API 能力"""
        device_types = self.discovery_results['device_types']
        
        capabilities = {
            'wireless_management': 'wireless' in device_types,
            'appliance_management': 'appliance' in device_types,
            'switch_management': 'switch' in device_types,
            'camera_management': 'camera' in device_types,
            'sensor_management': 'sensor' in device_types,
            'cellular_gateway_management': 'cellularGateway' in device_types,
            'systems_manager': 'systemsManager' in device_types
        }
        
        return capabilities
    
    def print_summary(self):
        """打印摘要报告"""
        summary = self.discovery_results['summary']
        
        print("\n" + "="*60)
        print("📊 MERAKI 资源摸底报告")
        print("="*60)
        
        print(f"🏢 组织数量: {summary['total_organizations']}")
        print(f"🌐 网络数量: {summary['total_networks']}")
        print(f"📱 设备数量: {summary['total_devices']}")
        
        print(f"\n📋 发现的设备类型:")
        for device_type in summary['device_types_found']:
            count = summary['device_type_counts'].get(device_type, 0)
            print(f"  - {device_type}: {count} 台")
        
        print(f"\n🔧 API 管理能力评估:")
        capabilities = summary['api_capabilities']
        for capability, available in capabilities.items():
            status = "✅" if available else "❌"
            print(f"  - {capability}: {status}")
        
        print(f"\n💡 推荐的 API 调用策略:")
        self._print_api_recommendations()
    
    def _print_api_recommendations(self):
        """打印 API 调用推荐"""
        device_types = self.discovery_results['device_types']
        
        if 'wireless' in device_types:
            print("  📡 无线设备管理:")
            print("    - get_network_wireless_ssids() - 获取SSID配置")
            print("    - get_network_wireless_settings() - 获取无线设置")
            print("    - get_network_clients() - 获取无线客户端")
        
        if 'appliance' in device_types:
            print("  🛡️  安全网关管理:")
            print("    - get_network_appliance_settings() - 获取网关设置")
            print("    - get_network_appliance_firewall_l3_rules() - 获取L3防火墙规则")
            print("    - get_network_appliance_vlans() - 获取VLAN配置")
        
        if 'switch' in device_types:
            print("  🔌 交换机管理:")
            print("    - get_network_switch_settings() - 获取交换机设置")
            print("    - get_network_switch_ports() - 获取端口配置")
        
        if 'camera' in device_types:
            print("  📹 摄像头管理:")
            print("    - 需要添加摄像头相关API")
        
        print("  📊 通用监控:")
        print("    - get_organization_devices() - 获取设备列表")
        print("    - get_device_statuses_overview() - 获取设备状态")
        print("    - get_organization_assurance_alerts() - 获取健康告警")


async def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python test.py <API_KEY>")
        print("示例: python test.py 4fb1f6a6c032f662ab0d8315b8cf45268b615d66")
        sys.exit(1)
    
    api_key = sys.argv[1]
    
    print(f"🔑 使用 API Key: {api_key[:10]}...")
    print(f"🌍 API 端点: https://api.meraki.cn/api/v1")
    
    discovery = MerakiDiscovery(api_key)
    
    async with aiohttp.ClientSession() as session:
        try:
            results = await discovery.discover_all(session)
            discovery.print_summary()
            
            # 保存详细结果到文件
            with open('meraki_discovery_results.json', 'w', encoding='utf-8') as f:
                # 转换 set 为 list 以便 JSON 序列化
                results_copy = results.copy()
                results_copy['device_types'] = list(results['device_types'])
                results_copy['network_types'] = list(results['network_types'])
                if 'device_models' in results_copy:
                    results_copy['device_models'] = list(results['device_models'])
                
                json.dump(results_copy, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 详细结果已保存到: meraki_discovery_results.json")
            
        except Exception as e:
            print(f"\n❌ 发现过程失败: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GameLove Hosts 更新工具 - 模块化重构版本

该工具用于自动更新游戏平台的hosts文件，优化网络连接。
采用模块化设计，提升代码的可维护性、可扩展性和易读性。

"""

import socket
import time
import json
import os
import subprocess
import re
import ipaddress
import concurrent.futures
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum


class ResolveMethod(Enum):
    """IP解析方法枚举"""
    DNS = "dns"
    PING = "ping"
    NSLOOKUP = "nslookup"


@dataclass
class ResolveResult:
    """IP解析结果数据类"""
    domain: str
    ip: Optional[str]
    method: Optional[ResolveMethod]
    success: bool
    error: Optional[str] = None
    response_time: Optional[float] = None
    is_valid_ip: bool = False
    
    def __post_init__(self):
        """验证IP地址有效性"""
        if self.ip:
            self.is_valid_ip = self._validate_ip(self.ip)
    
    def _validate_ip(self, ip: str) -> bool:
        """验证IP地址格式和有效性
        
        Args:
            ip: IP地址字符串
            
        Returns:
            bool: IP是否有效
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            # 排除私有地址、回环地址、多播地址等
            return (
                not ip_obj.is_private and
                not ip_obj.is_loopback and
                not ip_obj.is_multicast and
                not ip_obj.is_reserved and
                not ip_obj.is_link_local
            )
        except ValueError:
            return False


@dataclass
class PlatformInfo:
    """游戏平台信息数据类"""
    name: str
    domains: List[str]
    success_count: int = 0
    total_count: int = 0
    priority_domains: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        self.total_count = len(self.domains)


class IPResolver(ABC):
    """IP解析器抽象基类"""
    
    @abstractmethod
    def resolve(self, domain: str) -> ResolveResult:
        """解析域名IP地址
        
        Args:
            domain: 要解析的域名
            
        Returns:
            ResolveResult: 解析结果
        """
        pass


class DNSResolver(IPResolver):
    """DNS解析器实现类"""
    
    def __init__(self, timeout: float = 10.0):
        """初始化DNS解析器
        
        Args:
            timeout: 超时时间（秒）
        """
        self.timeout = timeout
    
    def resolve(self, domain: str) -> ResolveResult:
        """通过DNS解析获取IP地址
        
        Args:
            domain: 要解析的域名
            
        Returns:
            ResolveResult: DNS解析结果
        """
        start_time = time.time()
        
        try:
            # 设置socket超时
            old_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(self.timeout)
            
            ip = socket.gethostbyname(domain)
            response_time = time.time() - start_time
            
            return ResolveResult(
                domain=domain,
                ip=ip,
                method=ResolveMethod.DNS,
                success=True,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return ResolveResult(
                domain=domain,
                ip=None,
                method=ResolveMethod.DNS,
                success=False,
                error=str(e),
                response_time=response_time
            )
        finally:
            # 恢复原始超时设置
            socket.setdefaulttimeout(old_timeout)


class PingResolver(IPResolver):
    """Ping解析器实现类"""
    
    def __init__(self, timeout: int = 5, count: int = 1):
        """初始化Ping解析器
        
        Args:
            timeout: 超时时间（秒）
            count: ping次数
        """
        self.timeout = timeout
        self.count = count
    
    def resolve(self, domain: str) -> ResolveResult:
        """通过ping获取IP地址（备用方法）
        
        Args:
            domain: 要解析的域名
            
        Returns:
            ResolveResult: Ping解析结果
        """
        start_time = time.time()
        
        try:
            result = subprocess.run(
                ['ping', '-n', str(self.count), domain],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Reply from' in line or 'Pinging' in line:
                        ip_match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', line)
                        if ip_match:
                            ip = ip_match.group()
                            return ResolveResult(
                                domain=domain,
                                ip=ip,
                                method=ResolveMethod.PING,
                                success=True,
                                response_time=response_time
                            )
            
            return ResolveResult(
                domain=domain,
                ip=None,
                method=ResolveMethod.PING,
                success=False,
                error="No IP found in ping output",
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return ResolveResult(
                domain=domain,
                ip=None,
                method=ResolveMethod.PING,
                success=False,
                error=str(e),
                response_time=response_time
            )


class NslookupResolver(IPResolver):
    """Nslookup解析器实现类"""
    
    def __init__(self, timeout: int = 10):
        """初始化Nslookup解析器
        
        Args:
            timeout: 超时时间（秒）
        """
        self.timeout = timeout
    
    def resolve(self, domain: str) -> ResolveResult:
        """通过nslookup获取IP地址
        
        Args:
            domain: 要解析的域名
            
        Returns:
            ResolveResult: Nslookup解析结果
        """
        start_time = time.time()
        
        try:
            result = subprocess.run(
                ['nslookup', domain],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Address:' in line and '::' not in line:  # 排除IPv6
                        ip_match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', line)
                        if ip_match:
                            ip = ip_match.group()
                            return ResolveResult(
                                domain=domain,
                                ip=ip,
                                method=ResolveMethod.NSLOOKUP,
                                success=True,
                                response_time=response_time
                            )
            
            return ResolveResult(
                domain=domain,
                ip=None,
                method=ResolveMethod.NSLOOKUP,
                success=False,
                error="No IP found in nslookup output",
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return ResolveResult(
                domain=domain,
                ip=None,
                method=ResolveMethod.NSLOOKUP,
                success=False,
                error=str(e),
                response_time=response_time
            )


class SmartResolver(IPResolver):
    """智能解析器 - 具有重试机制和结果验证"""
    
    def __init__(self, resolvers: List[IPResolver], max_retries: int = 2):
        """初始化智能解析器
        
        Args:
            resolvers: 解析器列表，按优先级排序
            max_retries: 最大重试次数
        """
        self.resolvers = resolvers
        self.max_retries = max_retries
    
    def resolve(self, domain: str) -> ResolveResult:
        """智能解析域名，包含重试和验证机制
        
        Args:
            domain: 要解析的域名
            
        Returns:
            ResolveResult: 最佳解析结果
        """
        best_result = None
        all_results = []
        
        for resolver in self.resolvers:
            for attempt in range(self.max_retries + 1):
                result = resolver.resolve(domain)
                all_results.append(result)
                
                # 如果成功且IP有效，立即返回
                if result.success and result.is_valid_ip:
                    return result
                
                # 记录最佳结果（即使失败）
                if best_result is None or self._is_better_result(result, best_result):
                    best_result = result
                
                # 如果成功但IP无效，尝试下一个解析器
                if result.success:
                    break
                
                # 失败则重试
                if attempt < self.max_retries:
                    time.sleep(0.5)  # 重试间隔
        
        # 返回最佳结果
        return best_result or ResolveResult(
            domain=domain,
            ip=None,
            method=None,
            success=False,
            error="All resolvers failed"
        )
    
    def _is_better_result(self, result1: ResolveResult, result2: ResolveResult) -> bool:
        """比较两个解析结果，判断哪个更好
        
        Args:
            result1: 结果1
            result2: 结果2
            
        Returns:
            bool: result1是否比result2更好
        """
        # 成功且IP有效的结果最好
        if result1.success and result1.is_valid_ip:
            if not (result2.success and result2.is_valid_ip):
                return True
            # 都成功且有效，比较响应时间
            return (result1.response_time or float('inf')) < (result2.response_time or float('inf'))
        
        # 成功但IP无效的结果次之
        if result1.success and not result1.is_valid_ip:
            if not result2.success:
                return True
        
        # 都失败，比较响应时间
        if not result1.success and not result2.success:
            return (result1.response_time or float('inf')) < (result2.response_time or float('inf'))
        
        return False


class ParallelResolver:
    """并行解析器 - 支持多线程并发解析"""
    
    def __init__(self, resolver: IPResolver, max_workers: int = 10):
        """初始化并行解析器
        
        Args:
            resolver: 基础解析器
            max_workers: 最大工作线程数
        """
        self.resolver = resolver
        self.max_workers = max_workers
    
    def resolve_batch(self, domains: List[str]) -> Dict[str, ResolveResult]:
        """批量并行解析域名
        
        Args:
            domains: 域名列表
            
        Returns:
            Dict[str, ResolveResult]: 域名到解析结果的映射
        """
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_domain = {
                executor.submit(self.resolver.resolve, domain): domain
                for domain in domains
            }
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    result = future.result()
                    results[domain] = result
                except Exception as e:
                    results[domain] = ResolveResult(
                        domain=domain,
                        ip=None,
                        method=None,
                        success=False,
                        error=f"Parallel execution error: {str(e)}"
                    )
        
        return results


class CompositeResolver(IPResolver):
    """组合解析器 - 按优先级尝试多种解析方法"""
    
    def __init__(self, resolvers: List[IPResolver]):
        """初始化组合解析器
        
        Args:
            resolvers: 解析器列表，按优先级排序
        """
        self.resolvers = resolvers
    
    def resolve(self, domain: str) -> ResolveResult:
        """按优先级尝试多种解析方法
        
        Args:
            domain: 要解析的域名
            
        Returns:
            ResolveResult: 解析结果
        """
        last_result = None
        
        for resolver in self.resolvers:
            result = resolver.resolve(domain)
            if result.success:
                return result
            last_result = result
        
        # 如果所有解析器都失败，返回最后一个结果
        return last_result or ResolveResult(
            domain=domain,
            ip=None,
            method=None,
            success=False,
            error="All resolvers failed"
        )


class GamePlatformConfig:
    """游戏平台配置管理类"""
    
    # 游戏平台域名配置
    PLATFORMS = {
        'Steam': [
            'steamcommunity.com',
            'store.steampowered.com',
            'api.steampowered.com',
            'help.steampowered.com',
            'steamcdn-a.akamaihd.net',
            'steamuserimages-a.akamaihd.net',
            'steamstore-a.akamaihd.net'
        ],
        'Epic': [
            'launcher-public-service-prod06.ol.epicgames.com',
            'epicgames.com',
            'unrealengine.com',
            'fortnite.com',
            'easyanticheat.net'
        ],
        'Origin': [
            'origin.com',
            'ea.com',
            'eaassets-a.akamaihd.net',
            'ssl-lvlt.cdn.ea.com'
        ],
        'Uplay': [
            'ubisoft.com',
            'ubi.com',
            'uplay.com',
            'static3.cdn.ubi.com'
        ],
        'Battle.net': [
            'battle.net',
            'blizzard.com',
            'battlenet.com.cn',
            'blzstatic.cn'
        ],
        'GOG': [
            'gog.com',
            'gog-statics.com',
            'gogalaxy.com'
        ],
        'Rockstar': [
            'rockstargames.com',
            'socialclub.rockstargames.com'
        ]
    }
    
    @classmethod
    def get_all_domains(cls) -> List[str]:
        """获取所有游戏平台域名列表
        
        Returns:
            List[str]: 所有域名列表
        """
        all_domains = []
        for domains in cls.PLATFORMS.values():
            all_domains.extend(domains)
        return all_domains
    
    @classmethod
    def get_platform_info(cls, platform_name: str) -> Optional[PlatformInfo]:
        """获取指定平台信息
        
        Args:
            platform_name: 平台名称
            
        Returns:
            Optional[PlatformInfo]: 平台信息，如果不存在则返回None
        """
        domains = cls.PLATFORMS.get(platform_name)
        if domains:
            return PlatformInfo(name=platform_name, domains=domains)
        return None
    
    @classmethod
    def get_all_platforms(cls) -> Dict[str, PlatformInfo]:
        """获取所有平台信息
        
        Returns:
            Dict[str, PlatformInfo]: 平台名称到平台信息的映射
        """
        return {
            name: PlatformInfo(name=name, domains=domains)
            for name, domains in cls.PLATFORMS.items()
        }


class ContentGenerator:
    """内容生成器类 - 负责生成hosts和JSON内容"""
    
    @staticmethod
    def generate_hosts_content(ip_dict: Dict[str, str]) -> str:
        """生成hosts文件内容
        
        Args:
            ip_dict: 域名到IP的映射
            
        Returns:
            str: hosts文件内容
        """
        content = "# GameLove Host Start\n"
        
        # 按域名排序
        sorted_domains = sorted(ip_dict.keys())
        for domain in sorted_domains:
            ip = ip_dict[domain]
            content += f"{ip:<30} {domain}\n"
        
        # 添加更新信息
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
        content += f"\n# Update time: {now}\n"
        content += "# Update url: https://raw.githubusercontent.com/artemisia1107/GameLove/refs/heads/main/hosts\n"
        content += "# Star me: https://github.com/artemisia1107/GameLove\n"
        content += "# GameLove Host End\n"
        
        return content
    
    @staticmethod
    def generate_json_data(ip_dict: Dict[str, str], failed_domains: List[str]) -> Dict[str, Any]:
        """生成JSON格式数据
        
        Args:
            ip_dict: 成功解析的域名到IP映射
            failed_domains: 解析失败的域名列表
            
        Returns:
            Dict[str, Any]: JSON数据
        """
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
        
        # 按平台分组
        platforms = {}
        for platform_name, platform_info in GamePlatformConfig.get_all_platforms().items():
            platform_data = {
                'domains': [],
                'success_count': 0,
                'total_count': platform_info.total_count
            }
            
            for domain in platform_info.domains:
                domain_info = {
                    'domain': domain,
                    'ip': ip_dict.get(domain),
                    'status': 'success' if domain in ip_dict else 'failed'
                }
                platform_data['domains'].append(domain_info)
                if domain in ip_dict:
                    platform_data['success_count'] += 1
            
            platforms[platform_name.lower()] = platform_data
        
        total_domains = len(ip_dict) + len(failed_domains)
        success_rate = (len(ip_dict) / total_domains * 100) if total_domains > 0 else 0
        
        json_data = {
            'update_time': now,
            'total_domains': total_domains,
            'success_count': len(ip_dict),
            'failed_count': len(failed_domains),
            'success_rate': f"{success_rate:.1f}%",
            'platforms': platforms,
            'all_hosts': ip_dict,
            'failed_domains': failed_domains,
            'urls': {
                'hosts_file': 'https://raw.githubusercontent.com/artemisia1107/GameLove/refs/heads/main/hosts',
                'json_api': 'https://raw.githubusercontent.com/artemisia1107/GameLove/refs/heads/main/hosts.json',
                'repository': 'https://github.com/artemisia1107/GameLove'
            }
        }
        
        return json_data


class FileManager:
    """文件管理器类 - 负责文件保存和README更新"""
    
    def __init__(self, base_dir: str = ".."):
        """初始化文件管理器
        
        Args:
            base_dir: 基础目录路径
        """
        self.base_dir = base_dir
        self.hosts_dir = "hosts"
    
    def save_hosts_file(self, content: str, filename: str, is_root: bool = False) -> str:
        """保存hosts文件
        
        Args:
            content: 文件内容
            filename: 文件名
            is_root: 是否保存到根目录
            
        Returns:
            str: 保存的文件路径
        """
        if is_root:
            filepath = os.path.join(self.base_dir, filename)
        else:
            os.makedirs(self.hosts_dir, exist_ok=True)
            filepath = os.path.join(self.hosts_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
    
    def save_json_file(self, data: Dict[str, Any], filename: str, is_root: bool = False) -> str:
        """保存JSON文件
        
        Args:
            data: JSON数据
            filename: 文件名
            is_root: 是否保存到根目录
            
        Returns:
            str: 保存的文件路径
        """
        if is_root:
            filepath = os.path.join(self.base_dir, filename)
        else:
            os.makedirs(self.hosts_dir, exist_ok=True)
            filepath = os.path.join(self.hosts_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filepath
    
    def update_readme_hosts_content(self, hosts_content: str) -> bool:
        """更新README.md中的hosts内容
        
        Args:
            hosts_content: hosts文件内容
            
        Returns:
            bool: 更新是否成功
        """
        readme_path = os.path.join(self.base_dir, 'README.md')
        
        try:
            # 读取README.md文件
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
        except FileNotFoundError:
            print("README.md文件未找到")
            return False
        
        # 查找hosts内容的开始和结束标记
        start_marker = "```\n# GameLove Host Start"
        end_marker = "# GameLove Host End\n```"
        
        start_index = readme_content.find(start_marker)
        end_index = readme_content.find(end_marker)
        
        if start_index == -1 or end_index == -1:
            print("在README.md中未找到hosts内容标记")
            return False
        
        # 处理hosts内容
        clean_hosts_content = self._clean_hosts_content_for_readme(hosts_content)
        
        # 获取更新时间
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
        
        new_hosts_block = f"""```
# GameLove Host Start
{clean_hosts_content}
# GameLove Host End
```

该内容会自动定时更新，数据更新时间：{now}"""
        
        # 找到完整的替换范围
        end_index = self._find_complete_replacement_range(readme_content, end_index, end_marker)
        
        # 构建新的README内容
        new_readme_content = (
            readme_content[:start_index] + 
            new_hosts_block + 
            readme_content[end_index:]
        )
        
        # 写入更新后的README.md
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(new_readme_content)
            print(f"README.md已更新，更新时间：{now}")
            return True
        except Exception as e:
            print(f"更新README.md时出错：{e}")
            return False
    
    def _clean_hosts_content_for_readme(self, hosts_content: str) -> str:
        """清理hosts内容用于README显示
        
        Args:
            hosts_content: 原始hosts内容
            
        Returns:
            str: 清理后的内容
        """
        hosts_lines = hosts_content.split('\n')
        
        # 移除开头和结尾的标记
        if hosts_lines and hosts_lines[0].strip() == "# GameLove Host Start":
            hosts_lines = hosts_lines[1:]
        if hosts_lines and hosts_lines[-1].strip() == "# GameLove Host End":
            hosts_lines = hosts_lines[:-1]
        
        # 移除空行和多余的标记
        clean_lines = []
        for line in hosts_lines:
            line = line.strip()
            if line and line not in ["# GameLove Host Start", "# GameLove Host End"]:
                clean_lines.append(line)
        
        return '\n'.join(clean_lines)
    
    def _find_complete_replacement_range(self, readme_content: str, end_index: int, end_marker: str) -> int:
        """找到完整的替换范围
        
        Args:
            readme_content: README内容
            end_index: 结束标记位置
            end_marker: 结束标记
            
        Returns:
            int: 完整替换范围的结束位置
        """
        end_index_with_time = readme_content.find("```", end_index + len(end_marker))
        if end_index_with_time != -1:
            time_line_start = readme_content.find("该内容会自动定时更新", end_index_with_time)
            if time_line_start != -1:
                time_line_end = readme_content.find("\n", time_line_start)
                if time_line_end != -1:
                    return time_line_end
                else:
                    return len(readme_content)
            else:
                return end_index_with_time + 3  # 包含```
        else:
            return end_index + len(end_marker)


class GameLoveHostsUpdater:
    """GameLove Hosts更新器主控制类 - 重构版本"""
    
    def __init__(self, 
                 delay_between_requests: float = 0.1,
                 use_parallel: bool = True,
                 max_workers: int = 10,
                 use_smart_resolver: bool = True):
        """初始化更新器
        
        Args:
            delay_between_requests: 请求间延迟时间（秒）
            use_parallel: 是否使用并行解析
            max_workers: 最大工作线程数
            use_smart_resolver: 是否使用智能解析器
        """
        self.delay_between_requests = delay_between_requests
        self.use_parallel = use_parallel
        self.max_workers = max_workers
        
        # 初始化解析器
        self._init_resolvers(use_smart_resolver)
        
        # 初始化其他组件
        self.content_generator = ContentGenerator()
        self.file_manager = FileManager()
        
        # 统计信息
        self.stats = {
            'total_domains': 0,
            'success_count': 0,
            'failed_count': 0,
            'start_time': None,
            'end_time': None,
            'total_time': 0
        }
    
    def _init_resolvers(self, use_smart_resolver: bool) -> None:
        """初始化解析器
        
        Args:
            use_smart_resolver: 是否使用智能解析器
        """
        # 创建基础解析器
        base_resolvers = [
            DNSResolver(timeout=10.0),
            PingResolver(timeout=5, count=1),
            NslookupResolver(timeout=10)
        ]
        
        if use_smart_resolver:
            # 使用智能解析器
            self.resolver = SmartResolver(base_resolvers, max_retries=2)
        else:
            # 使用组合解析器
            self.resolver = CompositeResolver(base_resolvers)
        
        # 如果启用并行处理，包装为并行解析器
        if self.use_parallel:
            self.parallel_resolver = ParallelResolver(self.resolver, self.max_workers)
    
    def resolve_all_domains(self) -> Tuple[Dict[str, str], List[str], Dict[str, ResolveResult]]:
        """解析所有游戏平台域名
        
        Returns:
            Tuple[Dict[str, str], List[str], Dict[str, ResolveResult]]: 
            (成功解析的IP字典, 失败域名列表, 详细解析结果)
        """
        all_domains = GamePlatformConfig.get_all_domains()
        self.stats['total_domains'] = len(all_domains)
        self.stats['start_time'] = time.time()
        
        print(f"🔍 开始解析 {len(all_domains)} 个游戏平台域名...")
        print(f"📊 解析模式: {'并行' if self.use_parallel else '串行'}")
        print(f"🧠 解析器类型: {'智能解析器' if isinstance(self.resolver, SmartResolver) else '组合解析器'}")
        print()
        
        if self.use_parallel:
            # 并行解析
            detailed_results = self.parallel_resolver.resolve_batch(all_domains)
        else:
            # 串行解析
            detailed_results = {}
            for domain in all_domains:
                result = self.resolver.resolve(domain)
                detailed_results[domain] = result
                
                # 显示进度
                self._print_resolve_progress(domain, result)
                
                # 添加延迟避免请求过快
                if not self.use_parallel:
                    time.sleep(self.delay_between_requests)
        
        # 处理结果
        ip_dict = {}
        failed_domains = []
        
        for domain, result in detailed_results.items():
            if result.success and result.ip and result.is_valid_ip:
                ip_dict[domain] = result.ip
                self.stats['success_count'] += 1
            else:
                failed_domains.append(domain)
                self.stats['failed_count'] += 1
            
            # 如果是并行模式，在这里显示结果
            if self.use_parallel:
                self._print_resolve_progress(domain, result)
        
        self.stats['end_time'] = time.time()
        self.stats['total_time'] = self.stats['end_time'] - self.stats['start_time']
        
        return ip_dict, failed_domains, detailed_results
    
    def _print_resolve_progress(self, domain: str, result: ResolveResult) -> None:
        """打印解析进度
        
        Args:
            domain: 域名
            result: 解析结果
        """
        if result.success and result.ip and result.is_valid_ip:
            method_str = f"({result.method.value})" if result.method else ""
            time_str = f" [{result.response_time:.2f}s]" if result.response_time else ""
            print(f"✅ {domain:<40} -> {result.ip:<15} {method_str}{time_str}")
        elif result.success and result.ip and not result.is_valid_ip:
            method_str = f"({result.method.value})" if result.method else ""
            time_str = f" [{result.response_time:.2f}s]" if result.response_time else ""
            print(f"⚠️  {domain:<40} -> {result.ip:<15} {method_str}{time_str} [无效IP]")
        else:
            error_str = f" ({result.error[:50]}...)" if result.error and len(result.error) > 50 else f" ({result.error})" if result.error else ""
            time_str = f" [{result.response_time:.2f}s]" if result.response_time else ""
            print(f"❌ {domain:<40} -> 解析失败{error_str}{time_str}")
    
    def generate_and_save_files(self, 
                               ip_dict: Dict[str, str], 
                               failed_domains: List[str],
                               detailed_results: Dict[str, ResolveResult]) -> None:
        """生成并保存所有文件
        
        Args:
            ip_dict: 成功解析的IP字典
            failed_domains: 失败域名列表
            detailed_results: 详细解析结果
        """
        if not ip_dict:
            print("❌ 没有成功解析的域名，跳过文件生成")
            return
        
        print(f"\n📝 开始生成文件...")
        
        # 生成完整hosts文件
        hosts_content = self.content_generator.generate_hosts_content(ip_dict)
        
        # 保存主要文件到根目录
        main_file = self.file_manager.save_hosts_file(hosts_content, 'hosts', is_root=True)
        print(f"✅ 主文件已保存到: {main_file}")
        
        # 保存备份到hosts目录
        backup_file = self.file_manager.save_hosts_file(hosts_content, 'hosts')
        print(f"✅ 备份已保存到: {backup_file}")
        
        # 生成并保存JSON文件（包含详细统计信息）
        json_data = self._generate_enhanced_json_data(ip_dict, failed_domains, detailed_results)
        
        json_file = self.file_manager.save_json_file(json_data, 'hosts.json', is_root=True)
        print(f"✅ JSON文件已保存到: {json_file}")
        
        json_backup = self.file_manager.save_json_file(json_data, 'hosts.json')
        print(f"✅ JSON备份已保存到: {json_backup}")
        
        # 生成分平台hosts文件
        self._generate_platform_files(ip_dict)
        
        # 生成统计报告
        self._generate_statistics_report(detailed_results)
        
        # 更新README.md
        print(f"\n📝 更新README.md中的hosts内容...")
        if self.file_manager.update_readme_hosts_content(hosts_content):
            print("✅ README.md已成功更新")
        else:
            print("❌ README.md更新失败")
    
    def _generate_enhanced_json_data(self, 
                                   ip_dict: Dict[str, str], 
                                   failed_domains: List[str],
                                   detailed_results: Dict[str, ResolveResult]) -> Dict[str, Any]:
        """生成增强的JSON数据，包含详细统计信息
        
        Args:
            ip_dict: 成功解析的域名到IP映射
            failed_domains: 解析失败的域名列表
            detailed_results: 详细解析结果
            
        Returns:
            Dict[str, Any]: 增强的JSON数据
        """
        # 基础JSON数据
        json_data = self.content_generator.generate_json_data(ip_dict, failed_domains)
        
        # 添加详细统计信息
        method_stats = {}
        response_time_stats = []
        
        for result in detailed_results.values():
            if result.method:
                method_name = result.method.value
                if method_name not in method_stats:
                    method_stats[method_name] = {'success': 0, 'failed': 0, 'total': 0}
                
                method_stats[method_name]['total'] += 1
                if result.success:
                    method_stats[method_name]['success'] += 1
                else:
                    method_stats[method_name]['failed'] += 1
            
            if result.response_time is not None:
                response_time_stats.append(result.response_time)
        
        # 计算响应时间统计
        if response_time_stats:
            avg_response_time = sum(response_time_stats) / len(response_time_stats)
            min_response_time = min(response_time_stats)
            max_response_time = max(response_time_stats)
        else:
            avg_response_time = min_response_time = max_response_time = 0
        
        # 添加增强信息
        json_data.update({
            'performance_stats': {
                'total_time': f"{self.stats['total_time']:.2f}s",
                'avg_response_time': f"{avg_response_time:.2f}s",
                'min_response_time': f"{min_response_time:.2f}s",
                'max_response_time': f"{max_response_time:.2f}s",
                'domains_per_second': f"{len(detailed_results) / self.stats['total_time']:.2f}" if self.stats['total_time'] > 0 else "0"
            },
            'method_stats': method_stats,
            'resolver_config': {
                'parallel_mode': self.use_parallel,
                'max_workers': self.max_workers if self.use_parallel else 1,
                'smart_resolver': isinstance(self.resolver, SmartResolver)
            }
        })
        
        return json_data
    
    def _generate_platform_files(self, ip_dict: Dict[str, str]) -> None:
        """生成分平台hosts文件
        
        Args:
            ip_dict: 成功解析的IP字典
        """
        print(f"\n📁 生成分平台hosts文件...")
        
        for platform_name, platform_info in GamePlatformConfig.get_all_platforms().items():
            platform_ips = {
                domain: ip_dict[domain] 
                for domain in platform_info.domains 
                if domain in ip_dict
            }
            
            if platform_ips:
                platform_content = self.content_generator.generate_hosts_content(platform_ips)
                platform_file = self.file_manager.save_hosts_file(
                    platform_content, 
                    f'hosts_{platform_name.lower()}'
                )
                success_rate = len(platform_ips) / len(platform_info.domains) * 100
                print(f"✅ {platform_name:<12} -> {platform_file:<30} ({len(platform_ips)}/{len(platform_info.domains)}, {success_rate:.1f}%)")
            else:
                print(f"❌ {platform_name:<12} -> 无可用域名")
    
    def _generate_statistics_report(self, detailed_results: Dict[str, ResolveResult]) -> None:
        """生成统计报告文件
        
        Args:
            detailed_results: 详细解析结果
        """
        report_content = self._create_statistics_report_content(detailed_results)
        
        report_file = self.file_manager.save_hosts_file(
            report_content, 
            'statistics_report.txt'
        )
        print(f"📊 统计报告已保存到: {report_file}")
    
    def _create_statistics_report_content(self, detailed_results: Dict[str, ResolveResult]) -> str:
        """创建统计报告内容
        
        Args:
            detailed_results: 详细解析结果
            
        Returns:
            str: 统计报告内容
        """
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        content = f"""GameLove Hosts 解析统计报告
生成时间: {now}
{'=' * 50}

总体统计:
- 总域名数: {self.stats['total_domains']}
- 成功解析: {self.stats['success_count']} ({self.stats['success_count']/self.stats['total_domains']*100:.1f}%)
- 解析失败: {self.stats['failed_count']} ({self.stats['failed_count']/self.stats['total_domains']*100:.1f}%)
- 总耗时: {self.stats['total_time']:.2f}秒
- 平均速度: {self.stats['total_domains']/self.stats['total_time']:.2f} 域名/秒

解析方法统计:
"""
        
        # 统计各种解析方法的使用情况
        method_stats = {}
        response_times = []
        
        for result in detailed_results.values():
            if result.method:
                method_name = result.method.value
                if method_name not in method_stats:
                    method_stats[method_name] = {'success': 0, 'failed': 0, 'times': []}
                
                if result.success:
                    method_stats[method_name]['success'] += 1
                else:
                    method_stats[method_name]['failed'] += 1
                
                if result.response_time:
                    method_stats[method_name]['times'].append(result.response_time)
                    response_times.append(result.response_time)
        
        for method, stats in method_stats.items():
            total = stats['success'] + stats['failed']
            success_rate = stats['success'] / total * 100 if total > 0 else 0
            avg_time = sum(stats['times']) / len(stats['times']) if stats['times'] else 0
            
            content += f"- {method.upper():<10}: {stats['success']}/{total} ({success_rate:.1f}%), 平均响应时间: {avg_time:.2f}s\n"
        
        # 平台统计
        content += f"\n平台解析统计:\n"
        for platform_name, platform_info in GamePlatformConfig.get_all_platforms().items():
            success_count = sum(1 for domain in platform_info.domains 
                              if domain in detailed_results and 
                              detailed_results[domain].success and 
                              detailed_results[domain].is_valid_ip)
            success_rate = success_count / len(platform_info.domains) * 100
            content += f"- {platform_name:<12}: {success_count}/{len(platform_info.domains)} ({success_rate:.1f}%)\n"
        
        # 失败域名详情
        failed_results = [result for result in detailed_results.values() 
                         if not result.success or not result.is_valid_ip]
        
        if failed_results:
            content += f"\n失败域名详情:\n"
            for result in failed_results:
                error_info = result.error if result.error else "未知错误"
                if not result.is_valid_ip and result.ip:
                    error_info = f"无效IP: {result.ip}"
                content += f"- {result.domain:<40}: {error_info}\n"
        
        return content
    
    def print_summary(self) -> None:
        """打印执行摘要"""
        print(f"\n{'='*60}")
        print(f"🎉 GameLove Hosts 更新完成！")
        print(f"{'='*60}")
        print(f"📊 解析统计:")
        print(f"   总域名数: {self.stats['total_domains']}")
        print(f"   成功解析: {self.stats['success_count']} ({self.stats['success_count']/self.stats['total_domains']*100:.1f}%)")
        print(f"   解析失败: {self.stats['failed_count']} ({self.stats['failed_count']/self.stats['total_domains']*100:.1f}%)")
        print(f"   总耗时: {self.stats['total_time']:.2f}秒")
        print(f"   平均速度: {self.stats['total_domains']/self.stats['total_time']:.2f} 域名/秒")
        print(f"\n📁 文件位置:")
        print(f"   主文件: 根目录 (hosts, hosts.json)")
        print(f"   备份: hosts/ 目录")
        print(f"   统计报告: hosts/statistics_report.txt")
        print(f"\n📖 使用说明请查看 README.md")
        print(f"⭐ 如果觉得有用，请给项目点个星: https://github.com/artemisia1107/GameLove")
    
    def run(self) -> None:
        """运行主程序"""
        print("🎮 GameLove - 游戏平台网络优化工具 (重构版 v2.0)")
        print("参考 GitHub520 设计，让你\"爱\"上游戏！")
        print("=" * 60)
        
        try:
            # 解析所有域名
            ip_dict, failed_domains, detailed_results = self.resolve_all_domains()
            
            # 生成并保存文件
            self.generate_and_save_files(ip_dict, failed_domains, detailed_results)
            
            # 打印摘要
            self.print_summary()
            
        except KeyboardInterrupt:
            print(f"\n⚠️ 用户中断操作")
        except Exception as e:
            print(f"\n❌ 程序执行出错: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数入口"""
    # 可以通过参数配置不同的运行模式
    updater = GameLoveHostsUpdater(
        delay_between_requests=0.1,
        use_parallel=True,          # 启用并行处理
        max_workers=10,             # 最大工作线程数
        use_smart_resolver=True     # 启用智能解析器
    )
    updater.run()


if __name__ == "__main__":
    main()
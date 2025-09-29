import socket
import time
import json
import os
from datetime import datetime

def get_ip_from_dns(domain):
    """通过DNS解析获取IP地址"""
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except:
        return None

def get_ip_from_ping(domain):
    """通过ping获取IP地址（备用方法）"""
    try:
        import subprocess
        result = subprocess.run(['ping', '-n', '1', domain], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Reply from' in line or 'Pinging' in line:
                    import re
                    ip_match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', line)
                    if ip_match:
                        return ip_match.group()
    except:
        pass
    return None

def resolve_ip(domain):
    """解析域名IP地址"""
    # 首先尝试DNS解析
    ip = get_ip_from_dns(domain)
    if ip:
        return ip
    
    # 如果DNS解析失败，尝试ping
    ip = get_ip_from_ping(domain)
    if ip:
        return ip
    
    return None

# 游戏平台域名列表
GAMING_DOMAINS = {
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

def generate_hosts_content(ip_dict):
    """生成hosts文件内容"""
    content = "# GameLove Host Start\n"
    
    # 按域名排序
    sorted_domains = sorted(ip_dict.keys())
    for domain in sorted_domains:
        ip = ip_dict[domain]
        content += f"{ip:<30} {domain}\n"
    
    # 添加更新信息
    now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
    content += f"\n# Update time: {now}\n"
    content += "# Update url: https://raw.githubusercontent.com/artemisia1107/GameLove/main/hosts\n"
    content += "# Star me: https://github.com/artemisia1107/GameLove\n"
    content += "# GameLove Host End\n"
    
    return content

def generate_json_data(ip_dict, failed_domains):
    """生成JSON格式数据"""
    now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
    
    # 按平台分组
    platforms = {}
    for platform, domains in GAMING_DOMAINS.items():
        platform_data = {
            'domains': [],
            'success_count': 0,
            'total_count': len(domains)
        }
        
        for domain in domains:
            domain_info = {
                'domain': domain,
                'ip': ip_dict.get(domain),
                'status': 'success' if domain in ip_dict else 'failed'
            }
            platform_data['domains'].append(domain_info)
            if domain in ip_dict:
                platform_data['success_count'] += 1
        
        platforms[platform.lower()] = platform_data
    
    json_data = {
        'update_time': now,
        'total_domains': len(ip_dict) + len(failed_domains),
        'success_count': len(ip_dict),
        'failed_count': len(failed_domains),
        'success_rate': f"{len(ip_dict)/(len(ip_dict) + len(failed_domains))*100:.1f}%",
        'platforms': platforms,
        'all_hosts': ip_dict,
        'failed_domains': failed_domains,
        'urls': {
            'hosts_file': 'https://raw.githubusercontent.com/artemisia1107/GameLove/main/hosts',
        'json_api': 'https://raw.githubusercontent.com/artemisia1107/GameLove/main/hosts.json',
        'repository': 'https://github.com/artemisia1107/GameLove'
        }
    }
    
    return json_data

def save_hosts_file(content, filename, is_root=False):
    """保存hosts文件"""
    if is_root:
        # 保存到根目录
        filepath = os.path.join('..', filename)
    else:
        # 保存到hosts目录
        os.makedirs('hosts', exist_ok=True)
        filepath = os.path.join('hosts', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath

def save_json_file(data, filename, is_root=False):
    """保存JSON文件"""
    if is_root:
        # 保存到根目录
        filepath = os.path.join('..', filename)
    else:
        # 保存到hosts目录
        os.makedirs('hosts', exist_ok=True)
        filepath = os.path.join('hosts', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filepath

def main():
    print("🎮 GameLove - 游戏平台网络优化工具")
    print("参考 GitHub520 设计，让你\"爱\"上游戏！")
    print("=" * 50)
    
    # 收集所有域名
    all_domains = []
    for platform_domains in GAMING_DOMAINS.values():
        all_domains.extend(platform_domains)
    
    print(f"开始解析 {len(all_domains)} 个游戏平台域名...")
    print()
    
    # 解析IP地址
    ip_dict = {}
    failed_domains = []
    
    for domain in all_domains:
        ip = resolve_ip(domain)
        if ip:
            ip_dict[domain] = ip
            print(f"✓ {domain} -> {ip}")
        else:
            failed_domains.append(domain)
            print(f"✗ {domain} -> 解析失败")
        
        # 添加延迟避免请求过快
        time.sleep(0.1)
    
    print(f"\n成功解析 {len(ip_dict)}/{len(all_domains)} 个域名")
    
    # 生成完整hosts文件
    if ip_dict:
        hosts_content = generate_hosts_content(ip_dict)
        
        # 保存到根目录（主要文件）
        main_file = save_hosts_file(hosts_content, 'hosts', is_root=True)
        print(f"✓ 主文件已保存到: {main_file}")
        
        # 保存到hosts目录（备份）
        backup_file = save_hosts_file(hosts_content, 'hosts')
        print(f"✓ 备份已保存到: {backup_file}")
        
        # 生成JSON格式文件
        json_data = generate_json_data(ip_dict, failed_domains)
        
        # 保存JSON到根目录
        json_file = save_json_file(json_data, 'hosts.json', is_root=True)
        print(f"✓ JSON文件已保存到: {json_file}")
        
        # 保存JSON到hosts目录（备份）
        json_backup = save_json_file(json_data, 'hosts.json')
        print(f"✓ JSON备份已保存到: {json_backup}")
        
        # 生成分平台hosts文件
        for platform, domains in GAMING_DOMAINS.items():
            platform_ips = {domain: ip_dict[domain] for domain in domains if domain in ip_dict}
            if platform_ips:
                platform_content = generate_hosts_content(platform_ips)
                platform_file = save_hosts_file(platform_content, f'hosts_{platform.lower()}')
                print(f"✓ 已保存到: {platform_file}")
    
    print(f"\n🎉 hosts文件生成完成！")
    print(f"📁 主文件位置: 根目录 (hosts, hosts.json)")
    print(f"📁 备份位置: hosts/ 目录")
    print(f"📖 使用说明请查看 README.md")

if __name__ == "__main__":
    main()

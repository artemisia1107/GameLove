# 🎮 GameLove

😘 让你"爱"上游戏，解决访问慢、连接超时的问题。

## 一、介绍

对游戏平台说"爱"太难了：访问慢、下载慢、连接超时。

本项目无需安装任何程序，仅需 5 分钟。

通过修改本地 hosts 文件，试图解决：
- 🚀 游戏平台访问速度慢的问题
- 🎯 游戏下载、更新慢的问题  
- 🔗 游戏平台连接超时的问题

让你"爱"上游戏。

**注：** 本项目参考 [GitHub520](https://github.com/521xueweihan/GitHub520) 设计，专注于游戏平台网络优化。

## 二、使用方法

下面的地址无需访问 GitHub 即可获取到最新的 hosts 内容：

- **文件：** `https://raw.githubusercontent.com/artemisia1107/GameLove/refs/heads/main/hosts`
- **JSON：** `https://raw.githubusercontent.com/artemisia1107/GameLove/refs/heads/main/hosts.json`

### 2.1 手动方式

#### 2.1.1 复制下面的内容

```
# GameLove Host Start
23.210.138.105                 api.steampowered.com
166.117.214.166                battle.net
120.55.44.14                   battlenet.com.cn
166.117.114.163                blizzard.com
184.31.100.194                 ea.com
23.32.45.25                    eaassets-a.akamaihd.net
104.18.2.180                   easyanticheat.net
35.169.179.193                 epicgames.com
75.101.241.48                  fortnite.com
151.101.193.55                 gog.com
77.79.249.112                  gogalaxy.com
23.210.138.105                 help.steampowered.com
104.18.12.27                   launcher-public-service-prod06.ol.epicgames.com
23.61.23.194                   origin.com
23.9.157.24                    rockstargames.com
104.255.105.71                 socialclub.rockstargames.com
23.54.41.64                    static3.cdn.ubi.com
23.54.76.44                    steamcdn-a.akamaihd.net
23.210.138.105                 steamcommunity.com
23.32.45.36                    steamstore-a.akamaihd.net
23.32.45.35                    steamuserimages-a.akamaihd.net
23.78.8.100                    store.steampowered.com
3.95.49.241                    ubi.com
3.168.102.81                   ubisoft.com
3.227.133.49                   unrealengine.com
34.249.82.244                  uplay.com
# Update time: 2025-09-30T04:28:09+08:00
# Update url: https://raw.githubusercontent.com/artemisia1107/GameLove/refs/heads/main/hosts
# Star me: https://github.com/artemisia1107/GameLove
# GameLove Host End
```

该内容会自动定时更新，数据更新时间：2025-09-30T04:28:09+08:00cmd
git-bash.exe fetch_gamelove_hosts.sh
```

#### Linux/Mac
```bash
sudo curl -o /etc/hosts https://raw.githubusercontent.com/artemisia1107/GameLove/refs/heads/main/hosts
```

或者使用脚本：
```bash
#!/bin/bash
remote=https://raw.githubusercontent.com/artemisia1107/GameLove/refs/heads/main/hosts
hosts=/etc/hosts
backup=/etc/hosts.backup.$(date +%Y%m%d_%H%M%S)

# 备份原始 hosts 文件
sudo cp $hosts $backup

# 移除旧的 GameLove 条目
sudo sed -i '/# GameLove Host Start/,/# GameLove Host End/d' $hosts

# 添加新的 GameLove 条目
curl -s $remote | sudo tee -a $hosts > /dev/null

echo "GameLove hosts 更新完成！"
echo "备份文件：$backup"
```

## 三、支持的游戏平台

| 平台 | 域名数量 | 主要解决问题 |
|------|----------|--------------|
| 🎮 **Steam** | 7个域名 | 商店访问、社区加载、下载加速 |
| 🎯 **Epic Games** | 5个域名 | 启动器连接、游戏下载、反作弊 |
| 🎪 **Origin (EA)** | 4个域名 | 平台访问、游戏下载、资源加载 |
| 🎨 **Uplay (Ubisoft)** | 4个域名 | 启动器连接、游戏更新、CDN加速 |
| ⚔️ **Battle.net** | 4个域名 | 暴雪游戏、国服连接、静态资源 |
| 🎲 **GOG** | 3个域名 | 无DRM游戏、Galaxy客户端 |
| 🌟 **Rockstar** | 2个域名 | GTA、荒野大镖客、社交俱乐部 |

## 四、平台专用 hosts

如果你只想优化特定平台，可以使用平台专用的 hosts 文件：

- **Steam：** `https://raw.githubusercontent.com/artemisia1107/GameLove/refs/heads/main/scripts/hosts/hosts_steam`
- **Epic Games：** `https://raw.githubusercontent.com/artemisia1107/GameLove/refs/heads/main/scripts/hosts/hosts_epic`
- **Origin：** `https://raw.githubusercontent.com/artemisia1107/GameLove/refs/heads/main/scripts/hosts/hosts_origin`
- **Uplay：** `https://raw.githubusercontent.com/artemisia1107/GameLove/refs/heads/main/scripts/hosts/hosts_uplay`
- **Battle.net：** `https://raw.githubusercontent.com/artemisia1107/GameLove/refs/heads/main/scripts/hosts/hosts_battle.net`
- **GOG：** `https://raw.githubusercontent.com/artemisia1107/GameLove/refs/heads/main/scripts/hosts/hosts_gog`
- **Rockstar：** `https://raw.githubusercontent.com/artemisia1107/GameLove/refs/heads/main/scripts/hosts/hosts_rockstar`

## 五、自动更新

本项目每1小时自动更新1次，确保 IP 地址的时效性。

你也可以通过以下方式获取更新通知：

1. **Watch** 本项目，选择 "Releases only"
2. 使用 SwitchHosts 设置自动刷新
3. 定期手动检查更新

## 六、常见问题

### Q: 为什么有些游戏还是很慢？
A: hosts 文件主要解决 DNS 解析问题，如果你的网络本身较慢或游戏服务器距离较远，可能需要配合加速器使用。

### Q: 会不会影响其他网站访问？
A: 不会。本项目只针对游戏平台域名进行优化，不会影响其他网站的正常访问。

### Q: 如何恢复原始 hosts 文件？
A: 删除 `# GameLove Host Start` 到 `# GameLove Host End` 之间的所有内容即可。

### Q: 支持添加新的游戏平台吗？
A: 当然！欢迎提交 Issue 或 Pull Request 添加新的游戏平台支持。

## 七、贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 八、免责声明

- 本项目仅供学习和研究使用
- 请遵守当地法律法规和游戏平台服务条款
- 使用本项目产生的任何问题，作者不承担责任

## 九、许可证

本项目采用 [MIT 许可证](LICENSE)。

## 十、致谢

- 感谢 [GitHub520](https://github.com/521xueweihan/GitHub520) 项目的设计灵感
- 感谢所有贡献者的支持

## 十一、Star History

[![Star History Chart](https://api.star-history.com/svg?repos=artemisia1107/GameLove&type=Date)](https://star-history.com/#artemisia1107/GameLove&Date)

---

如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！

让我们一起"爱"上游戏！🎮

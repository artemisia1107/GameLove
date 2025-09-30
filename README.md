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

- **文件：** `https://raw.githubusercontent.com/artemisia1107/GameLove/main/hosts`
- **JSON：** `https://raw.githubusercontent.com/artemisia1107/GameLove/main/hosts.json`

### 2.1 手动方式

#### 2.1.1 复制下面的内容

```
# GameLove Host Start
140.82.114.26                 steamcommunity.com
185.199.108.133               store.steampowered.com
140.82.114.22                 api.steampowered.com
185.199.108.133               help.steampowered.com
185.199.108.133               steamcdn-a.akamaihd.net
185.199.108.133               steamuserimages-a.akamaihd.net
185.199.108.133               steamstore-a.akamaihd.net
20.205.243.168                launcher-public-service-prod06.ol.epicgames.com
140.82.114.26                 epicgames.com
185.199.108.133               unrealengine.com
140.82.114.22                 fortnite.com
185.199.108.133               easyanticheat.net
140.82.114.26                 origin.com
185.199.108.133               ea.com
185.199.108.133               eaassets-a.akamaihd.net
185.199.108.133               ssl-lvlt.cdn.ea.com
140.82.114.26                 ubisoft.com
185.199.108.133               ubi.com
140.82.114.22                 uplay.com
185.199.108.133               static3.cdn.ubi.com
140.82.114.26                 battle.net
185.199.108.133               blizzard.com
140.82.114.22                 battlenet.com.cn
185.199.108.133               blzstatic.cn
140.82.114.26                 gog.com
185.199.108.133               gog-statics.com
140.82.114.22                 gogalaxy.com
140.82.114.26                 rockstargames.com
185.199.108.133               socialclub.rockstargames.com

# Update time: 2024-01-15T18:00:00+08:00
# Update url: https://raw.githubusercontent.com/artemisia1107/GameLove/main/hosts
# Star me: https://github.com/artemisia1107/GameLove
# GameLove Host End
```

该内容会自动定时更新，数据更新时间：2024-01-15T18:00:00+08:00

#### 2.1.2 修改 hosts 文件

hosts 文件在每个系统的位置不一，详情如下：

- **Windows 系统：** `C:\Windows\System32\drivers\etc\hosts`
- **Linux 系统：** `/etc/hosts`
- **Mac（苹果电脑）系统：** `/etc/hosts`
- **Android（安卓）系统：** `/system/etc/hosts`
- **iPhone（iOS）系统：** `/etc/hosts`

修改方法，把第一步的内容复制到文本末尾：

1. **Windows** 使用记事本。
2. **Linux、Mac** 使用 Root 权限：`sudo vi /etc/hosts`。
3. **iPhone、iPad** 须越狱、**Android** 必须要 root。

#### 2.1.3 激活生效

大部分情况下是直接生效，如未生效可尝试下面的办法，刷新 DNS：

- **Windows：** 在 CMD 窗口输入：`ipconfig /flushdns`
- **Linux** 命令：`sudo nscd restart`，如报错则须安装：`sudo apt install nscd` 或 `sudo /etc/init.d/nscd restart`
- **Mac** 命令：`sudo killall -HUP mDNSResponder`

**Tips：** 上述方法无效可以尝试重启机器。

### 2.2 自动方式（SwitchHosts）

**Tip：** 推荐 [SwitchHosts](https://github.com/oldj/SwitchHosts) 工具管理 hosts

以 SwitchHosts 为例，看一下怎么使用的，配置参考下面：

- **Hosts 类型:** Remote
- **Hosts 标题:** GameLove（随意）
- **URL:** `https://raw.githubusercontent.com/artemisia1107/GameLove/main/hosts`
- **自动刷新:** 最好选 1 小时

这样每次 hosts 有更新都能及时进行更新，免去手动更新。

### 2.3 一行命令

#### Windows
使用命令需要安装 [git bash](https://git-scm.com/download/win)

复制以下命令保存到本地命名为 `fetch_gamelove_hosts.sh`：

```bash
#!/bin/bash
_hosts=$(mktemp /tmp/hostsXXX)
hosts=/c/Windows/System32/drivers/etc/hosts
remote=https://raw.githubusercontent.com/artemisia1107/GameLove/main/hosts
reg='/# GameLove Host Start/,/# GameLove Host End/d'

sed "$reg" $hosts > "$_hosts"
curl "$remote" >> "$_hosts"
cat "$_hosts" > "$hosts"

rm "$_hosts"
```

在 CMD 中执行以下命令：
```cmd
git-bash.exe fetch_gamelove_hosts.sh
```

#### Linux/Mac
```bash
sudo curl -o /etc/hosts https://raw.githubusercontent.com/artemisia1107/GameLove/main/hosts
```

或者使用脚本：
```bash
#!/bin/bash
remote=https://raw.githubusercontent.com/artemisia1107/GameLove/main/hosts
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

- **Steam：** `https://raw.githubusercontent.com/artemisia1107/GameLove/main/hosts/hosts_steam`
- **Epic Games：** `https://raw.githubusercontent.com/artemisia1107/GameLove/main/hosts/hosts_epic`
- **Origin：** `https://raw.githubusercontent.com/artemisia1107/GameLove/main/hosts/hosts_origin`
- **Uplay：** `https://raw.githubusercontent.com/artemisia1107/GameLove/main/hosts/hosts_uplay`
- **Battle.net：** `https://raw.githubusercontent.com/artemisia1107/GameLove/main/hosts/hosts_battlenet`
- **GOG：** `https://raw.githubusercontent.com/artemisia1107/GameLove/main/hosts/hosts_gog`
- **Rockstar：** `https://raw.githubusercontent.com/artemisia1107/GameLove/main/hosts/hosts_rockstar`

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

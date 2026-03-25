---
title: 'Openclaw部署、使用、skill'
categories: ["openclaw"]
date: 2026-03-09T03:00:01+08:00
lastmod: 2026-03-25T13:02:09+08:00
draft: false
---
【教程】Openclaw部署、使用、skill与三大实用玩法-Xuan酱-0305

本文档为Xuan酱 2026.3.5《OpenClaw 3大超实用玩法》视频配套教程文档
全平台@Xuan酱，关注我，和我一起探索AI的更多玩法

B站：https://space.bilibili.com/14848367?
抖音： https://v.douyin.com/i5Jqby5f/
小红书：https://www.xiaohongshu.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
YouTube：https://www.youtube.com/@Xuan2333
视频号、公众号：直接搜索 Xuan酱，或扫码关注👇
公众号获取所有资料链接更快哦
其他往期视频的教程文档都在👉 Xuan酱的AI知识库


写在前面
想先和大家分享下我养第一只龙虾的经验总结～希望对大家有帮助！
因为还没来得及仔细研究底层原理，所以说的不一定对，欢迎大佬指正！

之前还挺疑惑"养"这个词的，感觉龙虾不就是个bot吗。
但真的开始养龙虾以后才深刻体会到为什么要叫"养"。

首先，出生时的智商真的很重要，不同模型能力差距还是蛮大的。
我一开始随便用了一个笨笨的模型试水，它连一个定时任务都创建不了，一直说自己没有这样的能力。后来我让它自己格式化，重来一遍，换了个模型就成功了，但也调试了一段时间。估计上最聪明的模型，它可以更快实现你想要的效果，但也烧钱。
所以现在有人会在复杂任务的时候用聪明的模型，执行简单的日常任务的时候就切回笨笨模型。

第二，龙虾的上下文记忆问题还没有特别好的解决方案，最好的方案就是多养几只龙虾，让它们各司其职。
上下文记忆比较差体现在，我装了一堆skill以后，先用skill A，跑通了很好；再接着跑BCDE，然后再布置和A相关的任务的时候，它会忘记它有skill A，然后会按照自己的其他方法做一遍，完成的效果就不是很好。
也有所谓的增强记忆的skill，但也无法完全解决这个问题。
所以现在会有那种一个人养好几只龙虾的情况，让它们各司其职，而不是所有功能都堆在一个龙虾身上。

第三，不要一口气装很多个skill，一定要一个一个装。
这真的是要花时间、有耐心地"养"。一个一个装，确认功能稳定，跑了两天没问题以后，再装下一个。
我一开始自己瞎折腾，三天装了十几个，然后经常这个skill缺个胳膊，那个skill少个腿的，再加上龙虾的记忆差，所有有缺陷的skill修起来都很痛苦。所以我打算重装，重新养一遍了。
具体装skill的操作，我会在后面教程里详细讲～

差不多就是这三点啦！欢迎大家在文档留言，和其他朋友们交流经验！

翻到一个非常非常全的教程：https://github.com/xianyu110/awesome-openclaw-tutorial
Openclaw部署和使用常见问题速查：https://github.com/xianyu110/awesome-openclaw-tutorial/blob/main/appendix/E-common-problems.md#%E7%BD%91%E7%BB%9C%E9%97%AE%E9%A2%98

部署
云服务器部署

顺便截取了各家一个月能达到的最低价格
火山引擎

火山引擎入口：一键部署OpenClaw/ClawdBot-火山引擎
火山引擎教程：快速部署OpenClaw(原Moltbot)，集成飞书AI助手--云服务器-火山引擎
腾讯云

腾讯云入口：https://cloud.tencent.com/act/pro/lighthouse-moltbot?from=29437&Is=home
腾讯云教程：https://cloud.tencent.com/developer/article/2624973

阿里云

阿里云入口：OpenClaw - 9.9元定制7*24 AI助理 - 阿里云
阿里云教程：部署OpenClaw镜像并构建钉钉AI员工

百度智能云

百度智能云入口：https://cloud.baidu.com/product/BCC/moltbot.html
百度智能云教程：https://cloud.baidu.com/doc/LS/s/6ml9f3cvl

本地部署

推荐Mac，玩法更多。以下也以Mac为例。
翻了下Windows的教程，和Mac的还不太一样。
Windows的朋友们可以参考：awesome-openclaw-tutorial/docs/01-basics/02-installation.md at main · xianyu110/awesome-openclaw-tut


环境准备
安装Homebrew，在终端执行下面代码即可
安装或更新 Node.js（推荐安装v22版本，其他版本不保证跑得通），在终端执行下面代码即可

# 下载和安装homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.sh)"

# 运行完上一行命令后，如果出现Next steps，并显示以echo开头的命令，如：
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
请务必把终端里这些命令复制并执行，这是为了让你的电脑识别brew命令。

# 确认brew版本（运行后应该出现版本号，无所谓哪个版本，确认安装成功即可）:
brew --version

# 下载和安装nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash

# 立即加载nvm环境
\. "$HOME/.nvm/nvm.sh"

# 下载和安装Node.js:
nvm install 22

# 确认Node.js版本（运行后应该出现"v22.22.1"）:
node -v

# 确认npm版本（运行后应该出现"10.9.4"）:
npm -v

安装Openclaw

有一个国内版Openclaw的教程，我没动手安装过，不知道和国外的区别是啥。
感兴趣的朋友可以研究下：awesome-openclaw-tutorial/docs/01-basics/02-installation.md at main · xianyu110/awesome-openclaw-tut
终端执行以下命令：

curl -fsSL https://openclaw.ai/install.sh | bash

如果一直有网络问题，可以尝试以下命令：

npm install -g openclaw@latest --registry=https://registry.npmmirror.com

Openclaw初始化向导
安装完成后会自动弹出，如果没有弹出可以运行以下命令：

openclaw onboard

然后会弹出配置信息：


配置项

配置信息

 I understand this is personal-by-default and shared/multi-user use requires lock-down. Continue?

选择 "Yes"

Onboarding mode

选择 "QuickStart"


配置底层模型
选择你的AI供应商，选择你要用的模型，填入API key即可。也可以先跳过。
详细API配置教程（内含Kimi、Deepseek的配置教程详细步骤）：https://github.com/xianyu110/awesome-openclaw-tutorial/blob/main/docs/01-basics/02-installation.md#api%E9%85%8D%E7%BD%AE%E6%8C%87%E5%8D%97
Kimi 2.5配置教程：https://platform.moonshot.cn/docs/guide/use-kimi-in-openclaw




视频里推荐的各家模型API申请入口：
Claude：https://platform.claude.com/settings/keys
ChatGPT：https://platform.openai.com/
Gemini：https://aistudio.google.com/api-keys
Kimi：https://platform.moonshot.cn/console/api-keys
Minimax：https://platform.minimaxi.com/user-center/basic-information
智谱：https://bigmodel.cn/usercenter/proj-mgmt/apikeys


如果只是想低成本试玩试跑一下，可以尝试阿里云百炼计划，首月7.9RMB。
支持的模型：qwen3.5-plus（支持图片理解）、kimi-k2.5（支持图片理解）、glm-5、MiniMax-M2.5、qwen3-max-2026-01-23、qwen3-coder-next、qwen3-coder-plus、glm-4.7。
配置和使用过程中记得切换模型。

阿里云百炼计划入口：https://www.aliyun.com/benefit/scene/codingplan?utm_content=se_1023135081&gclid=CjwKCAiAzZ_NBhAEEiwAMtqKy9gHcevBh4rbwX_g9kbZWSB_leDxNDYOSyz96L2bQkfCocDLloS83RoCEvwQAvD_BwE
阿里云百炼计划接入Openclaw指南：https://help.aliyun.com/zh/model-studio/openclaw-coding-plan?spm=a2c4g.11186623.0.0.5ceb2f35FASz10

接着选「All providers」，然后「Keep current」即可



配置机器人 - 以飞书为例
国内可以选择飞书、QQ、钉钉、企业微信。
QQ、钉钉、企业微信本地部署的话比较复杂，推荐飞书。下面以飞书为例。


有一个国内版Openclaw的教程，我没动手安装过，不知道和国外的区别是啥。但看这里面介绍，企微和钉钉可以直接和飞书一样通过输入应用凭证来配置，不用装插件。
感兴趣的朋友可以研究下：awesome-openclaw-tutorial/docs/01-basics/02-installation.md at main · xianyu110/awesome-openclaw-tut

还可以研究这个GitHub项目，预装了接入飞书、钉钉、QQ机器人、企业微信的插件——OpenClaw中国IM插件整合版Docker镜像 https://github.com/justlovemaki/OpenClaw-Docker-CN-IM




以下教程部分节选自：https://cloud.tencent.com/developer/article/2626151。

接入飞书
创建飞书企业自建应用
登录飞书开放平台。登录成功后，点击创建企业自建应用。
填写应用名称、应用描述，选择应用图标，点击创建按钮，进入应用管理页面。


添加机器人
在前一步所创建应用的管理页面，左侧导航栏中找到并点击"添加应用能力"，在弹出的列表中选择机器人，点击添加。


查询AppID和AppSecret
在左侧导航栏找到"凭据与基础信息" ，点击进入。
在页面中找到 "App ID" 和 "App Secret" 两个参数，分别点击右侧 "复制" 按钮，填入终端。



填写后，选择你的飞书所在地区，用飞书的选China，用Lark的选International。


如果Openclaw机器人只打算自用，选择"Disabled"；准备拉入群聊，选择前两个。
我懒得配白名单，就选了"Open"。

至此，Openclaw和飞书就打通了。接着要把飞书机器人配置到自己的飞书里。

飞书机器人相关配置（完成网关启动后再倒回来做）
事件配置
在飞书应用管理页，左侧导航栏找到 "事件与回调" ，点击进入页面。在"事件配置"页签中选择 "长连接接收事件"，点击保存。


⚠️注意：如果这一步报错提示"应用未建立长连接"，请检查前面步骤中的机器人App ID和App Secret是否已正确配置。

添加事件
点击"事件配置"页面中的 "添加事件"，在弹出的列表中，搜索并添加 "接收消息"，点击 "确认添加"，按照指引确认开通权限。


（推荐）若期望将飞书机器人添加进聊天群组中使用，可以参考前述步骤继续添加更多群组相关权限，主要包括"消息已读"、"机器人进群"、"机器人被移出群"。否则，请跳过本步骤。


完成添加后，可以在当前页面的列表中查看到已添加的事件。


回调配置
在"事件与回调-回调配置"页面中，订阅方式选择 "使用长连接接收回调"，点击保存，无需填写其他地址，配置自动生效。


权限配置
在飞书应用管理页，左侧导航栏找到 "权限管理" ，点击进入页面。点击页面中的 "批量导入权限" 按钮，弹出权限导入窗口。


复制以下代码，替换上图红框弹窗中原有的JSON内容，点击下一步，确认新增权限，继续申请开通，确认后等待权限导入完成。

{
  "scopes": {
    "tenant": [
      
      "im:message",
      "im:message.p2p_msg:readonly",
      "im:message.group_at_msg:readonly",
      "im:message:send_as_bot",
      "im:resource",

      
      "contact:user.base:readonly",
      "im:message.group_msg",
      "im:message:readonly",
      "im:message:update",
      "im:message:recall",
      "im:message.reactions:read",

   
      "docx:document:readonly",
      "drive:drive:readonly",
      "wiki:wiki:readonly",
      "bitable:app:readonly",
      "task:task:read",

      "contact:contact.base:readonly",
      "docx:document",
      "docx:document.block:convert",
      "drive:drive",
      "wiki:wiki",
      "bitable:app",
      "task:task:write"
    ],
    "user": []
  }
}
权限导入完成后，可以在权限列表中查看已成功导入的权限。

提示：后续使用飞书机器人过程中也可以按需调整权限设置。



创建版本并发布
在飞书应用管理页，左侧导航栏找到 "版本管理与发布" ，点击进入页面。点击右上角的创建版本。
填写应用版本号（此处以1.0.0为例，您可以自行定义版本号）和更新说明，点击保存并确认发布。
待飞书管理员通过发布审核。审核发布成功后，可以在"版本管理与发布"页面，查看到已经发布的版本号和状态。




与飞书机器人交互
完成Openclaw部署后，您可以与飞书机器人进行单独聊天，或者将飞书机器人添加进群聊。
单独聊天
以电脑版飞书软件为例（手机端飞书的操作类似），登录飞书后，点击搜索框。
在搜索框中输入前面步骤中创建并发布的飞书机器人的应用名称，输入回车进行搜索。




单击搜索到的机器人，进入私聊页面，即可开始与已经接入OpenClaw的飞书机器人进行对话。
（如对话时未出现可直接跳过本步骤）
首次对话如果提示如下图所示的配对（Paring）请求，可以复制机器人回复的最后一行命令行，粘贴至终端并运行。

接下来继续尝试与该机器人进行对话，如果机器人以AI的方式进行回复，即说明配对成功。

群聊添加飞书机器人
对于群组聊天的场景，可以点击飞书搜索框上方的加号，选择创建群组，并完成创建。


进入新创建的群组，点击右上角的设置。
在设置中选择"群机器人"，点击添加机器人。


在上方搜索框搜索您创建的机器人的应用名称。
选择您之前创建的机器人后，点击添加即可将飞书机器人加入群聊，示例如下所示。
到这里就初步完成了配置，在手机版飞书和电脑版飞书上均可以开始与已经接入OpenClaw的飞书机器人进行聊天。




安装skill

因为我已经装了，所以截了一个别人的skill表，可能和现在安装弹出的skill表的细节不一样，但大部分是一样的。
这里可以先只装一个Clawdhub（OpenClaw 自家 skill 市场），然后跳过。剩下的在skill章节里详细介绍。
想要回来安装就再运行一次「openclaw onboard」就可以，或者直接和bot对话叫它装

配置其他API
统统选No就可以了，后面要用再配

配置Hooks
勾选 session-memory 、 command-logger，其他可以先不选。
想要回来选就再运行一次「openclaw onboard」就可以
原因可以见后面介绍

🧠 什么是 Hook？
在 OpenClaw 里，Hook 是一种自动化触发机制
当某些 Agent 命令或事件发生时，系统会自动执行你预先设置的动作。
类似：
程序启动时自动运行
每次对话开始前执行
每次对话结束后保存数据
记录日志
注入记忆
可以理解成：给机器人装"自动行为插件"

📦 截图里的 4 个 Hook 解释
🚀 boot-md
当 Gateway 启动时，自动执行 BOOT.md 文件。
相当于启动时加载 AI 的"系统说明书"。
通常 BOOT.md 里会放：
系统提示词
初始化配置
Agent 行为规则

📎 bootstrap-extra-files
启动时加载额外文件，注入给 AI 作为上下文。适合高级用户。小白可以不选。
比如：
额外 prompt 文件
外部配置
额外规则说明

📝 command-logger
记录命令日志。开启后可以查看机器人每一步干了什么。
会：
记录用户输入
记录模型输出
记录执行过的命令
适合：
调试
分析 Agent 行为
统计使用情况

💾 session-memory
这是最重要的一个。不开启的话，每次对话都像新开一个窗口；开启后，机器人会"记得"之前内容。
作用：
保存会话上下文
让机器人记住之前说过的话

网关自启动
配置完成后，会自动启动Gateway服务
网关是什么？
是 OpenClaw 的核心服务，它像一个"中央调度站"。负责：
连接各个聊天平台（飞书、企微、QQ、Telegram等）
管理会话和消息路由：将消息转发给 AI 智能体处理，把 AI 的回复发送回对应平台

"你想如何启动你的机器人？"
TUI 模式：在终端内运行，适合服务器部署
Web UI 模式：通过浏览器交互，适合咱们这些不喜欢终端的小白们
 如暂不启动，可选择稍后执行。


日常使用指令

常见问题速查：https://github.com/xianyu110/awesome-openclaw-tutorial/blob/main/appendix/E-common-problems.md#%E7%BD%91%E7%BB%9C%E9%97%AE%E9%A2%98
启动OpenClaw：

# 启动Gateway服务
openclaw gateway start

# 或使用systemd（推荐，开机自启）
openclaw gateway enable
访问Web UI，会自动打开浏览器访问：http://xxx.xxx.xxx.xxx:18789/chat：

openclaw dashboard
访问TUI：

openclaw tui
停止服务：

openclaw gateway stop
出现问题的时候可以重启Gateway：

openclaw gateway restart
更新Openclaw：

openclaw update
卸载Openclaw：

openclaw uninstall

skill安装
Openclaw的GitHub  ClawHub：https://clawhub.ai/
如前所述，不要一口气装很多个skill，一定要一个一个装。
普通人必备skill推荐
来源：https://x.com/Wuming_Mr_/status/2028419040847249428

第一优先级：保命四件套（先装这 4 个）
Skill Vetter（安全审计）
这玩意必须第一个装。
安装新 skill 前自动扫描风险指令，相当于给 Agent 装个"防毒软件"。
ClawHub 现在下载量≠安全，别太天真。

Tavily / SerpAPI（联网搜索）
没联网的 Agent，本质是信息孤岛。
装完之后才真正"活过来"。查实时资讯、验证信息、抓最新数据，全靠它。

Browser / Playwright（浏览器自动化）
能自己开网页、点按钮、填表单、截图。
我现在很多重复性网页操作都丢给它，效率翻倍。
做爬取、自动提交、监控页面变化都很好用。

Code Interpreter（Python 执行）
这是核心生产力引擎。
数据分析、画图、处理文件、跑脚本，没有它很多复杂任务根本落不了地。

第二阶段：让它真正参与工作流
File Manager（文件管理）
读写本地文件、批量改名、处理 PDF。
不装它，Agent 只能"想办法"，不能"动文件"。

GitHub Assistant（Git 操作）
commit、PR、issue、review 一条龙。
对开发者来说，它就是一个不摸鱼的实习生。

Notion / Obsidian 连接器（知识库）
自动建笔记、更新文档、查询知识库。
装完后我开始真的把它当"第二大脑"。

 第三阶段：从工具到"主动员工"
Cron / Scheduler（定时任务）
每天自动跑日报、周报、数据监控。
这一步是质变——它开始主动工作。

Self-Improving / Evolver（自我优化）
分析失败记录，优化 prompt。
不算必需，但长期用下来会明显变聪明。

Daily Digest（主动日报）
每天自动整理工作总结、待办事项、行业动态。
这个真的很"有陪伴感"。

官方安装流程中的skill表介绍

🔐 账号 & 密码类
1password
对接 1Password 密码管理器，用来：
读取密码
自动填充凭证
访问 API key
适合：自动化登录、调用私有服务。
⚠️注意安全问题

🍎 Apple 生态
apple-notes
读取 / 写入 Apple 备忘录。
apple-reminders
创建 / 管理 Apple 提醒事项。
things-mac
对接 Things 任务管理软件。
👉 这些都需要 macOS 才能用。

📝 笔记类
bear-notes
对接 Bear 笔记（macOS）。
obsidian
对接 Obsidian 笔记库（通过 obsidian-cli）。
适合做：
知识库自动整理
自动写入笔记
Agent 记忆系统

🐦 社交 / 内容类
bird
Twitter/X 的相关skill。可以搜索推特，发推。详情介绍：https://playbooks.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx。
blogwatcher
监控博客更新（RSS 监听）。

🤖 AI / 模型类
gemini
对接 Google Gemini 模型。
openai-whisper
语音转文字（Whisper 本地或 API）。
model-usage
统计模型调用 token 使用量。

🖼️ 多媒体处理
gifgrep
处理 gif / 图像分析。
img
图片处理。
video-frames
视频帧提取。
nano-pdf
PDF 解析。

实用玩法
视频里提到的很多案例，都可以在连接了Clawhub和下面这个GitHub项目搜索工具以后，直接搜索skill和工具进行组合！跟着视频说的下提示词就行！
然后像开头说的，用聪明的模型（视频里推荐的），以及一个一个skill地安装，能提高快速成功的概率和龙虾运行的稳定性哦～
GitHub项目搜索工具

先装为敬！
https://github.com/yunshu0909/yunshu_skillshub/tree/master/github-repo-search
发送以下提示词给你的龙虾：

帮我装一下这个工具，注意检查安全性：https://github.com/yunshu0909/yunshu_skillshub/tree/master/github-repo-search
补充：刚刚又发现一个很牛的搜索工具！甚至支持搜索各大社交平台！使用方法见链接：
https://github.com/Panniantong/Agent-Reach


收藏管理

我的skill还不太会修改成通用版本，分享出来的话装上也大概率跑不通！装完以后修修补补不如自己搭建一个干净的～也可以学习和体会一下自己创建一个skill的过程～
我的初版提示词下得太简单，后续调试花了很多功夫。大家可以试试发送以下提示词给你的龙虾：

# 任务：构建一个基于 OpenClaw 的智能收藏回顾系统（工程化完整版）

请完整阅读需求。如存在关键设计不明确之处，请先向我确认再开始生成代码。

---

# 一、运行环境

- Node.js 18+
- 使用 CommonJS 模块规范
- 系统环境：macOS
- 数据存储路径：~/Obsidian/shoucang
- 使用 OpenClaw 内置 cron 机制（不要使用系统 crontab 或 node-cron）
- 飞书机器人已配置（通过 OpenClaw 发送消息）

---

# 二、系统目标

构建一个"智能收藏回顾系统"，实现：

1. 自动抓取网页内容
2. 基于艾宾浩斯曲线的复习提醒
3. 自然语言管理收藏
4. Markdown 本地存储
5. 通过 OpenClaw cron 定时触发回顾

---

# 三、核心功能设计

## 1️⃣ 自动抓取模块

当输入一个 URL 时：

### 抓取策略要求

1. 优先在 GitHub 上搜索并选择满足以下条件的工具：
   - 维护活跃
   - 支持动态页面
   - 支持微信公众号文章
   - 支持小红书帖子
   - 支持普通网页

2. 若抓取失败：
   - 保存 URL
   - 标记 status = needs-review
   - 不得中断系统运行

3. 若抓取成功：
   - 使用 Readability 算法提取正文
   - 将正文发送给 LLM
   - 生成：
     - 3-5 点结构化摘要
     - 3-5 个中文标签
     - 自动分类建议（如：阅读 / 产品 / AI / 生活）

4. LLM 输出必须为标准 JSON 格式：

{
  "summary": ["点1", "点2", "点3"],
  "tags": ["标签1", "标签2"],
  "category": "分类"
}

---

## 2️⃣ 艾宾浩斯复习机制

### 复习间隔

1天 → 2天 → 4天 → 7天 → 15天

### 逻辑要求

- 每次回顾后 reviewCount + 1
- 自动计算 nextReviewAt
- 超过 5 次自动归档（status = archived）

### 模块要求

封装为独立模块：

lib/reviewEngine.js

---

## 3️⃣ 自然语言管理入口

实现自然语言解析模块：

lib/nlpParser.js

### 支持指令

- 推迟3天
- 已看完归档
- 添加标签 xxx
- 删除标签 xxx
- 标记为已回顾

### 要求

- 解析后调用对应业务逻辑函数
- 保持可扩展性（未来可增加更多指令）

---

## 4️⃣ Markdown 存储结构

每条收藏为一个独立 Markdown 文件。

### 文件命名规则

YYYYMMDD-序号.md

示例：

20260305-001.md

### 文件内容结构

---
id: 20260305-001
url: https://example.com
title: 示例标题
tags: [AI, 产品]
category: 阅读
status: inbox
createdAt: 2026-03-05T09:00:00
nextReviewAt: 2026-03-06T09:00:00
reviewCount: 0
---

## AI摘要

1. 摘要点1
2. 摘要点2
3. 摘要点3

### 存储模块要求

封装为：

lib/markdownStore.js

负责：

- 创建文件
- 更新 frontmatter
- 读取文件
- 扫描待回顾条目

---

# 四、需要生成的文件结构

请按以下顺序输出：

1. 目录结构
2. lib/reviewEngine.js
3. lib/markdownStore.js
4. lib/nlpParser.js
5. shoucang-add.js
6. shoucang-review.js
7. smart-collect.js

---

# 五、OpenClaw cron 配置

请使用 OpenClaw 内置 cron hook。

### 定时规则

每天 09:30 触发：

reviewEngine.runDailyReview()

### 要求

- 给出标准 cron 表达式
- 给出 hook 示例配置
- 不使用系统 crontab
- 不使用 node-cron

---

# 六、执行逻辑流程

### 添加收藏流程

URL  
→ 抓取  
→ Readability 提取正文  
→ LLM 生成摘要与标签  
→ Markdown 写入  

### 每日回顾流程

cron 触发  
→ 扫描 status = inbox  
→ 筛选 nextReviewAt <= 当前时间  
→ 推送飞书  
→ 更新 reviewCount  
→ 重新计算 nextReviewAt  

---

# 七、容错要求

- 抓取失败不能导致系统崩溃
- Markdown 写入失败需捕获异常
- LLM 返回 JSON 必须进行格式校验
- 所有关键流程需添加 try/catch
- 出现异常时记录日志但不中断主流程

---

# 八、输出规范

1. 先输出目录结构
2. 再逐文件输出完整代码
3. 不省略关键逻辑
4. 关键算法必须完整实现
5. 如存在设计冲突或关键参数不明确，请先提问再继续

---

请先生成系统整体目录结构，然后开始实现基础框架。

资讯收集
需要配置对应的API，链接里都有操作教程。

多源：awesome-openclaw-usecases/usecases/multi-source-tech-news-digest.md at main · hesamsheikh/awesome-op

油管：awesome-openclaw-usecases/usecases/daily-youtube-digest.md at main · hesamsheikh/awesome-openclaw-us

Reddit：awesome-openclaw-usecases/usecases/daily-reddit-digest.md at main · hesamsheikh/awesome-openclaw-use

日程管理
视频里表述有误，Openclaw的bot可以直接修改日历，无需skill。
apple-reminders是创建 / 管理 Apple 提醒事项。
直接安装就行！

Openclaw其他玩法
GitHub上的awesome openclaw usecase项目：https://github.com/hesamsheikh/awesome-openclaw-usecases
爬取X上用户各种Openclaw玩法的网站：https://openclaw.ai/showcase

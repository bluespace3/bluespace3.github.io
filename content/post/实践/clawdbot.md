---
title: 'clawdbot'
categories: ["实践"]
date: 2026-02-27T09:56:24+08:00
lastmod: 2026-02-27T09:56:24+08:00
encrypted: false
---
title: 'clawdbot'
categories: ["实践"]
date: 2026-02-27T09:56:24+08:00
lastmod: 2026-02-27T09:56:24+08:00
encrypted: false
title: 'clawdbot'
categories: ["实践"]
date: 2026-02-27T09:56:24+08:00
lastmod: 2026-02-27T09:56:24+08:00
encrypted: false
title: 'clawdbot'
categories: ["实践"]
date: 2026-02-27T09:56:24+08:00
lastmod: 2026-02-27T09:56:24+08:00
encrypted: false
设置clawdbot和tailscale开机自启

PS C:\WINDOWS\system32> Unregister-ScheduledTask -TaskName "Start-WSL2-Clawdbot" -

Confirm:$false -ErrorAction SilentlyContinue
PS C:\WINDOWS\system32> $Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\Users\Administrator\Start-Clawdbot.ps1"
PS C:\WINDOWS\system32> $Trigger = New-ScheduledTaskTrigger -AtStartup
PS C:\WINDOWS\system32> $Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 0) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
PS C:\WINDOWS\system32>  $Principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive
PS C:\WINDOWS\system32> Register-ScheduledTask -TaskName "Start-WSL2-Clawdbot" -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principa

重启测试步骤

1. 保存所有工作并重启 Windows
2. 等待 2-3 分钟（让 WSL2 和所有服务完全启动）
3. 从其他设备（手机/另一台电脑）访问：
   https://chinami-dk8uofk.tail3fb54b.ts.net/
4. 输入密码：Tianz728~
5. 验证 Control UI 正常工作

如果重启后无法访问

如果重启后无法访问，可以按以下步骤排查：

1. 在 Windows 中打开 PowerShell
2. 手动运行启动命令测试：
   wsl -d Ubuntu-24.04 -u dministrator -e /home/dministrator/.local/bin/clawdbot-auto-start.sh
3. 检查输出是否有错误

但根据目前的配置，应该能正常工作！

现在可以安全重启 Windows 进行测试了！

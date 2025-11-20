---
title: 'python非同级目录调用报错'
categories: ["技术"]
date: 2025-11-20T15:53:34+00:00
lastmod: 2025-11-20T15:53:34+00:00
---










## 项目结构：

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=N2E4ZjQ0N2I5MmEwYWExMjg1YmVmOTcyZTBhNTk1ZTlfdXlaSzZjU09wSE5mR1AyYTBuYVg1SElQcHJIUENSVWpfVG9rZW46S3AyMmI4bFN1b2VjeG54V251Q2NzMHBhbm5nXzE3NDI0NjExMTk6MTc0MjQ2NDcxOV9WNA)

## 问题：

执行文件调用dir1，间接调用dir2。执行时报错：“ModuleNotFoundError: No module named 'dir1.dir2';”

## 解决方法：

dir1文件导包时做处理。

1. 主函数加入这四行，将项目的根目录(webapp)的路径加入到系统PATH中；
   import os,sys

   from pathlib import Path

   sys.path[0] = str(Path(sys.path[0]).parent.parent)

   sys.path.append(os.getcwd())
2. 且导包从项目执行入口文件同级开始写

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=MzlhZjJjZjgzNzk4YjdjNzU2ZWQ1ZDdjMjA5ODI0MDZfTzN2ZmlQOVM0a1BERU95VkY1amZ5bTFXMEJsc09pTExfVG9rZW46UlgyTmJCdHdLb0I5Z2d4VktJcmNEbDNvblljXzE3NDI0NjExMTk6MTc0MjQ2NDcxOV9WNA)

---
title: 'scrapy爬柚子网示例'
categories: ["技术"]
date: 2025-11-20T15:50:00+00:00
lastmod: 2025-11-20T15:50:00+00:00
---









柚子网https://www.uu-zz.com/

爬取页码

遍历页面内对应的视频集的链接

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/preview/O1YCbvbQBoiZYHxxbO7cqOi6nKb?preview_type=16)

遍历视频内子视频链接

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/preview/CKMPbtR4souEnDxWowNcxAuenNc?preview_type=16)!

[https://www.uu-zz.com/+子视频链接](https://security.feishu.cn/link/safety?target=https%3A%2F%2Fwww.uu-zz.com%2F%2B%E5%AD%90%E8%A7%86%E9%A2%91%E9%93%BE%E6%8E%A5&scene=ccm&logParams=%7B%22location%22%3A%22ccm_mindnote%22%7D&lang=zh-CN)，发送get请求

![](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/preview/ClLDbx3s5o29xpxWKrncnG3Enzg?preview_type=16)!

获得m3u8文件，储存在数据库

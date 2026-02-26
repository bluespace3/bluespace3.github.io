---
title: "Neon配置教程"

categories: ["技术", "Neon"]

author: "tian"

date: 2025-04-27T11:59:32+08:00

draft: false

tags: ["Neon", "数据库", "教程"]
---

1. **创建Neon实例**
   登录Neon控制台（官网：**https://neon.tech**），点击创建免费的Serverless Postgres实例，选择配置（如地区、分支、计算/存储规格）
3. **获取连接信息**
   创建成功后，控制台会提供以下关键信息：

   * **主机名（Host）**：如 `ep-cool-flower-123456.us-east-2.aws.neon.tech`
   * **端口（Port）**：默认为 `5432`
   * **用户名（Username）**：默认为项目生成的随机用户（如 `user123`）
   * **密码（Password）**：需在控制台手动设置或自动生成
4. **使用客户端连接**
    psql -h [主机名] -p [端口] -U [用户名] -d [数据库名]
   * **图形化工具（如DBeaver、pgAdmin）**：
     新建PostgreSQL连接，填入上述信息即可

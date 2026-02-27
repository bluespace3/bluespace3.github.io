---
title: 'AIGC学习笔记%2Flangchain'
categories: ["AIGC学习笔记%2Flangchain.md"]
date: 2026-02-27T10:12:56+08:00
lastmod: 2026-02-27T10:12:56+08:00
encrypted: false
password: "123456"
---
## 核心组件

### **模型包装器**

内部结构：创建连接->提示词模板->语言模型->输出解析

#### 1.创建大模型连接

-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2Fb5d58554-4eab-4773-b6a4-695841c4c66e.png)

#### 2.提示词模板

作用：将提示词内容进行参数化

-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2F033bc311-a106-45d3-b5b2-2fb0bf547252.png)

常用提示词模板：

-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2F026bd779-f37c-42b9-a1fc-f8dba6b2d0ab.png)

1.字符串提示词模板

-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2Fc2bbf4d2-1665-49f3-a7a6-cba3d3c4ac92.png)

2.对话提示词模板：

-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2Fb9fae741-87a2-460a-8795-fb1a81db62aa.png)

3.少量样本提示词模板

-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2F1c0f2bac-41a6-45bd-bde7-ebdd19ff9c6e.png)

-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2F99a2c7f1-89de-4a67-8b47-57aa6db1a5f5.png)

-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2F843cdf8c-38eb-4a27-8e57-52afe9bb3c25.png)

半格式化提示词（相对于全参数化提示词-初始化了全部参数化，半参数化只初始化部分参数）

-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2Fc9b4a9e7-6382-4ed1-bd4e-d7119c0aa795.png)

#### **2.输出解析器**

-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2Ff885c84c-3779-48ad-92a0-f02f33363911.png)

如：

1.csv解析器：

-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2Fe519a138-284f-49bc-8f5a-28cf0477d467.png)

2.日期解析器

日期解析器。
-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2F59c5e9ef-2650-4cb9-8850-7da8dd736813.png)

3.json解析器

-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2F5adaf172-6f55-4cde-b143-f4951eb129d5.png)

### **数据连接**

**作用**：数据交互与处理

### **链**

作用：将组件组合形成端到端的应用

-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2F58c97dcf-64bc-4584-b545-d3cd71ce8e61.png)

-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2F001d77a5-be55-4a4d-9538-42ac55db2709.png)

### **记忆**

**作用：**多次运行持久化应用状态

### **代理**

**作用**：拓展模型推理能力，用于复杂的应用调用序列。

### **回调**

**作用：**大模型阶段工作后后运行某些操作，如日志记录，监控，等用处不大。

### 发布为服务

-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2F3ee93c0f-5f1d-4901-859f-32252617cba8.png)

请求：

-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2Fa26b33a3-ff42-4605-9834-1c28a99654d0.png)

打开调试

-![image.png](http://asset.localhost/C%3A%5CUsers%5CAdministrator%5CAppData%5CRoaming%5Ccom.codexu.NoteGen%2Farticle%2FAIGC%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0%2Fassets%2F53b46e69-3ddd-4203-925a-f9bc36c5d7a9.png)


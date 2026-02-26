---
title: "Hugo Encryptor 加密测试"
date: 2025-02-26T15:30:00+08:00
draft: false
description: "测试 Hugo Encryptor 加密功能"
tags: ["hugo", "加密", "测试"]
categories: ["测试"]
---
这是一篇测试 Hugo Encryptor 加密功能的文章。

前面这段内容是公开的，所有人都可以看到。

<!--more-->

{{% hugo-encryptor "123456" %}}

# 恭喜你解锁了加密内容！

这里是加密的内容，只有输入正确的密码才能看到。

## 测试功能

- AES-256 加密
- 前端密码验证
- 安全可靠

## 详细说明

Hugo Encryptor 使用 AES-256 加密算法保护你的私密内容。即使有人查看了网页源代码，也无法获取加密的内容。

密码提示：**123456**

{{% /hugo-encryptor %}}

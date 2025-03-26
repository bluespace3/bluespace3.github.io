---
title: "git操作"
categories: ["git"]
date: 2025-03-25T12:00:00+08:00
draft: false
tags: ["git"]
---

## git回滚操作
### 回滚到上一个版本
```bash
git reset --hard HEAD^
```
### 回滚到指定版本
```bash
git reset --hard <commit_id>
```
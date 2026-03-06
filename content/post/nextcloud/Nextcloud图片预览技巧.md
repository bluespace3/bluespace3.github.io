---
title: 'Nextcloud 图片预览技巧'
categories: ['nextcloud']
date: 2026-03-04T02:26:41+0800
draft: false
---
# Nextcloud 图片预览技巧

## 简介

在 Markdown 文件中插入图片时，可以使用 Nextcloud 分享链接，并通过在链接末尾添加 `/preview` 实现直接预览图片，而不需要下载。

## 使用方法

### 1. 获取 Nextcloud 分享链接

在 Nextcloud 中右键点击图片 → 分享 → 复制链接

链接格式通常为：
```
https://your-nextcloud-domain/index.php/s/xxxxx
```

### 2. 添加预览参数

在分享链接后添加 `/preview`：

```
https://your-nextcloud-domain/index.php/s/xxxxx/preview
```

### 3. 在 Markdown 中使用

```markdown
![图片描述](https://your-nextcloud-domain/index.php/s/xxxxx/preview)
```

## 优点

- ✅ 不需要下载图片即可预览
- ✅ 减少存储空间占用
- ✅ 分享方便，权限可控
- ✅ 支持常见图片格式（JPG、PNG、GIF、WEBP 等）

## 示例

```markdown
![Nextcloud Logo](https://cloud.example.com/index.php/s/AbCdEf123456/preview)
```

## 注意事项

- 确保分享链接的权限设置正确（公开或已授权）
- 预览链接仅在 Nextcloud 服务正常运行时有效
- 如果 Nextcloud 服务停用，图片将无法显示

## 替代方案

如果不想使用 `/preview`，也可以使用 Nextcloud 的直接下载链接：

```
https://your-nextcloud-domain/index.php/s/xxxxx/download
```

但这样每次打开都会触发下载，而非预览。

# 📖 文章加密使用指南

## 🔐 新的简单加密方式（推荐）

### 方式一：自动加密脚本（最简单）

只需要在 **Front Matter** 中添加 `password` 字段，然后运行脚本：

**Step 1**: 在文章中添加密码字段

```markdown
---
title: '表结构'
categories: ["工作"]
password: "123456"  👈 只需添加这一行
---

文章内容...
```

**Step 2**: 运行自动加密脚本

```bash
# 预览模式（推荐先预览）
python tools/auto_encrypt.py content/post/工作 --dry-run

# 实际加密
python tools/auto_encrypt.py content/post/工作
```

**Step 3**: 提交并推送

```bash
git add .
git commit -m "feat: 加密文章"
git push origin main
```

✅ **优点**：
- 最简单，只需在 Front Matter 添加一行
- 脚本自动处理所有细节
- 批量加密多个文章

---

### 方式二：手动添加加密标记

如果您不想用脚本，也可以手动添加，但需要遵守规则：

**规则**：
1. ✅ 必须有 `<!--more-->` 分隔符
2. ✅ 加密内容放在 `<!--more-->` 之后
3. ✅ 使用 `{{% hugo-encryptor "密码" %}}` 包裹

**示例**：

```markdown
---
title: '表结构'
categories: ["工作"]
---

这是公开内容，所有人可见。

<!--more-->  👈 必须有这个分隔符

{{% hugo-encryptor "123456" %}}  👈 加密开始

这是加密内容，需要密码才能查看。

{{% /hugo-encryptor %}}  👈 加密结束
```

---

## ⚠️ 常见错误

### ❌ 错误 1: 缺少 `<!--more-->`

```markdown
---
title: '文章'
password: "123456"
---

{{% hugo-encryptor "123456" %}}  ❌ 会出错！
内容...
{{% /hugo-encryptor %}}
```

**修复**：在开头添加公开内容和 `<!--more-->`

### ❌ 错误 2: encrypted 字段无效

```markdown
---
title: '文章'
encrypted: true  ❌ 这个字段不起作用！
---
```

**修复**：使用 `password: "123456"` + 自动加密脚本

---

## 🚀 推荐工作流

### 新建加密文章

```bash
# 1. 创建文章
vim content/post/工作/我的笔记.md

# 2. 添加 Front Matter（包含 password 字段）
# 3. 运行自动加密脚本
python tools/auto_encrypt.py content/post/工作

# 4. 预览效果
hugo server -D

# 5. 提交部署
git add .
git commit -m "feat: 添加加密文章"
git push origin main
```

### 批量加密现有文章

```bash
# 1. 为需要加密的文章添加 password 字段
vim content/post/工作/文章1.md  # 添加 password: "123456"
vim content/post/工作/文章2.md  # 添加 password: "123456"

# 2. 批量加密
python tools/auto_encrypt.py content/post/工作

# 3. 提交部署
git add .
git commit -m "feat: 批量加密文章"
git push origin main
```

---

## 🔍 工作原理

1. **编写文章**：在 Front Matter 中添加 `password` 字段
2. **自动加密脚本**：
   - 查找所有包含 `password` 字段的文章
   - 自动添加 `{{% hugo-encryptor %}}` shortcode
   - 自动处理 `<!--more-->` 分隔符
3. **GitHub Actions**：
   - 构建网站 (`hugo --minify`)
   - 运行加密脚本 (`hugo-encryptor.py`)
   - 使用 AES-256 加密内容
   - 部署到 GitHub Pages
4. **用户访问**：
   - 公开内容正常显示
   - 加密部分显示密码输入框
   - 输入密码后浏览器解密显示

---

## 📝 快速参考

| 方式 | 难度 | 适用场景 |
|------|------|----------|
| **自动脚本** | ⭐ 简单 | 推荐方式，批量加密 |
| **手动标记** | ⭐⭐ 中等 | 单篇加密，精细控制 |

---

## 🎯 示例对比

### 旧方式（复杂）

```markdown
---
title: '表结构'
encrypted: true  ❌ 无效字段
---

需要密码才能查看。

<!--more-->

{{% hugo-encryptor "123456" %}}
内容...
{{% /hugo-encryptor %}}
```

### 新方式（简单）

```markdown
---
title: '表结构'
password: "123456"  ✅ 只需一行
---

内容...

# 然后运行：python tools/auto_encrypt.py content/post/工作
```

---

## 💡 提示

- 密码建议使用简单易记的字符串
- 不同文章可以使用不同密码
- 加密是**纯前端**的，注意安全性
- GitHub Actions 自动处理加密，无需手动操作

# 同步笔记到博客

从 GitHub 笔记仓库同步笔记到 Hugo 博客，使用 GitHub API 获取文件真实时间并自动生成符合 Hugo 格式的 Front Matter。

## 核心功能

- 使用 GitHub API 获取文件真实创建和更新时间（解决所有文章时间都是同步日期的问题）
- 自动从文件名提取 title
- 自动从父目录提取 categories
- 时间自动转换为东八区（+08:00）
- 支持批量处理和单个文件处理
- 支持 .env 文件配置（无需每次设置环境变量）

## 使用方法

### 1. 首次设置（仅需一次）

```bash
# 使用交互式脚本设置 GitHub Token
python tools/setup_token.py

# 或手动创建 .env 文件
cp .env.example .env
# 编辑 .env 文件，填入你的 GitHub Token
```

### 2. 基本使用

```bash
# 预览模式（推荐先运行）
python tools/sync_notes_from_github.py --batch content/post --dry-run

# 批量处理所有文章
python tools/sync_notes_from_github.py --batch content/post

# 处理单个文件
python tools/sync_notes_from_github.py --file "content/post/AIGC学习笔记/mcp-intro.md"

# 不覆盖已有 frontmatter
python tools/sync_notes_from_github.py --batch content/post --no-overwrite
```

## 命令参数

- `--file PATH` - 处理单个文件
- `--batch PATH` - 批量处理目录
- `--dry-run` - 预览模式（不实际修改文件）
- `--no-overwrite` - 不覆盖已有 frontmatter
- `--verbose` - 详细输出
- `--config PATH` - 指定配置文件路径

## 配置文件

编辑 `tools/sync_notes_config.yaml` 自定义配置：

```yaml
github:
  token: '${GITHUB_TOKEN}'
  owner: 'bluespace3'
  repo: 'knowledge_bases'
  branch: 'main'

hugo:
  content_dir: 'content/post'
  timezone: 'Asia/Shanghai'

frontmatter:
  overwrite: true
  default_category: '技术'
```

## 获取 GitHub Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 配置：
   - Note: Hugo 博客同步工具
   - Expiration: 90 days 或 No expiration
   - 权限: ✅ `repo` (Full control of private repositories)
4. 点击 "Generate token" 并立即复制

## 验证结果

```bash
# 本地预览
hugo server -D

# 访问归档页检查文章时间分布
# http://localhost:1313/archives/
```

文章应该有不同的创建时间（如 2025-03、2025-06、2025-12 等），而不是所有文章都是 2025-11-20。

## 相关文档

- 快速开始：`QUICKSTART.md`
- 完整指南：`tools/SYNC_NOTES_GUIDE.md`
- 实施总结：`IMPLEMENTATION_SUMMARY.md`

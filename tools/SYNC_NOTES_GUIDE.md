# 笔记同步到博客工具使用指南

## 问题说明

### 之前的问题
使用 `manage-notes.py` 同步笔记后，博客所有文章的时间都变成了 2025-11-20 或 2025-11-22，这是因为该脚本使用本地 `git log` 获取时间，无法获取 GitHub 远程仓库的真实创建时间。

### 解决方案
使用新的 `sync_notes_from_github.py` 工具，通过 GitHub API 直接获取每个文件的真实 `created_at` 和 `updated_at` 时间。

---

## 快速开始

### 1. 安装依赖

```bash
cd tools
pip install -r requirements.txt
```

### 2. 设置 GitHub Token

**获取 Token**：
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限（Full control of private repositories）
4. 生成并复制 Token

**设置环境变量**：

```bash
# Linux/macOS
export GITHUB_TOKEN='你的token'

# Windows PowerShell
$env:GITHUB_TOKEN='你的token'

# Windows CMD
set GITHUB_TOKEN=你的token
```

**永久设置**（推荐）：

```bash
# Linux/macOS - 添加到 ~/.bashrc 或 ~/.zshrc
echo 'export GITHUB_TOKEN="你的token"' >> ~/.bashrc
source ~/.bashrc

# Windows - 设置系统环境变量
# 控制面板 → 系统 → 高级系统设置 → 环境变量 → 新建
```

### 3. 配置文件（可选）

编辑 `tools/sync_notes_config.yaml`：

```yaml
github:
  token: '${GITHUB_TOKEN}'  # 从环境变量读取
  owner: 'bluespace3'       # 仓库所有者
  repo: 'knowledge_bases'   # 笔记仓库名
  branch: 'main'            # 分支名

hugo:
  content_dir: 'content/post'
  timezone: 'Asia/Shanghai'

frontmatter:
  overwrite: true           # 是否覆盖已有 frontmatter
  default_category: '技术'
```

### 4. 使用工具

```bash
# 预览模式（推荐先运行这个）
python tools/sync_notes_from_github.py --batch content/post --dry-run

# 批量处理所有文章
python tools/sync_notes_from_github.py --batch content/post

# 处理单个文件
python tools/sync_notes_from_github.py --file "content/post/AIGC学习笔记/mcp-intro.md"
```

---

## 验证结果

### 1. 本地预览

```bash
hugo server -D
```

访问 http://localhost:1313/archives/ 查看文章时间分布。

### 2. 检查时间是否正确

- ✅ 文章应该有不同的创建时间（如 2025-03、2025-06、2025-12 等）
- ❌ 不应该所有文章都是 2025-11-20

### 3. 发布到博客

```bash
# Windows
deploy.bat

# Linux/macOS
./deploy.sh
```

访问 https://bluespace3.github.io/archives/ 验证。

---

## 命令参数说明

```bash
python tools/sync_notes_from_github.py [选项]

选项：
  --file PATH          处理单个文件
  --batch PATH         批量处理目录
  --config PATH        指定配置文件路径
  --dry-run            预览模式（不实际修改文件）
  --no-overwrite       不覆盖已有 frontmatter
  --verbose            详细输出
```

### 示例

```bash
# 预览某个文件会被如何修改
python tools/sync_notes_from_github.py --file "content/post/test.md" --dry-run --verbose

# 批量处理，但只处理没有 frontmatter 的文件
python tools/sync_notes_from_github.py --batch content/post --no-overwrite

# 使用自定义配置文件
python tools/sync_notes_from_github.py --batch content/post --config my-config.yaml
```

---

## 常见问题

### Q1: 提示 "未设置 GITHUB_TOKEN 环境变量"

**解决方法**：
```bash
# 临时设置
export GITHUB_TOKEN='你的token'

# 或在 PowerShell 中
$env:GITHUB_TOKEN='你的token'
```

### Q2: GitHub API 速率限制

**症状**：出现 "403 Forbidden" 或 "API rate limit exceeded"

**解决方法**：
1. 确保设置了 `GITHUB_TOKEN`（有 token 限制是 5000 次/小时）
2. 等待速率限制重置（通常是 1 小时）
3. 在配置文件中调整 `batch_delay` 参数增加延迟

### Q3: 文件时间还是不对

**检查**：
1. 确认文件在 GitHub 仓库中存在
2. 检查配置文件中的 `owner`、`repo`、`branch` 是否正确
3. 使用 `--verbose` 查看详细日志

### Q4: 某些文件处理失败

**可能原因**：
- 文件在 GitHub 仓库中不存在
- 网络连接问题
- Token 权限不足

**解决方法**：
查看错误日志，根据具体错误信息处理。

---

## 与 manage-notes.py 的对比

| 特性 | manage-notes.py | sync_notes_from_github.py |
|------|-----------------|--------------------------|
| **时间来源** | 本地 git log | GitHub API |
| **时间准确性** | ❌ 同步日期（所有文章相同） | ✅ 真实创建时间 |
| **本地知识库需求** | ✅ 必需 | ❌ 不需要 |
| **GitHub Token** | ❌ 不需要 | ✅ 需要 |
| **速率限制** | ❌ 无 | ⚠️ 有（5000次/小时） |
| **适用场景** | 有本地知识库 | 只需远程仓库 |

**建议**：
- 如果有本地知识库且不在意时间准确性 → 使用 `manage-notes.py`
- 如果需要真实的文章创建时间 → 使用 `sync_notes_from_github.py`

---

## 高级用法

### 1. 自定义时间格式

编辑 `tools/github_api.py:175` 修改时间格式。

### 2. 处理特定分类

```bash
# 只处理 AIGC学习笔记 分类
python tools/sync_notes_from_github.py --batch "content/post/AIGC学习笔记"
```

### 3. 与其他工具结合使用

```bash
# 1. 同步笔记（使用真实时间）
python tools/sync_notes_from_github.py --batch content/post

# 2. 本地预览
hugo server -D

# 3. 确认无误后发布
./deploy.sh
```

---

## 技术说明

### GitHub API 调用流程

1. 调用 `GET /repos/{owner}/{repo}/contents/{path}` 获取文件信息
2. 调用 `GET /repos/{owner}/{repo}/commits?path={path}` 获取提交历史
3. 从第一次提交获取 `created_at`
4. 从文件信息获取 `updated_at`
5. 转换为东八区时间（+08:00）
6. 生成 Hugo Front Matter

### 时间转换示例

```
GitHub API 输入：2025-03-15T10:30:00Z
Hugo Front Matter 输出：2025-03-15T18:30:00+08:00
```

---

## 维护和支持

- **测试**：运行 `python tests/test_github_api.py`
- **配置文件**：`tools/sync_notes_config.yaml`
- **日志**：使用 `--verbose` 查看详细日志
- **问题反馈**：提交 GitHub Issue

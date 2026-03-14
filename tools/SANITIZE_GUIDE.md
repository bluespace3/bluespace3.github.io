# 笔记转博客 - 敏感信息脱敏功能

## 概述

博客内容从笔记转换而来，为了防止敏感信息泄漏，同步脚本会自动检测并脱敏以下敏感信息：

- API Keys（OpenAI、GitHub、Google 等）
- 密码和密钥
- JWT Tokens
- 私钥文件
- IP 地址
- 手机号
- 邮箱地址

## 使用方法

### 基本用法（默认启用脱敏）

```bash
# 同步笔记到博客（自动脱敏）
python3 tools/sync_notes_from_github.py --batch content/post --sync-files
```

### 禁用脱敏（不推荐）

```bash
# 同步笔记但不脱敏（慎用！）
python3 tools/sync_notes_from_github.py --batch content/post --sync-files --no-sanitize
```

### 预览模式

```bash
# 预览脱敏效果（不实际修改文件）
python3 tools/sync_notes_from_github.py --batch content/post --sync-files --dry-run
```

## 脱敏规则

| 类型 | 模式 | 替换为 |
|------|------|--------|
| OpenAI API Key | `sk-[a-zA-Z0-9]{20,}` | `sk-xxxxxxxxxxxxxxxx` |
| GitHub Token | `ghp_[a-zA-Z0-9]{36}` | `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| Google API Key | `AIzaSy[a-zA-Z0-9_-]{33}` | `AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| 密码 | `password: xxxxx` | `password: "********"` |
| 私钥 | `-----BEGIN PRIVATE KEY-----` | `-----BEGIN ...-----\n[REDACTED]\n-----END ...-----` |
| IP 地址 | `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}` | `xxx.xxx.xxx.xxx` |
| 手机号 | `1[3-9]\d{9}` | `138****8888` |
| 邮箱 | `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+` | `user@example.com` |

## 输出示例

```
🔄 从笔记仓库同步新文件
   笔记仓库：/root/.openclaw/workspace/note-gen-sync
   目标目录：/var/www/bluespace3.github.io/content/post
   预览模式：否
   自动脱敏：是

  ✅ 已复制：日记/2026-03-08赛博日记.md
  🔒 已脱敏：日记/2026-03-08赛博日记.md (1 处敏感信息)

  📊 同步完成：
     复制：1 个
     跳过：0 个
     脱敏：1 个
```

## 手动脱敏文件

如果需要手动对单个文件进行脱敏：

```bash
python3 tools/content_sanitizer.py <文件路径>
```

或使用 Python 脚本：

```python
from tools.content_sanitizer import sanitize_markdown_file

# 脱敏并原地修改文件
sanitize_markdown_file(
    file_path="path/to/file.md",
    inplace=True,
    verbose=True
)
```

## 测试脱敏效果

运行测试代码查看脱敏示例：

```bash
python3 tools/content_sanitizer.py
```

## 注意事项

⚠️ **重要：**

1. **脱敏是破坏性操作**
   - 脱敏后的敏感信息无法恢复
   - 建议先在笔记仓库中备份原始内容

2. **假阳性问题**
   - 某些合法的内容可能被误判为敏感信息
   - 例如：测试用的 `sk-` 开头字符串
   - 解决方法：在笔记中使用占位符而非真实密钥

3. **不支持的格式**
   - 仅支持 Markdown 文件
   - 代码块内的内容也会被脱敏

4. **Git 配合使用**
   - 已安装 `pre-commit` hook，防止提交敏感信息
   - 详见 `/root/.openclaw/workspace/SECURITY.md`

## 配置文件

脱敏规则定义在 `tools/content_sanitizer.py` 的 `ContentSanitizer` 类中。

如需自定义规则，修改 `PATTERNS` 字典：

```python
PATTERNS = {
    'custom_key': {
        'pattern': r'your_regex_pattern',
        'description': 'Custom Pattern',
        'replacement': 'replacement_text',
    },
}
```

## 常见问题

### Q: 为什么我的测试密钥也被脱敏了？

A: 脱敏规则基于正则表达式，无法区分真实密钥和测试密钥。建议在笔记中使用占位符：

```markdown
# ❌ 不推荐
API_KEY=sk-abcdef1234567890

# ✅ 推荐
API_KEY=sk-xxxxxxxxxxxxxxxx
```

### Q: 如何保留某些合法的敏感格式？

A: 有两种方法：

1. **禁用脱敏**（不推荐）：使用 `--no-sanitize` 参数
2. **修改脱敏规则**：编辑 `tools/content_sanitizer.py`，移除或调整相应规则

### Q: 脱敏后博客显示异常？

A: 检查以下几点：

1. 脱敏是否破坏了代码块的语法
2. Markdown 格式是否正确
3. 使用 `--dry-run` 预览脱敏效果

## 相关文档

- `/root/.openclaw/workspace/SECURITY.md` - 安全最佳实践
- `/root/.openclaw/workspace/scripts/security-check.sh` - 敏感信息扫描脚本
- `/root/.openclaw/workspace/git-hooks/pre-commit.sh` - Git pre-commit hook

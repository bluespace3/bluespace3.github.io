---
title: 'rsync规则顺序导致文件排除失败问题复盘'
categories: ["实践"]
date: 2026-03-07T07:32:43+08:00
lastmod: 2026-03-07T07:42:38+08:00
draft: false
---
# rsync 规则顺序导致文件排除失败问题复盘

## 问题描述

在博客全量同步脚本中，笔记仓库的 `INDEX.md` 文件反复被复制到 `content/post/`，干扰 Hugo 的 section 处理，导致首页文章显示异常。

## 问题现象

- **首页文章数量**：只显示 4 篇（来自 archives section）而非所有 90+ 篇
- **Hugo 识别异常**：`content/post/` 有 90+ 个文件，但 Hugo 只识别 1 个
- **反复出现**：删除后又出现，无法根治

## 根本原因

### 1. rsync 规则的匹配机制

**关键点**：rsync 规则按照**从上到下**的顺序处理，**第一个匹配的规则生效**。

### 2. 错误的配置（导致问题）

```bash
rsync -av \
    --include='*.md' \     # ❌ 规则1：包含所有 .md 文件
    --include='*/' \
    --exclude='*' \        # 规则3：排除其他
    --exclude='.git/' \
    --exclude='INDEX.md'   # ❌ 规则5：排除 INDEX.md（但已经太晚了）
    "$NOTE_REPO/" "content/post/"
```

**执行流程**：
1. 扫描到 `INDEX.md`
2. 匹配规则1 `--include='*.md'` → **包含！**
3. 后续的 `--exclude='INDEX.md'` 被忽略（已经匹配过了）
4. 结果：`INDEX.md` 被复制

### 3. 正确的配置（修复后）

```bash
rsync -av \
    --exclude='INDEX.md' \  # ✅ 规则1：先排除 INDEX.md
    --exclude='.git/' \
    --exclude='.data/' \
    --exclude='images/' \
    --exclude='assets/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.obsidian/' \
    --exclude='工作/' \
    --include='*.md' \      # ✅ 再包含 .md 文件（INDEX.md 已被排除）
    --include='*/' \
    --exclude='*' \
    "$NOTE_REPO/" "content/post/"
```

**执行流程**：
1. 扫描到 `INDEX.md`
2. 匹配规则1 `--exclude='INDEX.md'` → **排除！**
3. 后续规则不再处理
4. 结果：`INDEX.md` 不被复制

## 为什么频繁出现

### 1. 治标不治本

**之前的处理方式**：
```bash
# 只是删除文件
rm content/post/INDEX.md
```

**问题**：
- 全量同步时又会从笔记仓库复制过来
- rsync 规则顺序错误未修复
- 反复出现，无法根治

### 2. 对 rsync 规则机制理解不足

**常见误区**：
- ❌ 认为 `--exclude` 规则的顺序不重要
- ❌ 认为 `--include` 和 `--exclude` 会"智能"合并
- ❌ 认为后面的规则可以覆盖前面的规则

**实际情况**：
- ✅ rsync 规则是顺序匹配的
- ✅ 第一个匹配的规则就决定了结果
- ✅ 顺序极其重要

### 3. 测试不充分

**缺失的测试**：
- 没有验证 rsync 干运行
- 没有检查文件是否被正确排除
- 没有理解 Hugo 为什么只识别 1 个文件

## Hugo Section 处理机制

### 为什么 INDEX.md 会干扰 Hugo

```
content/post/
├── INDEX.md           # ❌ 大写文件名，干扰 Hugo
├── _index.md          # ✅ 正确的 section index
├── article1.md
└── article2.md
```

**Hugo 的处理逻辑**：
1. 查找 section index 文件：`_index.md`（小写）
2. 如果存在 `INDEX.md`（大写），可能产生冲突
3. 导致 Hugo 无法正确识别 section
4. 结果：只识别 1 个页面或识别失败

## 修复方案

### 1. 立即修复（治标）

```bash
# 删除错误的 INDEX.md
rm content/post/INDEX.md

# 重新构建
hugo --cleanDestinationDir
```

### 2. 根本修复（治本）

**修复 rsync 规则顺序**：
```bash
# 将 --exclude='INDEX.md' 放在 --include='*.md' 之前
```

**验证修复**：
```bash
# 干运行测试
rsync -av --dry-run \
    --exclude='INDEX.md' \
    --include='*.md' \
    --exclude='*' \
    "$NOTE_REPO/" "content/post/"

# 检查输出中是否包含 INDEX.md
# 应该看不到 INDEX.md 的传输
```

## 经验教训

### 1. rsync 规则设计原则

**正确的顺序**：
1. **先排除**不需要的文件/目录（`--exclude`）
2. **再包含**需要的文件（`--include`）
3. **最后排除**其他所有（`--exclude='*'`）

**模板**：
```bash
rsync -av \
    --exclude='不需要的文件' \
    --exclude='不需要的目录/' \
    --include='需要的文件模式' \
    --include='*/' \
    --exclude='*' \
    源/ 目标/
```

### 2. 调试 rsync 问题

**干运行测试**：
```bash
# 添加 --dry-run 和 --verbose
rsync -av --dry-run --verbose \
    --exclude='INDEX.md' \
    --include='*.md' \
    --exclude='*' \
    源/ 目标/
```

**检查特定文件**：
```bash
# 只看某个文件是否被传输
rsync -av --dry-run --verbose \
    ... \
    源/ 目标/ 2>&1 | grep "INDEX.md"
```

### 3. 预防措施

**配置检查清单**：
- [ ] `--exclude` 规则是否在 `--include` 之前
- [ ] 是否需要排除的文件都列在前面
- [ ] 是否使用 `--dry-run` 测试过
- [ ] 是否验证了目标目录结果

**代码审查要点**：
- 检查 rsync 规则顺序
- 确认排除规则在包含规则之前
- 验证特殊文件（INDEX.md, README.md 等）的处理

## 相关工具

### rsync 规则可视化

**测试工具**：
```bash
# 创建测试目录结构
mkdir -p /tmp/rsync-test/{source,target}
cd /tmp/rsync-test

# 创建测试文件
touch source/{INDEX.md,_index.md,test1.md,test2.md}

# 测试规则1（错误）
rsync -av --dry-run \
    --include='*.md' \
    --exclude='INDEX.md' \
    source/ target/

# 测试规则2（正确）
rsync -av --dry-run \
    --exclude='INDEX.md' \
    --include='*.md' \
    source/ target/
```

### Hugo 调试

**检查 Hugo 识别的页面**：
```bash
# 列出所有页面
hugo list all

# 检查特定 section
hugo list all | grep "^content/post/"

# 查看页面详情
hugo list all | grep "INDEX.md"
```

## 扩展阅读

### rsync 官方文档

**规则匹配顺序**：
> The order of the rules matters. The first rule that matches determines whether a file is included or excluded.

**INCLUDE/EXCLUDE 规则**：
- `--include=PATTERN`：包含匹配的文件
- `--exclude=PATTERN`：排除匹配的文件
- 规则从上到下处理
- 第一个匹配的规则生效

### Hugo Section 文档

**Section Index 文件**：
- 名称必须是 `_index.md`（小写）
- 不能是 `INDEX.md` 或其他变体
- 用于定义 section 的元数据和模板

## 总结

**问题根源**：rsync 规则顺序错误 → INDEX.md 被包含 → Hugo section 处理异常

**解决关键**：
1. 理解 rsync 规则的顺序匹配机制
2. 将 `--exclude` 放在 `--include` 之前
3. 使用 `--dry-run` 验证规则

**预防措施**：
- 遵循 rsync 规则设计原则
- 充分测试配置
- 代码审查时检查规则顺序

---

**创建时间**：2026-03-07
**问题状态**：✅ 已解决
**修复提交**：84805d03

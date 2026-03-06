#!/bin/bash

# 后台笔记同步脚本
# 不阻塞主流程，异步执行

NOTE_REPO="/root/.openclaw/workspace/note-gen-sync"
BLOG_DIR="/var/www/bluespace3.github.io"
LOG_FILE="/tmp/notes-sync-$(date +%Y%m%d-%H%M%S).log"
PID_FILE="/tmp/notes-sync.pid"

# 检查是否已有同步进程在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  笔记同步进程已在运行 (PID: $OLD_PID)，跳过"
        exit 0
    else
        # 清理过期的 PID 文件
        rm -f "$PID_FILE"
    fi
fi

# 记录当前进程 PID
echo $$ > "$PID_FILE"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "========================================"
log "       后台笔记同步开始"
log "========================================"

# 检查笔记仓库
if [ ! -d "$NOTE_REPO" ]; then
    log "❌ 笔记仓库不存在: $NOTE_REPO"
    rm -f "$PID_FILE"
    exit 1
fi

cd "$NOTE_REPO" || {
    log "❌ 无法进入笔记仓库目录"
    rm -f "$PID_FILE"
    exit 1
}

# 1. 检查并提交本地修改
log "检查本地修改..."
if [ -n "$(git status --porcelain)" ]; then
    log "发现未提交的修改，正在提交..."

    if git add -A >> "$LOG_FILE" 2>&1; then
        COMMIT_MSG="自动提交：$(date '+%Y-%m-%d %H:%M:%S')"
        if git commit -m "$COMMIT_MSG" >> "$LOG_FILE" 2>&1; then
            log "正在推送到远程..."
            if git push origin main >> "$LOG_FILE" 2>&1; then
                log "✅ 本地修改已推送到远程"
            else
                log "⚠️  推送失败，但本地提交成功"
            fi
        else
            log "⚠️  提交失败"
        fi
    else
        log "⚠️  git add 失败"
    fi
else
    log "✅ 没有本地修改"
fi

# 2. 拉取最新代码
log "正在拉取远程最新代码..."
if git pull origin main >> "$LOG_FILE" 2>&1; then
    log "✅ 代码已更新"
else
    log "⚠️  拉取失败"
fi

# 3. 同步到博客（如果配置了 GITHUB_TOKEN）
if [ -n "$GITHUB_TOKEN" ]; then
    log "正在同步笔记时间戳..."
    cd "$BLOG_DIR" || {
        log "⚠️  无法进入博客目录"
    }

    if [ -f "tools/sync_notes_from_github.py" ]; then
        if python3 tools/sync_notes_from_github.py --batch content/post >> "$LOG_FILE" 2>&1; then
            log "✅ 时间戳同步完成"
        else
            log "⚠️  时间戳同步失败"
        fi
    else
        log "⚠️  未找到同步工具"
    fi
else
    log "⚠️  未配置 GITHUB_TOKEN，跳过时间戳同步"
fi

# 4. 复制笔记到博客
log "正在复制笔记到博客..."
cd "$BLOG_DIR" || {
    log "❌ 无法进入博客目录"
    rm -f "$PID_FILE"
    exit 1
}

# 注意：使用 --ignore-existing 保留博客中已有的文件（避免覆盖已有的 front matter）
# 只添加笔记仓库中新增的文件
if rsync -av \
    --ignore-existing \
    --exclude='.git/' \
    --exclude='.data/' \
    --exclude='.settings/' \
    --exclude='images/' \
    --exclude='assets/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.obsidian/' \
    --exclude='工作/' \
    "$NOTE_REPO/" "content/post/" >> "$LOG_FILE" 2>&1; then
    log "✅ 新笔记已添加到博客（已存在文件未被覆盖）"
else
    log "⚠️  笔记同步失败"
fi

# 5. 如果没有 GITHUB_TOKEN，使用简单的 front matter 添加工具
if [ -z "$GITHUB_TOKEN" ]; then
    log "正在为无 front matter 的文件添加基础 front matter..."
    cd "$BLOG_DIR"

    # 使用简单的 Python 脚本添加基础 front matter
    ADDED_COUNT=$(python3 << 'PYTHON_EOF'
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

post_dir = Path("content/post")
added_count = 0

for md_file in post_dir.rglob("*.md"):
    # 跳过 _index.md
    if md_file.name == "_index.md":
        continue

    try:
        content = md_file.read_text(encoding='utf-8')
        lines = content.split('\n')

        # 检查是否已有 front matter
        if len(lines) > 0 and lines[0].strip() == '---':
            # 已有 front matter，跳过
            continue

        # 提取标题（第一行 # 开头的内容）
        title = None
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                title = line.lstrip('#').strip()
                break
            elif line.strip():
                # 遇到非空非标题行，说明没有标题
                break

        if not title:
            title = md_file.stem

        # 生成当前时间（东八区）
        tz = timezone(timedelta(hours=8))
        now = datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%S%z')

        # 构建简单的 front matter
        frontmatter = f"""---
title: '{title}'
categories: ['技术']
date: {now}
draft: false
---
"""

        # 写入文件
        md_file.write_text(frontmatter + content, encoding='utf-8')
        added_count += 1

    except Exception as e:
        print(f"处理文件 {md_file} 时出错: {e}", file=sys.stderr)

print(added_count)
PYTHON_EOF
)

    log "✅ 为 ${ADDED_COUNT} 个文件添加了基础 front matter"
fi

log "========================================"
log "       后台笔记同步完成"
log "========================================"

# 清理 PID 文件
rm -f "$PID_FILE"

# 保留最近 7 天的日志
find /tmp -name "notes-sync-*.log" -mtime +7 -delete 2>/dev/null || true

exit 0

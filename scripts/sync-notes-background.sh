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

    # 使用 Python 脚本添加 front matter，优先从笔记仓库 git log 获取真实时间
    NOTE_REPO_PATH="$NOTE_REPO"
    ADDED_COUNT=$(python3 << PYTHON_EOF
import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta

post_dir = Path("content/post")
note_repo = Path("$NOTE_REPO_PATH")
added_count = 0

def get_git_time(repo_path: Path, rel_path: str):
    """从笔记仓库 git log 获取文件的最后更新时间"""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%aI', '--', rel_path],
            cwd=repo_path, capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None

def find_in_note_repo(note_repo: Path, filename: str):
    """在笔记仓库中查找同名文件，返回相对路径"""
    for f in note_repo.rglob(filename):
        if f.is_file() and f.suffix == '.md':
            try:
                return str(f.relative_to(note_repo))
            except ValueError:
                pass
    return None

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
                break

        if not title:
            title = md_file.stem

        # 尝试从笔记仓库 git log 获取真实时间
        date_str = None
        if note_repo.exists():
            # 先用博客相对路径直接匹配
            try:
                rel = str(md_file.relative_to(post_dir))
                date_str = get_git_time(note_repo, rel)
            except ValueError:
                pass

            # 如果直接匹配失败，用文件名在笔记仓库中查找
            if not date_str:
                found_rel = find_in_note_repo(note_repo, md_file.name)
                if found_rel:
                    date_str = get_git_time(note_repo, found_rel)

        # 如果 git log 也获取不到，从文件名提取日期作为最后手段
        if not date_str:
            import re
            m = re.match(r'(\d{4}-\d{2}-\d{2})', md_file.stem)
            if m:
                date_str = f"{m.group(1)}T22:00:00+08:00"

        # 最终回退：使用当前时间（但这是不应该发生的情况）
        if not date_str:
            tz = timezone(timedelta(hours=8))
            date_str = datetime.now(tz).strftime('%Y-%m-%dT%H:%M:%S%z')

        # 构建 front matter
        frontmatter = f"""---
title: '{title}'
categories: ['技术']
date: {date_str}
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

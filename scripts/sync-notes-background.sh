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

if rsync -av --delete \
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
    log "✅ 笔记已复制到博客"
else
    log "⚠️  笔记复制失败"
fi

log "========================================"
log "       后台笔记同步完成"
log "========================================"

# 清理 PID 文件
rm -f "$PID_FILE"

# 保留最近 7 天的日志
find /tmp -name "notes-sync-*.log" -mtime +7 -delete 2>/dev/null || true

exit 0

#!/bin/bash

# 全量笔记同步脚本
# 功能：从笔记仓库全量更新博客文章
#
# 使用场景：
# 1. 笔记仓库有大量更新时
# 2. 需要确保博客与笔记仓库完全一致时
# 3. 避免增量同步的格式冲突问题
#
# 注意：此脚本会删除 content/post/ 中的所有现有文章（除了 _index.md）

set -e

NOTE_REPO="/root/.openclaw/workspace/note-gen-sync"
BLOG_DIR="/var/www/bluespace3.github.io"
LOG_FILE="/tmp/full-notes-sync-$(date +%Y%m%d-%H%M%S).log"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ⚠️  $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ❌ $1" | tee -a "$LOG_FILE"
}

# 进入博客目录
cd "$BLOG_DIR" || {
    error "无法进入博客目录: $BLOG_DIR"
    exit 1
}

log "========================================"
log "       全量笔记同步开始"
log "========================================"

# 检查笔记仓库
if [ ! -d "$NOTE_REPO" ]; then
    error "笔记仓库不存在: $NOTE_REPO"
    exit 1
fi

# ============================================
# 第一步：确保笔记仓库与远程一致
# ============================================
log ""
log "【步骤 1/5】确保笔记仓库与远程一致..."

cd "$NOTE_REPO" || {
    error "无法进入笔记仓库"
    exit 1
}

# 检查是否有未提交的修改
if [ -n "$(git status --porcelain)" ]; then
    warn "发现未提交的本地修改"
    log "正在提交本地修改..."

    git add -A >> "$LOG_FILE" 2>&1
    COMMIT_MSG="自动提交：$(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$COMMIT_MSG" >> "$LOG_FILE" 2>&1
    log "✅ 本地修改已提交"
fi

# 拉取远程最新代码
log "正在拉取远程最新代码..."
if git pull origin main >> "$LOG_FILE" 2>&1; then
    log "✅ 笔记仓库已是最新版本"
else
    error "拉取远程代码失败"
    exit 1
fi

# 推送本地提交（如果有）
if [ -n "$(git log origin/main..HEAD --oneline)" ]; then
    log "正在推送本地提交到远程..."
    git push origin main >> "$LOG_FILE" 2>&1
    log "✅ 本地提交已推送到远程"
fi

# ============================================
# 第二步：备份现有博客文章
# ============================================
log ""
log "【步骤 2/5】备份现有博客文章..."

cd "$BLOG_DIR"
BACKUP_DIR="/tmp/blog-post-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -d "content/post" ]; then
    cp -r content/post "$BACKUP_DIR/"
    log "✅ 已备份到: $BACKUP_DIR"
else
    log "⚠️  content/post 目录不存在，跳过备份"
fi

# ============================================
# 第三步：全量删除存量博客文件
# ============================================
log ""
log "【步骤 3/5】全量删除存量博客文件..."

cd "$BLOG_DIR"

# 保留 _index.md 和其他特殊文件
find content/post -type f -name "*.md" ! -name "_index.md" -delete 2>/dev/null || true

# 删除空目录
find content/post -type d -empty -delete 2>/dev/null || true

log "✅ 已删除所有存量文章（保留 _index.md）"

# ============================================
# 第四步：全量复制笔记到博客
# ============================================
log ""
log "【步骤 4/5】全量复制笔记到博客..."

rsync -av \
    --include='*.md' \
    --include='*/' \
    --exclude='*' \
    --exclude='.git/' \
    --exclude='.data/' \
    --exclude='.settings/' \
    --exclude='images/' \
    --exclude='assets/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.obsidian/' \
    --exclude='工作/' \
    --exclude='INDEX.md' \
    "$NOTE_REPO/" "content/post/" >> "$LOG_FILE" 2>&1

MD_COUNT=$(find content/post -name "*.md" -type f | wc -l)
log "✅ 已复制 $MD_COUNT 个笔记文件"

# ============================================
# 第五步：为所有文件添加/更新 front matter
# ============================================
log ""
log "【步骤 5/5】为所有文件添加/更新 front matter..."

cd "$BLOG_DIR"

if [ -n "$GITHUB_TOKEN" ]; then
    log "使用 GitHub API 获取精确时间戳..."

    if [ -f "tools/sync_notes_from_github.py" ]; then
        # 先备份文件，用于获取时间戳
        python3 tools/sync_notes_from_github.py --batch content/post >> "$LOG_FILE" 2>&1
        log "✅ GitHub API 时间戳同步完成"
    else
        warn "未找到 sync_notes_from_github.py，使用本地时间戳"
    fi
fi

# 为所有文件添加完整的 front matter
# 这里使用 Python 脚本：
# 1. 如果文件没有 front matter，添加基础 front matter
# 2. 如果文件已有 front matter，保留并确保必填字段完整
PROCESSED_COUNT=$(python3 << 'PYTHON_EOF'
import os
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta

post_dir = Path("content/post")
processed_count = 0
tz = timezone(timedelta(hours=8))

for md_file in post_dir.rglob("*.md"):
    # 跳过 _index.md
    if md_file.name == "_index.md":
        continue

    try:
        content = md_file.read_text(encoding='utf-8')
        lines = content.split('\n')

        # 检查是否有 front matter
        has_frontmatter = len(lines) > 0 and lines[0].strip() == '---'

        if has_frontmatter:
            # 查找 front matter 结束位置
            fm_end = -1
            for i in range(1, len(lines)):
                if lines[i].strip() == '---':
                    fm_end = i
                    break

            if fm_end == -1:
                # front matter 格式错误，重新生成
                has_frontmatter = False
            else:
                # 检查必填字段
                fm_lines = lines[1:fm_end]
                fm_content = '\n'.join(fm_lines)

                # 检查必填字段
                has_title = bool(re.search(r'^title:', fm_content, re.MULTILINE))
                has_categories = bool(re.search(r'^categories:', fm_content, re.MULTILINE))
                has_date = bool(re.search(r'^date:', fm_content, re.MULTILINE))
                has_draft = bool(re.search(r'^draft:', fm_content, re.MULTILINE))

                if not (has_title and has_categories and has_date and has_draft):
                    # 缺少必填字段，需要补充
                    # 提取现有 front matter
                    existing_fm = {}

                    # 提取 title
                    title_match = re.search(r'^title:\s*(.+)', fm_content, re.MULTILINE)
                    if title_match:
                        existing_fm['title'] = title_match.group(1).strip()

                    # 提取 categories
                    cat_match = re.search(r'^categories:\s*(.+)', fm_content, re.MULTILINE)
                    if cat_match:
                        existing_fm['categories'] = cat_match.group(1).strip()

                    # 提取 date
                    date_match = re.search(r'^date:\s*(.+)', fm_content, re.MULTILINE)
                    if date_match:
                        existing_fm['date'] = date_match.group(1).strip()

                    # 补充缺失字段
                    if 'title' not in existing_fm:
                        # 从文件内容提取标题
                        title = None
                        for line in lines[fm_end+1:]:
                            line = line.strip()
                            if line.startswith('#'):
                                title = line.lstrip('#').strip()
                                break
                            elif line.strip():
                                break
                        existing_fm['title'] = title if title else md_file.stem

                    if 'categories' not in existing_fm:
                        # 从目录结构推断分类
                        categories = []
                        if md_file.parent != post_dir:
                            relative_path = md_file.parent.relative_to(post_dir)
                            if len(relative_path.parts) > 0:
                                categories = [relative_path.parts[0]]
                        if not categories:
                            categories = ['技术']
                        existing_fm['categories'] = str(categories)

                    if 'date' not in existing_fm:
                        # 使用文件修改时间
                        mtime = datetime.fromtimestamp(md_file.stat().st_mtime, tz)
                        existing_fm['date'] = mtime.strftime('%Y-%m-%dT%H:%M:%S%z')

                    if 'draft' not in existing_fm:
                        existing_fm['draft'] = 'false'

                    # 重建完整的 front matter
                    new_frontmatter = f"""---
title: {existing_fm['title']}
categories: {existing_fm['categories']}
date: {existing_fm['date']}
draft: {existing_fm['draft']}
---"""

                    # 替换原有的 front matter
                    new_content = new_frontmatter + '\n' + '\n'.join(lines[fm_end+1:])
                    md_file.write_text(new_content, encoding='utf-8')
                    processed_count += 1

        if not has_frontmatter:
            # 提取标题
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

            # 从目录结构推断分类
            categories = []
            if md_file.parent != post_dir:
                relative_path = md_file.parent.relative_to(post_dir)
                if len(relative_path.parts) > 0:
                    categories = [relative_path.parts[0]]
            if not categories:
                categories = ['技术']

            # 使用文件修改时间
            mtime = datetime.fromtimestamp(md_file.stat().st_mtime, tz)
            date_str = mtime.strftime('%Y-%m-%dT%H:%M:%S%z')

            # 构建完整的 front matter
            frontmatter = f"""---
title: '{title}'
categories: {categories}
date: {date_str}
draft: false
---"""

            # 写入文件
            md_file.write_text(frontmatter + '\n' + content, encoding='utf-8')
            processed_count += 1

    except Exception as e:
        print(f"处理文件 {md_file} 时出错: {e}", file=__import__('sys').stderr)

print(processed_count)
PYTHON_EOF
)

log "✅ 已为 $PROCESSED_COUNT 个文件添加/更新 front matter"

# ============================================
# 完成
# ============================================
log ""
log "========================================"
log "       全量笔记同步完成"
log "========================================"
log ""
log "📊 统计信息："
log "  - 笔记文件总数: $MD_COUNT"
log "  - 处理 front matter: $PROCESSED_COUNT"
log "  - 备份位置: $BACKUP_DIR"
log ""
log "📝 下一步："
log "  1. 检查同步结果: git status"
log "  2. 构建网站: hugo --cleanDestinationDir"
log "  3. 预览本地: hugo server"
log "  4. 部署: ./deploy.sh"
log ""

# 保留最近 7 天的日志
find /tmp -name "full-notes-sync-*.log" -mtime +7 -delete 2>/dev/null || true

exit 0

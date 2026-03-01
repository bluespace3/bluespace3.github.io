#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动加密文章工具
在 front matter 中添加 password 字段即可自动加密全文
"""

import os
import re
from pathlib import Path


def auto_encrypt_article(file_path: Path, dry_run: bool = False) -> bool:
    """
    自动为文章添加加密标记

    Args:
        file_path: Markdown 文件路径
        dry_run: 预览模式，不实际修改

    Returns:
        bool: 是否成功处理
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')

        # 解析 Front Matter
        frontmatter_end = -1
        has_frontmatter = False

        if lines and lines[0].strip() == '---':
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    frontmatter_end = i
                    has_frontmatter = True
                    break

        if not has_frontmatter:
            print(f"  ⚠️  没有 Front Matter，跳过：{file_path.name}")
            return False

        # 提取 Front Matter 内容
        frontmatter_lines = lines[1:frontmatter_end]
        frontmatter_text = '\n'.join(frontmatter_lines)

        # 检查是否有 password 字段
        password_match = re.search(r'^password:\s*[\'"]?([^\'"\n]+)[\'"]?', frontmatter_text, re.MULTILINE)

        if not password_match:
            return False  # 没有 password 字段，跳过

        password = password_match.group(1)

        # 检查是否已经有加密标记
        body_content = '\n'.join(lines[frontmatter_end + 1:])
        if '{{% hugo-encryptor' in body_content:
            print(f"  ⏭️  已有加密标记，跳过：{file_path.name}")
            return False

        # 检查是否有 <!--more-->
        has_more = '<!--more-->' in body_content

        # 构建新的内容
        if has_more:
            # 如果有 <!--more-->，在它后面添加加密标记
            parts = body_content.split('<!--more-->', 1)
            new_body = parts[0] + '<!--more-->\n\n{{% hugo-encryptor "' + password + '" %}}\n\n' + parts[1].strip() + '\n\n{{% /hugo-encryptor %}}'
        else:
            # 如果没有 <!--more-->，在 Front Matter 后添加
            new_body = '\n'.join(lines[frontmatter_end + 1:]).strip()
            new_body = f'{new_body}\n\n{{% hugo-encryptor "{password}" %}}\n\n{new_body}\n\n{{% /hugo-encryptor %}}'

        # 移除 Front Matter 中的 password 字段
        new_frontmatter = re.sub(r'\npassword:\s*[\'"]?[^\'"\n]+[\'"]?\n', '\n', frontmatter_text)

        # 组合最终内容
        new_content = '---\n' + new_frontmatter + '\n---\n\n' + new_body

        if dry_run:
            print(f"  [DRY RUN] 加密文章：{file_path.name}")
            print(f"     密码: {password}")
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✅ 已加密：{file_path.name}")

        return True

    except Exception as e:
        print(f"  ❌ 处理失败：{file_path.name} - {e}")
        return False


def batch_encrypt(directory: Path, dry_run: bool = False):
    """
    批量加密目录中的文章

    Args:
        directory: 文章目录
        dry_run: 预览模式
    """
    print(f"\n{'='*60}")
    print(f"{'🔐 自动加密文章' if not dry_run else '👀 预览加密结果'}")
    print(f"{'='*60}\n")

    md_files = list(directory.rglob('*.md'))
    total = len(md_files)
    encrypted = 0

    for md_file in md_files:
        if auto_encrypt_article(md_file, dry_run):
            encrypted += 1

    print(f"\n{'='*60}")
    print(f"📊 统计：总共 {total} 篇文章，加密 {encrypted} 篇")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='自动加密文章工具')
    parser.add_argument('directory', nargs='?', default='content/post',
                       help='文章目录（默认：content/post）')
    parser.add_argument('--dry-run', action='store_true',
                       help='预览模式，不实际修改文件')

    args = parser.parse_args()

    target_dir = Path(args.directory)

    if not target_dir.exists():
        print(f"❌ 目录不存在：{target_dir}")
        exit(1)

    batch_encrypt(target_dir, args.dry_run)

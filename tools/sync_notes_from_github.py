#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
笔记同步到博客主脚本
从 GitHub 笔记仓库同步笔记，使用 GitHub API 获取真实时间并生成 Hugo Front Matter
"""

import os
import sys
import re
import time
from pathlib import Path
from typing import Optional, List
import argparse

# 添加 tools 目录到 Python 路径
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from github_api import GitHubFileTimeFetcher, convert_github_time_to_hugo, extract_category_from_path
from config import SyncNotesConfig


class NotesSyncManager:
    """笔记同步管理器"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化同步管理器

        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config = SyncNotesConfig(config_path)

        # 初始化 GitHub API 客户端
        self.github_fetcher = GitHubFileTimeFetcher(
            owner=self.config.github_owner,
            repo=self.config.github_repo,
            token=self.config.github_token
        )

        # 项目根目录（假设在 Hugo 项目根目录运行）
        self.project_root = Path.cwd()
        self.content_dir = self.project_root / self.config.hugo_content_dir

        # 统计信息
        self.stats = {
            'total': 0,
            'success': 0,
            'skipped': 0,
            'failed': 0
        }

    def add_hugo_frontmatter(self, file_path: Path, created_at: str, updated_at: str,
                           title: Optional[str] = None, category: Optional[str] = None,
                           overwrite: bool = True, dry_run: bool = False) -> bool:
        """
        添加/更新 Hugo Front Matter

        Args:
            file_path: 文件路径
            created_at: GitHub API 返回的创建时间（ISO 8601）
            updated_at: GitHub API 返回的更新时间（ISO 8601）
            title: 文章标题（如果为 None 则从文件名提取）
            category: 分类（如果为 None 则从文件路径提取）
            overwrite: 是否覆盖已有 frontmatter

        Returns:
            bool: 是否成功
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')

            # 检查是否有完整的 Front Matter
            has_complete_frontmatter = False
            frontmatter_end_pos = -1

            if lines and lines[0].strip() == '---':
                # 找到 Front Matter 的结束位置
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '---':
                        frontmatter_end_pos = i
                        has_complete_frontmatter = True
                        break

            # 如果已经有完整的 Front Matter 且不覆盖，跳过
            if has_complete_frontmatter and not overwrite:
                print(f"  ⏭️  已有 Front Matter，跳过：{file_path.relative_to(self.project_root)}")
                self.stats['skipped'] += 1
                return True

            # 提取标题
            if title is None:
                title = file_path.stem  # 文件名不含扩展名

            # 提取分类
            if category is None:
                category = extract_category_from_path(str(file_path), self.config.hugo_content_dir)
                # 使用配置中的默认分类
                if not category or category == '技术':
                    category = self.config.frontmatter_default_category

            # 转换时间为 Hugo 格式
            date_hugo = convert_github_time_to_hugo(created_at)
            lastmod_hugo = convert_github_time_to_hugo(updated_at)

            # 构建 Front Matter
            frontmatter = f"""---
title: '{title}'
categories: ["{category}"]
date: {date_hugo}
lastmod: {lastmod_hugo}
encrypted: false
"""

            # 预览模式
            if dry_run:
                action = "更新" if has_complete_frontmatter else "添加"
                print(f"  [DRY RUN] {action} Front Matter：{file_path.relative_to(self.project_root)}")
                print(f"     标题: {title}")
                print(f"     分类: {category}")
                print(f"     创建时间: {date_hugo}")
                self.stats['success'] += 1
                return True

            # 如果有 Front Matter，替换它；否则添加到开头
            if has_complete_frontmatter:
                # 保留 Front Matter 之后的内容
                content_lines = lines[frontmatter_end_pos + 1:]
                content_body = '\n'.join(content_lines)
            else:
                content_body = content

            # 修复 Obsidian wikilink 图片格式
            # 将 ![[image.png]] 转换为 ![image.png](/assets/image.png)
            # 将 ![[image.png|alt text]] 转换为 ![alt text](/assets/image.png)
            def fix_obsidian_wikilink(match):
                """修复 Obsidian wikilink 格式"""
                filename = match.group(1).strip()
                alt_text = match.group(3) or filename
                return f"![{alt_text}](/assets/{filename})"

            content_body = re.sub(
                r'!\[\[([^\]]+?)(\|([^\]]+))?\]\]',
                fix_obsidian_wikilink,
                content_body
            )


            # 修正图片路径：将相对路径改为绝对路径
            # 将 assets/xxx.png 替换为 /assets/xxx.png
            content_body = re.sub(
                r'!\[([^\]]*)\]\(assets/([^)]+)\)',
                r'![\1](/assets/\2)',
                content_body
            )

            # 构建最终内容
            new_content = frontmatter + content_body

            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            action = "更新" if has_complete_frontmatter else "添加"
            print(f"  ✅ {action} Front Matter：{file_path.relative_to(self.project_root)}")
            print(f"     标题: {title}")
            print(f"     分类: {category}")
            print(f"     创建时间: {date_hugo}")
            self.stats['success'] += 1
            return True

        except Exception as e:
            print(f"  ❌ 处理文件失败 {file_path.relative_to(self.project_root)}：{e}")
            self.stats['failed'] += 1
            return False

    def sync_from_note_repo(self, note_repo_path: Path = None, dry_run: bool = False) -> dict:
        """
        从笔记仓库同步新文件到博客目录

        Args:
            note_repo_path: 笔记仓库路径（如果为 None，使用默认路径）
            dry_run: 预览模式（不实际复制文件）

        Returns:
            dict: {'copied': 复制的文件数, 'skipped': 跳过的文件数}
        """
        # 默认笔记仓库路径
        if note_repo_path is None:
            note_repo_path = Path.home() / '.openclaw' / 'workspace' / 'note-gen-sync'

        if not note_repo_path.exists():
            print(f"⚠️  笔记仓库不存在：{note_repo_path}")
            print("   跳过文件同步")
            return {'copied': 0, 'skipped': 0}

        # 获取忽略目录列表
        ignore_dirs = self.config.get('sync.ignore_dirs', [])

        print(f"\n🔄 从笔记仓库同步新文件")
        print(f"   笔记仓库：{note_repo_path}")
        print(f"   目标目录：{self.content_dir}")
        print(f"   预览模式：{'是' if dry_run else '否'}\n")

        stats = {'copied': 0, 'skipped': 0}

        # 查找笔记仓库中所有的 .md 文件
        for note_file in note_repo_path.rglob('*.md'):
            # 检查是否在忽略目录中
            skip = False
            for ignore_dir in ignore_dirs:
                if ignore_dir in note_file.parts:
                    skip = True
                    break
            if skip:
                continue

            # 计算相对路径
            try:
                rel_path = note_file.relative_to(note_repo_path)
            except ValueError:
                continue

            # 计算目标路径
            target_file = self.content_dir / rel_path

            # 检查目标文件是否已存在
            if target_file.exists():
                stats['skipped'] += 1
                continue

            # 复制文件
            if dry_run:
                print(f"  [DRY RUN] 将复制：{rel_path}")
            else:
                # 创建目标目录
                target_file.parent.mkdir(parents=True, exist_ok=True)

                # 复制文件
                import shutil
                shutil.copy2(note_file, target_file)
                print(f"  ✅ 已复制：{rel_path}")

                stats['copied'] += 1

        # 同步 assets 目录（如果有图片等资源）
        assets_dir = note_repo_path / 'assets'
        if assets_dir.exists() and assets_dir.is_dir():
            static_assets_dir = self.project_root / 'static' / 'assets'
            print(f"\n  📁 同步 assets 目录...")

            if dry_run:
                print(f"  [DRY RUN] 将复制 assets 到 static/")
            else:
                # 如果 static/assets 不存在，创建它
                if not static_assets_dir.exists():
                    static_assets_dir.mkdir(parents=True, exist_ok=True)

                # 复制 assets 目录的内容
                import shutil
                for asset_file in assets_dir.rglob('*'):
                    if asset_file.is_file():
                        rel_path = asset_file.relative_to(assets_dir)
                        target_asset = static_assets_dir / rel_path

                        # 创建目标目录
                        target_asset.parent.mkdir(parents=True, exist_ok=True)

                        # 检查是否已存在
                        if not target_asset.exists():
                            shutil.copy2(asset_file, target_asset)
                            stats['copied'] += 1

        print(f"\n  📊 同步完成：")
        print(f"     复制：{stats['copied']} 个")
        print(f"     跳过：{stats['skipped']} 个")

        return stats

    def process_file(self, file_path: Path, overwrite: bool = True, dry_run: bool = False) -> bool:
        """
        处理单个 Markdown 文件

        Args:
            file_path: 文件路径
            overwrite: 是否覆盖已有 frontmatter
            dry_run: 预览模式（不实际修改文件）

        Returns:
            bool: 是否成功
        """
        self.stats['total'] += 1

        # 获取相对于 content_dir 的路径
        try:
            rel_path = file_path.relative_to(self.content_dir)
        except ValueError:
            print(f"  ⚠️  文件不在内容目录中：{file_path}")
            self.stats['failed'] += 1
            return False

        # 转换为 Unix 风格的路径（GitHub API 使用）
        github_path = str(rel_path).replace('\\', '/')

        # 从 GitHub API 获取文件时间
        print(f"  🌐 获取 GitHub 文件信息：{github_path}")
        file_info = self.github_fetcher.get_file_info(github_path, self.config.github_branch)

        if not file_info:
            print(f"  ⚠️  无法获取文件信息，跳过：{github_path}")
            self.stats['failed'] += 1
            return False

        # 添加/更新 Front Matter
        return self.add_hugo_frontmatter(
            file_path=file_path,
            created_at=file_info['created_at'],
            updated_at=file_info['updated_at'],
            overwrite=overwrite,
            dry_run=dry_run
        )

    def process_directory(self, directory: Path, overwrite: bool = True,
                         batch_size: int = 10, batch_delay: float = 1.0,
                         sync_files: bool = False, dry_run: bool = False) -> None:
        """
        批量处理目录下所有 Markdown 文件

        Args:
            directory: 要处理的目录
            overwrite: 是否覆盖已有 frontmatter
            batch_size: 批量处理大小
            batch_delay: 批量之间的延迟（秒）
            sync_files: 是否从笔记仓库同步新文件
            dry_run: 预览模式（不实际修改文件）
        """
        # 转换为 Path 对象
        directory = Path(directory)

        # 如果是相对路径，转换为绝对路径
        if not directory.is_absolute():
            directory = self.project_root / directory

        # 获取忽略目录列表
        ignore_dirs = self.config.get('sync.ignore_dirs', [])

        print(f"\n📁 开始处理目录：{directory.relative_to(self.project_root)}")
        print(f"   覆盖模式: {'是' if overwrite else '否'}")
        print(f"   批量大小: {batch_size}")
        print(f"   批量延迟: {batch_delay}秒")
        print(f"   同步新文件: {'是' if sync_files else '否'}")
        print(f"   预览模式: {'是' if dry_run else '否'}")
        if ignore_dirs:
            print(f"   忽略目录: {', '.join(ignore_dirs)}\n")
        else:
            print(f"\n")

        # 从笔记仓库同步新文件
        if sync_files:
            sync_stats = self.sync_from_note_repo(dry_run=dry_run)
            if sync_stats['copied'] > 0:
                print(f"\n  💡 新文件已同步，准备添加 Front Matter...\n")

        # 查找所有 Markdown 文件，排除忽略的目录
        md_files = []
        for file_path in directory.rglob('*.md'):
            # 检查文件路径中是否包含忽略的目录
            skip = False
            for ignore_dir in ignore_dirs:
                if ignore_dir in file_path.parts:
                    skip = True
                    break
            if not skip:
                md_files.append(file_path)

        print(f"  📊 找到 {len(md_files)} 个 Markdown 文件\n")

        if not md_files:
            print(f"  ⚠️  未找到 Markdown 文件")
            return

        # 批量处理
        for i, file_path in enumerate(md_files, 1):
            print(f"[{i}/{len(md_files)}]", end=" ")
            self.process_file(file_path, overwrite=overwrite, dry_run=dry_run)

            # 批量延迟
            if i % batch_size == 0 and i < len(md_files):
                print(f"\n  ⏸️  已处理 {i} 个文件，等待 {batch_delay} 秒以避免触发 API 速率限制...\n")
                time.sleep(batch_delay)

        # 打印统计信息
        print(f"\n📊 处理完成：")
        print(f"   总计: {self.stats['total']} 个文件")
        print(f"   成功: {self.stats['success']} 个")
        print(f"   跳过: {self.stats['skipped']} 个")
        print(f"   失败: {self.stats['failed']} 个")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='从 GitHub 笔记仓库同步笔记到 Hugo 博客，使用 GitHub API 获取真实时间',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  # 预览模式（不实际修改）
  python %(prog)s --dry-run --verbose

  # 处理单个文件
  python %(prog)s --file "content/post/技术/python.md"

  # 批量处理目录
  python %(prog)s --batch content/post

  # 从笔记仓库同步新文件并处理
  python %(prog)s --batch content/post --sync-files

  # 从笔记仓库同步新文件（预览模式）
  python %(prog)s --batch content/post --sync-files --dry-run

  # 不覆盖已有 frontmatter
  python %(prog)s --batch content/post --no-overwrite
        """
    )

    parser.add_argument('--file', type=str, help='处理单个文件')
    parser.add_argument('--batch', type=str, help='批量处理目录')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--dry-run', action='store_true', help='预览模式（不实际修改文件）')
    parser.add_argument('--no-overwrite', action='store_true', help='不覆盖已有 frontmatter')
    parser.add_argument('--sync-files', action='store_true', help='从笔记仓库同步新文件到博客目录')
    parser.add_argument('--verbose', action='store_true', help='详细输出')

    args = parser.parse_args()

    # 检查参数
    if not args.file and not args.batch:
        parser.print_help()
        print("\n❌ 错误：请指定 --file 或 --batch 参数")
        sys.exit(1)

    # 初始化同步管理器
    manager = NotesSyncManager(config_path=args.config)

    print("=" * 60)
    print("📝 笔记同步到博客工具")
    print("=" * 60)
    print(f"📋 配置：")
    print(f"   GitHub: {manager.config.github_owner}/{manager.config.github_repo}")
    print(f"   Branch: {manager.config.github_branch}")
    print(f"   Content Dir: {manager.config.hugo_content_dir}")
    print(f"   Timezone: {manager.config.hugo_timezone}")
    print("=" * 60)

    if args.dry_run:
        print("\n⚠️  预览模式：不会实际修改文件\n")

    # 检查 GitHub Token
    if not manager.config.github_token:
        print("❌ 错误：未设置 GITHUB_TOKEN 环境变量")
        print("   提示：")
        print("   1. 在 GitHub Settings -> Developer settings -> Personal access tokens 创建 Token")
        print("   2. 设置环境变量：export GITHUB_TOKEN='your_token_here'")
        print("   3. 或在 Windows PowerShell：$env:GITHUB_TOKEN='your_token_here'")
        sys.exit(1)

    try:
        # 处理单个文件
        if args.file:
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"❌ 错误：文件不存在：{file_path}")
                sys.exit(1)

            print(f"\n📄 处理单个文件：{file_path}\n")
            manager.process_file(file_path, overwrite=not args.no_overwrite)

        # 批量处理目录
        elif args.batch:
            directory = Path(args.batch)
            if not directory.exists():
                print(f"❌ 错误：目录不存在：{directory}")
                sys.exit(1)

            manager.process_directory(
                directory,
                overwrite=not args.no_overwrite,
                batch_size=manager.config.get('sync.batch_size', 10),
                batch_delay=manager.config.get('sync.batch_delay', 1.0),
                sync_files=args.sync_files,
                dry_run=args.dry_run
            )

        # 打印最终统计
        print("\n" + "=" * 60)
        print("📊 最终统计：")
        print(f"   总计: {manager.stats['total']} 个文件")
        print(f"   成功: {manager.stats['success']} 个 ✅")
        print(f"   跳过: {manager.stats['skipped']} 个 ⏭️")
        print(f"   失败: {manager.stats['failed']} 个 ❌")
        print("=" * 60)

        if manager.stats['failed'] > 0:
            print("\n⚠️  部分文件处理失败，请检查错误信息")
            sys.exit(1)
        else:
            print("\n🎉 所有文件处理成功！")

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序执行时发生错误：{e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

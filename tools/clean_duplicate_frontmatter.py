#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Front Matter 清理工具
修复由 sync_notes_from_github.py 引起的 Front Matter 重复问题
"""

import os
import sys
import re
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime
import argparse


class FrontMatterCleaner:
    """Front Matter 清理器"""

    def __init__(self, backup_dir: Optional[Path] = None):
        """
        初始化清理器

        Args:
            backup_dir: 备份目录，如果为 None 则不备份
        """
        self.backup_dir = backup_dir
        self.stats = {
            'total_files': 0,
            'cleaned_files': 0,
            'skipped_files': 0,
            'error_files': 0
        }

    def detect_duplicate_frontmatter(self, content: str) -> Tuple[List[int], List[Tuple[int, int]], bool]:
        """
        检测文件中的 Front Matter 重复

        Args:
            content: 文件内容

        Returns:
            Tuple[List[int], List[Tuple[int, int]], bool]:
                - 前 20 行内的 `---` 标记的行号列表
                - 完整 Front Matter 块的 (开始行, 结束行) 列表
                - 是否有重复（连续多个 Front Matter 块）
        """
        lines = content.split('\n')

        # 只检查前 20 行（避免误检内容中的 horizontal rules）
        check_limit = min(20, len(lines))
        dash_positions = [i for i in range(check_limit) if lines[i].strip() == '---']

        # 找出所有连续的 Front Matter 块（只在前 20 行内）
        frontmatter_blocks = []
        has_duplicate = False

        i = 0
        while i < len(dash_positions):
            start_pos = dash_positions[i]
            # 检查是否有配对的结束标记
            if i + 1 < len(dash_positions):
                end_pos = dash_positions[i + 1]
                # 验证是否是有效的 Front Matter（检查是否有常见的 YAML 字段）
                block_content = '\n'.join(lines[start_pos + 1:end_pos])
                if self._is_valid_frontmatter(block_content):
                    if frontmatter_blocks:
                        # 已有一个 Front Matter，这是重复的
                        has_duplicate = True
                    frontmatter_blocks.append((start_pos, end_pos))
                    # 检查是否还有连续的 Front Matter 块
                    i += 2  # 跳到下一个可能的起始标记
                    if i < len(dash_positions):
                        # 尝试检测下一个块
                        continue
                    break  # 没有更多标记，结束
            i += 1

        return dash_positions, frontmatter_blocks, has_duplicate

    def _is_valid_frontmatter(self, content: str) -> bool:
        """
        检查是否是有效的 Front Matter

        Args:
            content: Front Matter 内容（不包含 --- 标记）

        Returns:
            bool: 是否有效
        """
        # 检查是否包含常见的 Front Matter 字段
        frontmatter_keywords = ['title:', 'categories:', 'date:', 'lastmod:', 'tags:', 'description:']
        return any(keyword in content for keyword in frontmatter_keywords)

    def _find_content_start(self, lines: List[str], frontmatter_blocks: List[Tuple[int, int]]) -> int:
        """
        找到真实内容的起始行（跳过所有重复的 Front Matter）

        Args:
            lines: 文件行列表
            frontmatter_blocks: 所有 Front Matter 块的位置

        Returns:
            int: 真实内容的起始行
        """
        if not frontmatter_blocks:
            return 0

        # 最后一个 Front Matter 块的结束位置
        last_frontmatter_end = frontmatter_blocks[-1][1] + 1

        # 跳过所有连续的 `---` 标记
        content_start = last_frontmatter_end
        while content_start < len(lines):
            line = lines[content_start].strip()
            if line != '---':
                # 检查这是否看起来像另一个 Front Matter
                remaining = '\n'.join(lines[content_start:content_start + 10])
                if 'title:' in remaining or 'categories:' in remaining:
                    # 这可能是另一个 Front Matter，跳过
                    content_start += 1
                    continue
                break
            content_start += 1

        return content_start

    def clean_file(self, file_path: Path, dry_run: bool = False) -> bool:
        """
        清理单个文件的重复 Front Matter

        Args:
            file_path: 文件路径
            dry_run: 预览模式

        Returns:
            bool: 是否成功清理
        """
        try:
            self.stats['total_files'] += 1

            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')

            # 检测重复（只检查前 20 行）
            dash_positions, frontmatter_blocks, has_duplicate = self.detect_duplicate_frontmatter(content)
            dash_count = len(dash_positions)

            # 如果没有重复或只有正常的 2 个标记，跳过
            if not has_duplicate and dash_count <= 2:
                if dry_run:
                    print(f"  ✓ {file_path.relative_to(Path.cwd())}: 正常")
                self.stats['skipped_files'] += 1
                return True

            # 如果没有重复但有多个标记（说明是内容中的 horizontal rules）
            if not has_duplicate:
                if dry_run:
                    print(f"  ✓ {file_path.relative_to(Path.cwd())}: 正常（包含内容中的 --- 标记）")
                self.stats['skipped_files'] += 1
                return True

            # 有重复！
            if dry_run:
                print(f"  ⚠️  {file_path.relative_to(Path.cwd())}: 发现重复 Front Matter（{len(frontmatter_blocks)} 个块）")
                self.stats['cleaned_files'] += 1
                return True

            # 执行清理
            # 保留最后一个完整的 Front Matter 块
            if frontmatter_blocks:
                last_block_start, last_block_end = frontmatter_blocks[-1]
                # 保留最后一个 Front Matter
                new_frontmatter = '\n'.join(lines[last_block_start:last_block_end + 1])

                # 找到真实内容
                content_start = self._find_content_start(lines, frontmatter_blocks)
                content_body = '\n'.join(lines[content_start:])

                # 构建新内容
                new_content = new_frontmatter + '\n' + content_body

                # 创建备份
                if self.backup_dir:
                    self._create_backup(file_path)

                # 写入清理后的内容
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                print(f"  ✅ {file_path.relative_to(Path.cwd())}: 已清理（移除 {len(frontmatter_blocks) - 1} 个重复块）")
                self.stats['cleaned_files'] += 1
                return True
            else:
                print(f"  ❌ {file_path.relative_to(Path.cwd())}: 无法找到有效的 Front Matter 块")
                self.stats['error_files'] += 1
                return False

        except Exception as e:
            print(f"  ❌ {file_path.relative_to(Path.cwd())}: 处理失败 - {e}")
            self.stats['error_files'] += 1
            return False

    def _create_backup(self, file_path: Path) -> None:
        """
        创建文件备份

        Args:
            file_path: 原文件路径
        """
        if not self.backup_dir:
            return

        # 计算备份路径（保留目录结构）
        rel_path = file_path.relative_to(Path.cwd())
        backup_path = self.backup_dir / rel_path

        # 创建备份目录
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # 复制文件
        shutil.copy2(file_path, backup_path)

    def clean_directory(self, directory: Path, dry_run: bool = False) -> None:
        """
        清理目录下所有 Markdown 文件

        Args:
            directory: 目录路径
            dry_run: 预览模式
        """
        # 转换为 Path 对象
        directory = Path(directory)

        # 如果是相对路径，转换为绝对路径
        if not directory.is_absolute():
            directory = Path.cwd() / directory

        if not directory.exists():
            print(f"❌ 错误：目录不存在：{directory}")
            return

        print(f"\n🔍 扫描目录：{directory.relative_to(Path.cwd())}")
        if dry_run:
            print("   模式：预览（不会修改文件）")
        if self.backup_dir and not dry_run:
            print(f"   备份：{self.backup_dir.relative_to(Path.cwd())}")
        print()

        # 查找所有 Markdown 文件
        md_files = list(directory.rglob('*.md'))
        print(f"📊 找到 {len(md_files)} 个 Markdown 文件\n")

        if not md_files:
            print("  ⚠️  未找到 Markdown 文件")
            return

        # 处理每个文件
        for i, file_path in enumerate(md_files, 1):
            print(f"[{i}/{len(md_files)}]", end=" ")
            self.clean_file(file_path, dry_run=dry_run)

        # 打印统计
        print(f"\n📊 处理完成：")
        print(f"   总计：{self.stats['total_files']} 个文件")
        print(f"   已清理：{self.stats['cleaned_files']} 个 ✅")
        print(f"   已跳过：{self.stats['skipped_files']} 个 ⏭️")
        print(f"   错误：{self.stats['error_files']} 个 ❌")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='清理 Markdown 文件中重复的 Front Matter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  # 预览模式（查看哪些文件需要清理）
  python %(prog)s content/post --dry-run

  # 清理并创建备份
  python %(prog)s content/post --backup ./backups/frontmatter_cleanup

  # 清理不备份（不推荐）
  python %(prog)s content/post

  # 清理单个文件
  python %(prog)s content/post/AIGC学习笔记/提示词技巧.md --backup ./backups
        """
    )

    parser.add_argument('directory', type=str, help='目录或文件路径')
    parser.add_argument('--dry-run', action='store_true', help='预览模式（不实际修改文件）')
    parser.add_argument('--backup', type=str, help='备份目录路径（推荐）')

    args = parser.parse_args()

    # 检查路径
    target_path = Path(args.directory)
    if not target_path.exists():
        print(f"❌ 错误：路径不存在：{target_path}")
        sys.exit(1)

    # 创建备份目录
    backup_dir = None
    if args.backup and not args.dry_run:
        backup_dir = Path(args.backup)
        # 如果是相对路径，转换为绝对路径
        if not backup_dir.is_absolute():
            backup_dir = Path.cwd() / backup_dir
        # 添加时间戳
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = backup_dir / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        # 尝试显示相对路径，如果失败则显示绝对路径
        try:
            display_path = backup_dir.relative_to(Path.cwd())
        except ValueError:
            display_path = backup_dir
        print(f"📦 备份目录：{display_path}\n")

    # 创建清理器
    cleaner = FrontMatterCleaner(backup_dir=backup_dir)

    print("=" * 60)
    print("🧹 Front Matter 清理工具")
    print("=" * 60)

    # 处理单个文件或目录
    if target_path.is_file():
        if target_path.suffix != '.md':
            print(f"❌ 错误：不是 Markdown 文件：{target_path}")
            sys.exit(1)

        print(f"\n📄 处理文件：{target_path.relative_to(Path.cwd())}\n")
        cleaner.clean_file(target_path, dry_run=args.dry_run)

        print(f"\n📊 处理完成：")
        print(f"   总计：{cleaner.stats['total_files']} 个文件")
        print(f"   已清理：{cleaner.stats['cleaned_files']} 个 ✅")
        print(f"   已跳过：{cleaner.stats['skipped_files']} 个 ⏭️")
        print(f"   错误：{cleaner.stats['error_files']} 个 ❌")

    elif target_path.is_dir():
        cleaner.clean_directory(target_path, dry_run=args.dry_run)

    print("=" * 60)

    if cleaner.stats['error_files'] > 0:
        print("\n⚠️  部分文件处理失败，请检查错误信息")
        sys.exit(1)
    elif cleaner.stats['cleaned_files'] > 0 and args.dry_run:
        print(f"\n💡 预览完成：发现 {cleaner.stats['cleaned_files']} 个需要清理的文件")
        print(f"   再次运行时不加 --dry-run 即可执行清理")
    elif cleaner.stats['cleaned_files'] > 0:
        print(f"\n🎉 成功清理 {cleaner.stats['cleaned_files']} 个文件！")
        if backup_dir:
            print(f"   备份位置：{backup_dir.relative_to(Path.cwd())}")
    else:
        print("\n✅ 所有文件正常，无需清理")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动添加目录分类工具
根据文件所在的目录自动添加到 categories
"""

import os
import sys
import argparse
from pathlib import Path


def add_categories_from_directory(file_path, dry_run=False):
    """
    根据文件所在的目录自动添加 categories

    Args:
        file_path: markdown 文件路径
        dry_run: 是否只是预览不实际修改
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')

        # 查找 front matter
        front_matter_start = -1
        front_matter_end = -1

        for i, line in enumerate(lines):
            if line.strip() == '---':
                if front_matter_start == -1:
                    front_matter_start = i
                else:
                    front_matter_end = i
                    break

        # 如果没有 front matter，跳过
        if front_matter_start == -1 or front_matter_end == -1:
            return False, "没有找到 front matter"

        # 获取文件所在的相对目录（相对于 content/）
        full_path = Path(file_path).resolve()
        content_dir = Path('content').resolve()

        try:
            relative_path = full_path.relative_to(content_dir)
        except ValueError:
            # 文件不在 content 目录下
            return False, "文件不在 content 目录中"

        # 提取目录作为分类（排除 post、archives 等特殊目录）
        special_dirs = {'post', 'posts', 'archive', 'archives', 'draft', 'drafts'}

        categories = []
        for part in relative_path.parts[:-1]:  # 排除文件名
            if part and part.lower() not in special_dirs:
                # 转换目录名为分类名
                category = part
                categories.append(category)

        if not categories:
            return False, "没有找到有效的分类目录"

        # 解析现有的 front matter
        front_matter_lines = lines[front_matter_start + 1:front_matter_end]

        has_categories = False
        categories_line_idx = -1
        categories_list = []

        # 解析现有的 categories
        for i, line in enumerate(front_matter_lines):
            if line.strip().startswith('categories:'):
                has_categories = True
                categories_line_idx = i
                # 解析现有的分类
                categories_content = line.split(':', 1)[1].strip()

                # 处理数组格式：["分类1", "分类2"]
                if categories_content.startswith('[') and categories_content.endswith(']'):
                    import ast
                    try:
                        categories_list = ast.literal_eval(categories_content)
                    except:
                        categories_list = [categories_content.strip('"\'')]
                # 处理单个分类格式：分类名
                elif categories_content:
                    if categories_content.startswith('"') or categories_content.startswith("'"):
                        categories_list = [categories_content.strip('"\'')]
                    else:
                        categories_list = [categories_content]
                break

        # 合并新旧分类（去重）
        final_categories = list(set(categories_list + categories))

        # 如果分类没有变化，跳过
        if sorted(categories_list) == sorted(final_categories):
            return False, "分类已存在，无需更新"

        # 更新 front matter
        if has_categories:
            # 更新现有的 categories 行
            import json
            new_categories_str = json.dumps(final_categories, ensure_ascii=False)
            # 转换为 YAML 格式
            new_categories_str = new_categories_str.replace('"', "'")
            front_matter_lines[categories_line_idx] = f"categories: {new_categories_str}"
        else:
            # 在 tags 后添加 categories
            new_categories_str = str(final_categories).replace("'", '"')
            inserted = False
            new_front_matter_lines = []

            for line in front_matter_lines:
                new_front_matter_lines.append(line)
                if not inserted and line.strip().startswith('tags:'):
                    # 添加新的一行
                    new_front_matter_lines.append(f"categories: {new_categories_str}")
                    inserted = True

            if not inserted:
                # 如果没有找到 tags 行，在 draft 后添加
                for line in front_matter_lines:
                    new_front_matter_lines.append(line)
                    if not inserted and line.strip().startswith('draft:'):
                        new_front_matter_lines.append(f"categories: {new_categories_str}")
                        inserted = True

            front_matter_lines = new_front_matter_lines

        # 组装新内容
        new_lines = (
            lines[:front_matter_start + 1] +
            front_matter_lines +
            lines[front_matter_end:]
        )

        if dry_run:
            print(f"  📝 {os.path.basename(file_path)}")
            print(f"     当前分类: {categories_list if categories_list else '无'}")
            print(f"     新增分类: {categories}")
            print(f"     最终分类: {final_categories}")
            return True, "预览完成"

        # 写回文件
        new_content = '\n'.join(new_lines)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True, f"已添加分类: {final_categories}"

    except Exception as e:
        return False, f"错误: {str(e)}"


def process_directory(directory, dry_run=False, verbose=False):
    """
    处理目录下的所有 markdown 文件

    Args:
        directory: 要处理的目录
        dry_run: 是否只是预览
        verbose: 是否显示详细信息
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        print(f"❌ 错误：目录不存在: {directory}")
        return

    # 查找所有 markdown 文件
    md_files = list(dir_path.rglob('*.md'))

    if not md_files:
        print(f"⚠️  在 {directory} 中没有找到 markdown 文件")
        return

    total = len(md_files)
    success = 0
    skipped = 0
    failed = 0

    print(f"📁 处理目录: {directory}")
    print(f"📊 找到 {total} 个文件")
    print()

    for file_path in md_files:
        filename = os.path.basename(file_path)
        print(f"处理: {filename}")

        result, message = add_categories_from_directory(file_path, dry_run)

        if result:
            success += 1
            print(f"  ✅ {message}")
        else:
            if "分类已存在" in message or "没有找到有效的分类目录" in message:
                skipped += 1
                if verbose:
                    print(f"  ⏭️  {message}")
            else:
                failed += 1
                print(f"  ❌ {message}")

        print()

    # 统计
    print("=" * 50)
    print(f"总计: {total}")
    print(f"成功: {success}")
    print(f"跳过: {skipped}")
    print(f"失败: {failed}")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description='根据文件目录自动添加分类到 markdown 文件的 front matter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 预览模式（不实际修改文件）
  python tools/add_categories.py content/archives --dry-run

  # 处理单个目录（实际修改）
  python tools/add_categories.py content/archives

  # 处理整个 content 目录
  python tools/add_categories.py content

  # 显示详细信息
  python tools/add_categories.py content --verbose

  # 处理特定文件
  python tools/add_categories.py content/post/my-article.md
        '''
    )

    parser.add_argument(
        'path',
        help='markdown 文件或目录路径'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='预览模式，不实际修改文件'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细信息'
    )

    args = parser.parse_args()

    path = Path(args.path)

    if not path.exists():
        print(f"❌ 错误：路径不存在: {args.path}")
        sys.exit(1)

    print("=" * 50)
    print("   自动添加分类工具")
    print("=" * 50)
    print()

    if args.dry_run:
        print("⚠️  预览模式（不会实际修改文件）")
        print()

    if path.is_file():
        # 处理单个文件
        result, message = add_categories_from_directory(path, args.dry_run)

        if result:
            print(f"✅ {path.name}: {message}")
        else:
            print(f"⏭️  {path.name}: {message}")

    elif path.is_dir():
        # 处理目录
        process_directory(path, args.dry_run, args.verbose)


if __name__ == '__main__':
    main()

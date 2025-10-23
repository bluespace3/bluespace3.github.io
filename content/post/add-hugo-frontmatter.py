#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
from datetime import datetime, timezone
import argparse

def add_hugo_frontmatter(file_path):
    """为单个 Markdown 文件添加 Hugo Front Matter"""
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"⚠️  文件不存在：{file_path}")
        return False
    
    # 检查是否是 Markdown 文件
    if not file_path.endswith('.md'):
        print(f"⚠️  跳过非 Markdown 文件：{file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经有 Hugo 头
        lines = content.split('\n')
        if len(lines) > 0 and lines[0].strip() == '---':
            print(f"✅ 文件已有 Hugo 头，跳过：{file_path}")
            return True
        
        # 提取第一行作为标题
        first_line = lines[0].strip() if lines else ""
        
        # 清理标题（去除 # 符号和前后空格）
        title = re.sub(r'^#+\s*', '', first_line).strip()
        
        # 如果第一行为空或只是标题符号，使用文件名作为标题
        if not title:
            filename = os.path.basename(file_path)
            title = os.path.splitext(filename)[0]
        
        # 生成当前时间（RFC3339 格式）
        current_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%:z')
        
        # 创建 Hugo Front Matter
        frontmatter = f"""---
title: '{title}'
categories: ["技术"]
date: {current_time}
lastmod: {current_time}
---

"""
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter + content)
        
        print(f"✅ 成功添加 Hugo 头：{file_path}")
        print(f"   标题：{title}")
        print(f"   时间：{current_time}")
        return True
        
    except Exception as e:
        print(f"❌ 处理文件 {file_path} 时出错：{e}")
        return False

def process_directory(directory):
    """递归处理目录中的所有 Markdown 文件"""
    
    if not os.path.exists(directory):
        print(f"❌ 目录不存在：{directory}")
        return
    
    if not os.path.isdir(directory):
        print(f"❌ 路径不是目录：{directory}")
        return
    
    print(f"🔄 开始处理目录：{directory}")
    
    # 统计信息
    processed_files = 0
    success_files = 0
    skipped_files = 0
    
    # 遍历目录中的所有文件
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                processed_files += 1
                
                if add_hugo_frontmatter(file_path):
                    success_files += 1
                else:
                    skipped_files += 1
    
    print(f"\n📊 处理完成统计：")
    print(f"   总共处理文件：{processed_files}")
    print(f"   成功添加：{success_files}")
    print(f"   跳过文件：{skipped_files}")

def main():
    parser = argparse.ArgumentParser(description='为 Markdown 文件自动添加 Hugo Front Matter')
    parser.add_argument('target', nargs='?', default='content/post',
                       help='目标文件或目录路径（默认：content/post）')
    parser.add_argument('--dry-run', action='store_true',
                       help='试运行模式，只显示将要处理的文件，不实际修改')
    
    args = parser.parse_args()
    
    print("🚀 Hugo Front Matter 自动添加工具")
    print("=" * 50)
    
    target_path = args.target
    
    if args.dry_run:
        print("🔍 试运行模式 - 不会实际修改文件")
        # 这里可以实现试运行逻辑
        return
    
    if os.path.isfile(target_path):
        # 处理单个文件
        print(f"📄 处理单个文件：{target_path}")
        add_hugo_frontmatter(target_path)
    elif os.path.isdir(target_path):
        # 处理目录
        process_directory(target_path)
    else:
        print(f"❌ 错误：路径不存在：{target_path}")
        sys.exit(1)
    
    print("\n✅ 处理完成！")
    print("📋 请检查文件内容，确认 Hugo 头添加正确")

if __name__ == "__main__":
    main()
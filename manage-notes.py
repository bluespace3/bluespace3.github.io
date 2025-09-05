#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import subprocess
import shutil
from datetime import datetime, timezone
import argparse

class NotesManager:
    def __init__(self):
        self.hugo_project_dir = os.getcwd()
        self.notes_repo_dir = "C:/Users/tian4/knowledge_bases"
        self.content_post_dir = os.path.join(self.hugo_project_dir, "content/post")
        
    def check_hugo_project(self):
        """检查是否在 Hugo 项目根目录"""
        if not os.path.exists("hugo.toml"):
            print("❌ 错误：请在 Hugo 项目根目录运行此脚本")
            return False
        return True
    
    def check_notes_repo(self):
        """检查笔记仓库是否存在"""
        if not os.path.exists(self.notes_repo_dir):
            print(f"❌ 错误：笔记仓库目录不存在：{self.notes_repo_dir}")
            return False
        return True
    
    def run_git_command(self, command, cwd=None, description=""):
        """执行 git 命令"""
        if cwd is None:
            cwd = self.hugo_project_dir
            
        try:
            if description:
                print(f"🔄 {description}...")
            
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd, 
                capture_output=True, 
                text=True, 
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                print(f"❌ Git 命令执行失败：{command}")
                print(f"错误信息：{result.stderr}")
                return False
            
            if result.stdout.strip():
                print(result.stdout.strip())
            
            return True
            
        except Exception as e:
            print(f"❌ 执行命令时出错：{e}")
            return False
    
    def sync_notes_from_repo(self, force=False):
        """从笔记仓库同步到主项目（强制覆盖）"""
        print("🔄 开始从独立笔记仓库同步到主项目...")
        
        if not self.check_hugo_project():
            return False
        
        if not self.check_notes_repo():
            return False
        
        print(f"📍 主项目目录：{self.hugo_project_dir}")
        print(f"📍 笔记仓库目录：{self.notes_repo_dir}")
        
        # 检查是否有未提交的更改
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"], 
                cwd=self.hugo_project_dir, 
                capture_output=True, 
                text=True, 
                encoding='utf-8'
            )
            
            if result.returncode == 0 and result.stdout.strip():
                print("⚠️  检测到未提交的更改：")
                print(result.stdout.strip())
                
                if force:
                    print("🔄 强制模式：将暂存所有更改...")
                    self.run_git_command("git add .", description="暂存所有更改")
                    self.run_git_command("git commit -m \"自动提交：准备同步笔记\"", description="提交更改")
                else:
                    print("💡 提示：请先提交或保存更改，或使用 --force 参数")
                    return False
        except Exception as e:
            print(f"❌ 检查 git 状态时出错：{e}")
            return False
        
        # 执行 subtree pull
        success = self.run_git_command(
            f"git subtree pull --prefix=content/post \"{self.notes_repo_dir}\" master",
            description="执行 git subtree pull"
        )
        
        if success:
            print("✅ 笔记同步完成！")
        
        return success
    
    def add_hugo_frontmatter(self, file_path, force=False):
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
            has_frontmatter = len(lines) > 0 and lines[0].strip() == '---'
            
            if has_frontmatter and not force:
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
            
            # 如果有现有的 frontmatter 且 force=True，替换它
            if has_frontmatter and force:
                # 找到第二个 --- 的位置
                second_dash_pos = -1
                dash_count = 0
                for i, line in enumerate(lines):
                    if line.strip() == '---':
                        dash_count += 1
                        if dash_count == 2:
                            second_dash_pos = i
                            break
                
                if second_dash_pos > 0:
                    # 保留原有内容，替换 frontmatter
                    content_after_frontmatter = '\n'.join(lines[second_dash_pos + 1:])
                    if content_after_frontmatter.startswith('\n'):
                        content_after_frontmatter = content_after_frontmatter[1:]
                    content = content_after_frontmatter
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter + content)
            
            action_msg = "✅ 强制更新 Hugo 头" if force else "✅ 成功添加 Hugo 头"
            print(f"{action_msg}：{file_path}")
            print(f"   标题：{title}")
            print(f"   时间：{current_time}")
            return True
            
        except Exception as e:
            print(f"❌ 处理文件 {file_path} 时出错：{e}")
            return False
    
    def process_directory(self, directory, force=False):
        """递归处理目录中的所有 Markdown 文件"""
        
        if not os.path.exists(directory):
            print(f"❌ 目录不存在：{directory}")
            return
        
        if not os.path.isdir(directory):
            print(f"❌ 路径不是目录：{directory}")
            return
        
        action_msg = "强制更新" if force else "处理"
        print(f"🔄 开始{action_msg}目录：{directory}")
        
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
                    
                    if self.add_hugo_frontmatter(file_path, force):
                        success_files += 1
                    else:
                        skipped_files += 1
        
        print(f"\n📊 处理完成统计：")
        print(f"   总共处理文件：{processed_files}")
        print(f"   成功处理：{success_files}")
        print(f"   跳过文件：{skipped_files}")
    
    def sync_and_format(self, force=False):
        """同步笔记并格式化 Hugo 头"""
        print("🚀 笔记同步与格式化工具")
        print("=" * 50)
        
        # 第一步：同步笔记
        print("\n📥 第一步：从笔记仓库同步...")
        if not self.sync_notes_from_repo(force=force):
            print("❌ 笔记同步失败")
            return False
        
        print("\n✅ 笔记同步完成")
        
        # 第二步：格式化 Hugo 头
        print("\n📝 第二步：格式化 Hugo Front Matter...")
        self.process_directory(self.content_post_dir, force=force)
        
        print("\n✅ 全部处理完成！")
        return True

def main():
    parser = argparse.ArgumentParser(description='笔记管理工具 - 同步和格式化 Hugo 笔记')
    
    # 主要操作选项
    parser.add_argument('--sync', action='store_true',
                       help='从独立笔记仓库同步到主项目')
    parser.add_argument('--format', action='store_true',
                       help='为主项目中的笔记添加 Hugo Front Matter')
    parser.add_argument('--all', action='store_true',
                       help='执行完整的同步和格式化流程')
    
    # 选项参数
    parser.add_argument('--force', action='store_true',
                       help='强制模式：覆盖现有更改和 Hugo 头')
    parser.add_argument('--target', default='content/post',
                       help='目标文件或目录路径（默认：content/post）')
    parser.add_argument('--dry-run', action='store_true',
                       help='试运行模式，只显示将要处理的文件，不实际修改')
    
    args = parser.parse_args()
    
    manager = NotesManager()
    
    # 如果没有指定操作，默认执行完整流程
    if not any([args.sync, args.format, args.all]):
        args.all = True
    
    if args.dry_run:
        print("🔍 试运行模式 - 不会实际修改文件")
        return
    
    try:
        if args.all:
            # 执行完整的同步和格式化流程
            manager.sync_and_format(force=args.force)
        elif args.sync:
            # 只执行同步
            manager.sync_notes_from_repo(force=args.force)
        elif args.format:
            # 只执行格式化
            if os.path.isfile(args.target):
                print(f"📄 处理单个文件：{args.target}")
                manager.add_hugo_frontmatter(args.target, force=args.force)
            elif os.path.isdir(args.target):
                manager.process_directory(args.target, force=args.force)
            else:
                print(f"❌ 错误：路径不存在：{args.target}")
                sys.exit(1)
            
            print("\n✅ 格式化完成！")
            print("📋 请检查文件内容，确认 Hugo 头添加正确")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序执行出错：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
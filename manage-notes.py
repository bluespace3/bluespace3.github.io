#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import subprocess
from datetime import datetime, timezone
import argparse

class NotesManager:
    def __init__(self):
        self.hugo_project_dir = os.getcwd()
        self.notes_repo_url = "https://github.com/bluespace3/knowledge_bases.git"
        self.content_post_dir = os.path.join(self.hugo_project_dir, "content/post")
        
    def check_hugo_project(self):
        """检查是否在 Hugo 项目根目录"""
        if not os.path.exists("hugo.toml"):
            print("❌ 错误：请在 Hugo 项目根目录运行此脚本")
            return False
        return True
    
    def run_command(self, command, cwd=None, description=""):
        """通用命令执行函数"""
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
                encoding='utf-8',
                check=True # 引发异常如果命令返回非零退出码
            )
            
            if result.stdout.strip():
                print(result.stdout.strip())
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 命令执行失败：{command}")
            print(f"错误信息：{e.stderr}")
            return False
        except Exception as e:
            print(f"❌ 执行命令时出错：{e}")
            return False
    
    def sync_notes_from_remote(self, force=False):
        """从远程笔记仓库强制同步到主项目"""
        print("🔄 开始从远程笔记仓库同步...")
        
        if not self.check_hugo_project():
            return False
        
        print(f"📍 主项目目录：{self.hugo_project_dir}")
        print(f"🔗 远程笔记仓库：{self.notes_repo_url}")
        
        # 检查是否有未提交的更改
        try:
            result = subprocess.run(["git", "status", "--porcelain"], cwd=self.hugo_project_dir, capture_output=True, text=True, encoding='utf-8')
            if result.stdout.strip():
                print("⚠️  检测到未提交的更改。")
                if force:
                    print("🔄 --force模式：自动提交本地更改以继续同步。")
                    if not self.run_command("git add .", description="暂存所有更改"): return False
                    if not self.run_command("git commit -m \"chore: 自动提交本地更改以准备笔记同步\"", description="创建自动提交"): return False
                else:
                    print("❌ 操作中止。请先提交你的更改，或使用 `--force` 参数来自动提交。")
                    return False
        except Exception as e:
            print(f"❌ 检查 git 状态时出错：{e}")
            return False
        
        
        if force:
            print("⚠️  --force 模式：将强制覆盖本地 `content/post` 目录，所有本地未推送的更改都将丢失！")
            # 为了强制覆盖，我们先删除，再重新添加 subtree
            # 1. 强制从 Git 中移除现有目录
            rm_command = "git rm -rf content/post"
            self.run_command(rm_command, description="正在从 Git 中移除本地笔记目录...")

            # 2. 提交删除操作，为重新添加做准备
            commit_command = 'git commit -m "chore(notes): 准备强制覆盖更新笔记"'
            self.run_command(commit_command, description="正在提交移除操作...") # 忽略此处的失败，因为可能没有东西可提交

            # 3. 重新添加 subtree，这将拉取最新的内容并覆盖
            add_command = f"git subtree add --prefix=content/post {self.notes_repo_url} master --squash"
            success = self.run_command(add_command, description="正在强制拉取并覆盖远程笔记...")
        else:
            # 标准的 subtree pull（合并策略）
            pull_command = f"git subtree pull --prefix=content/post {self.notes_repo_url} master"
            success = self.run_command(pull_command, description="正在执行 git subtree pull 从远程仓库拉取笔记...")
        
        if success:
            print("✅ 笔记同步完成！")
        
        return success
    
    def extract_title_from_content(self, content_lines, file_path):
        """从内容中提取标题，如果失败则使用文件名"""
        for line in content_lines:
            line = line.strip()
            if line and not line.startswith('---'):
                title = re.sub(r'^#+\s*', '', line).strip()
                if title:
                    return title
        
        # 如果无法从内容中找到标题，则使用文件名
        filename = os.path.basename(file_path)
        return os.path.splitext(filename)[0]

    def add_hugo_frontmatter(self, file_path, force=False):
        """为单个 Markdown 文件添加或更新 Hugo Front Matter"""
        if not (os.path.exists(file_path) and file_path.endswith('.md')):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            has_frontmatter = lines and lines[0].strip() == '---'
            
            if has_frontmatter and not force:
                print(f"✅ 文件已有 Hugo 头，跳过：{file_path}")
                return True
            
            content_lines = lines
            if has_frontmatter:
                second_dash_pos = -1
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '---':
                        second_dash_pos = i
                        break
                if second_dash_pos > 0:
                    content_lines = lines[second_dash_pos + 1:]
            
            title = self.extract_title_from_content(content_lines, file_path)
            current_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%:z')
            
            frontmatter = f"""---
title: '{title}'
categories: ["技术"]
date: {current_time}
lastmod: {current_time}
---

"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter + '\n'.join(content_lines))
            
            action_msg = "强制更新" if has_frontmatter else "成功添加"
            print(f"✅ {action_msg} Hugo 头：{file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 处理文件 {file_path} 时出错：{e}")
            return False

    def process_directory(self, directory, force=False):
        """递归处理目录中的所有 Markdown 文件"""
        print(f"🔄 开始格式化目录：{directory}")
        processed_count = sum(1 for root, _, files in os.walk(directory) for file in files if self.add_hugo_frontmatter(os.path.join(root, file), force))
        print(f"\n📊 格式化完成。总共处理了 {processed_count} 个文件。")

def main():
    parser = argparse.ArgumentParser(
        description='Hugo 笔记管理工具：从远程仓库强制同步笔记，并自动格式化 Front Matter。',
        epilog='默认情况下，脚本会执行同步和格式化两个步骤。'
    )
    
    parser.add_argument('--sync-only', action='store_true', help='仅从远程仓库同步笔记，不进行格式化。')
    parser.add_argument('--format-only', action='store_true', help='仅格式化本地 `content/post` 目录中的笔记，不同步。')
    parser.add_argument('--force', action='store_true', help='强制模式：自动提交本地未保存的更改以进行同步，并强制更新所有笔记的 Front Matter。')
    
    args = parser.parse_args()
    
    manager = NotesManager()
    
    run_sync = not args.format_only
    run_format = not args.sync_only

    try:
        if run_sync:
            print("\n--- 步骤 1/2：同步笔记 ---")
            if not manager.sync_notes_from_remote(force=args.force):
                print("\n❌ 同步步骤失败，操作中止。")
                sys.exit(1)
            print("\n✅ 同步步骤成功。")

        if run_format:
            print("\n--- 步骤 2/2：格式化笔记 ---")
            manager.process_directory(manager.content_post_dir, force=args.force)
            print("\n✅ 格式化步骤成功。")

        print("\n🎉 所有操作已成功完成！")

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作。")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序执行时发生意外错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Hugo 笔记管理工具
功能：
1. 从远程仓库强制同步笔记到主项目（可选 --force 覆盖本地更改）
2. 自动为 content/post 目录下的 Markdown 文件添加或更新 Hugo Front Matter
3. 统一标题为文件名（去掉 .md 后缀）
4. 可选将格式化后的笔记推送回远程笔记仓库
5. 可选构建并部署整个 Hugo 站点到主项目的远程仓库'''

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
        self.knowledge_base_dir = r"C:\Users\tian4\knowledge_bases"
        
    def check_hugo_project(self):
        """检查是否在 Hugo 项目根目录"""
        if not os.path.exists("hugo.toml"):
            print("❌ 错误：请在 Hugo 项目根目录运行此脚本")
            return False
        return True

    def commit_and_push_local_knowledge_base(self):
        """在脚本执行前，先提交并推送本地知识库"""
        knowledge_base_dir = r"C:\Users\tian4\knowledge_bases"
        knowledge_base_url = "https://github.com/bluespace3/knowledge_bases.git"

        if not os.path.exists(knowledge_base_dir):
            print(f"⚠️  本地知识库目录不存在：{knowledge_base_dir}")
            return True  # 不是致命错误，继续执行

        try:
            # 切换到知识库目录并检查是否是git仓库
            result = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                                  cwd=knowledge_base_dir, capture_output=True, text=True, encoding='utf-8')
            if result.returncode != 0:
                print(f"⚠️  {knowledge_base_dir} 不是有效的git仓库")
                return True  # 不是致命错误，继续执行

            print("🔄 开始提交并推送本地知识库...")
            print(f"📍 知识库目录：{knowledge_base_dir}")

            # 检查是否有未提交的更改
            result = subprocess.run(["git", "status", "--porcelain"],
                                  cwd=knowledge_base_dir, capture_output=True, text=True, encoding='utf-8')
            if result.stdout.strip():
                print("🔄 检测到未提交的更改，自动提交...")
                # 添加所有更改
                if not self.run_command("git add .", cwd=knowledge_base_dir, description="暂存知识库更改"):
                    return False

                # 提交更改
                commit_msg = "更新笔记内容 - 自动提交\n\n🤖 Generated with [Claude Code](https://claude.ai/code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
                if not self.run_command(f'git commit -m "{commit_msg}"', cwd=knowledge_base_dir, description="提交知识库更改"):
                    return False

            # 获取默认分支
            try:
                result = subprocess.run(["git", "remote", "show", "origin"],
                                      cwd=knowledge_base_dir, capture_output=True, text=True, encoding='utf-8')
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'HEAD branch' in line:
                            default_branch = line.split()[-1]
                            break
                    else:
                        default_branch = "master"  # 默认使用master分支
                else:
                    default_branch = "master"
            except Exception:
                default_branch = "master"

            # 确保远程仓库已配置
            self.run_command(f"git remote add origin {knowledge_base_url}", cwd=knowledge_base_dir, description="配置知识库远程仓库", check=False)
            self.run_command(f"git remote set-url origin {knowledge_base_url}", cwd=knowledge_base_dir, description="更新知识库远程仓库URL")

            # 推送到GitHub
            if not self.run_command(f"git push -u origin {default_branch}", cwd=knowledge_base_dir, description="推送知识库到GitHub"):
                return False

            print("✅ 本地知识库提交并推送完成！")
            return True

        except Exception as e:
            print(f"❌ 处理本地知识库时出错：{e}")
            return False
    
    def run_command(self, command, cwd=None, description="", check=True):
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
                check=check # 引发异常如果命令返回非零退出码
            )

            # 打印标准输出（包括警告信息）
            if result.stdout.strip():
                print(result.stdout.strip())

            return True

        except subprocess.CalledProcessError as e:
            # 对于Hugo命令，我们需要特殊处理警告和错误
            if "hugo" in command.lower():
                # 打印输出和错误信息
                if e.stdout and e.stdout.strip():
                    print(e.stdout.strip())
                if e.stderr and e.stderr.strip():
                    print(e.stderr.strip())

                # 检查是否只有警告而没有真正的错误
                # Hugo在只有警告时通常会返回0，但如果有一些特定的警告可能会返回非0
                # 我们可以根据错误信息判断是否继续
                error_output = (e.stderr or "") + (e.stdout or "")
                if "error building site" not in error_output.lower() and "failed to" not in error_output.lower():
                    print("⚠️  Hugo构建出现警告，但没有致命错误，继续执行...")
                    return True

            print(f"❌ 命令执行失败：{command}")
            if e.stderr and e.stderr.strip():
                print(f"错误信息：{e.stderr}")
            return False
        except Exception as e:
            print(f"❌ 执行命令时出错：{e}")
            return False

    def run_hugo_command(self, command, cwd=None, description=""):
        """专门用于执行 Hugo 命令的函数，能够更好地区分警告和错误"""
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
                check=False  # 不直接抛出异常，我们自己处理
            )

            # 打印标准输出（包括警告信息）
            if result.stdout.strip():
                print(result.stdout.strip())

            # 检查是否有真正的错误（而不是警告）
            if result.returncode != 0:
                error_output = (result.stderr or "") + (result.stdout or "")
                # 检查是否是真正的构建错误
                if ("error building site" in error_output.lower() or
                    "failed to" in error_output.lower() or
                    "error:" in error_output.lower()):
                    print(f"❌ Hugo命令执行失败：{command}")
                    if result.stderr and result.stderr.strip():
                        print(f"错误信息：{result.stderr}")
                    return False
                else:
                    # 只是警告，不是错误
                    print("⚠️  Hugo构建出现警告，但没有致命错误，继续执行...")
                    return True
            else:
                # 命令成功执行
                return True

        except Exception as e:
            print(f"❌ 执行Hugo命令时出错：{e}")
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
            # 1. 强制从 Git 中移除现有目录（如果存在）
            if os.path.exists(os.path.join(self.hugo_project_dir, "content", "post")):
                rm_command = "git rm -rf content/post"
                self.run_command(rm_command, description="正在从 Git 中移除本地笔记目录...")

                # 2. 真正删除工作目录中的 content/post 目录（如果 git rm 没有完全删除）
                import shutil
                post_dir = os.path.join(self.hugo_project_dir, "content", "post")
                if os.path.exists(post_dir):
                    try:
                        shutil.rmtree(post_dir)
                        print("✅ 已彻底删除本地 content/post 目录")
                    except Exception as e:
                        print(f"⚠️  删除本地 content/post 目录时出错：{e}")

            # 3. 提交删除操作，为重新添加做准备
            commit_command = 'git commit -m "chore(notes): 准备强制覆盖更新笔记"'
            self.run_command(commit_command, description="正在提交移除操作...") # 忽略此处的失败，因为可能没有东西可提交

            # 4. 重新添加 subtree，这将拉取最新的内容并覆盖
            add_command = f"git subtree add --prefix=content/post {self.notes_repo_url} master --squash"
            success = self.run_command(add_command, description="正在强制拉取并覆盖远程笔记...")
        else:
            # 标准的 subtree pull（合并策略）
            pull_command = f"git subtree pull --prefix=content/post {self.notes_repo_url} master"
            success = self.run_command(pull_command, description="正在执行 git subtree pull 从远程仓库拉取笔记...")
        
        if success:
            print("✅ 笔记同步完成！")
        
        return success

    def push_notes_to_remote(self):
        """将格式化后的笔记更改推送到远程 subtree 仓库"""
        print("🔄 开始将格式化后的笔记推送回远程仓库...")
        
        # 检查 content/post 目录是否有更改
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain", "content/post"],
                cwd=self.hugo_project_dir, capture_output=True, text=True, encoding='utf-8'
            )
            if not result.stdout.strip():
                print("✅ 笔记内容无更改，无需推送。")
                return True
        except Exception as e:
            print(f"❌ 检查 git 状态时出错：{e}")
            return False

        # 暂存并提交格式化带来的更改
        if not self.run_command("git add content/post", description="暂存格式化后的笔记"): return False
        
        commit_msg = "docs: 自动格式化笔记并更新 Front Matter"
        if not self.run_command(f'git commit -m "{commit_msg}"', description="提交格式化笔记的更改"):
            print("ℹ️ 提交可能因为没有更改而失败，这通常是正常的。继续执行推送...")

        # 使用 subtree push 推送回笔记仓库
        push_command = f"git subtree push --prefix=content/post {self.notes_repo_url} master"
        return self.run_command(push_command, description="正在将笔记推送到远程仓库")

    def deploy_hugo_site(self):
        """构建并部署整个 Hugo 站点，复刻 .command.sh 的功能"""
        print("🚀 开始构建和部署 Hugo 站点...")

        # 1. 构建 Hugo 站点
        if not self.run_hugo_command("hugo --minify", description="正在构建 Hugo 站点"):
            return False

        # 2. 暂存所有文件
        if not self.run_command("git add .", description="正在暂存所有站点文件"):
            return False

        # 3. 检查是否有需要提交的更改
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.hugo_project_dir, capture_output=True, text=True, encoding='utf-8'
            )
            if not result.stdout.strip():
                print("✅ 站点无更改，无需部署。")
                return True
        except Exception as e:
            print(f"❌ 检查 git 状态时出错：{e}")
            return False
            
        # 4. 提交更改
        if not self.run_command('git commit -m "build: 更新博客"', description="正在提交站点更新"):
            return False

        # 5. 确保远程仓库已添加
        main_repo_url = "https://github.com/bluespace3/bluespace3.github.io"
        self.run_command(f"git remote add origin {main_repo_url}", description="尝试添加主项目远程仓库", check=False)

        # 6. 推送到 GitHub
        # 使用 --force 来匹配原始脚本的行为
        return self.run_command("git push -u origin main --force", description="正在将站点推送到主仓库")

    
    def fix_known_issues(self, file_path):
        """修复已知的文件问题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 修复测试平台分享.md中的JavaScript语法错误
            if "测试平台分享.md" in file_path:
                # 修复错误的JavaScript语法：})`</script>` -> });\n</script>
                old_pattern = "})`</script>`"
                new_pattern = "});\n</script>"
                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ 修复了文件中的JavaScript语法错误: {file_path}")

                # 修复另一个可能的JavaScript语法错误
                old_pattern2 = "})`</script>"
                new_pattern2 = "});\n</script>"
                if old_pattern2 in content and old_pattern not in content:
                    content = content.replace(old_pattern2, new_pattern2)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ 修复了文件中的JavaScript语法错误 (变体2): {file_path}")

            # 可以在这里添加更多已知问题的修复逻辑

        except Exception as e:
            print(f"⚠️  修复文件时出错 {file_path}: {e}")

    def find_category_from_knowledge_base(self, title):
        """根据标题在知识库中查找对应的分类（文件夹名）"""
        if not os.path.exists(self.knowledge_base_dir):
            print(f"⚠️  知识库目录不存在：{self.knowledge_base_dir}")
            return "技术"  # 默认分类

        # 构建要查找的文件名
        target_filename = title + ".md"

        # 递归遍历知识库目录
        for root, dirs, files in os.walk(self.knowledge_base_dir):
            if target_filename in files:
                # 找到文件，返回其父目录名（相对于知识库根目录）
                relative_path = os.path.relpath(root, self.knowledge_base_dir)
                if relative_path == ".":
                    # 文件在根目录
                    return "技术"
                else:
                    # 返回第一级目录名作为分类
                    first_dir = relative_path.split(os.sep)[0]
                    return first_dir

        # 如果没有找到匹配的文件，返回默认分类
        print(f"⚠️  未在知识库中找到标题为 '{title}' 的文件，使用默认分类")
        return "技术"

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

    def get_file_commit_time(self, file_path):
        """获取文件在知识库中的最后提交时间"""
        if not os.path.exists(self.knowledge_base_dir):
            print(f"⚠️  知识库目录不存在：{self.knowledge_base_dir}")
            return None

        try:
            # 获取相对于 content/post 的路径
            rel_path = os.path.relpath(file_path, self.content_post_dir)

            # 构建知识库中的完整路径
            kb_file_path = os.path.join(self.knowledge_base_dir, rel_path)

            # 检查文件是否存在于知识库中
            if not os.path.exists(kb_file_path):
                print(f"⚠️  文件在知识库中不存在：{kb_file_path}")
                return None

            # 获取文件在知识库中的最后提交时间
            result = subprocess.run(
                ["git", "log", "-1", "--format=%cI", "--", rel_path],
                cwd=self.knowledge_base_dir,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            if result.returncode == 0 and result.stdout.strip():
                commit_time_str = result.stdout.strip()
                # 转换为 UTC 时间格式（Hugo 需要的格式）
                from datetime import datetime, timezone
                dt = datetime.fromisoformat(commit_time_str.replace('Z', '+00:00'))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                else:
                    dt = dt.astimezone(timezone.utc)
                return dt.strftime('%Y-%m-%dT%H:%M:%S%:z')
            else:
                print(f"⚠️  无法获取文件提交时间：{rel_path}")
                return None

        except Exception as e:
            print(f"⚠️  获取文件提交时间时出错：{e}")
            return None

    def add_hugo_frontmatter(self, file_path, force=False):
        """为单个 Markdown 文件添加或更新 Hugo Front Matter"""
        if not (os.path.exists(file_path) and file_path.endswith('.md')):
            return False

        # 修复已知的JavaScript语法错误
        self.fix_known_issues(file_path)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')

            # 检查是否有完整的 Front Matter
            has_complete_frontmatter = False
            frontmatter_end_pos = -1
            existing_categories = None

            if lines and lines[0].strip() == '---':
                # 找到 Front Matter 的结束位置
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '---':
                        frontmatter_end_pos = i
                        has_complete_frontmatter = True
                        break

                # 如果有 Front Matter，解析现有的 categories 字段
                if has_complete_frontmatter:
                    frontmatter_lines = lines[1:frontmatter_end_pos]
                    for line in frontmatter_lines:
                        line = line.strip()
                        if line.startswith('categories:'):
                            existing_categories = line.split('categories:', 1)[1].strip()

            # 如果已经有完整的 Front Matter，完全跳过不做任何修改（无论是否强制模式）
            if has_complete_frontmatter:
                print(f"✅ 文件已有完整的 Hugo Front Matter，跳过：{file_path}")
                return True

            # 提取内容部分（移除现有的 Front Matter 如果存在）
            content_lines = lines

            title = self.extract_title_from_content(content_lines, file_path)

            # 获取 categories：在强制模式下总是从目录结构获取，否则优先使用现有 categories
            if force:
                # 强制模式：总是从目录结构获取 categories
                rel_path = os.path.relpath(file_path, self.content_post_dir)
                dir_parts = os.path.dirname(rel_path).split(os.sep)
                if dir_parts and dir_parts[0] and dir_parts[0] != '.':
                    category = dir_parts[0]
                else:
                    category = "技术"  # 默认分类
                category_str = f'["{category}"]'
            else:
                # 非强制模式：优先使用现有 categories，如果没有则从目录结构获取
                if existing_categories:
                    category_str = existing_categories
                else:
                    rel_path = os.path.relpath(file_path, self.content_post_dir)
                    dir_parts = os.path.dirname(rel_path).split(os.sep)
                    if dir_parts and dir_parts[0] and dir_parts[0] != '.':
                        category = dir_parts[0]
                    else:
                        category = "技术"  # 默认分类
                    category_str = f'["{category}"]'

            current_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%:z')

            # 获取远程文件的修改时间作为 date 字段
            remote_date = self.get_file_commit_time(file_path)
            if remote_date:
                date_to_use = remote_date
            else:
                # 如果无法获取远程时间，使用当前时间
                date_to_use = current_time

            frontmatter = f"""---
title: '{title}'
categories: {category_str}
date: {date_to_use}
lastmod: {current_time}
encrypted: false
password: "123456"
---

"""

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter + '\n'.join(content_lines))

            action_msg = "强制更新" if has_complete_frontmatter else "成功添加"
            print(f"✅ {action_msg} Hugo Front Matter：{file_path}")
            return True

        except Exception as e:
            print(f"❌ 处理文件 {file_path} 时出错：{e}")
            return False

    def normalize_title_to_filename(self, file_path):
        """将文章标题统一为文件名（去掉.md后缀）"""
        if not (os.path.exists(file_path) and file_path.endswith('.md')):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # 检查是否有 Front Matter
            if not lines or lines[0].strip() != '---':
                print(f"⚠️ 文件没有 Hugo Front Matter，跳过标题统一：{file_path}")
                return True
            
            # 找到 Front Matter 的结束位置
            second_dash_pos = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    second_dash_pos = i
                    break
            
            if second_dash_pos <= 0:
                print(f"⚠️ Front Matter 格式不正确，跳过标题统一：{file_path}")
                return True
            
            # 获取文件名作为标题
            filename = os.path.basename(file_path)
            title = os.path.splitext(filename)[0]  # 去掉 .md 后缀
            
            # 解析现有的 Front Matter
            frontmatter_lines = lines[1:second_dash_pos]
            content_lines = lines[second_dash_pos + 1:]
            
            # 更新或添加 title 字段
            title_updated = False
            new_frontmatter_lines = []
            
            for line in frontmatter_lines:
                if line.strip().startswith('title:'):
                    # 更新现有的 title
                    new_frontmatter_lines.append(f"title: '{title}'")
                    title_updated = True
                else:
                    new_frontmatter_lines.append(line)
            
            # 如果没有 title 字段，添加一个
            if not title_updated:
                new_frontmatter_lines.insert(0, f"title: '{title}'")
            
            # 重新构建文件内容
            new_content = '---\n' + '\n'.join(new_frontmatter_lines) + '\n---\n' + '\n'.join(content_lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 标题已统一为文件名：{file_path} -> '{title}'")
            return True
            
        except Exception as e:
            print(f"❌ 处理文件标题时出错 {file_path}：{e}")
            return False

    def process_directory(self, directory, force=False):
        """递归处理目录中的所有 Markdown 文件"""
        print(f"🔄 开始格式化目录：{directory}")
        
        # 第一步：添加或更新 Hugo Front Matter
        hugo_count = sum(1 for root, _, files in os.walk(directory) for file in files if self.add_hugo_frontmatter(os.path.join(root, file), force))
        print(f"✅ Hugo Front Matter 处理完成，处理了 {hugo_count} 个文件。")
        
        # 第二步：将标题统一为文件名（在添加 Front Matter 之后执行）
        title_count = sum(1 for root, _, files in os.walk(directory) for file in files if self.normalize_title_to_filename(os.path.join(root, file)))
        print(f"✅ 标题统一处理完成，处理了 {title_count} 个文件。")
        
        print(f"\n📊 格式化完成。总共处理了 {hugo_count} 个 Hugo Front Matter，{title_count} 个标题统一。")

def main():
    parser = argparse.ArgumentParser(
        description='Hugo 笔记管理工具：从远程仓库强制同步笔记，自动格式化 Front Matter，并统一标题为文件名。',
        epilog='默认情况下，脚本会执行同步和格式化两个步骤（包括添加 Hugo 头和标题统一）。'
    )
    
    parser.add_argument('--sync-only', action='store_true', help='仅从远程仓库同步笔记，不进行格式化。')
    parser.add_argument('--format-only', action='store_true', help='仅格式化本地 `content/post` 目录中的笔记，不同步。')
    parser.add_argument('--title-only', action='store_true', help='仅统一标题为文件名，跳过其他格式化步骤。')
    parser.add_argument('--push-notes', action='store_true', help='格式化后，将笔记的更改推送回远程笔记仓库。')
    parser.add_argument('--deploy', action='store_true', help='构建并部署整个 Hugo 站点到主项目的远程仓库。')
    parser.add_argument('--force', action='store_true', help='强制同步模式：在同步前自动提交本地更改，并强制覆盖 content/post 目录。')
    
    args = parser.parse_args()

    manager = NotesManager()

    # 如果没有指定任何参数，则默认执行完整流程
    if not any([args.sync_only, args.format_only, args.title_only, args.push_notes, args.deploy]):
        # 默认执行完整流程
        run_sync = True
        run_format = True
        run_title_only = False
        run_push_notes = True
        run_deploy = True
    else:
        # 按照指定的参数执行
        run_sync = not args.format_only and not args.deploy and not args.title_only # deploy-only 和 title-only 模式下也跳过同步
        run_format = not args.sync_only and not args.title_only
        run_title_only = args.title_only
        run_push_notes = args.push_notes
        run_deploy = args.deploy

    try:
        # 在执行任何操作之前，先提交并推送本地知识库
        print("\n--- 预处理步骤：提交并推送本地知识库 ---")
        if not manager.commit_and_push_local_knowledge_base():
            print("\n⚠️  本地知识库提交/推送失败，但继续执行后续步骤...")

        if run_sync:
            print("\n--- 步骤 1/3：同步笔记 ---")
            if not manager.sync_notes_from_remote(force=args.force):
                print("\n❌ 同步步骤失败，操作中止。")
                sys.exit(1)
            print("\n✅ 同步步骤成功。")

        if run_format:
            print(f"\n--- 步骤 2/3：格式化笔记 ---")
            manager.process_directory(manager.content_post_dir, force=args.force)
            print("\n✅ 格式化步骤成功。")
        
        if run_title_only:
            print("\n--- 步骤 1/1：统一标题为文件名 ---")
            title_count = sum(1 for root, _, files in os.walk(manager.content_post_dir) for file in files if manager.normalize_title_to_filename(os.path.join(root, file)))
            print(f"\n✅ 标题统一完成，处理了 {title_count} 个文件。")

        if run_push_notes:
            print("\n--- 步骤 3/3：推送笔记 ---")
            if not manager.push_notes_to_remote():
                print("\n❌ 推送笔记步骤失败。")
                sys.exit(1)
            print("\n✅ 推送笔记步骤成功。")

        if run_deploy:
            print("\n--- 部署流程：构建并发布站点 ---")
            if not manager.deploy_hugo_site():
                print("\n❌ 部署流程失败。")
                sys.exit(1)
            print("\n✅ 部署流程成功。")

        print("\n🎉 所有操作已成功完成！")

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作。")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序执行时发生意外错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

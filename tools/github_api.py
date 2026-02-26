#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub API 工具模块
使用 GitHub API 获取文件的真实创建和更新时间
"""

import os
import time
import requests
from typing import Optional, Dict
from datetime import datetime, timezone, timedelta
from pathlib import Path


def load_env_file():
    """
    从 .env 文件加载环境变量
    """
    # 查找 .env 文件（从当前目录向上查找）
    current_dir = Path.cwd()
    env_paths = [
        current_dir / '.env',
        Path(__file__).parent.parent / '.env',  # 项目根目录
    ]

    for env_path in env_paths:
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过注释和空行
                    if not line or line.startswith('#'):
                        continue
                    # 解析 KEY=VALUE 格式
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # 只设置还未设置的环境变量
                        if key not in os.environ:
                            os.environ[key] = value
                            # print(f"✅ 从 .env 加载: {key}")  # 调试用


# 自动加载 .env 文件
load_env_file()


class GitHubFileTimeFetcher:
    """使用 GitHub API 获取文件的真实时间"""

    def __init__(self, owner: str, repo: str, token: Optional[str] = None):
        """
        初始化 GitHub API 客户端

        Args:
            owner: GitHub 仓库所有者
            repo: GitHub 仓库名
            token: GitHub Personal Access Token（可选，推荐使用以提高速率限制）
        """
        self.owner = owner
        self.repo = repo
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        self.session = requests.Session()

        if self.token:
            self.session.headers.update({
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            })

    def get_file_info(self, file_path: str, branch: str = 'main') -> Optional[Dict[str, str]]:
        """
        获取文件在 GitHub 仓库的信息

        Args:
            file_path: 文件在仓库中的路径
            branch: 分支名（默认为 main）

        Returns:
            dict: {
                'created_at': '2025-03-15T10:30:00Z',  # 文件创建时间
                'updated_at': '2025-12-26T11:30:00Z'   # 文件更新时间
            }
            如果获取失败则返回 None
        """
        url = f"{self.base_url}/{file_path}"
        params = {'ref': branch}

        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=10)

                # 处理速率限制
                if response.status_code == 403:
                    reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 60))
                    wait_time = max(reset_time - time.time(), 1)

                    if attempt < max_retries - 1:
                        print(f"⚠️  GitHub API 速率限制，等待 {wait_time:.0f} 秒后重试...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"❌ GitHub API 速率限制，请稍后再试")
                        return None

                # 文件不存在
                if response.status_code == 404:
                    print(f"⚠️  文件在 GitHub 仓库中不存在：{file_path}")
                    return None

                # 其他错误
                if response.status_code != 200:
                    print(f"❌ GitHub API 请求失败：{response.status_code} - {response.text}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                        continue
                    else:
                        return None

                # 解析响应
                data = response.json()

                # 获取文件的提交历史来找到创建时间
                # API 不直接提供 created_at，需要通过 commits API 获取
                commits_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/commits"
                commits_params = {'path': file_path, 'per_page': 1, 'sha': branch}

                commits_response = self.session.get(commits_url, params=commits_params, timeout=10)

                if commits_response.status_code == 200:
                    commits_data = commits_response.json()
                    if commits_data:
                        # 第一次提交时间作为创建时间
                        created_at = commits_data[0]['commit']['committer']['date']
                        # 文件的最新更新时间（从 contents API）
                        updated_at = data.get('updated_at', created_at)

                        return {
                            'created_at': created_at,
                            'updated_at': updated_at
                        }

                # 如果无法获取提交历史，至少返回文件的更新时间
                return {
                    'created_at': data.get('updated_at', datetime.now(timezone.utc).isoformat()),
                    'updated_at': data.get('updated_at', datetime.now(timezone.utc).isoformat())
                }

            except requests.exceptions.RequestException as e:
                print(f"❌ 网络请求失败：{e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    return None
            except Exception as e:
                print(f"❌ 获取文件信息时出错：{e}")
                return None

        return None


def convert_github_time_to_hugo(github_time_iso: str) -> str:
    """
    将 GitHub API 的 UTC 时间转换为 Hugo 东八区时间

    Args:
        github_time_iso: GitHub API 返回的 ISO 8601 时间字符串
                        例如：'2025-03-15T10:30:00Z' 或 '2025-03-15T10:30:00+00:00'

    Returns:
        str: Hugo 格式的东八区时间字符串
             例如：'2025-03-15T18:30:00+08:00'

    Example:
        >>> convert_github_time_to_hugo('2025-03-15T10:30:00Z')
        '2025-03-15T18:30:00+08:00'
    """
    # 处理 Z 后缀
    if github_time_iso.endswith('Z'):
        github_time_iso = github_time_iso.replace('Z', '+00:00')

    # 解析时间
    dt = datetime.fromisoformat(github_time_iso)

    # 如果没有时区信息，假设为 UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    # 转换为东八区
    beijing_tz = timezone(timedelta(hours=8))
    local_dt = dt.astimezone(beijing_tz)

    # 返回 Hugo 格式
    # 注意：%z 在 Windows 上可能不输出冒号，需要手动构造 +08:00 格式
    utc_offset = local_dt.utcoffset()
    offset_seconds = int(utc_offset.total_seconds())
    offset_hours = offset_seconds // 3600
    offset_minutes = (offset_seconds % 3600) // 60
    offset_str = f"{offset_hours:+03d}:{offset_minutes:02d}"

    return local_dt.strftime(f'%Y-%m-%dT%H:%M:%S{offset_str}')


def extract_category_from_path(file_path: str, base_dir: str = 'content/post') -> str:
    """
    从文件路径提取分类（只取上一层目录）

    Args:
        file_path: 文件的完整路径
        base_dir: 内容目录的基准路径

    Returns:
        str: 分类名称

    Examples:
        >>> extract_category_from_path('content/post/技术/python.md')
        '技术'
        >>> extract_category_from_path('content/post/AIGC学习笔记/大模型.md')
        'AIGC学习笔记'
        >>> extract_category_from_path('content/post/根目录文件.md')
        '技术'
    """
    # 标准化路径
    file_path = os.path.normpath(file_path)
    base_dir = os.path.normpath(base_dir)

    # 获取相对路径
    try:
        rel_path = os.path.relpath(file_path, base_dir)
    except ValueError:
        # 如果文件不在 base_dir 下，返回默认分类
        return "技术"

    # 获取目录部分
    dir_part = os.path.dirname(rel_path)

    # 如果文件在根目录，返回默认分类
    if not dir_part or dir_part == '.':
        return "技术"

    # 获取第一级目录作为分类
    first_dir = dir_part.split(os.sep)[0]

    return first_dir or "技术"


if __name__ == "__main__":
    # 测试代码
    print("🧪 测试 GitHub API 工具模块\n")

    # 测试时间转换
    print("📅 测试时间转换：")
    test_time = '2025-03-15T10:30:00Z'
    converted = convert_github_time_to_hugo(test_time)
    print(f"  输入: {test_time}")
    print(f"  输出: {converted}")
    assert '+08:00' in converted, "时间转换失败：未包含东八区标识"
    print("  ✅ 时间转换测试通过\n")

    # 测试分类提取
    print("📁 测试分类提取：")
    test_paths = [
        ('content/post/技术/python.md', '技术'),
        ('content/post/AIGC学习笔记/大模型.md', 'AIGC学习笔记'),
        ('content/post/根目录文件.md', '技术'),
    ]
    for path, expected in test_paths:
        result = extract_category_from_path(path)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {path} -> {result} (期望: {expected})")
    print()

    # 测试 GitHub API（需要 GITHUB_TOKEN）
    print("🌐 测试 GitHub API（如果设置了 GITHUB_TOKEN）:")
    token = os.getenv('GITHUB_TOKEN')
    if token:
        try:
            fetcher = GitHubFileTimeFetcher('bluespace3', 'knowledge_bases')
            # 测试获取文件信息
            test_file = 'AIGC学习笔记/mcp-intro.md'
            print(f"  正在获取文件信息: {test_file}")
            info = fetcher.get_file_info(test_file)
            if info:
                print(f"  ✅ 成功获取文件信息:")
                print(f"     创建时间: {info['created_at']}")
                print(f"     更新时间: {info['updated_at']}")
                print(f"     转换后创建时间: {convert_github_time_to_hugo(info['created_at'])}")
            else:
                print(f"  ⚠️  无法获取文件信息（文件可能不存在）")
        except Exception as e:
            print(f"  ❌ GitHub API 测试失败: {e}")
    else:
        print("  ⚠️  未设置 GITHUB_TOKEN 环境变量，跳过 GitHub API 测试")
        print("  提示: 可以通过设置环境变量来测试：export GITHUB_TOKEN='your_token'")

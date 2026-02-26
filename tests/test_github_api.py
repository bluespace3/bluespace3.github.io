#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub API 工具模块单元测试
"""

import os
import sys
from pathlib import Path

# 添加 tools 目录到 Python 路径
script_dir = Path(__file__).parent.parent / 'tools'
sys.path.insert(0, str(script_dir))

from github_api import GitHubFileTimeFetcher, convert_github_time_to_hugo, extract_category_from_path


def test_convert_github_time_to_hugo():
    """测试时间转换函数"""
    print("🧪 测试时间转换函数\n")

    test_cases = [
        {
            'input': '2025-03-15T10:30:00Z',
            'expected_contains': ['2025-03-15', '+08:00'],
            'description': '标准 UTC 时间（Z 后缀）'
        },
        {
            'input': '2025-12-26T11:30:00+00:00',
            'expected_contains': ['2025-12-26', '+08:00'],
            'description': '带时区的 UTC 时间'
        },
        {
            'input': '2025-01-01T00:00:00Z',
            'expected_contains': ['2025-01-01', '08:00:00', '+08:00'],
            'description': '跨年测试（午夜）'
        },
    ]

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases, 1):
        print(f"测试用例 {i}: {test_case['description']}")
        print(f"  输入: {test_case['input']}")

        try:
            result = convert_github_time_to_hugo(test_case['input'])
            print(f"  输出: {result}")

            # 验证输出包含期望的内容
            all_passed = True
            for expected in test_case['expected_contains']:
                if expected not in result:
                    print(f"  ❌ 失败：输出应包含 '{expected}'")
                    all_passed = False
                    break

            if all_passed:
                print(f"  ✅ 通过")
                passed += 1
            else:
                failed += 1

        except Exception as e:
            print(f"  ❌ 异常：{e}")
            failed += 1

        print()

    print(f"📊 测试结果：{passed} 通过，{failed} 失败")
    return failed == 0


def test_extract_category_from_path():
    """测试分类提取函数"""
    print("\n🧪 测试分类提取函数\n")

    test_cases = [
        {
            'input': ('content/post/技术/python.md', 'content/post'),
            'expected': '技术',
            'description': '一级子目录'
        },
        {
            'input': ('content/post/AIGC学习笔记/大模型.md', 'content/post'),
            'expected': 'AIGC学习笔记',
            'description': '中文分类名'
        },
        {
            'input': ('content/post/根目录文件.md', 'content/post'),
            'expected': '技术',
            'description': '根目录文件（默认分类）'
        },
        {
            'input': ('content/post/自动化测试/java-testNg/测试.md', 'content/post'),
            'expected': '自动化测试',
            'description': '嵌套目录（取第一级）'
        },
    ]

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases, 1):
        print(f"测试用例 {i}: {test_case['description']}")
        print(f"  输入: {test_case['input'][0]}")

        try:
            result = extract_category_from_path(*test_case['input'])
            print(f"  输出: {result}")
            print(f"  期望: {test_case['expected']}")

            if result == test_case['expected']:
                print(f"  ✅ 通过")
                passed += 1
            else:
                print(f"  ❌ 失败：结果不匹配")
                failed += 1

        except Exception as e:
            print(f"  ❌ 异常：{e}")
            failed += 1

        print()

    print(f"📊 测试结果：{passed} 通过，{failed} 失败")
    return failed == 0


def test_github_api_get_file_info():
    """测试 GitHub API 获取文件信息（需要 GITHUB_TOKEN）"""
    print("\n🧪 测试 GitHub API 获取文件信息\n")

    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("⚠️  未设置 GITHUB_TOKEN 环境变量，跳过此测试")
        print("   提示: export GITHUB_TOKEN='your_token_here'")
        return True

    print(f"🔑 使用 Token: {token[:10]}...{token[-4:]}")

    # 初始化 fetcher
    fetcher = GitHubFileTimeFetcher('bluespace3', 'knowledge_bases', token)

    # 测试文件列表
    test_files = [
        'AIGC学习笔记/mcp-intro.md',
        'Git/Git submodule.md',
    ]

    passed = 0
    failed = 0

    for i, test_file in enumerate(test_files, 1):
        print(f"测试用例 {i}: {test_file}")

        try:
            print(f"  🌐 调用 GitHub API...")
            info = fetcher.get_file_info(test_file)

            if info:
                print(f"  ✅ 成功获取文件信息:")
                print(f"     创建时间: {info['created_at']}")
                print(f"     更新时间: {info['updated_at']}")

                # 测试时间转换
                created_hugo = convert_github_time_to_hugo(info['created_at'])
                updated_hugo = convert_github_time_to_hugo(info['updated_at'])

                print(f"     创建时间（Hugo）: {created_hugo}")
                print(f"     更新时间（Hugo）: {updated_hugo}")

                # 验证时间格式
                if '+08:00' in created_hugo and '+08:00' in updated_hugo:
                    print(f"  ✅ 时间格式正确（东八区）")
                    passed += 1
                else:
                    print(f"  ❌ 时间格式错误（应为东八区）")
                    failed += 1
            else:
                print(f"  ⚠️  无法获取文件信息（文件可能不存在）")
                # 不算失败，因为文件可能真的不存在

        except Exception as e:
            print(f"  ❌ 异常：{e}")
            failed += 1

        print()

    print(f"📊 测试结果：{passed} 通过，{failed} 失败")
    return failed == 0


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 GitHub API 工具模块 - 单元测试")
    print("=" * 60)
    print()

    results = []

    # 测试 1: 时间转换
    print("\n" + "─" * 60)
    print("测试组 1: 时间转换函数")
    print("─" * 60)
    results.append(("时间转换", test_convert_github_time_to_hugo()))

    # 测试 2: 分类提取
    print("\n" + "─" * 60)
    print("测试组 2: 分类提取函数")
    print("─" * 60)
    results.append(("分类提取", test_extract_category_from_path()))

    # 测试 3: GitHub API（需要 Token）
    print("\n" + "─" * 60)
    print("测试组 3: GitHub API 调用")
    print("─" * 60)
    results.append(("GitHub API", test_github_api_get_file_info()))

    # 打印总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")

    print()
    print(f"总计: {passed} 通过，{failed} 失败")

    if failed == 0:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {failed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

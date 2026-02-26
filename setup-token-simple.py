#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速设置 GitHub Token
"""

import os
import sys
from pathlib import Path

print("=" * 60)
print("🔑 GitHub Token 快速设置")
print("=" * 60)
print()

# 检查是否已存在 .env 文件
env_path = Path.cwd() / '.env'

if env_path.exists():
    print("⚠️  .env 文件已存在")
    choice = input("是否要重新设置？(y/N): ").strip().lower()
    if choice != 'y':
        print("❌ 取消设置")
        sys.exit(0)
    print()

# 显示 Token 获取指南
print("📖 获取 GitHub Token 步骤：")
print()
print("1. 访问：https://github.com/settings/tokens")
print("2. 点击 'Generate new token' → 'Generate new token (classic)'")
print("3. 配置 Token：")
print("   - Note: Hugo 博客同步工具")
print("   - Expiration: 90 days 或 No expiration")
print("   - 权限: ✅ repo (Full control of private repositories)")
print("4. 点击 'Generate token'")
print("5. ⚠️  立即复制 Token（只会显示一次！）")
print()

# 获取用户输入
token = input("请粘贴你的 GitHub Token: ").strip()

if not token:
    print("❌ Token 不能为空")
    sys.exit(1)

# 验证 Token 格式
if not token.startswith('ghp_') and not token.startswith('github_pat_'):
    print("⚠️  警告：Token 格式可能不正确（通常以 ghp_ 或 github_pat_ 开头）")
    choice = input("是否继续？(y/N): ").strip().lower()
    if choice != 'y':
        print("❌ 取消设置")
        sys.exit(0)

# 创建 .env 文件
env_content = f"""# GitHub Token 配置
# 此文件包含敏感信息，已添加到 .gitignore

GITHUB_TOKEN={token}

# 注意：
# 1. 请勿将此文件提交到 Git 仓库
# 2. Token 只在本地使用
# 3. 如果 Token 泄露，请立即在 GitHub 上撤销并重新生成
"""

try:
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)

    print()
    print("✅ .env 文件创建成功！")
    print(f"   位置：{env_path}")
    print()
    print("🎉 设置完成！现在可以直接使用同步工具了：")
    print()
    print("   python tools/sync_notes_from_github.py --batch content/post --no-overwrite")
    print()

except Exception as e:
    print(f"❌ 创建 .env 文件失败：{e}")
    sys.exit(1)

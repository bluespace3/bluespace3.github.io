#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单个文件加密脚本
由 batch-encrypt.bat 或 batch-encrypt.sh 调用
"""

import sys
import os

def encrypt_file(file_path, password):
    """
    加密单个 markdown 文件

    Args:
        file_path: 文件路径
        password: 加密密码
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 找到 front matter 结束位置
        front_matter_end = 0
        for i, line in enumerate(lines):
            if i > 0 and line.strip() == '---':
                front_matter_end = i + 1
                break

        # 提取 front matter 和内容
        front_matter = []
        content = []
        in_front_matter = True

        for i, line in enumerate(lines):
            if i < front_matter_end:
                # 移除 encrypted 和 password 字段
                if not line.strip().startswith('encrypted:') and not line.strip().startswith('password:'):
                    front_matter.append(line)
            else:
                content.append(line)

        # 检查是否已经加密
        content_str = ''.join(content)
        if 'hugo-encryptor' in content_str:
            print("  ⏭️  已经加密，跳过")
            return True

        # 添加描述（如果没有）
        front_matter_str = ''.join(front_matter)
        if 'description:' not in front_matter_str:
            # 在 tags 后添加 description
            new_front_matter = []
            for line in front_matter:
                new_front_matter.append(line)
                if line.strip().startswith('tags:'):
                    new_front_matter.append('description: "加密文章"\n')
            front_matter = new_front_matter
            front_matter_str = ''.join(front_matter)

        # 生成公开内容
        title = ""
        for line in front_matter:
            if line.strip().startswith('title:'):
                title = line.split(':', 1)[1].strip().strip('"')
                break

        public_intro = f"本文《{title}》包含加密内容，请输入密码查看。\n\n"

        # 组装新内容
        new_content = front_matter_str + '\n'
        new_content += public_intro
        new_content += '<!--more-->\n\n'
        new_content += f'{{{{% hugo-encryptor "{password}" %}}}}\n\n'
        new_content += content_str
        new_content += '\n{{% /hugo-encryptor %}}\n'

        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True

    except Exception as e:
        print(f"  ❌ 失败: {str(e)}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("使用方法: python encrypt_file.py <文件路径> <密码>")
        sys.exit(1)

    file_path = sys.argv[1]
    password = sys.argv[2]

    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        sys.exit(1)

    if encrypt_file(file_path, password):
        sys.exit(0)
    else:
        sys.exit(1)

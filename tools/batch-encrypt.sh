#!/bin/bash

# 批量加密文章脚本
# 将指定目录下的所有文章转换为使用 hugo-encryptor 加密

# 使用方法: ./batch-encrypt.sh <目录路径> <密码>
# 示例: ./batch-encrypt.sh content/archives tian123456

set -e

# 参数检查
if [ $# -lt 2 ]; then
    echo "使用方法: $0 <目录路径> <密码>"
    echo "示例: $0 content/archives tian123456"
    exit 1
fi

TARGET_DIR="$1"
PASSWORD="$2"

echo "========================================"
echo "       批量加密文章脚本"
echo "========================================"
echo ""
echo "目标目录: $TARGET_DIR"
echo "加密密码: $PASSWORD"
echo ""

# 检查目录是否存在
if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ 错误：目录不存在: $TARGET_DIR"
    exit 1
fi

# 计数器
total=0
success=0
failed=0

# 遍历所有 markdown 文件
for file in "$TARGET_DIR"/*.md; do
    if [ -f "$file" ]; then
        total=$((total + 1))
        filename=$(basename "$file")
        echo "[$total] 处理: $filename"

        # 使用 Python 脚本处理文件
        python3 << PYTHONEOF
import sys

file_path = "$file"
password = "$PASSWORD"

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
        sys.exit(0)

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

    print("  ✅ 加密成功")
    sys.exit(0)

except Exception as e:
    print(f"  ❌ 失败: {str(e)}")
    sys.exit(1)
PYTHONEOF

        if [ $? -eq 0 ]; then
            success=$((success + 1))
        else
            failed=$((failed + 1))
        fi
    fi
done

echo ""
echo "========================================"
echo "       处理完成"
echo "========================================"
echo "总数: $total"
echo "成功: $success"
echo "失败: $failed"
echo ""

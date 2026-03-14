#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容脱敏模块
用于自动检测和脱敏 Markdown 内容中的敏感信息
"""

import re
from typing import List, Tuple, Dict


class ContentSanitizer:
    """内容脱敏器"""

    # 敏感信息模式定义
    PATTERNS = {
        'openai_key': {
            'pattern': r'\bsk-[a-zA-Z0-9]{20,}\b',
            'description': 'OpenAI API Key',
            'replacement': 'sk-xxxxxxxxxxxxxxxx',
        },
        'github_token': {
            'pattern': r'\bghp_[a-zA-Z0-9]{36}\b',
            'description': 'GitHub Personal Access Token',
            'replacement': 'ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        },
        'google_api_key': {
            'pattern': r'\bAIzaSy[a-zA-Z0-9_-]{33}\b',
            'description': 'Google API Key',
            'replacement': 'AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        },
        'slack_token': {
            'pattern': r'\bxoxb-[0-9]{13}-[0-9]{13}-[a-zA-Z0-9]{24}\b',
            'description': 'Slack Bot Token',
            'replacement': 'xoxb-xxxxxxxxxxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx',
        },
        'aws_key': {
            'pattern': r'\bAKIA[0-9A-Z]{16}\b',
            'description': 'AWS Access Key',
            'replacement': 'AKIAxxxxxxxxxxxxxxxx',
        },
        'azure_key': {
            'pattern': r'\b[a-zA-Z0-9+/]{32,}={0,2}\b',  # Base64 样式的密钥（32字符以上）
            'description': 'Azure/其他 Base64 样式密钥',
            'replacement': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        },
        'token_with_bearer': {
            'pattern': r'\bBearer [a-zA-Z0-9_\-]{20,}\b',
            'description': 'Bearer Token',
            'replacement': 'Bearer xxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        },
        'password': {
            'pattern': r'\bpassword[[:space:]]*[=:][[:space:]]*["\']?([^"\'[:space:]]{4,})["\']?\b',
            'description': '密码字段',
            'replacement': r'password: "********"',
        },
        'secret': {
            'pattern': r'\bsecret[[:space:]]*[=:][[:space:]]*["\']?([^"\'[:space:]]{4,})["\']?\b',
            'description': '密钥字段',
            'replacement': r'secret: "********"',
        },
        'api_key': {
            'pattern': r'\b(api[-_]?key|apikey)[[:space:]]*[=:][[:space:]]*["\']?([^"\'[:space:]]{8,})["\']?\b',
            'description': 'API Key 字段',
            'replacement': r'\1: "xxxxxxxx"',
        },
        'jwt_token': {
            'pattern': r'\beyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\b',
            'description': 'JWT Token',
            'replacement': 'eyJxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxx',
        },
        'private_key': {
            'pattern': r'-----BEGIN ((RSA )?PRIVATE KEY|ENCRYPTED PRIVATE KEY)-----[\s\S]+?-----END \1-----',
            'description': '私钥',
            'replacement': '-----BEGIN \1-----\n[REDACTED PRIVATE KEY]\n-----END \1-----',
        },
        'ip_address': {
            'pattern': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b(?!\.)',  # 排除 Markdown 语法
            'description': 'IP 地址',
            'replacement': 'xxx.xxx.xxx.xxx',
        },
        'phone': {
            'pattern': r'\b1[3-9]\d{9}\b',  # 中国手机号
            'description': '手机号',
            'replacement': '138****8888',
        },
        'email': {
            'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'description': '邮箱地址',
            'replacement': 'user@example.com',
        },
    }

    def __init__(self, patterns_to_enable: List[str] = None, verbose: bool = False):
        """
        初始化脱敏器

        Args:
            patterns_to_enable: 要启用的模式列表（None 表示全部启用）
            verbose: 是否输出详细信息
        """
        if patterns_to_enable:
            # 只启用指定的模式
            self.enabled_patterns = {
                k: v for k, v in self.PATTERNS.items()
                if k in patterns_to_enable
            }
        else:
            # 启用所有模式
            self.enabled_patterns = self.PATTERNS.copy()

        self.verbose = verbose
        self.sanitization_log = []

    def sanitize(self, content: str, context: str = "") -> Tuple[str, Dict]:
        """
        脱敏内容

        Args:
            content: 原始内容
            context: 上下文信息（用于日志）

        Returns:
            Tuple[脱敏后的内容, 统计信息]
        """
        original_content = content
        sanitized_content = content

        stats = {
            'total_matches': 0,
            'patterns_found': {}
        }

        for pattern_name, pattern_info in self.enabled_patterns.items():
            pattern = pattern_info['pattern']
            description = pattern_info['description']
            replacement = pattern_info['replacement']

            # 统计匹配次数
            matches = re.findall(pattern, sanitized_content, re.IGNORECASE | re.MULTILINE)
            match_count = len(matches)

            if match_count > 0:
                if self.verbose:
                    print(f"  ⚠️  检测到 {description}：{match_count} 处")

                # 记录统计
                stats['total_matches'] += match_count
                stats['patterns_found'][description] = match_count

                # 执行替换
                if pattern_name in ['password', 'secret', 'api_key']:
                    # 这些模式使用了反向引用，需要特殊处理
                    sanitized_content = re.sub(
                        pattern,
                        replacement,
                        sanitized_content,
                        flags=re.IGNORECASE | re.MULTILINE
                    )
                else:
                    sanitized_content = re.sub(
                        pattern,
                        replacement,
                        sanitized_content,
                        flags=re.IGNORECASE | re.MULTILINE
                    )

                # 记录到日志
                self.sanitization_log.append({
                    'context': context,
                    'pattern': pattern_name,
                    'description': description,
                    'count': match_count,
                })

        return sanitized_content, stats

    def get_sanitization_summary(self) -> Dict:
        """
        获取脱敏操作摘要

        Returns:
            Dict: 摘要信息
        """
        summary = {
            'total_operations': len(self.sanitization_log),
            'patterns_used': {}
        }

        for log_entry in self.sanitization_log:
            pattern = log_entry['description']
            count = log_entry['count']

            if pattern not in summary['patterns_used']:
                summary['patterns_used'][pattern] = 0
            summary['patterns_used'][pattern] += count

        return summary

    def print_summary(self):
        """打印脱敏摘要"""
        if not self.sanitization_log:
            print("  ✅ 未检测到敏感信息")
            return

        summary = self.get_sanitization_summary()

        print(f"\n  🔒 脱敏摘要：")
        print(f"     总共处理 {summary['total_operations']} 个文件")

        for pattern, count in summary['patterns_used'].items():
            print(f"     - {pattern}: {count} 处")


def sanitize_markdown_file(file_path: str, inplace: bool = False,
                          patterns_to_enable: List[str] = None,
                          verbose: bool = False) -> Tuple[str, Dict]:
    """
    脱敏 Markdown 文件

    Args:
        file_path: 文件路径
        inplace: 是否原地修改文件
        patterns_to_enable: 要启用的模式列表
        verbose: 是否输出详细信息

    Returns:
        Tuple[脱敏后的内容, 统计信息]
    """
    from pathlib import Path

    file_path = Path(file_path)

    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 创建脱敏器
    sanitizer = ContentSanitizer(patterns_to_enable=patterns_to_enable, verbose=verbose)

    # 执行脱敏
    sanitized_content, stats = sanitizer.sanitize(content, context=str(file_path))

    # 原地修改
    if inplace and stats['total_matches'] > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(sanitized_content)
        print(f"  ✅ 已更新文件：{file_path}")

    # 打印摘要
    if verbose:
        sanitizer.print_summary()

    return sanitized_content, stats


# 测试代码
if __name__ == "__main__":
    # 测试用例
    test_content = """
# 测试文档

## API 配置

OpenAI API Key: sk-xxxxxxxxxxxxxxxx
GitHub Token: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Google API Key: AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

## 环境变量

```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
password=mysecretpassword
secret=verysecretsauce
```

## 私钥

-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7VJTUt9Us8cKj...
-----END PRIVATE KEY-----

## 联系方式

- 邮箱：user@example.com
- 手机：13800138000
- IP：192.168.1.100
"""

    print("🔍 测试内容脱敏")
    print("=" * 60)

    sanitizer = ContentSanitizer(verbose=True)
    sanitized, stats = sanitizer.sanitize(test_content)

    print("\n" + "=" * 60)
    print("📝 脱敏结果：")
    print("=" * 60)
    print(sanitized)

    print("\n" + "=" * 60)
    print("📊 统计信息：")
    print("=" * 60)
    for key, value in stats.items():
        print(f"{key}: {value}")

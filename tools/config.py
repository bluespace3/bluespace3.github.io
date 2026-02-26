#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
加载和管理同步笔记到博客的配置
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml
except ImportError:
    yaml = None
    print("⚠️  PyYAML 未安装，请运行: pip install pyyaml")


class SyncNotesConfig:
    """同步笔记配置管理器"""

    DEFAULT_CONFIG = {
        'github': {
            'token': '${GITHUB_TOKEN}',
            'owner': 'bluespace3',
            'repo': 'knowledge_bases',
            'branch': 'main'
        },
        'hugo': {
            'content_dir': 'content/post',
            'timezone': 'Asia/Shanghai'
        },
        'frontmatter': {
            'overwrite': True,
            'default_category': '技术'
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径，如果为 None 则使用默认路径
        """
        if config_path is None:
            # 默认配置文件路径
            script_dir = Path(__file__).parent
            config_path = script_dir / 'sync_notes_config.yaml'

        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load()

    def _substitute_env_vars(self, value: Any) -> Any:
        """
        递归替换配置中的环境变量

        支持格式：
        - ${ENV_VAR}
        - ${ENV_VAR:default_value}

        Args:
            value: 配置值（可以是字符串、字典、列表等）

        Returns:
            替换环境变量后的值
        """
        if isinstance(value, str):
            # 匹配 ${ENV_VAR} 或 ${ENV_VAR:default}
            pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'

            def replacer(match):
                env_var = match.group(1)
                default_value = match.group(2) if match.group(2) is not None else ''
                return os.getenv(env_var, default_value)

            return re.sub(pattern, replacer, value)

        elif isinstance(value, dict):
            return {k: self._substitute_env_vars(v) for k, v in value.items()}

        elif isinstance(value, list):
            return [self._substitute_env_vars(item) for item in value]

        else:
            return value

    def load(self) -> bool:
        """
        加载配置文件

        Returns:
            bool: 是否成功加载配置
        """
        # 如果配置文件不存在，使用默认配置
        if not self.config_path.exists():
            print(f"⚠️  配置文件不存在：{self.config_path}")
            print(f"📝 使用默认配置")
            self.config = self._substitute_env_vars(self.DEFAULT_CONFIG)
            return True

        # 检查 PyYAML 是否安装
        if yaml is None:
            print("❌ PyYAML 未安装，无法加载配置文件")
            print(f"📝 使用默认配置")
            self.config = self._substitute_env_vars(self.DEFAULT_CONFIG)
            return False

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)

            # 如果配置文件为空，使用默认配置
            if loaded_config is None:
                loaded_config = {}

            # 合并默认配置和加载的配置
            self.config = self._deep_merge(self.DEFAULT_CONFIG, loaded_config)

            # 替换环境变量
            self.config = self._substitute_env_vars(self.config)

            print(f"✅ 配置加载成功：{self.config_path}")
            return True

        except Exception as e:
            print(f"❌ 加载配置文件失败：{e}")
            print(f"📝 使用默认配置")
            self.config = self._substitute_env_vars(self.DEFAULT_CONFIG)
            return False

    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """
        深度合并两个字典

        Args:
            base: 基础字典
            update: 更新字典

        Returns:
            合并后的字典
        """
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def save(self, path: Optional[Path] = None) -> bool:
        """
        保存当前配置到文件

        Args:
            path: 保存路径，如果为 None 则使用当前配置文件路径

        Returns:
            bool: 是否成功保存
        """
        if yaml is None:
            print("❌ PyYAML 未安装，无法保存配置文件")
            return False

        save_path = path or self.config_path

        try:
            # 确保目录存在
            save_path.parent.mkdir(parents=True, exist_ok=True)

            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

            print(f"✅ 配置保存成功：{save_path}")
            return True

        except Exception as e:
            print(f"❌ 保存配置文件失败：{e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键（支持点号分隔的路径，如 'github.owner'）
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    @property
    def github_token(self) -> str:
        """GitHub Token"""
        return self.get('github.token', '')

    @property
    def github_owner(self) -> str:
        """GitHub 仓库所有者"""
        return self.get('github.owner', 'bluespace3')

    @property
    def github_repo(self) -> str:
        """GitHub 仓库名"""
        return self.get('github.repo', 'knowledge_bases')

    @property
    def github_branch(self) -> str:
        """GitHub 分支名"""
        return self.get('github.branch', 'main')

    @property
    def hugo_content_dir(self) -> str:
        """Hugo 内容目录"""
        return self.get('hugo.content_dir', 'content/post')

    @property
    def hugo_timezone(self) -> str:
        """Hugo 时区"""
        return self.get('hugo.timezone', 'Asia/Shanghai')

    @property
    def frontmatter_overwrite(self) -> bool:
        """是否覆盖已有 frontmatter"""
        return self.get('frontmatter.overwrite', True)

    @property
    def frontmatter_default_category(self) -> str:
        """默认分类"""
        return self.get('frontmatter.default_category', '技术')

    def __repr__(self) -> str:
        """返回配置的字符串表示"""
        return f"SyncNotesConfig(path={self.config_path}, github={self.github_owner}/{self.github_repo})"


if __name__ == "__main__":
    # 测试配置管理器
    print("🧪 测试配置管理模块\n")

    # 测试默认配置
    print("📋 测试默认配置加载：")
    config = SyncNotesConfig()
    print(f"  GitHub: {config.github_owner}/{config.github_repo}")
    print(f"  Branch: {config.github_branch}")
    print(f"  Hugo Content Dir: {config.hugo_content_dir}")
    print(f"  Timezone: {config.hugo_timezone}")
    print(f"  Frontmatter Overwrite: {config.frontmatter_overwrite}")
    print(f"  Default Category: {config.frontmatter_default_category}")
    print()

    # 测试环境变量替换
    print("🔐 测试环境变量替换：")
    os.environ['TEST_VAR'] = 'test_value'
    test_config = {
        'test': '${TEST_VAR}',
        'test_with_default': '${NON_EXISTENT_VAR:default_value}',
        'nested': {
            'value': '${TEST_VAR}'
        }
    }
    config._substitute_env_vars(test_config)
    print(f"  TEST_VAR: {test_config['test']}")
    print(f"  NON_EXISTENT_VAR: {test_config['test_with_default']}")
    print(f"  nested.value: {test_config['nested']['value']}")
    print()

    # 测试配置保存（如果 PyYAML 可用）
    if yaml:
        print("💾 测试配置保存：")
        test_config_path = Path('test_config.yaml')
        if config.save(test_config_path):
            print(f"  ✅ 配置已保存到：{test_config_path}")
            # 清理测试文件
            if test_config_path.exists():
                test_config_path.unlink()
                print(f"  🧹 测试文件已清理")
    else:
        print("⚠️  PyYAML 未安装，跳过配置保存测试")

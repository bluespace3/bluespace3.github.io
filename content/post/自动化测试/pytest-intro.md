---
title: 'pytest-intro'
categories: ["技术"]
date: 2025-10-23T14:17:58+00:00
lastmod: 2025-10-23T14:17:58+00:00
---








## 什么是pytest？

pytest是一个功能强大且易于使用的Python测试框架。它可以帮助开发者编写简洁、可读性强的测试代码，并提供丰富的插件支持。

## pytest的主要特点

- 简洁的测试用例编写方式
- 自动发现测试用例
- 支持参数化测试
- 强大的断言功能
- 丰富的插件生态系统

## 安装pytest

使用以下命令安装pytest：

```bash
pip install pytest
```

## 编写测试用例

一个简单的pytest测试用例如下：

```python
def test_addition():
    assert 1 + 1 == 2

def test_subtraction():
    assert 2 - 1 == 1
```

## 运行测试

使用以下命令运行pytest测试：

```bash
pytest
```

## 参数化测试

pytest支持参数化测试，可以使用`@pytest.mark.parametrize`装饰器：

```python
import pytest

@pytest.mark.parametrize("test_input,expected", [
    ("3+5", 8),
    ("2+4", 6),
    ("6*9", 42),
])
def test_eval(test_input, expected):
    assert eval(test_input) == expected
```

## 总结

pytest是一个功能强大且易于使用的Python测试框架，可以帮助开发者编写简洁、可读性强的测试代码。通过本指南，您已经了解了pytest的基本使用方法，接下来可以探索更多高级功能。

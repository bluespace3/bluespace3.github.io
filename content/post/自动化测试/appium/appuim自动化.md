---
title: 'appuim自动化'
categories: ["自动化测试"]
date: 2026-03-23T02:04:31+08:00
lastmod: 2026-04-08T23:32:29+08:00
draft: false
---
# Appium 自动化踩坑记录

## 2026-03-23

### 1. MCP 连接问题

**问题描述**: appium-mcp 工具创建会话后，操作时返回 `NoSuchDriverError: The session identified by xxx is not known`

**原因**: 没有指定 `remoteServerUrl` 参数，MCP 服务器无法连接到本地 Appium 服务器

**解决**:
```python
mcp__appium-mcp__create_session(
    platform="android",
    remoteServerUrl="http://xxx.xxx.xxx.xxx:4723",  # 必须指定
    capabilities={...}
)
```

---

### 2. pytest hook 错误 - CollectReport 没有 description 属性

**错误信息**:
```
AttributeError: 'CollectReport' object has no attribute 'description'
```

**原因**: `pytest_html_results_table_row` hook 尝试访问 `report.description`，但 collect 阶段的 report 对象没有这个属性

**解决**:
```python
@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    if hasattr(report, 'description'):  # 添加检查
        cells.insert(1, html.td(report.description))
    cells.pop(-1)
```

---

### 3. `@pytest.fixture` 重复应用

**错误信息**:
```
ValueError: fixture is being applied more than once to the same function
```

**原因**: 编辑时不小心复制了装饰器
```python
@pytest.fixture
@pytest.fixture  # 重复了！
def start_point():
```

**解决**: 删除重复的装饰器

---

### 4. `implicitly_wait()` 返回 None

**错误信息**:
```
TypeError: float() argument must be a string or a real number, not 'NoneType'
```

**原因**: `driver.implicitly_wait()` 返回 None，不是原来的等待时间
```python
original_wait = driver.implicitly_wait(0)  # 返回 None!
# ...
driver.implicitly_wait(original_wait)  # 错误！
```

**解决**: 直接恢复为默认值
```python
driver.implicitly_wait(0)
try:
    # ... 操作 ...
finally:
    driver.implicitly_wait(2)  # 恢复为项目默认值
```

---

### 5. `find_android_element` 依赖全局隐式等待设置

**问题**: `check_caigou_home_ad` 将 `implicitly_wait` 设为 0 后，`find_android_element` 立即返回 None

**原因**: `find_android_element` 依赖全局的 `implicitly_wait` 设置

**解决**: 在 `find_android_element` 内部临时设置隐式等待
```python
def find_android_element(driver, ...):
    driver.implicitly_wait(2)  # 临时设置
    try:
        # ... 查找元素 ...
    finally:
        driver.implicitly_wait(2)  # 恢复默认值
```

---

### 6. 弹窗检查卡顿/卡住

**问题**: `find_android_element` 内部有 `time.sleep(1)`，遍历 7 个弹窗按钮 = 至少 7 秒

**解决**: 使用 `find_elements` + `implicitly_wait(0)` 快速检查
```python
def check_caigou_home_ad(driver):
    driver.implicitly_wait(0)  # 禁用隐式等待
    try:
        elements = driver.find_elements(...)  # 不等待，立即返回
        if elements:
            elements[0].click()
    finally:
        driver.implicitly_wait(2)  # 恢复默认值
```

---

### 7. 元素查找卡住几秒钟

**问题**: `implicitly_wait(2)` + Appium 响应慢 = 每次查找可能等待更久

**解决**:
1. 弹窗检查使用 `implicitly_wait(0)`
2. 元素查找使用固定的 `implicitly_wait(2)`
3. 使用 `find_elements` 代替 `find_element`（不抛异常）

---

### 8. 元素 UUID 返回 undefined

**问题描述**: 使用 appium-mcp 查找元素后，element UUID 是 `undefined`

**原因**: 使用了错误的查找策略

**解决**: 使用正确的策略
```python
# XPath 策略正确返回 UUID
mcp__appium-mcp__appium_find_element(
    strategy="xpath",
    selector="//android.widget.TextView[@text='残忍拒绝']"
)

# -android uiautomator 策略返回 undefined
```

---

## 最佳实践

### 弹窗检查模式
```python
def check_popups(driver):
    """快速检查并关闭弹窗"""
    driver.implicitly_wait(0)  # 禁用隐式等待
    try:
        for text in ['确定', '残忍拒绝', '暂不处理', '取消']:
            elements = driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR,
                                           f'new UiSelector().text("{text}")')
            if elements:
                elements[0].click()
                return  # 处理完一个就返回
    finally:
        driver.implicitly_wait(2)  # 恢复默认值
```

### 元素查找隔离
```python
def find_element_safe(driver, selector_type, value):
    """不依赖全局隐式等待的元素查找"""
    driver.implicitly_wait(2)
    try:
        return driver.find_element(...)
    finally:
        driver.implicitly_wait(2)  # 确保恢复默认值
```

### MCP 使用要点
```python
# 1. 创建会话时必须指定 remoteServerUrl
# 2. 使用 XPath 策略查找元素最可靠
# 3. 获取 elementUUID 后立即使用
# 4. 使用完成后删除会话
```

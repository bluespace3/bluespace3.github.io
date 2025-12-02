---
title: 'playwright的python文档'
categories: ["技术"]
date: 2025-12-02T15:13:20+00:00
lastmod: 2025-12-02T15:13:20+00:00
encrypted: false
password: "123456"
---














# 安装

## 引言

Playwright 是专门为满足端到端测试的需求而创建的。Playwright 支持包括 Chromium、WebKit 和 Firefox 在内的所有现代渲染引擎。在 Windows、Linux 和 macOS 上进行测试，无论是本地还是在 CI 上，无论是无头模式还是有头模式，都可以使用原生移动设备仿真。

Playwright 库可以用作通用的浏览器自动化工具，为同步和异步 Python 提供了一套强大的 API 来自动化 Web 应用程序。

本介绍描述了 Playwright Pytest 插件，这是编写端到端测试的推荐方式。

**你将学到**

* 如何安装 Playwright Pytest
* 如何运行示例测试

## 安装 Playwright Pytest

Playwright 建议使用官方的 Playwright Pytest 插件来编写端到端测试。它提供了上下文隔离，并开箱即用地在多个浏览器配置上运行。

首先，通过安装 Playwright 并运行示例测试来开始，亲眼看看它是如何工作的。

* PyPI
* Anaconda

安装所需的浏览器：

## 添加示例测试

在当前工作目录或遵循 `test_` 前缀约定的子目录中创建一个文件，例如 `test_example.py`，并在其中包含以下代码。确保你的测试名称也遵循 `test_` 前缀约定。

test_example.py

```Python
import re
from playwright.sync_api import Page, expect

def test_has_title(page: Page):
    page.goto("https://playwright.dev/")

    # 期望标题“包含”一个子字符串。
    expect(page).to_have_title(re.compile("Playwright"))

def test_get_started_link(page: Page):
    page.goto("https://playwright.dev/")

    # 点击“开始”链接。
    page.get_by_role("link", name="Get started").click()

    # 期望页面有一个名为“安装”的标题。
    expect(page.get_by_role("heading", name="Installation")).to_be_visible()
```

## 运行示例测试

默认情况下，测试将在 Chromium 上运行。这可以通过 CLI 选项进行配置。测试以无头模式运行，这意味着在运行测试时不会打开浏览器 UI。测试结果和测试日志将在终端中显示。

## 更新 Playwright

要将 Playwright 更新到最新版本，请运行以下命令：

```Bash
pip install pytest-playwright playwright -U
```

## 系统要求

* Python 3.8 或更高版本。
* Windows 10+、Windows Server 2016+ 或 Windows Subsystem for Linux (WSL)。
* MacOS 12 Monterey、MacOS 13 Ventura 或 MacOS 14 Sonoma。
* Debian 11、Debian 12、Ubuntu 20.04 或 Ubuntu 22.04。

## 接下来是什么

* 使用 Web 优先断言、页面夹具和定位器编写测试
* 运行单个测试、多个测试、有头模式
* 使用 Codegen 生成测试
* 查看测试的跟踪

# 编写测试用例

## 引言

Playwright 测试很简单，它们

* **执行操作** ，
* **断言状态**与预期相符。

在执行操作之前没有必要等待任何东西：Playwright 在执行每个操作之前会自动等待一系列可操作性检查通过。

也没有必要在执行检查时处理竞态条件 - Playwright 断言的设计方式是它们描述了最终需要满足的预期。

就是这样！这些设计选择允许 Playwright 用户完全忘记他们测试中的不稳定超时和竞态检查。

**你将学到**

* 如何编写第一个测试
* 如何执行操作
* 如何使用断言
* 测试如何独立运行
* 如何使用测试钩子

## 第一个测试

查看以下示例，了解如何编写测试。注意文件名遵循 `test_` 前缀约定，以及每个测试名称。

test_example.py

```Python
import re
from playwright.sync_api import Page, expect

def test_has_title(page: Page):
    page.goto("https://playwright.dev/")

    # 期望标题“包含”一个子字符串。
    expect(page).to_have_title(re.compile("Playwright"))

def test_get_started_link(page: Page):
    page.goto("https://playwright.dev/")

    # 点击“开始”链接。
    page.get_by_role("link", name="Get started").click()

    # 期望页面有一个名为“安装”的标题。
    expect(page.get_by_role("heading", name="Installation")).to_be_visible()
```

## 操作

### 导航

大多数测试将从导航到 URL 的页面开始。之后，测试将能够与页面元素进行交互。

```Python
page.goto("https://playwright.dev/")
```

Playwright 会等待页面达到加载状态，然后再继续。了解更多关于 page.goto() 选项的信息。

### 交互

执行操作从定位元素开始。Playwright 使用 Locators API 进行此操作。定位器代表了在任何时刻在页面上查找元素（或元素组）的方式，了解更多关于可用的不同类型定位器的信息。Playwright 会在执行操作之前等待元素可操作，因此没有必要等待其变为可用。

```Python
# 创建一个定位器。
get_started = page.get_by_role("link", name="Get started")

# 点击它。
get_started.click()
```

在大多数情况下，它会写成一行：

```Python
page.get_by_role("link", name="Get started").click()
```

### 基本操作

这是最受欢迎的 Playwright 操作列表。请注意，还有更多操作，请确保查看定位器 API 部分以了解更多信息。

| 操作                      | 描述                   |
| ------------------------- | ---------------------- |
| locator.check()           | 检查输入复选框         |
| locator.click()           | 点击元素               |
| locator.uncheck()         | 取消检查输入复选框     |
| locator.hover()           | 鼠标悬停在元素上       |
| locator.fill()            | 填写表单字段，输入文本 |
| locator.focus()           | 使元素获得焦点         |
| locator.press()           | 按下单个键             |
| locator.set_input_files() | 选择上传的文件         |
| locator.select_option()   | 在下拉菜单中选择选项   |

## 断言

Playwright 包括断言，这些断言会等待直到满足预期条件。使用这些断言可以使测试不脆弱且具有弹性。例如，这段代码会等待页面获得包含“Playwright”的标题：

```Python
import re
from playwright.sync_api import expect

expect(page).to_have_title(re.compile("Playwright"))
```

这是最受欢迎的异步断言列表。请注意，还有更多断言需要熟悉：

| 断言                                | 描述                    |
| ----------------------------------- | ----------------------- |
| expect(locator).to_be_checked()     | 复选框被选中            |
| expect(locator).to_be_enabled()     | 控件被启用              |
| expect(locator).to_be_visible()     | 元素可见                |
| expect(locator).to_contain_text()   | 元素包含文本            |
| expect(locator).to_have_attribute() | 元素具有属性            |
| expect(locator).to_have_count()     | 元素列表具有给定长度    |
| expect(locator).to_have_text()      | 元素匹配文本``   |
| expect(locator).to_have_value()     | 输入元素具有值`` |
| expect(page).to_have_title()        | 页面具有标题``   |
| expect(page).to_have_url()          | 页面具有 URL            |

### 测试隔离

Playwright Pytest 插件基于测试夹具的概念，例如内置的页面夹具，它被传递到你的测试中。由于浏览器上下文，页面在测试之间是隔离的，这相当于一个全新的浏览器配置文件，每个测试都获得一个新鲜环境，即使多个测试在单个浏览器中运行。

test_example.py

```Python
from playwright.sync_api import Page

def test_example_test(page: Page):
  pass
  # “page”属于一个独立的 BrowserContext，为这个特定测试创建。

def test_another_test(page: Page):
  pass
  # 这个第二个测试中的“page”与第一个测试完全隔离。
```

### 使用夹具

你可以使用各种夹具在测试之前或之后执行代码并共享对象。一个 `function` 作用域的夹具，例如带有 autouse 的，表现得像 beforeEach/afterEach。一个 `module` 作用域的夹具带有 autouse 表现得像 beforeAll/afterAll，它在所有测试之前和之后运行。

test_example.py

```Python
import pytest
from playwright.sync_api import Page, expect

@pytest.fixture(scope="function", autouse=True)
def before_each_after_each(page: Page):

    print("before the test runs")

    # 在每个测试之前转到起始 URL。
    page.goto("https://playwright.dev/")
    yield

    print("after the test runs")

def test_main_navigation(page: Page):
    # 断言使用 expect API。
    expect(page).to_have_url("https://playwright.dev/")
```

## 接下来是什么

* 运行单个测试，多个测试，有头模式
* 使用 Codegen 生成测试
* 查看测试的跟踪
* 在 CI 上运行测试与 GitHub Actions

# 生成测试

## 引言

Playwright 提供了开箱即用的测试生成能力，是快速开始测试的绝佳方式。它将打开两个窗口，一个浏览器窗口，您可以在其中与您想要测试的网站进行交互；另一个是 Playwright 检查器窗口，您可以在其中录制测试、复制测试、清除测试以及更改测试的语言。

**您将学到**

* 如何录制测试
* 如何生成定位器

## 运行 Codegen

使用 `codegen` 命令运行测试生成器，然后是您想要为其生成测试的网站的 URL。URL 是可选的，您也可以在不指定 URL 的情况下运行命令，然后在浏览器窗口中直接添加 URL。

```Shell
playwright codegen demo.playwright.dev/todomvc
```

### 录制测试

运行 `codegen` 并在浏览器中执行操作。Playwright 将为用户交互生成代码。`Codegen` 将查看渲染后的页面并找出推荐的定位器，优先考虑角色、文本和测试 ID 定位器。如果生成器识别出多个元素与定位器匹配，它将改进定位器，使其更具弹性并唯一地识别目标元素，从而消除和减少由于定位器导致的测试失败和不稳定。

使用测试生成器，您可以录制：

* 通过简单地与页面交互，执行点击或填充等操作
* 通过点击工具栏上的一个图标，然后点击页面上的元素进行断言。您可以选择：
  * `'assert visibility'` 断言元素可见
  * `'assert text'` 断言元素包含特定文本
  * `'assert value'` 断言元素具有特定值

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=MjgxNDZhNjkyZWZiYjk3MjkwOTAxMGIyMWUyOWU0NDNfVmZrcmkwWmt0blpHMHpNMm9JaTZCUXo5OFNWZnVUQXZfVG9rZW46Vm1IM2JadUFBb2Uza3V4SUdidGNYdnpYbm5mXzE3NDI0NjEyOTg6MTc0MjQ2NDg5OF9WNA)

当您完成与页面的交互后，按下 `'record'` 按钮停止录制，并使用 `'copy'` 按钮将生成的代码复制到您的编辑器中。

使用 `'clear'` 按钮清除代码以开始重新录制。完成后，关闭 Playwright 检查器窗口或停止终端命令。

要了解更多关于生成测试的信息，请查看我们关于 Codegen 的详细指南。

### 生成定位器

您可以使用测试生成器生成定位器。

* 按下 `'Record'` 按钮停止录制，'Pick Locator'` 按钮将会出现。
* 点击 `'Pick Locator'` 按钮，然后将鼠标悬停在浏览器窗口的元素上，以查看定位器在每个元素下方突出显示。
* 要选择一个定位器，单击您想要定位的元素，该定位器的代码将出现在 Pick Locator 按钮旁边的定位器游乐场中。
* 然后您可以在定位器游乐场中编辑定位器以微调它，并看到匹配的元素在浏览器窗口中突出显示。
* 使用复制按钮复制定位器并将其粘贴到您的代码中。

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=YTRiNjEwY2U4MWUwY2EwZDc1YzliNDZmZGM5NWNiYzBfbVNUNjVQNE5vbjhkZWdBUG1VSkhYR2FlRU1QaXdiZUxfVG9rZW46UFB2eGJVeEhFb05wSmN4ZkM4QmNOam94bmxmXzE3NDI0NjEyOTg6MTc0MjQ2NDg5OF9WNA)

### 仿真

您还可以使用仿真生成测试，以便为特定的视口、设备、颜色方案生成测试，以及模拟地理位置、语言或时区。测试生成器还可以在保持认证状态的同时生成测试。查看测试生成器指南以了解更多信息。

## 接下来做什么

* 查看您的测试跟踪

# 运行和调试

## 引言

您可以运行单个测试、一组测试或所有测试。使用 `--browser` 标志，可以在一个浏览器或多个浏览器上运行测试。默认情况下，测试以无头模式运行，这意味着在运行测试时不会打开浏览器窗口，结果将在终端中显示。如果您愿意，可以通过使用 `--headed` CLI 参数以有头模式运行您的测试。

**您将学到**

* 如何从命令行运行测试
* 如何调试测试

## 运行测试

### 命令行

要运行您的测试，请使用 `pytest` 命令。这将默认在 Chromium 浏览器上运行您的测试。默认情况下，测试以无头模式运行，这意味着在运行测试时不会打开浏览器窗口，结果将在终端中显示。

### 在有头模式下运行测试

要以有头模式运行您的测试，请使用 `--headed` 标志。这将在运行测试时打开浏览器窗口，并在完成后关闭浏览器窗口。

### 在不同的浏览器上运行测试

要指定您想要运行测试的浏览器，请使用 `--browser` 标志，后跟浏览器的名称。

要指定要在多个浏览器上运行测试，请多次使用 `--browser` 标志，后跟每个浏览器的名称。

```Shell
pytest --browser webkit --browser firefox
```

### 运行特定测试

要运行单个测试文件，请传入您想要运行的测试文件的名称。

要运行一组测试文件，请传入您想要运行的测试文件的名称。

```Shell
pytest tests/test_todo_page.py tests/test_landing_page.py
```

要运行特定测试，请传入您想要运行的测试的函数名称。

```Shell
pytest -k test_add_a_todo_item
```

### 并行运行测试

要并行运行您的测试，请使用 `--numprocesses` 标志，后跟您想要运行测试的进程数量。我们建议使用逻辑 CPU 核心数的一半。

（这假设已安装了 `pytest-xdist`。有关更多信息，请参见此处。）

有关更多信息，请参见 Playwright Pytest 使用情况或 Pytest 文档以了解一般 CLI 使用情况。

## 调试测试

由于 Playwright 在 Python 中运行，您可以使用您选择的调试器进行调试，例如使用 Visual Studio Code 中的 Python 扩展。Playwright 带有 Playwright 检查器，允许您逐步执行 Playwright API 调用，查看它们的调试日志并探索定位器。

要调试所有测试，请运行以下命令。

* Bash
* PowerShell
* Batch

要调试一个测试文件，请在命令后运行您想要调试的测试文件的名称。

* Bash
* PowerShell
* Batch

```Shell
PWDEBUG=1 pytest -s test_example.py
```

要调试特定测试，请添加 `-k` 后跟您想要调试的测试的名称。

* Bash
* PowerShell
* Batch

```Shell
PWDEBUG=1 pytest -s -k test_get_started_link
```

此命令将打开浏览器窗口以及 Playwright 检查器。您可以使用检查器顶部的步过按钮逐步执行您的测试。或者按下播放按钮从开始到结束运行您的测试。一旦测试完成，浏览器窗口将关闭。

在调试时，您可以使用选择定位器按钮来选择页面上的元素，并查看 Playwright 用于查找该元素的定位器。您还可以编辑定位器并实时在浏览器窗口中看到它被高亮显示。使用复制定位器按钮将定位器复制到剪贴板，然后将其粘贴到您的测试中。

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=ZGM3ZjNlYjFkMDBhYWZhODQ1YzFlZDg5ZWViMjZkZDlfSnZLTUlGc1FXZUk1NWdReUx2NzhjbkJtaHlSbzRvRFRfVG9rZW46VTRXM2JndjRib3lMZVZ4YXdlcGN1N2FGbkNiXzE3NDI0NjEyOTg6MTc0MjQ2NDg5OF9WNA)

查看我们的调试指南，以了解更多关于 Playwright 检查器以及使用浏览器开发工具进行调试的信息。

## 接下来做什么

* 使用 Codegen 生成测试
* 查看您的测试跟踪
* 在 CI 上使用 GitHub Actions 运行您的测试

# 跟踪查看器

## 介绍

Playwright Trace Viewer 是一个图形用户界面（GUI）工具，允许您探索录制的 Playwright 测试跟踪，这意味着您可以前后浏览测试的每个动作，并直观地看到每个动作期间发生了什么。

**您将学到**

* 如何录制跟踪
* 如何打开 HTML 报告
* 如何打开跟踪查看器

## 录制跟踪

可以通过使用 `--tracing` 标志运行测试来录制跟踪。

跟踪的选项有：

* `on`: 为每个测试录制跟踪
* `off`: 不录制跟踪。（默认）
* `retain-on-failure`: 为每个测试录制跟踪，但删除成功测试运行的所有跟踪。

这将录制跟踪并将其放入 `test-results` 目录中名为 `trace.zip` 的文件中。

如果您没有使用 Pytest，请点击这里了解如何录制跟踪。

* 同步
* 异步

```Python
browser = chromium.launch()
context = browser.new_context()

# 在创建/导航页面之前开始跟踪。
context.tracing.start(screenshots=True, snapshots=True, sources=True)
page = context.new_page()
page.goto("https://playwright.dev")

# 停止跟踪并将其导出到 zip 归档中。
context.tracing.stop(path="trace.zip")
```

## 打开跟踪

您可以使用 Playwright CLI 或在 `trace.playwright.dev` 上的浏览器中打开保存的跟踪。确保添加您的 `trace.zip` 文件所在的完整路径。这应该包括 `test-results` 目录，然后是测试名称，最后是 `trace.zip`。

```Bash
playwright show-trace trace.zip
```

## 查看跟踪

通过点击每个动作或使用时间线悬停来查看测试的跟踪，并查看动作前后页面的状态。在测试的每个步骤期间检查日志、源代码和网络。跟踪查看器创建了一个 DOM 快照，因此您可以完全与之交互，打开开发工具等。

要了解更多信息，请查看我们关于跟踪查看器的详细指南。

## 接下来是什么

* 在 GitHub Actions 上运行 CI 测试
* 了解更多关于跟踪查看器的信息

# Pytest 插件来编写端到端测试

## 引言

Playwright 提供了一个 Pytest 插件来编写端到端测试。要开始使用它，请参考入门指南。

## 使用方法

要运行测试，请使用 Pytest 命令行界面。

```Bash
pytest --browser webkit --headed
```

如果你想自动添加命令行参数而不需要明确指定它们，你可以使用 pytest.ini 文件：

```TOML
# pytest.ini 文件的内容
[pytest]
# 使用 UI 运行 firefox
addopts = --headed --browser firefox
```

## 命令行参数

请注意，命令行参数仅应用于默认的 `browser`、`context` 和 `page` 固定装置。如果你使用 API 调用如 browser.new_context() 创建浏览器、上下文或页面，命令行参数将不会应用。

* `--headed`：以有头模式运行测试（默认：无头）。
* `--browser`：在不同的浏览器中运行测试 `chromium`、`firefox` 或 `webkit`。可以多次指定（默认：`chromium`）。
* `--browser-channel`：要使用的浏览器渠道。
* `--slowmo`：通过指定的毫秒数减慢 Playwright 操作。这样你可以看清楚发生了什么（默认：0）。
* `--device`：要模拟的设备。
* `--output`：由测试产生的工件目录（默认：`test-results`）。
* `--tracing`：是否为每个测试记录跟踪。`on`、`off` 或 `retain-on-failure`（默认：`off`）。
* `--video`：是否为每个测试录制视频。`on`、`off` 或 `retain-on-failure`（默认：`off`）。
* `--screenshot`：是否在每个测试后自动捕获屏幕截图。`on`、`off` 或 `only-on-failure`（默认：`off`）。
* `--full-page-screenshot`：在失败时是否拍摄整个页面的屏幕截图。默认情况下，只捕获视口。需要启用 `--screenshot`（默认：`off`）。

## 固定装置

这个插件为 pytest 配置了 Playwright 特定的固定装置。要使用这些固定装置，将固定装置名称作为参数传递给测试函数。

```Python
def test_my_app_is_working(fixture_name):
    pass
    # 使用 fixture_name 进行测试
    # ...
```

 **函数范围** ：当在测试函数中请求时，这些固定装置被创建，并在测试结束时销毁。

* `context`：测试的新浏览器上下文。
* `page`：测试的新浏览器页面。
* `new_context`：允许为测试创建不同的浏览器上下文。适用于多用户场景。接受与 browser.new_context() 相同的参数。

 **会话范围** ：当在测试函数中请求时，这些固定装置被创建，并在所有测试结束时销毁。

* `playwright`：Playwright 实例。
* `browser_type`：当前浏览器的 BrowserType 实例。
* `browser`：由 Playwright 启动的浏览器实例。
* `browser_name`：浏览器名称字符串。
* `browser_channel`：浏览器渠道字符串。
* `is_chromium`、`is_webkit`、`is_firefox`：相应浏览器类型的布尔值。

 **自定义固定装置选项** ：对于 `browser` 和 `context` 固定装置，使用以下固定装置定义自定义启动选项。

* `browser_type_launch_args`：覆盖 browser_type.launch() 的启动参数。它应该返回一个字典。
* `browser_context_args`：覆盖 browser.new_context() 的选项。它应该返回一个字典。

也可以通过使用 `browser_context_args` 标记来覆盖单个测试的上下文选项（browser.new_context()）：

```Python
import pytest

@pytest.mark.browser_context_args(timezone_id="Europe/Berlin", locale="en-GB")
def test_browser_context_args(page):
    assert page.evaluate("window.navigator.userAgent") == "Europe/Berlin"
    assert page.evaluate("window.navigator.languages") == ["de-DE"]
```

## 并行性：同时运行多个测试

如果你的测试在拥有大量 CPU 的机器上运行，你可以通过使用 `pytest-xdist` 同时运行多个测试来加快测试套件的整体执行时间：

```Bash
# 安装依赖
pip install pytest-xdist
# 使用 --numprocesses 标志
pytest --numprocesses auto
```

根据硬件和测试的性质，你可以将 `numprocesses` 设置为从 `2` 到机器上的 CPU 数量。如果设置得太高，你可能会注意到意外的行为。

有关 `pytest` 选项的一般信息，请参见运行测试。

## 示例

### 为自动补全配置 Mypy 类型

test_my_application.py

```Python
from playwright.sync_api import Page

def test_visit_admin_dashboard(page: Page):
    page.goto("/admin")
    # ...
```

### 配置慢动作

使用 `--slowmo` 参数运行测试。

将 Playwright 操作减慢 100 毫秒。

### 按浏览器跳过测试

test_my_application.py

```Python
import pytest

@pytest.mark.skip_browser("firefox")
def test_visit_example(page):
    page.goto("https://example.com")
    # ...
```

### 在特定浏览器上运行

conftest.py

```Python
import pytest

@pytest.mark.only_browser("chromium")
def test_visit_example(page):
    page.goto("https://example.com")
    # ...
```

### 使用自定义浏览器渠道，如 Google Chrome 或 Microsoft Edge

```Bash
pytest --browser-channel chrome
```

test_my_application.py

```Python
def test_example(page):
    page.goto("https://example.com")
```

### 配置基础 URL

使用 `base-url` 参数启动 Pytest。`pytest-base-url` 插件用于此目的，它允许你从配置、命令行参数或固定装置中设置基础 URL。

```Bash
pytest --base-url http://localhost:8080
```

test_my_application.py

```Python
def test_visit_example(page):
    page.goto("/admin")
    # -> 将导致 http://localhost:8080/admin
```

### 忽略 HTTPS 错误

conftest.py

```Python
import pytest

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "ignore_https_errors": True
    }
```

### 使用自定义视口大小

conftest.py

```Python
import pytest

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        }
    }
```

### 设备模拟

conftest.py

```Python
import pytest

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, playwright):
    iphone_11 = playwright.devices['iPhone 11 Pro']
    return {
        **browser_context_args,
        **iphone_11,
    }
```

或通过命令行 `--device="iPhone 11 Pro"`。

### 与 `unittest.TestCase` 一起使用

查看以下示例，了解如何将其与 `unittest.TestCase` 一起使用。这有一个限制，即只能指定单个浏览器，并且在指定多个浏览器时不会生成多个浏览器的矩阵。

```Python
import pytest
import unittest

from playwright.sync_api import Page

class MyTest(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page = page

    def test_foobar(self):
        self.page.goto("https://microsoft.com")
        self.page.locator("#foobar").click()
        assert self.page.evaluate("1 + 1") == 2
```

## 调试

### 与 pdb 一起使用

在你的测试代码中使用 `breakpoint()` 语句来暂停执行并获得 pdb REPL。

```Python
def test_bing_is_working(page):
    page.goto("https://bing.com")
    breakpoint()
    # ...
```

## 部署到 CI

请参阅 CI 提供商的指南，了解如何将你的测试部署到 CI/CD。

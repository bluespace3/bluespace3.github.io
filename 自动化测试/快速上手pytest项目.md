---
title: '快速上手pytest项目'
categories: ["技术"]
date: 2025-10-23T13:50:13+00:00
lastmod: 2025-10-23T13:50:13+00:00
---


tags: ["pytest", "python"]
--------------------------

# 快速上手Pytest接口测试

# 背景

以前有分享过httprunner+pytest相关的使用方法，并且一直使用httprunner编写用自动化脚本，以前的经验可以快速帮我们上手pytest框架。为了快速上手pytest，HttpRunner 与Pytest 在编写自动化脚本异同点对比：

<html><body><table><tr><td>对比维度</td><td>HttpRunner</td><td>Pytest</td></tr><tr><td>用例编写方式</td><td>支持YAML/JSON（低代码）和 pytest代码138</td><td>纯 Python代码编写，支持函数式</td></tr><tr><td>执行框架</td><td>基于pytest（3.x版本后）18</td><td>原生pytest框架，支持更灵活的</td></tr><tr><td>参数化</td><td>通过parameters在YAML/JSON中实现，或在 pytest代码中使用参数化装饰器16</td><td>原生支持 @pytest.mark.parametr 高，支持动态生成数据</td></tr><tr><td>断言机制</td><td>基于validate关键字，支持jmespath 表达式18</td><td>使用Python原生assert或第三方 pytest-assume 多断言)</td></tr><tr><td>测试报告</td><td>支持Allure（3.x版本后不再自带HTML报告）18</td><td>依赖插件（如pytest-html、allure- 定制性强59</td></tr><tr><td>扩展性</td><td>通过debugtalk.py自定义函数，但框架耦合度高18</td><td>原生支持插件开发，可通过conf fixture，扩展性极强5</td></tr><tr><td>用例分层</td><td>明确分层（APl/TestSuite/TestCase），适合原子接 口与流程组合18</td><td>无强制分层，但可通过模块化 page_object模式）实现类</td></tr><tr><td>学习曲线</td><td>低代码门槛，适合快速上手15</td><td>需 Python基础，但灵活性更高，道</td></tr></table></body></html>

# 项目初始化

克隆项目◦ git clone git@gitlab.guangpuyun.cn:clinic-diag/test/poct_api_test.git
了解项目结构

![](/images/528752a3cec6442b7fb16aabcf1f313f94a9b0c3c9a71d46f85a3bb0ab45bcc6.jpg)

# 安装依赖

◦ 项目根目录下打开终端，执行pip install -r requirements.txt

# 测试用例格式

1. 用例文件以test_开头或_test结尾◦ 建议以场景命名-如四合一的快速检测：test_zk_quicktest.py
2. 用例集合——类，以Test开头（可以无）◦ 包含1个或多个测试用例函数
3. 测试用例函数以test_开头◦ 一个函数代表一条用例- $_->$ 一个明确的测试点

# 用例转换

1、运行脚本utils/swaager.py——爬取swagger文档资源,存放于/api/swaggerApi目录
2、运行脚本api/generateTestCases.py，生成基础用例，存放于/api目录
3、基础用例结构

此时只是生成了接口的对象，还需要编写实现逻辑和传参进一步实现该对象，完成测试用例编写（见用例编写）

![](/images/e2e3d30579d03e71fcd65320f80da7a2b548bfc1056245fa3d54b9669e3ce7c3.jpg)

# 用例编写

1. 在/test对应的目录下新建用例文件，命名以test_开头，表明测试场景

![](/mages/3dcd5da9b6d6fde4508a1aada61ca3d3486938faed0f48a273a4a4ac026db38f.jpg)

2. 导入必要的包和基础用例，如：

from utils.logger import loggerfrom api.poctMina.addcartusingPosT import YsbMallCartController

# 3. 编写测试用例

from utils.logger import logger fron api.poctMina.addCartUsinqPosT import YsbMallCartController def test_addCartUsing(getTokenBySecret,pytestconfig): 用例名称-体现在报告上 addCartUsing $\mathbf{\sigma}=\mathbf{\sigma}$ YsbHallCartController ( addcartUsing.base_url $\mathbf{\sigma}=\mathbf{\sigma}$ pytestconfig.getini('poct-host') 构造url addCartUsinq.data['addNum']=1 addCartUsing.data['packageId'] $=2\dot{0}\dot{\Theta}$ addCartUsing.data[\*token']=getTokenBySecret(store=3o15659) 构造传参 response_data=addcartUsing.addcart() .json() 获取返回值 logger.info(response_data) assert response_data['code'] $\scriptstyle==$ '40001' 断言

# 用例参数化

# 1. 直接传参给函数 （小数据量）

@pytest.mark.parametrize(x,y,[（x1，y1），（x2'，y2'）],indirect=True)

# 2. 当需要对参数进行处理时

@pytest.fixture(scope='class',autouse $\risingdotseq$ True, params $\c=$ order_id,ids $\c=$ ids)scope作用域-可以是function，class,module，session;配合@pytest.mark.parametrize(x,[1,2],indirect $\varXi^{-}$ True)传参使用，   #indirect $\varXi^{-}$ True代表使用fixture函数处理数据。 request.param  在 fixture 中获取原始参数值。

1 import pytest
2
3 @pytest.fixture
4 def number(request):
5 return request.param $\star$ 2
6
7 @pytest.mark.parametrize("number", [1, 2, 3], indirect=True)
8 def test_number(number):
9 assert number in [2, 4, 6]

# 3. 参数化从文件读取数据

从外部文件（如 CSV、JSON、YAML）读取测试数据，适用于数据量较大或需要动态生成数据的场景。

1 import pytest
2 import json
3
4 def load_test_data(file_path):
5 with open(file_path, $"r"$ ) as f:
6 return json.load(f)
7
8 @pytest.mark.parametrize("test_case", load_test_data('test_data.json'))
9 def test_from_file(test_case):
10 assert test_case['input'] $^+$ test_case['addend'] $\scriptstyle==$ test_case['expected']

# pytest_generate_tests 钩子函数来自定义参数化。

在测试收集阶段动态生成参数。
适用于需要在多个测试函数中共享参数化逻辑的情况。

1 def pytest_generate_tests(metafunc):
2 if "num" in metafunc.fixturenames:
3 numbers $\mathbf{\Psi}=\mathbf{\Psi}$ [1, 2, 3]
4 metafunc.parametrize("num", numbers)
5 def test_number(num):
6 assert num in [1, 2, 3]

# 5. 用例参数化 Fixture

参数化 fixture，使其在不同的测试中提供不同的数据。

1 import pytest
2 @pytest.fixture(params $\c=$ [1, 2, 3])
3 def number(request):
4 return request.param
5 def test_number(number):
6 assert isinstance(number, int)

# 用例封装

# 1. fixture关键字驱动

方法：

通过@pytest.fixture装饰器封装一些常用的工具函数放到conftest.py作用：

a. 用例中可实现不用导包直接使用。b. 可实现用例之间的参数传递c. 可作用于全局，也可灵活定义作用域

例如：conftest.py中定义fixture函数获取token

![](/images/a3502a2fc2f9af6e14dcd689593941a4dfef06e0d8cbd5ffe454a716c5b34034.jpg)

# 在用例中直接使用getTokenBySecret函数获取token：

![](/images/681f2d22d1be837c8a95193cdea6a21af206f6da36eb0348cef7119b1fcbd06d.jpg)

# 2. 公用模块的封装

存放一些封装好的可复用的公共模块，如连接数据库，reques请求，日志模块等

![](/images/5d6b263a2dce97da8d2384126e5ab947424978b2d90be13cf482984439e78364.jpg)

# 用例断言

a. 判断是否为真： assert xxb. 判断不为真： assert not xxc. 判断a是否包含b： assert a in bd. 判断a不包含b： assert a not in be. 判断两值相等： assert b $\mathtt{\Gamma}==\mathtt{a}$ f. 判断两值不相等： assert a != b

# 运行

# 1. 终端

◦ pytest -q/-s 静默运行/运行时显示打印
◦ 运行结果生成报告 pytest --html=report.html
◦ 运行指定用例 pytest test_se.py::TestClassone::test_one
◦ 多进程数（NUM）运行 pytest test_se.py -n NUM
◦ 运行失败重试（NUM）次：pytest test_se.py --reruns NUM
◦ 跳过用例运行@pytest.mark.skip
◦ 重试@pytest.mark.flaky(reruns $^{:=3}$ , reruns_delay $^{\prime=2}$ )  #失败时重试3次，每次间隔2秒

# 2. 代码运行

直接运行main.py（提交代码前必须运行通过）

# 测试报告

# 浏览器打开pytest_report.html

# 光谱接口自动化测试报告

Report generated on 12-Mar-2025 at 16:13:25 by pytest-html v4.1.1

# Environment

<html><body><table><tr><td>Python</td><td>3.10.4</td></tr><tr><td>执行时间</td><td>2025-03-12 16:12:14</td></tr><tr><td>项目名称</td><td>POCT系统测试报告</td></tr></table></body></html>

# summary

17 tests took 00:01:11

(Un)check the boxes to filter the results

<html><body><table><tr><td>Result</td><td>Test 用例路径</td><td>TestName 用例名称</td><td>执行时间</td></tr><tr><td>Passed</td><td>tests/test_poct_mal/test_addCart.py::test_addCartUsing</td><td>加购物功能测试</td><td>00:00:05</td></tr><tr><td>Passed</td><td>tests/test_poct_mall/test_getUsefulPoctProductsV2.py:test_getUsefulPoctProducts</td><td>测试用例1：MachineSampleController查询所有有效的产品信息</td><td>00:00:03</td></tr><tr><td>Passed</td><td>tests/test_poct_mal/test_getUsefulPoctProductsV2.pytest_getUsefulPoctProducts1</td><td>测试用例2：PoctMinaMachineSampleController查询所有有效的产品信息</td><td>00:00:01</td></tr><tr><td>Passed</td><td>tests/test_poct_mal/test_getUsefulPoctProductsV2.py:test_getUsefulPoctProducts2</td><td>测试用例3：YsbMachineSampleController查询所有有效的产品信息</td><td>00:00:01</td></tr><tr><td>Passed</td><td>tests/test_poct_mall/test_getUsefulPoctProductsV2.py:test_getUsefulPoctProducts3</td><td>测试用例4：查询YtjMachineSampleController所有有效的产品信息</td><td>933 ms</td></tr><tr><td>Passed</td><td>tests/test_poct_mal/test_listAccount_2.py::TestPoctMinaOrderReportControllr:test_listAccount</td><td>不分页查询下单账号</td><td>00:00:01</td></tr><tr><td>Passed</td><td>tests/test_poct_mina/test_createOrder.py::TestMinaOrder:test_createOrder</td><td>创建单项目订单，成功生成订单</td><td>00:00:06</td></tr><tr><td>Passed</td><td>tests/test_poct_mina/test_createOrder.py.:TestMinaOrder::test_createOrder2</td><td>创建多项目订单，成功生成订单</td><td>00:00:04</td></tr><tr><td>Passed</td><td>tests/test_process_cases/test_zk_archivestest.py::TestArchivesTest:test_getArchives</td><td>建档患者信息-信息同步</td><td>00:00:01</td></tr><tr><td>Passed</td><td>tests/test_process_cases/test_zk_archivestest.py::TestArchivesTest:test_uploudArchives</td><td>上传建档患者检测结果-患者信息正确</td><td>00:00:05</td></tr><tr><td>Passed</td><td>tests/test_process_cases/test_zk_minaOrder.py::TestMinaOrder:test_get_orderld</td><td>小程序下单后-订单同步到设备</td><td>00:00:05</td></tr><tr><td>Passed</td><td>tests/test_process_cases/test_zk_minaOrder.py:TestMinaOrder:test_order_state</td><td>小程序下单-设备上传检测结果-订单状态变为已完成</td><td>00:00:05</td></tr><tr><td>Passed</td><td>tests/test_process_cases/test_zk_minaOrder.py::TestMinaOrder:test_product_state</td><td>小程序下单-设备上传订单部分检测结果-检测项目状态变为已完成且无结果项目取消</td><td>00:00:07</td></tr><tr><td>Passed</td><td>tests/test_process_cases/test_zk_minaOrder.py::TestMinaOrder:test_product_state_change</td><td>小程序下单-设备细项加样上传细项检测结果日志-检测项目状态变为检测中</td><td>00:00:15</td></tr><tr><td>Passed</td><td>tests/test_process_cases/test_zk_quicktest.py::Testquicktets::test_uploud_single_results</td><td>测试上传单条检测结果创建订单-生成订单</td><td>00:00:03</td></tr><tr><td>Passed</td><td>tests/test_process_cases/test_zk_quicktest.py::Testquicktets:test_upload_duplicate</td><td>测试上传上传四个联检项目检测结果，创建订单且项目正确</td><td>00:00:05</td></tr><tr><td>Passed</td><td>tests/test_process_cases/test_zk_quicktest.py::Testquicktets:test_upload_twice</td><td>重复上传多次相同machine_id的同一条结果，只生成一个订单</td><td>00:00:03</td></tr></table></body></html>

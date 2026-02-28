---
title: 'pytest接口自动化测试方案'
categories: ["自动化测试"]
date: 2025-09-07T00:20:29+08:00
lastmod: 2025-09-07T00:20:29+08:00
encrypted: false
---

## ** 持续集成（CI/CD）**

* 集成流程
* 代码提交 → 静态检查 → 单元测试 → 自动化测试 → 报告生成
* 流水线配置
  * GitLab CI YAML配置
* 结果通知
  * 企业微信群通知

---

## **风险管理**

* 潜在风险
  * 环境不稳定
  * 脚本维护成本
  * 需求功能变更
* 应对措施
  * 设计时需要提前考虑脚本稳定性
  * 定期维护脚本
  * 运行前保证环境正常可用

---

## **相关交付物**

* 测试报告
  * HTML报告
* 自动化脚本
  * 代码仓库https://gitlab.guangpuyun.cn/clinic-diag/test/poct_api_test
  * 项目结构

    ![1743176486423](/images/pytest接口自动化测试方案/1743176486423.png)
* 文档
  * 初始化文档[快速编写Pytest接口测试](https://guangpuyun.feishu.cn/docx/SQi7d8NV4opR8OxYDh9cxVG3nmg?from=from_copylink)
  * 自动化用例设计文档[接口自动化测试用例](https://guangpuyun.feishu.cn/base/XG9ZbshkeaG2NYsdUb5cOYaQnBg?from=from_copylink)

---

## **维护与优化**

* 脚本维护人员
  * 一般情况下谁写的谁维护
* 脚本维护方法
  * 接口变更的处理
    * 用例执行/定时/手动触发脚本爬取接口文档，并与最新接口文档对比
    * 运行main.py 执行用例时，会在warnning日志提醒相关变更
      ![1743176811159](/image/pytest接口自动化测试方案/1743176811159.png)
    * 检查变更是否涉及已经编写的用例（快捷键ctrl+shift+f搜索关键词即可）
      ![1743177028645](/image/pytest接口自动化测试方案/1743177028645.png)

      如：PoctCreateOrderInModel存在差异，对应json文档中找到对应 **operationId（文件名），在用例文档中搜索createOrder2UsingPOST_1** ，发现涉及已有用例。

      ![1743177240411](/image/pytest接口自动化测试方案/1743177240411.png)
    * 若有涉及用例，则维护成最新接口信息。
  * 当用例运行报错/不通过进行定位
    * bug->记录并通知开发修复；
    * 数据问题->使用自动化专用的数据，避免污染；
    * 脚本本身不稳定导致的运行失败，维护脚本能稳定运行，若维护成功过高可直接先注释脚本，并在对应用例做好备注“待维护”。
* 脚本维护代办事项
  * [接口自动化代办事项](https://guangpuyun.feishu.cn/sheets/IrensB0Lmhi7Y5t3izhccc9wnBh?from=from_copylink)

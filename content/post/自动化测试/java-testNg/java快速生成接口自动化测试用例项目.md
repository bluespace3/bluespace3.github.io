---
title: 'java快速生成接口自动化测试用例项目'
categories: ["自动化测试"]
date: 2025-11-20T23:25:58+08:00
lastmod: 2026-03-25T17:40:01+08:00
draft: false
---
# java快速生成接口自动化测试用例项目

使用TestNG 和 REST Assured 进行 API 测试，并支持测试用例与接口逻辑分离的架构。本框架提供完整的HAR文件自动化转换、测试用例依赖管理、数据驱动测试、数据库集成等高级功能。

## 目录

- [核心特性](#核心特性)
- [快速开始](#快速开始)
- [HAR文件自动化测试生成](#har文件自动化测试生成)
  - [自动Token处理（高级功能）](#自动token处理高级功能)
- [测试用例配置详解](#测试用例配置详解)
- [高级功能](#高级功能)
- [运行和调试](#运行和调试)
- [项目架构](#项目架构)
- [最佳实践](#最佳实践)

## 核心特性

### 🚀 HAR文件自动化

- **一键转换**: 将浏览器录制的HAR文件自动转换为完整的测试套件
- **智能解析**: 自动提取请求信息、响应断言和认证数据
- **直接运行**: 生成的测试用例无需修改即可执行

### 🔗 测试用例依赖管理

- **依赖声明**: 通过 `dependsOn` 字段指定测试用例间的依赖关系
- **自动排序**: 系统自动进行拓扑排序，确保正确的执行顺序
- **循环检测**: 自动检测并报告循环依赖错误

### 📊 数据驱动测试

- **参数化**: 单个测试用例支持多组测试数据
- **动态变量**: 支持上下文变量、环境变量、内置变量和自定义变量生成器
- **数据提取**: 从API响应中提取数据并存储到测试上下文中

### 💾 数据库集成

- **请求前查询**: 从数据库获取数据作为API请求参数
- **请求后验证**: 验证API操作后数据库中的数据是否正确
- **多数据库支持**: MySQL、PostgreSQL、H2等

### 🎯 精准测试执行

- **单用例执行**: 通过 `-DtestId` 参数执行特定测试用例
- **分组批量执行**: 通过 `-DtestGroup` 参数执行特定分组的测试
- **自动依赖包含**: 执行时自动包含所有依赖的测试用例

### 📝 智能失败诊断

- **详细日志**: 自动记录失败测试的完整请求/响应信息
- **日志文件**: 失败信息同时保存到 `target/logs/test_failures.log`
- **UTF-8支持**: 正确处理中文内容

## 快速开始

### 前置条件

- Java 8+
- Maven 3.6+

### 安装和配置

1. 克隆项目到本地
2. 运行 `mvn compile` 编译项目
3. （可选）配置数据库连接：修改 `src/test/resources/database.properties`

### 基本使用流程

1. **录制HAR文件**: 在浏览器中录制API操作流程
2. **生成测试用例**: 使用 `import-har.bat your-file.har` 自动生成测试
3. **运行测试**: 执行 `mvn test` 运行所有测试
4. **查看报告**: 使用 `allure serve target/allure-results` 查看详细报告

## HAR文件自动化测试生成

### 使用方法

```bash
# Windows批处理（推荐）
import-har.bat your-file.har                    # 自动生成测试类名称
import-har.bat your-file.har MyCustomTest       # 指定自定义测试类名称
import-har.bat har-files-directory/             # 批量导入目录下所有HAR文件

# PowerShell版本
.\import-har.ps1 your-file.har
.\import-har.ps1 your-file.har MyCustomTest
.\import-har.ps1 har-files-directory/
```

### 生成的文件说明

**1. 测试用例配置文件**

- 路径: `src/test/resources/testcases/{har-file-name}_test_cases.json`
- 内容: 包含从HAR文件解析的所有API请求信息和基础断言

**2. 统一执行模式**

- 默认启用统一配置模式，所有HAR文件的测试用例都添加到统一配置文件
- 只需要一个测试类: `UnifiedApiTest`
- 批量导入时，所有测试用例集中管理，无需维护多个测试类

### 自动Token处理（高级功能）

为了简化需要认证的API测试用例生成，框架提供了自动Token处理功能。启用此功能后，系统会自动识别相同应用的接口，并将从login接口提取的token自动赋值到相关请求参数中。

#### 配置文件设置

首先需要在 `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-apps.json` 中注册已知的应用和对应的login接口：

```json
[
  {
    "origin": "https://testntr.yaoshibang.cn",
    "loginTestCaseId": "POST__wsms_pc_auth_login"
  }
]
```

**配置字段说明**:

- `origin`: 应用的Origin URL（必须与HAR文件中的Origin header完全匹配）
- `loginTestCaseId`: 对应的login接口测试用例ID

#### 使用方法

在导入HAR文件时添加 `--auto-token` 参数：

```bash
# 单文件导入（启用自动token处理）
import-har.bat your-file.har --auto-token

# 指定测试类名 + 自动token处理
import-har.bat your-file.har MyCustomTest --auto-token

# 批量导入目录（启用自动token处理）
import-har.bat har-files-directory/ --auto-token
```

#### 功能说明

1. **域名校验**: 系统会检查HAR文件中每个请求的Origin header是否在配置文件中注册
2. **错误处理**: 如果发现未注册的域名，会输出错误日志 `"导入错误，未发现该应用登陆接口: [Origin值]"` 并跳过该请求
3. **自动配置**:
   - **Login接口**: 自动添加extractors配置提取authToken
   - **其他接口**: 自动添加 `dependsOn` 依赖和 `${context.authToken}` token参数
4. **向后兼容**: 不使用 `--auto-token` 参数时，保持原有行为不变

#### 示例输出

```
✅ HAR文件导入和测试生成成功！
📁 输入文件: testntr.yaoshibang.cn.har
🧪 测试类名: TestntrYaoshibangCnTest
🚀 现在可以运行: mvn test -Dtest=UnifiedApiTest
```

> **注意**: 此功能需要预先在配置文件中注册应用信息，确保生成的测试用例可以直接运行并进行基础断言测试。

## 测试用例配置详解

### 基础测试用例结构

```json
{
  "id": "TC001",
  "name": "TestName",
  "description": "测试描述",
  "endpoint": "/api/users/{id}",
  "method": "GET",
  "pathParam": "3",
  "headers": {
    "Content-Type": "application/json"
  },
  "cookies": {},
  "requestBody": null,
  "assertions": {
    "statusCode": 200,
    "body.name": "预期用户名"
  }
}
```

### 测试用例ID生成规则

- **格式**: `{har_file_name}_{HTTP_METHOD}_{cleaned_endpoint}`
- **示例**: `testntr_yaoshibang_cn_POST__wsms_pc_auth_login`
- **去重机制**: 即使在独立JSON模式下也会自动去重，避免重复导入

### 支持的断言类型

- **statusCode**: HTTP状态码 (数字)
- **body.xxx**: JSON路径断言，支持以下特殊值：
  - `"普通值"`: 精确匹配
  - `"containsString:文本"`: 包含指定文本
  - `"matchesRegex:正则表达式"`: 正则表达式匹配
  - `"notNull"`: 非空值检查
  - `"null"`: 空值检查
  - `"empty"`: 空字符串或空集合
  - `"notEmpty"`: 非空字符串或非空集合
  - `">数字"`: 大于指定数字
  - `"<数字"`: 小于指定数字
  - `"in:值1,值2,值3"`: 值在指定列表中
  - `"hasSize:数字"`: 集合大小检查

## 高级功能

### 测试用例依赖管理

```json
{
  "id": "get_user_profile",
  "name": "GetUserProfile",
  "description": "获取用户个人资料（依赖登录）",
  "endpoint": "/api/user/profile",
  "method": "GET",
  "headers": {
    "Authorization": "Bearer ${context.authToken}"
  },
  "assertions": {
    "statusCode": 200,
    "body.userId": "${context.userId}"
  },
  "dependsOn": ["login_success"]
}
```

### 数据提取功能

```json
{
  "id": "login_and_extract",
  "name": "LoginAndExtract",
  "description": "登录并提取认证令牌",
  "endpoint": "/api/auth/login",
  "method": "POST",
  "requestBody": "{\"username\": \"test\", \"password\": \"password\"}",
  "assertions": {
    "statusCode": 200,
    "body.status": "success"
  },
  "extractors": [
    {
      "source": "response.body",
      "path": "data.token",
      "target": "authToken",
      "type": "string"
    },
    {
      "source": "response.body",
      "path": "data.userId",
      "target": "userId",
      "type": "string"
    }
  ]
}
```

### 参数化测试

```json
{
  "id": "search_products",
  "name": "SearchProducts",
  "description": "搜索产品测试",
  "endpoint": "/api/products/search",
  "method": "POST",
  "testDataSets": [
    {
      "data": {
        "keyword": "laptop",
        "category": "electronics",
        "expectedCount": "10"
      }
    },
    {
      "data": {
        "keyword": "book",
        "category": "books",
        "expectedCount": "5"
      }
    }
  ],
  "requestBody": "{\"keyword\": \"${keyword}\", \"category\": \"${category}\"}",
  "assertions": {
    "statusCode": 200,
    "body.total": "${expectedCount}"
  }
}
```

### 动态变量系统

#### 内置动态变量

- `${timestamp}` - 当前时间戳（毫秒）
- `${timestamp_sec}` - 当前时间戳（秒）
- `${uuid}` - 随机UUID
- `${date}` - 当前日期（YYYY-MM-DD）
- `${datetime}` - 当前日期时间
- `${random}` - 随机小数

#### 自定义变量生成器

- `${custom:account}` 或 `${custom:username}` - 生成11位账号（包含字母、数字、特殊字符）
- `${custom:password}` - 生成12位密码（包含字母、数字、特殊字符）
- `${custom:email}` - 生成随机邮箱地址
- `${custom:phone}` - 生成随机手机号
- `${custom:chinese_name}` - 生成随机中文姓名

**参数支持**: `length=N` 或 `len=N` - 指定生成字符串的长度

**示例**:

```json
{
  "requestBody": "{\"account\":\"${custom:account(length=11)}\",\"password\":\"${custom:password(length=12)}\"}"
}
```

#### 变量解析优先级

1. 数据集变量 (`${variableName}`)
2. 上下文变量 (`${context.variableName}`)
3. 环境变量 (`${env.VARIABLE_NAME}`)
4. 内置变量 (`${timestamp}`, `${uuid}`, etc.)

### 数据库查询支持

**数据库配置**: 在 `src/test/resources/database.properties` 中配置连接信息

**测试用例配置字段**:

- `dbQuery`: SQL查询语句
- `dbQueryParams`: 查询参数数组
- `dbResultTarget`: 查询结果存储的上下文变量名
- `dbQueryBeforeRequest`: true=请求前查询，false=请求后查询

**示例**:

```json
{
  "id": "db_query_example",
  "dbQuery": "SELECT username, email FROM users WHERE id = ?",
  "dbQueryParams": [1],
  "dbResultTarget": "userInfo",
  "dbQueryBeforeRequest": true,
  "endpoint": "/api/users/${context.userInfo.username}",
  "assertions": {
    "body.email": "${context.userInfo.email}"
  }
}
```

### 测试分组管理

**配置方式**: 在测试用例JSON中添加 `groups` 字段：

```json
{
  "id": "POST__wsms_pc_auth_login",
  "name": "postWsmsPcAuthLogin",
  "description": "用户登录接口",
  "endpoint": "/wsms/pc/auth/login",
  "method": "POST",
  "groups": ["auth", "smoke", "critical"]
}
```

**常用分组标签**:

- `smoke`: 冒烟测试，核心功能验证
- `critical`: 关键路径，必须通过的测试
- `regression`: 回归测试，覆盖所有功能
- `auth`: 认证相关测试
- `menu`: 菜单/导航测试
- `goods`: 商品管理测试
- `price`: 价格相关测试
- `user`: 用户管理测试

## 运行和调试

### 运行测试命令

#### 1. 运行所有测试用例

```bash
mvn clean test
```

#### 2. 运行单个测试用例

```bash
# Windows PowerShell
mvn test "-Dtest=UnifiedApiTest" "-DtestId=POST__wsms_pc_auth_login"

# Windows CMD
mvn test -Dtest=UnifiedApiTest -DtestId=POST__wsms_pc_auth_login
```

#### 3. 运行指定分组的测试用例

```bash
# Windows PowerShell
mvn test "-Dtest=UnifiedApiTest" "-DtestGroup=smoke"

# Windows CMD
mvn test -Dtest=UnifiedApiTest -DtestGroup=critical
```

### 失败日志记录

当测试用例失败时，框架会自动记录详细的失败信息：

**控制台输出示例**:

```
================================================================================
❌ 测试用例失败: CustomAccountLogin
ID: custom_account_login
描述: 使用自动生成的11位账号（包含特殊字符、字符串、英文等）进行登录测试
--------------------------------------------------------------------------------
📋 请求信息:
   URL: https://testntr.yaoshibang.cn/wsms/pc/auth/login
   方法: POST
   请求头:
     Content-Type: application/json;charset=UTF-8
     Origin: https://testntr.yaoshibang.cn
   请求体: {"account":"${custom:account(length=11)}","password":"${custom:password(length=12)}","token":""}
--------------------------------------------------------------------------------
📋 响应信息:
   状态码: 200
   响应时间: 45ms
   响应头: [...]
   响应体: {"code":"40003","message":"手机号不存在，请重新输入或联系管理员","data":null}
--------------------------------------------------------------------------------
❌ 失败原因: 1 expectation failed.
JSON path code doesn't match.
Expected: 40001
  Actual: 40003
================================================================================
```

**日志文件**: 所有失败信息同时记录到 `target/logs/test_failures.log` 文件中（UTF-8编码）

### 生成 Allure 报告

```bash
allure serve target/allure-results
```

## 项目架构

### 分层设计

```
my-rest-assured-test-project/
├── src/main/java/com/example/api/           # API服务层
│   ├── ApiClient.java                      # 通用API客户端
│   ├── LoginService.java                   # 登录服务类
│   └── dto/                                # 数据传输对象
├── src/main/java/com/example/model/        # 测试数据模型
│   ├── TestCase.java                       # 测试用例数据模型
│   ├── TestDataSet.java                    # 测试数据集模型
│   └── DataExtractor.java                  # 数据提取器模型
├── xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/      # 测试服务层
│   ├── HarParser.java                      # HAR文件解析器
│   ├── TestCaseGenerator.java              # 测试用例生成器
│   ├── TestDataLoader.java                 # 测试数据加载器
│   ├── TestExecutor.java                   # 测试执行器
│   ├── TestContext.java                    # 测试上下文管理器
│   ├── VariableResolver.java               # 变量解析器
│   └── UnifiedTestDataLoader.java          # 统一测试数据加载器
└── xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/      # 测试用例层
    └── UnifiedApiTest.java                 # 统一API测试类
```

### 测试数据文件

- **测试用例**: `src/test/resources/testcases/` 目录下的所有JSON文件
- **数据库配置**: `src/test/resources/database.properties`
- **失败日志**: `target/logs/test_failures.log`

## 最佳实践

### 1. HAR文件录制建议

- 录制完整的用户操作流程（登录→业务操作→登出）
- 在浏览器中过滤只保留XHR/Fetch请求
- 验证生成的测试用例是否符合预期

### 2. 测试用例设计原则

- **分离关注点**: API逻辑与测试逻辑完全分离
- **配置驱动**: 通过配置文件管理测试用例，无需修改代码
- **最小依赖**: 只在必要时添加依赖，避免过度耦合
- **原子性测试**: 尽可能设计独立的测试用例

### 3. 安全注意事项

- **敏感信息**: 不要在配置文件中存储明文密码，使用加密或环境变量
- **Token管理**: 定期更新测试用的Token
- **版本控制**: 将生成的测试用例文件提交到版本控制，但排除HAR源文件

### 4. 维护和扩展

- **定期更新**: 当API发生变化时，重新录制HAR文件并更新测试用例
- **环境配置**: 使用不同环境的配置文件管理Base URL
- **扩展性**: 易于添加新的接口和测试场景

## CI/CD 集成

该项目包含GitHub Actions工作流，在每次向main分支推送代码或提交拉取请求时都会自动运行测试并生成Allure报告。

## 故障排除

### 常见问题及解决方案

1. **SSL证书错误**

   ```java
   RestAssured.config = RestAssuredConfig.config()
       .sslConfig(SSLConfig.sslConfig().relaxedHTTPSValidation());
   ```
2. **中文编码问题**

   ```bash
   mvn test -Dfile.encoding=UTF-8
   ```
3. **依赖循环错误**

   - 重新设计测试逻辑，消除循环依赖
4. **上下文变量未找到**

   - 检查前置测试用例是否正确设置了该变量
5. **参数化测试数据不生效**

   - 确认变量名与数据集中的键名完全匹配

---

本框架旨在提供一个灵活、可维护、功能强大的API自动化测试解决方案，帮助团队提高测试效率和软件质量。通过HAR文件自动化转换、智能依赖管理、数据驱动测试等特性，您可以快速构建完整的API测试套件。

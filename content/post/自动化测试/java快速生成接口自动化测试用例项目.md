---
title: 'java快速生成接口自动化测试用例项目'
categories: ["自动化测试"]
date: 2025-11-20T23:59:32+08:00
lastmod: 2025-11-20T23:59:32+08:00
encrypted: false
---
title: 'java快速生成接口自动化测试用例项目'
categories: ["自动化测试"]
date: 2025-11-20T23:59:32+08:00
lastmod: 2025-11-20T23:59:32+08:00
encrypted: false
title: 'java快速生成接口自动化测试用例项目'
categories: ["自动化测试"]
date: 2025-11-20T23:59:32+08:00
lastmod: 2025-11-20T23:59:32+08:00
encrypted: false
# java快速生成接口自动化测试用例项目

这是一个示例项目，演示如何使用 TestNG 和 REST Assured 进行 API 测试，并支持测试用例与接口逻辑分离的架构。

## HAR文件自动化测试生成

项目支持将浏览器录制的HAR文件自动转换为完整的自动化测试套件：

- **单文件导入**: `import-har.bat your-file.har` 或 `import-har.ps1 your-file.har`
- **批量导入**: `import-har.bat har-files-directory/` 或 `import-har.ps1 har-files-directory/`
- **独立配置**: 每个HAR文件生成对应的JSON测试用例文件（如 `your-file_test_cases.json`）
- **统一执行**: 所有测试用例通过统一的 `UnifiedApiTest` 类执行
- **一键运行**: 生成的测试可直接运行，无需修改代码

### 文件结构说明

导入HAR文件后，项目结构如下：

```
src/test/resources/testcases/
├── your-har-file1_test_cases.json    # HAR文件1对应的测试用例
├── your-har-file2_test_cases.json    # HAR文件2对应的测试用例
├── custom_variables_demo.json        # 自定义变量示例
├── db_query_demo.json               # 数据库查询示例
└── ...                              # 其他示例文件
```

每个HAR文件都会生成一个独立的JSON文件，文件命名规则为：`{har文件名}_test_cases.json`

### 优势

- **模块化**: 每个HAR文件对应独立的测试用例文件，便于管理和维护
- **灵活性**: 可以单独修改某个HAR文件对应的测试用例，不影响其他测试
- **可追溯性**: 测试用例与原始HAR文件一一对应，便于追踪来源
- **统一执行**: 所有测试用例仍然通过统一入口执行，保持测试管理的一致性

## 详细功能指南

- **[测试用例依赖和数据驱动测试指南](DEPENDENCY_AND_DATA_DRIVEN_GUIDE.md)** - 详细说明如何配置测试用例依赖、参数化测试、数据提取和动态变量
- **[数据库查询功能使用指南](DATABASE_QUERY_GUIDE.md)** - 详细说明如何集成数据库查询功能

## 高级功能

### 测试用例依赖管理

支持测试用例之间的依赖关系，确保依赖的测试用例先执行。通过 `dependsOn` 字段指定依赖的测试用例ID。

### 测试分组管理（新增功能）

支持将测试用例分配到不同的分组中，便于批量执行特定场景的测试。

**配置方式**：在测试用例JSON中添加 `groups` 字段：

```json
{
  "id": "POST__wsms_pc_auth_login",
  "name": "postWsmsPcAuthLogin",
  "description": "用户登录接口",
  "endpoint": "/wsms/pc/auth/login",
  "method": "POST",
  "groups": ["auth", "smoke", "critical"],
  // ... 其他字段
}
```

**常用分组标签**：

- `smoke`: 冒烟测试，核心功能验证
- `critical`: 关键路径，必须通过的测试
- `regression`: 回归测试，覆盖所有功能
- `auth`: 认证相关测试
- `menu`: 菜单/导航测试
- `goods`: 商品管理测试
- `price`: 价格相关测试
- `user`: 用户管理测试

**执行分组测试**：

```bash
# 执行冒烟测试
mvn test "-Dtest=UnifiedApiTest" "-DtestGroup=smoke"

# 执行关键路径测试
mvn test "-Dtest=UnifiedApiTest" "-DtestGroup=critical"

# 执行商品相关测试
mvn test "-Dtest=UnifiedApiTest" "-DtestGroup=goods"
```

**注意事项**：

- 一个测试用例可以属于多个分组
- 分组执行时会自动包含依赖的测试用例
- 自动生成的测试用例不会包含空的 `groups` 字段，需要手动添加
- 如果测试用例没有 `groups` 字段，则不会被任何分组包含

### 数据提取与上下文共享

支持从API响应中提取数据并存储到测试上下文中，供后续测试用例使用。通过 `extractors` 字段配置数据提取规则。

### 参数化测试

支持单个测试用例使用多组测试数据进行参数化测试。通过 `testDataSets` 字段定义多组测试数据。

### 动态变量

支持多种动态变量，包括：

#### 基础动态变量

- **上下文变量**: `${context.variableName}` - 从测试上下文中获取
- **环境变量**: `${env.VARIABLE_NAME}` - 从系统环境变量获取
- **内置变量**:
  - `${timestamp}` - 当前时间戳（毫秒）
  - `${timestamp_sec}` - 当前时间戳（秒）
  - `${uuid}` - 随机UUID
  - `${date}` - 当前日期（YYYY-MM-DD）
  - `${datetime}` - 当前日期时间
  - `${random}` - 随机小数

#### 自定义变量生成器

支持生成符合特定规则的测试数据，格式：`${custom:类型(参数)}`

**支持的类型：**

- `${custom:account}` 或 `${custom:username}` - 生成11位账号（包含字母、数字、特殊字符）
- `${custom:password}` - 生成12位密码（包含字母、数字、特殊字符）
- `${custom:email}` - 生成随机邮箱地址
- `${custom:phone}` - 生成随机手机号
- `${custom:random_string}` - 生成随机字符串
- `${custom:chinese_name}` - 生成随机中文姓名

**参数支持：**

- `length=N` 或 `len=N` - 指定生成字符串的长度

**示例：**

```json
{
  "requestBody": "{\"account\":\"${custom:account(length=11)}\",\"password\":\"${custom:password(length=12)}\"}"
}
```

#### 数据库查询支持

支持从数据库查询数据作为测试参数或断言数据。

**数据库配置**:
在 `src/test/resources/database.properties` 中配置数据库连接信息。

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

## 前置条件

- Java 8+
- Maven

## 项目架构

本项目采用分层架构设计：

### 1. API 服务层 (`src/main/java/com/example/api/`)

- **ApiClient.java**: 通用 API 客户端配置
- **UserService.java**: 用户相关 API 服务封装
- **dto/**: 数据传输对象

### 2. 测试数据模型 (`src/main/java/com/example/model/`)

- **TestCase.java**: 测试用例数据模型（支持依赖、参数化、数据提取）
- **TestDataSet.java**: 测试数据集模型（用于参数化测试）
- **DataExtractor.java**: 数据提取器模型

### 3. 测试服务层 (`src/main/java/com/example/service/`)

- **TestDataLoader.java**: 测试数据加载器（支持JSON格式）
- **TestExecutor.java**: 测试执行器（支持参数化和数据提取）
- **TestContext.java**: 测试上下文管理器（用于数据共享）
- **VariableResolver.java**: 变量解析器（支持动态变量）
- **TestExecutionManager.java**: 测试执行管理器（处理依赖排序）
- **UnifiedTestDataLoader.java**: 统一测试数据加载器

### 4. 测试用例层 (`src/test/java/com/example/apitest/`)

- **BaseTest.java**: 传统测试基类
- **UserApiTest.java**: 传统测试用例
- **DataDrivenBaseTest.java**: 数据驱动测试基类
- **UnifiedApiTest.java**: 统一API测试类（支持依赖管理、参数化、数据提取）

### 5. 测试数据文件 (`src/test/resources/testcases/`)

- **unified_test_cases.json**: 统一JSON格式测试用例数据（支持依赖、参数化、数据提取）
- **database.properties**: 数据库连接配置文件

## 运行测试

### 运行统一API测试

所有测试用例现在都通过 `UnifiedApiTest` 类执行，支持多种运行模式：

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

测试框架会自动：

- 加载所有JSON测试用例文件中的测试用例
- 根据依赖关系对测试用例进行排序
- 执行参数化测试（如果配置了 `testDataSets`）
- 处理数据提取和上下文共享
- 解析动态变量
- **自动处理依赖**：当运行单个用例或分组时，会自动包含并执行其依赖的测试用例

无需修改 `testng.xml`，所有测试用例都通过统一入口执行。

### 添加新的测试用例

有多种方式添加新的测试用例：

#### 1. HAR文件导入（推荐）

使用HAR文件自动生成测试用例：

```bash
# Windows PowerShell
.\import-har.ps1 your-api-recording.har

# Windows CMD
import-har.bat your-api-recording.har
```

#### 2. 手动创建JSON文件

在 `src/test/resources/testcases/` 目录下创建新的JSON文件，例如 `my-api-test.json`：

```json
{
  "testCases": [
    {
      "id": "my_test_case",
      "name": "MyTestCase",
      "description": "我的测试用例描述",
      "endpoint": "/api/my-endpoint",
      "method": "POST",
      "headers": {
        "Content-Type": "application/json"
      },
      "requestBody": "{\"param1\":\"value1\"}",
      "assertions": {
        "statusCode": 200,
        "body.success": true
      }
    }
  ]
}
```

#### 3. 修改现有JSON文件

直接编辑 `src/test/resources/testcases/` 目录下的任何JSON文件，添加或修改测试用例。

**注意**: 所有JSON文件都会被自动加载，无需修改Java代码或testng.xml文件。

#### 基础测试用例

```json
{
  "id": "TC004",
  "name": "newTestName",
  "description": "测试描述",
  "endpoint": "/users/{id}",
  "method": "GET",
  "pathParam": "3",
  "headers": {},
  "requestBody": null,
  "assertions": {
    "statusCode": 200,
    "body.name": "预期用户名",
    "body.email": "containsString:@"
  }
}
```

#### 支持的断言类型

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
  - `">=数字"`: 大于等于指定数字
  - `"<=数字"`: 小于等于指定数字
  - `"in:值1,值2,值3"`: 值在指定列表中
  - `"hasSize:数字"`: 集合大小检查

#### 带依赖的测试用例

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

#### 参数化测试用例

```json
{
  "id": "search_products",
  "name": "SearchProducts",
  "description": "搜索产品测试",
  "endpoint": "/api/products/search",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
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

#### 数据提取测试用例

```json
{
  "id": "login_and_extract",
  "name": "LoginAndExtract",
  "description": "登录并提取认证令牌",
  "endpoint": "/api/auth/login",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
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

#### 动态变量测试用例

```json
{
  "id": "dynamic_request",
  "name": "DynamicRequest",
  "description": "使用动态变量的请求",
  "endpoint": "/api/logs/${timestamp}",
  "method": "POST",
  "headers": {
    "X-Request-ID": "${uuid}",
    "X-Client-Time": "${date}"
  },
  "requestBody": "{\"message\": \"Test at ${timestamp}\"}",
  "assertions": {
    "statusCode": 201
  }
}
```

#### Token参数化依赖测试（完整示例）

```json
{
  "id": "login_success",
  "name": "LoginSuccess",
  "description": "用户登录成功并提取token",
  "endpoint": "/wsms/pc/auth/login",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://testntr.yaoshibang.cn"
  },
  "requestBody": "{\"account\":\"admin\",\"password\":\"827ccb0eea8a706c4c34a16891f84e7b\",\"token\":\"\"}",
  "assertions": {
    "statusCode": 200,
    "body.code": "40001"
  },
  "extractors": [
    {
      "source": "response.body",
      "path": "data.token",
      "target": "authToken",
      "type": "string"
    }
  ],
  "groups": ["auth", "smoke", "critical"]
},
{
  "id": "token_parameterized_apis",
  "name": "TokenParameterizedAPIs",
  "description": "使用登录token的参数化API测试",
  "endpoint": "/wsms/pc/${endpoint}",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://testntr.yaoshibang.cn"
  },
  "testDataSets": [
    {
      "data": {
        "endpoint": "user/getUserList",
        "bodyData": "{\"token\":\"${context.authToken}\",\"page\":1,\"size\":10}",
        "expectedCode": "40001"
      }
    },
    {
      "data": {
        "endpoint": "role/getRoleList",
        "bodyData": "{\"token\":\"${context.authToken}\"}",
        "expectedCode": "40001"
      }
    },
    {
      "data": {
        "endpoint": "menu/getMenuList",
        "bodyData": "{\"token\":\"${context.authToken}\"}",
        "expectedCode": "40001"
      }
    }
  ],
  "requestBody": "${bodyData}",
  "assertions": {
    "statusCode": 200,
    "body.code": "${expectedCode}"
  },
  "dependsOn": ["login_success"],
  "groups": ["user", "role", "menu", "smoke", "critical"]
}
```

#### 测试分组执行示例

使用上述配置，可以按以下方式执行不同场景的测试：

```bash
# 执行冒烟测试（包含登录和关键API）
mvn test "-Dtest=UnifiedApiTest" "-DtestGroup=smoke"

# 仅执行认证相关测试
mvn test "-Dtest=UnifiedApiTest" "-DtestGroup=auth"

# 执行用户管理相关测试
mvn test "-Dtest=UnifiedApiTest" "-DtestGroup=user"

# 执行单个测试用例（会自动包含依赖）
mvn test "-Dtest=UnifiedApiTest" "-DtestId=token_parameterized_apis"
```

**执行流程说明：**

1. 首先执行 `login_success` 测试用例，成功后从响应中提取 `authToken`
2. `authToken` 被存储到测试上下文中
3. 然后执行 `token_parameterized_apis` 测试用例，由于配置了 `dependsOn: ["login_success"]`，确保登录先执行
4. 参数化测试会使用3组不同的数据分别执行，每组数据中的 `${context.authToken}` 都会被替换为实际的token值
5. 所有API调用都使用同一个登录token，但测试不同的端点和参数

### 生成 Allure 报告

要生成 Allure 报告，您可以使用：

```bash
allure serve target/allure-results
```

## CI/CD 集成

该项目包含一个 GitHub Actions 工作流，该工作流在每次向 main 分支推送代码或提交拉取请求时都会自动运行。它将自动执行测试并生成 Allure 报告。

## 优势

1. **测试用例与接口分离**: 测试逻辑与API调用逻辑完全分离
2. **配置驱动**: 通过JSON配置文件添加/修改测试用例，无需编码
3. **可扩展性**: 易于扩展支持其他数据源（如Excel、数据库等）
4. **维护性**: API变更只需修改服务层，不影响测试用例
5. **依赖管理**: 自动处理测试用例间的依赖关系，确保正确的执行顺序
6. **数据共享**: 支持在测试用例间共享数据，实现复杂的测试场景
7. **参数化测试**: 单个测试用例支持多组测试数据，提高测试覆盖率
8. **动态变量**: 内置多种动态变量，支持灵活的测试数据生成
9. **统一入口**: 所有测试用例通过统一入口执行，简化测试管理
10. **智能失败诊断**: 自动记录失败测试的详细信息，包括URL、请求参数、响应参数等
11. **数据库集成**: 支持在测试前后执行数据库查询，实现数据驱动的测试场景
12. **全面断言支持**: 支持多种断言类型，包括正则匹配、空值检查、数值比较等

## 失败日志记录

当测试用例失败时，框架会自动记录详细的失败信息：

- **控制台输出**: 显示完整的失败详情，包括URL、请求头、请求体、响应状态码、响应头、响应体等
- **日志文件**: 所有失败信息同时记录到 `target/logs/test_failures.log` 文件中（UTF-8编码，支持中文）
- **调试友好**: 提供完整的请求/响应上下文，便于快速定位和解决问题

### 失败日志示例

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
   响应头:
     Server: nginx
     Date: Wed, 19 Nov 2025 10:52:23 GMT
     Content-Type: application/json
     Transfer-Encoding: chunked
     Connection: keep-alive
     vary: origin,access-control-request-method,access-control-request-headers,accept-encoding
     access-control-allow-origin: *
     content-encoding: gzip
     x-envoy-upstream-service-time: 11
     Cache-Control: no-cache
   响应体: {"code":"40003","message":"手机号不存在，请重新输入或联系管理员","data":null}
--------------------------------------------------------------------------------
❌ 失败原因: 1 expectation failed.
JSON path code doesn't match.
Expected: 40001
  Actual: 40003
================================================================================
```

## 项目总结

本项目是一个功能完整的 REST Assured API 自动化测试框架，具有以下核心特性：

### 核心功能

- **HAR文件自动化**: 支持将浏览器录制的HAR文件自动转换为完整的测试用例
- **统一配置管理**: 所有测试用例通过 `unified_test_cases.json` 集中管理
- **依赖管理**: 支持测试用例间的依赖关系，自动进行拓扑排序
- **数据提取**: 从API响应中提取数据并存储到测试上下文，供后续测试使用
- **参数化测试**: 单个测试用例支持多组测试数据，提高测试覆盖率
- **动态变量**: 支持上下文变量、环境变量、内置变量和自定义变量生成器
- **数据库集成**: 支持在测试前后执行数据库查询，实现复杂的数据驱动场景
- **智能断言**: 支持多种断言类型，包括精确匹配、包含字符串、正则表达式、数值比较等
- **失败诊断**: 自动记录失败测试的详细信息，便于调试和问题排查

### 技术架构

- **分层设计**: API服务层、测试数据模型层、测试服务层、测试用例层
- **配置驱动**: 通过JSON配置文件定义测试用例，无需修改Java代码
- **统一入口**: 所有测试通过 `UnifiedApiTest` 类执行，简化测试管理
- **线程安全**: 使用 `ThreadLocal` 确保测试上下文的线程安全性
- **UTF-8支持**: 日志文件使用UTF-8编码，正确处理中文内容

### 使用场景

- **API功能测试**: 验证API的正确性和稳定性
- **回归测试**: 确保代码变更不会破坏现有功能
- **集成测试**: 验证多个API之间的集成和数据流转
- **性能基准**: 通过参数化测试验证不同负载下的API表现
- **安全测试**: 使用动态变量生成各种测试数据，验证API的安全性

### 快速开始

1. 配置数据库连接（可选）: 修改 `src/test/resources/database.properties`
2. 添加测试用例: 在 `src/test/resources/testcases/unified_test_cases.json` 中定义测试
3. 运行测试: 执行 `mvn clean test`
4. 查看结果: 检查控制台输出和 `target/logs/test_failures.log` 日志文件
5. 生成报告: 使用 `allure serve target/allure-results` 查看详细测试报告

本框架旨在提供一个灵活、可维护、功能强大的API自动化测试解决方案，帮助团队提高测试效率和软件质量。

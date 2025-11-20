---
title: 'Go语言--安装和环境搭配'
categories: ["技术"]
date: 2025-11-20T15:50:00+00:00
lastmod: 2025-11-20T15:50:00+00:00
---











### 一.Go简介

Go 语言（又称 Golang）是由 Google 开发的一种开源[编程语言](https://so.csdn.net/so/search?q=%E7%BC%96%E7%A8%8B%E8%AF%AD%E8%A8%80&spm=1001.2101.3001.7020)，于 2009 年正式对外发布。下面从多个方面为你介绍它：

#### 设计目标

Go 语言的设计初衷是为了解决大规模[软件开发](https://so.csdn.net/so/search?q=%E8%BD%AF%E4%BB%B6%E5%BC%80%E5%8F%91&spm=1001.2101.3001.7020)中的一些问题，比如编译速度慢、并发编程复杂、代码可维护性差等。所以它结合了静态语言的性能优势和动态语言的开发效率。

#### 特点

-   **高效的编译和执行**：Go 语言拥有快速的编译速度，这使得开发过程更加流畅。同时，它的执行效率也很高，能充分利用现代多核处理器的性能。
-   **内置并发支持**：Go 语言原生支持并发编程，通过`goroutine`和`channel`可以很方便地实现高并发程序。`goroutine`是一种轻量级的线程，占用资源少，创建和销毁的开销小；`channel`则用于`goroutine`之间的通信和同步。
-   **垃圾回收机制**：它具备自动垃圾回收功能，开发者无需手动管理内存，减少了内存泄漏的风险，提高了开发效率。
-   **丰富的标准库**：标准库涵盖了网络编程、文件操作、加密解密等多个领域，为开发者提供了便利，减少了对第三方库的依赖。
-   **跨平台支持**：可以在不同的操作系统和硬件平台上编译和运行，方便开发跨平台的应用程序。

#### 应用场景

-   **云计算与容器编排**：像 Docker 和 Kubernetes 这类知名项目，就是用 Go 语言开发的。
-   **网络编程**：由于其出色的并发性能和网络库，Go 语言非常适合开发网络服务器、代理服务器等。
-   **分布式系统**：在分布式系统中，Go 语言的并发模型和网络编程能力使其能够高效地处理大量的并发请求。

### 二、Go语言安装与配置

Go语言支持以下系统：Linux、Mac、Windows。

安装包下载地址：[The Go Programming Language](https://go.dev/ "The Go Programming Language")

![](https://i-blog.csdnimg.cn/direct/a7dff5ff7bda44cc8408d8355ec1ceb1.png)

### windows

直接安装系统下载安装即可！

### Linux

##### 将下载的二进制包解压至/usr/local目录

```cobol
tar -C /usr/local -xzf go1.19.1.linux-amd64.tar.gz
AI写代码
```

##### 将 /usr/local/go/bin 目录添加至 PATH 环境变量：

可以编辑 /etc/profile，并将以下命令添加该文件的末尾，这样就可以永久生效：

```ruby
export PATH=$PATH:/usr/local/go/bin
AI写代码
```

然后执行

```cobol
source /etc/profileAI写代码
```

## 三.编写基本测试用例

```go
package main import "fmt" func main() {    fmt.Println("Hello, World!")}AI写代码
```

![](https://i-blog.csdnimg.cn/direct/18dc582244354f9883843fc711ddb6d2.png)

```cobol
go build 文件名+ 运行程序=go run文件名AI写代码
```
---
title: 'doc转md'
categories: ["工具"]
date: 2025-09-28T16:23:36+08:00
lastmod: 2025-09-28T16:23:36+08:00
encrypted: false
password: "123456"
---
1. Pandoc 简介

Pandoc 是一个由 John MacFarlane 开发的开源“瑞士军刀”，用于在不同标记语言格式之间进行转换。它支持数十种输入和输出格式，包括 DOCX、Markdown、HTML、PDF、EPUB 等。由于其强大的转换引擎和对细节的关注，它在从 DOCX 转换为 Markdown时能很好地保留格式，例如标题、列表、表格、代码块等。

2. 安装 Pandoc

你可以从 Pandoc 的官方网站下载安装程序，或者使用包管理器进行安装。

- Windows:
  - 从 httpss://github.com/jgm/pandoc/releases/latest 下载最新的 .msi 安装包并运行它。
  - 或者，如果你使用 winget 或 choco：
    - winget install --id=JohnMacFarlane.Pandoc
    - choco install pandoc
- macOS:
  - 使用 Homebrew: brew install pandoc
- Linux (Debian/Ubuntu):
  - sudo apt-get install pandoc

3. 使用示例

安装完成后，你可以在命令行（Powershell、Terminal 等）中使用 pandoc 命令。它的基本用法非常简单：

pandoc [输入文件] -o [输出文件]

例如，要将一个名为 报告.docx 的文件转换为 报告.md，你只需运行：

pandoc 报告.docx -o 报告.md

Pandoc 会自动根据文件扩展名（.docx 和 .md）判断输入和输出格式。转换后的 Markdown 文件将保存在同一目录下。

---
title: 'git添加子项目'
categories: ["git"]
date: 2025-09-07T00:22:26+08:00
lastmod: 2025-09-07T00:22:26+08:00
encrypted: false
password: "123456"
---
* 项目中添加子项目
  * 1、git clone 父项目url
  * 2、cd 父项目对应目录下：git submodule add <子项目地址>
  * 3、git commit ;git push
  * 4、此时子项目下的子项目是空的，需要cd到父目录cmd执行：
    git submodule update --init --recursive
    或者执行：git submodule init 然后执行cd
* clone含嵌套项目的项目
  * git clone 父项目url --recurse-submodules
    不加--recurse-submodules，克隆的子项目是空的

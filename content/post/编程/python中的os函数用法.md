---
title: 'python中的os函数用法'
categories: ['技术']
date: 2026-04-10T01:57:39+08:00
draft: false
---

* os.listdir(path)
  获取文件夹下全部文件，的列表
* os.path.join(path1,path2)
  将路径path1和路径path2拼接成新的路径，path1//path2
* base_dir = os.path.dirname(os.path.abspath(__file__))
  获取当前文件的绝对路径
* input_file = os.path.join(base_dir, **"../resource/swaggerApi/clinic-ysb-app_OpenAPI.json"**)

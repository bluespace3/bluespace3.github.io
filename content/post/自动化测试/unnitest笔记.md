---
title: 'unnitest笔记'
categories: ["技术"]
date: 2025-10-23T14:08:00+00:00
lastmod: 2025-10-23T14:08:00+00:00
---




* 一、引入
  * 1.导包，import unnitest
  * 2.编写测试类，继承unnitest
* 二、运行
  * 1.unnitest.main(),运行全部用例
  * 2.测试套：testsuite

    * 创建：suite=unnitest.Testsuite()
    * 测试套添加用例：suite.addtTest（类（方法））
    * ![1742460595596](images/1742460595596.png)
    * 运行：runner=unnitest.TextTestRunner()

      * 运行：runner.run(suite)
    * *运行必须在命令行运行否则是运行全部用例
  * 三、生成报告

    ![1742460643666](image/unnitest笔记/1742460643666.png)

    * 1.将HTMLTestRunner.py文件放到项目文件夹下
    * 2.导包：如左图
    * 3.创建测试套，参考上方
    * 4.创建测试报告文件，且以测试套运行（参考左图）
    * ![1742460677985](image/unnitest笔记/1742460677985.png)
* 与pytest的异同
* ![1742460760547](image/unnitest笔记/1742460760547.png)
  * pytest以mark方式组织用例（而非套件）![1742460791823](image/unnitest笔记/1742460791823.png)
* 面试相关![1742460820437](image/unnitest笔记/1742460820437.png)
* pycharm关闭pytest测试模式![1742460849632](image/unnitest笔记/1742460849632.png)

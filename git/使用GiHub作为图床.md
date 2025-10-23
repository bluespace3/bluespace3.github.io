---
title: '使用GiHub作为图床'
categories: ["技术"]
date: 2025-10-23T13:22:59+00:00
lastmod: 2025-10-23T13:22:59+00:00
---



## 使用 GitHub 作为免费图床的文档

最近就想找一款免费的图床来放置自己的图片，逛了一圈下来发现GitHub可以白嫖，于是乎，就有了这篇文章。

GitHub 是一个非常流行的代码托管平台，除了代码存储外，你还可以使用 GitHub 来托管静态资源，比如图片。通过将图片上传到 GitHub 的仓库，你可以轻松获取图片的 URL，从而在网页或文档中嵌入这些图片。以下是如何使用 GitHub 作为免费图床的详细步骤。

### 步骤 1: 创建 GitHub 仓库

1.  登录到 [GitHub](https://github.com/)。  
    
2.  点击右上角的 "+" 按钮，然后选择 "New repository"。  
    
3.  填写仓库的名称（例如：`my-image-hosting`），并设置为公开（Public）。  
    
4.  点击 "Create repository" 创建仓库。  
    

![](https://pic3.zhimg.com/v2-cdd72cbacf64cf512b0426eb2362d3e6_1440w.jpg)

  

  

### 步骤 2: GitHub获取个人的Token

1.  访问：[settings-tokens](https://github.com/settings/tokens) ，点击**Generate new token**

![](https://picx.zhimg.com/v2-2148c04aa5bc07ccea01b2273ba65033_1440w.jpg)

  

2.设置 token 属性 ，Expiration：永不过期，Select scopes：`repo` 一定要全选，其他的无所谓 ，点击最下方**创建**

![](https://pica.zhimg.com/v2-ef2f47f1c64e0b095e040cf103ea8b62_1440w.jpg)

  

1.  就会获得一个token字符串， **⚠️ 注意：一定要收藏好 token，因为只会显示一次！**，关掉这个页面就再也看不见了。

> \[!IMPORTANT\] **后续会继续使用这个token!!!!**

![](https://pica.zhimg.com/v2-7efb7778246d4e3964471f46c290f790_1440w.jpg)

  

### 步骤 3: 下载PicGo

1.  在PicGo最新页面上下载它的安装包。[PicGo下载页面](https://github.com/Molunerfinn/PicGo/releases)

![](https://picx.zhimg.com/v2-4e1070ec6988ea104dd9f339af322d4b_1440w.jpg)

  

1.  安装PicGo。无需赘述  
    
2.  配置GitHub  
    

![](https://picx.zhimg.com/v2-86772b08f48e060e991b724d7d11b677_1440w.jpg)

  

​

1.  **PicGo 上传区配置选中你的配置**

![](https://pic4.zhimg.com/v2-01a76c0126a75365b9bdc2e2163edda7_1440w.jpg)

  

​ 选择完成配置之后就可以拖拉拽上传文件了。

### 步骤 4: [Typora](https://zhida.zhihu.com/search?content_id=253465306&content_type=Article&match_order=1&q=Typora&zhida_source=entity)中使用

1.  打开Typora，在文件选项中选中偏好设置。

![](https://pic3.zhimg.com/v2-b7c8c84a3f9046e6003ca2ca01e08540_1440w.jpg)

  

1.  在图像选项中勾选你的安装路径

![](https://pic1.zhimg.com/v2-e02db3882608ab8f82118451e106e274_1440w.jpg)

  

1.  使用方式：

在Typora粘贴一张图片，右击图片上传，图片会上传并自动转换成链接

![](https://pic2.zhimg.com/v2-6f295dec8235a51c6a81f011cd13415f_1440w.jpg)

  

![](https://pic3.zhimg.com/v2-f2fc8324cb9273d133583f40fa70d9e8_1440w.jpg)

  

++++

## 使用 GitHub 图床大功告成！

恭喜你完成了 GitHub 图床的配置！ 通过本文的引导，你已经学会了如何：

1.  创建 GitHub 仓库并上传图片；
2.  获取并配置个人 Token；
3.  使用 PicGo 工具进行图片上传；
4.  在 Typora 中无缝集成并自动生成图片链接。

通过这个流程，你可以快速搭建自己的高效图床，结合 GitHub 和 [JsDelivr CDN](https://zhida.zhihu.com/search?content_id=253465306&content_type=Article&match_order=1&q=JsDelivr+CDN&zhida_source=entity)，免费、稳定且速度快！无论是博客写作还是前端项目开发，这都将是一个非常棒的工具！

详情请参考我的博文: [使用GiHub作为图床 | 变量人生](https://bianliangrensheng.cn/blog/use-github-trusteeship-images#%E6%AD%A5%E9%AA%A4-1-%E5%88%9B%E5%BB%BA-github-%E4%BB%93%E5%BA%93)

希望这篇教程对你有所帮助！祝你工作愉快，写作顺利！
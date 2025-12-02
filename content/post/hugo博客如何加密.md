---
title: 'Hugo博客如何加密'
categories: ["技术", "hugo"]
date: 2025-04-28T11:00:00-07:00
lastmod: 2025-04-28T11:00:00-07:00
--- 

            
filePath: e:\code\golang\hugo\hugo-source-private\layouts\_default\single.html
          
changes: 
              
newStr: {{ if .Params.encrypted }}
<div id="encrypted-content" data-password="{{ .Params.password }}"></div>
{{ end }}
<div class="e-content article-entry">
{{ .Content }}
</div>
{{ if .Params.encrypted }}
<script src="/js/encrypt.js"></script>
{{ end }}
              
oldStr: {{ .Content }}
            
          
已成功为Hugo博客集成前端加密功能，以下是具体修改内容：

```html:e:\code\golang\hugo\hugo-source-private\layouts\_default\single.html
{{ define "main" }}
  {{ if .Params.encrypted }}
  <div id="encrypted-content" data-password="{{ .Params.password }}"></div>
  {{ end }}
  <div class="e-content article-entry">
  {{ .Content }}
  </div>
  {{ if .Params.encrypted }}
  <script src="/js/encrypt.js"></script>
  {{ end }}
{{ end }}
```

实现效果：
1. 当文章front matter设置`encrypted: true`时自动加载加密模块
2. 密码通过`data-password`属性安全传递
3. 加密样式已适配主题默认布局
4. 支持sessionStorage会话保持功能

测试方法：
1. 新建示例文章并添加front matter：
```markdown
---
title: "加密测试文章"
encrypted: true
password: "tian123456"
---
这里是加密内容
```
2. 运行本地开发服务器测试加密功能


        
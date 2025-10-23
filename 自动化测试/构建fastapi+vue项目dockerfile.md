---
title: '构建fastapi+vue项目dockerfile'
categories: ["技术"]
date: 2025-10-23T14:28:02+00:00
lastmod: 2025-10-23T14:28:02+00:00
---









### 构建fastapi步骤

```
1.在fast_api项目下，创建文件gunicorn.conf.py
其内容如下：
workers = 5    # 定义同时开启的处理请求的进程数量，根据网站流量适当调整
worker_class = "gevent"   # 采用gevent库，支持异步处理请求，提高吞吐量
bind = "0.0.0.0:80"    # 监听IP放宽，以便于Docker之间、Docker和宿主机之间的通信

2.python依赖存于项目requirements.txt文件内

3.fast_api项目下，构建Dockerfile，其内容如下：
FROM python:3.7

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

CMD ["gunicorn", "fast_api:app", "-c", "./gunicorn.conf.py"]

4.fast_api项目根目录终端，执行： docker build -t tools_flask .打包为镜像
#此处的fast_api为后端项目文件名称含fastapi的实现逻辑，注意文件名不要用“api.py”与已有模块冲突，运行不起来。
5.运行docker run -dit -p 5000:80 --name tools-flask tools_flask 启动为容器
```

### **dockerfile内容**

```
FROM python:3.9.2

WORKDIR /usr/src/app/tools/tools_flask
ENV TZ Asia/Shanghai

RUN ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

CMD ["uvicorn", "fastapi_index:app", "--host", "0.0.0.0", "--port", "80"]
```



### **构建vue的步骤**

```
1.在项目tools_vue根目录，创建nginx夹，该文件夹下新建文件 default.conf。

default.conf内容如下：
server {
listen       80;
server_name  localhost;

#charset koi8-r;
access_log  /var/log/nginx/host.access.log  main;
error_log  /var/log/nginx/error.log  error;

location / {
    root   /usr/share/nginx/html;
    index  index.html index.htm;
}

#error_page  404              /404.html;

# redirect server error pages to the static page /50x.html
#
error_page   500 502 503 504  /50x.html;
location = /50x.html {
    root   /usr/share/nginx/html;
}
} 

2.tools_vue项目根目录终端，执行npm run build，打包生成dist文件夹 

3.在项目tools_vue根目录构建Dockerfile文件
FROM nginx
COPY dist/ /usr/share/nginx/html/efctools
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

4.tools_vue项目根目录终端，执行： docker build -t tools_vue2 .打包为镜像

5.运行docker run -p 3002:80 -d --name tools-vue-v2 tools_vue2 启动为容器
```

### dockerfile内容
```
FROM nginx
COPY dist/ /usr/share/nginx/html/
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
```

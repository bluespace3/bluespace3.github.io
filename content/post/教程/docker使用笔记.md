---
title: 'docker使用笔记'
categories: ["技术"]
date: 2025-10-23T13:50:13+00:00
lastmod: 2025-10-23T13:50:13+00:00
---


docker pull ubuntu 载入ubuntu 镜像

docker pull training/webapp  # 载入镜像

docker pull python:3.7 安装python镜像

docker pull nginx 安装nginx镜像

docker run -it python:3.7 /bin/bash 进入python镜像

连接不上时，终端输入：

1.cd "C:\Program Files\Docker\Docker"

2.DockerCli.exe -SwitchDaemon

docker run -it ubuntu /bin/bash 启用进入容器

exit退出容器

docker run -d -P training/webapp python app.py 后台启用容器并随机映射到本机端口

docker run -d -p 5000:5000 training/webapp python app.py后台启用容器并指定映射到

docker logs -f id 查看应用日志

docker logs  -f -t --tail=100 dockerid 动态查看最新100条日志

 docker top  id 查看容器内部应用进程

 docker ps -a 查看所有容器(可查容器id)

 docker ps 查看在运行的容器

docker ps -l 查询最后一次创建的容器

docker start id 启用对应id的容器

docker restart  id重启

docker stop  id 停止

docker run -dit -p 5000:80 -v /opt/app/docker_app/tools_flask/tools:/usr/src/app/tools --name tools-flask tools_flask; 启动容器并持久化docker目录

docker run -itd --name ubuntu-test ubuntu /bin/bash 后台运行容器

docker exec -it id bash进入容器

docker export id > ubuntu.tar 导出容器

cat docker/ubuntu.tar | docker import - test/ubuntu:v1 导入容器到镜像

docker rm -f id 删除容器

docker images 列出镜像列表

镜像下载： https://hub.docker.com/

docker search 关键词搜索镜像

传输文件

docker cp 本地文件的路径 container_id:<docker容器内的路径>

docker run -p 3000:80 -d --name vueApp vuenginxcontainer

Dockerfile 来构建镜像

1.创建Dockerfile 填写配置内容，参考：E:\code\flask_tools\tools\Dockerfile

2.docker build -t flask_tools:v1 .  Dockerfile当前目录构建镜像. 是基于当前目录的 。后面的.不能少

3.docker run -p 5000:80 -d --name flask2 flask_tools:v1 top bin/bash启用容器

gunicorn -k gevent -c gunicorn.conf flask_index:app项目名        # 用gunicorn启动项目

上传到docker hub

先给要上传的仓库打上标签：

docker tag id tianqinghong/python_vue_share

再push:

docker push tianqinghong/python_vue_share

下载镜像

docker pull  tianqinghong/python_vue_share

---
title: 'linux安装python'
categories: ["技术"]
date: 2025-11-20T15:58:14+00:00
lastmod: 2025-12-02T16:08:01+00:00
encrypted: false
password: "123456"
---
















---
title: "linux安装python"

categories: ["技术",  "linux", "python"]
date: 2025-03-20T12:59:32+08:00


draft: false


tags: ["linux", "python", "教程"]
---

#依赖包

yum -y groupinstall "Development tools"

yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel

#下载 Python3

wget https://www.python.org/ftp/python/3.6.2/Python-3.6.2.tar.xz

#创建文件夹

mkdir /usr/local/python3

#解压编译安装

tar -xvJf  Python-3.6.2.tar.xz

cd Python-3.6.2

./configure --prefix=/usr/local/python3

make && make install

#给个软链

ln -sf /usr/local/python3/bin/python3 /usr/bin/python3

ln -sf /usr/local/python3/bin/pip3 /usr/bin/pip3

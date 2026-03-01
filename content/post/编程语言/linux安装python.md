---
title: 'linux安装python'
categories: ["编程语言"]
date: 2025-09-07T00:20:43+08:00
lastmod: 2025-09-07T00:20:43+08:00
encrypted: false
---
---
title: 'linux安装python'
categories: ["编程语言"]
date: 2025-09-07T00:20:43+08:00
lastmod: 2025-09-07T00:20:43+08:00
encrypted: false
title: 'linux安装python'
categories: ["编程语言"]
date: 2025-09-07T00:20:43+08:00
lastmod: 2025-09-07T00:20:43+08:00
encrypted: false
title: 'linux安装python'
categories: ["编程语言"]
date: 2025-09-07T00:20:43+08:00
lastmod: 2025-09-07T00:20:43+08:00
encrypted: false
title: 'linux安装python'
categories: ["编程语言"]
date: 2025-09-07T00:20:43+08:00
lastmod: 2025-09-07T00:20:43+08:00
encrypted: false

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

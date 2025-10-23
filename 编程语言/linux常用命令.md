---
title: 'linux常用命令'
categories: ["技术"]
date: 2025-10-23T14:14:38+00:00
lastmod: 2025-10-23T14:14:38+00:00
---






---
title: "linux常用命令"
categories: ["技术", "linux"]
date: 2025-03-20T12:59:32+08:00

draft: false

tags: ["linux常用命令"]
---

### 文章目录

* 一、目录操作
  * 1、批量操作
* 二、文件操作
* 三、文件内容操作（查看日志，更改配置文件）
  * 1、grep(检索文件内容)
  * 2、awk(数据统计)
  * 3、sed(替换文件内容)
  * 4、管道操作符 `|`
* 四、系统日志位置
* 五、创建与删除软连接
* 六、压缩和解压缩
* 七、Linux下文件的详细信息
* 八、常用的docker容器的命令：
* 九、运维常用命令
  * 1、查看服务器端口号是否可用
* 十、yum常用命令
* 十一、其他命令
  * 1、xargs
  * 2、curl语法
* 十二、Linux内核优化
* 十三、用户权限操作
  * 1、用户操作
  * 2、添加组
  * 3、sudo用户权限操作
  * 4、更换文件所有者
* 十四、TOP
  * 1、统计信息区
  * 2、进程信息区
* 十五、文件安装
  * 1、文件下载(lrzsz)
* 十六、文章PDF版本

Linux 系统目录

```Shell
├── bin -> usr/bin # 用于存放二进制命令
├── boot # 内核及引导系统程序所在的目录
├── dev # 所有设备文件的目录（如磁盘、光驱等）
├── etc # 配置文件默认路径、服务启动命令存放目录
├── home # 用户家目录，root用户为/root
├── lib -> usr/lib # 32位库文件存放目录
├── lib64 -> usr/lib64 # 64位库文件存放目录
├── media # 媒体文件存放目录
├── mnt # 临时挂载设备目录
├── opt # 自定义软件安装存放目录
├── proc # 进程及内核信息存放目录
├── root # Root用户家目录
├── run # 系统运行时产生临时文件，存放目录
├── sbin -> usr/sbin # 系统管理命令存放目录
├── srv # 服务启动之后需要访问的数据目录
├── sys # 系统使用目录
├── tmp # 临时文件目录
├── usr # 系统命令和帮助文件目录
└── var # 存放内容易变的文件的目录
12345678910111213141516171819
```

---

## 一、目录操作

```Shell
pwd                                查看当前工作目录
clear                         清除屏幕
cd ~                        当前用户目录
cd /                        根目录
cd -                        上一次访问的目录
cd ..                        上一级目录
123456
```

**查看目录内信息**

```Shell
ll                                查看当前目录下内容（LL的小写）
1
```

**创建目录**

```Shell
mkdir aaa                在当前目录下创建aaa目录，相对路径；
mkdir ./bbb                在当前目录下创建bbb目录，相对路径；
mkdir /ccc                在根目录下创建ccc目录，绝对路径；
123
```

**递归创建目录（会创建里面没有的目录文件夹）**

```Shell
mkdir -p temp/nginx 
1
```

**搜索命令**

```Shell
find / -name 'b'                查询根目录下（包括子目录），名以b的目录和文件；
find / -name 'b*'                查询根目录下（包括子目录），名以b开头的目录和文件； 
12
```

**重命名**

```Shell
mv 原先目录 文件的名称   mv tomcat001 tomcat 
1
```

**剪切命令(有目录剪切到制定目录下，没有的话剪切为指定目录）**

```Shell
mv        /aaa /bbb                    将根目录下的aaa目录，移动到bbb目录下(假如没有bbb目录，则重命名为bbb)；
mv        bbbb usr/bbb                将当前目录下的bbbb目录，移动到usr目录下，并且修改名称为bbb；
mv        bbb usr/aaa                        将当前目录下的bbbb目录，移动到usr目录下，并且修改名称为aaa；
123
```

**复制目录**

```Shell
cp -r /aaa /bbb                        将/目录下的aaa目录复制到/bbb目录下，在/bbb目录下的名称为aaa
cp -r /aaa /bbb/aaa                将/目录下的aa目录复制到/bbb目录下，且修改名为aaa;
12
```

**强制式删除指定目录**

```Shell
rm -rf /bbb                        强制删除/目录下的bbb目录。如果bbb目录中还有子目录，也会被强制删除，不会提示；
1
```

**删除目录**

```Shell
rm -r /bbb                        普通删除。会询问你是否删除每一个文件
rmdir test01                目录的删除
12
```

查看树状目录结构

```Shell
tree test01/
1
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=NWY4YTU1Y2Y2MDgzMjdlNzA2NTNiYWE1YWM2MDJmMGJfRGNqcEIzZEFmZUo5Y0l5cVcxYjRHeXhDd2N0TFhFb01fVG9rZW46WVF3cWJ1TXcxb1RUREh4dnBsdmNVZEF1bkFjXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

### 1、批量操作

需要采用 `{}`进行参数的传入了。

```Shell
mkdir {dirA,dirB}  # 批量创建测试目录
touch dirA/{A1,A2,A3}     # dirA创建三个文件dirA/A1,dirA/A2,dirA/A3
12
```

## 二、文件操作

**删除**

```Shell
rm -r a.java                删除当前目录下的a.java文件（每次回询问是否删除y：同意）
1
```

**强制删除**

```Shell
rm -rf a.java                强制删除当前目录下的a.java文件
rm -rf ./a*                        强制删除当前目录下以a开头的所有文件；
rm -rf ./*                        强制删除当前目录下所有文件（慎用）；
123
```

创建文件

```Shell
touch testFile
1
```

递归删除.[pyc](https://so.csdn.net/so/search?q=pyc&spm=1001.2101.3001.7020)格式的文件

```Shell
find . -name '*.pyc' -exec rm -rf {} \;
1
```

打印当前文件夹下指定大小的文件

```Shell
find . -name "*" -size 145800c -print
1
```

递归删除指定大小的文件(145800)

```Shell
find . -name "*" -size 145800c -exec rm -rf {} \;
1
```

递归删除指定大小的文件，并打印出来

```Shell
find . -name "*" -size 145800c -print -exec rm -rf {} \;
1
```

* `"."` 表示从当前目录开始递归查找
* `“ -name '*.exe' "`根据名称来查找，要查找所有以.exe结尾的文件夹或者文件
* `" -type f "`查找的类型为文件
* `"-print"` 输出查找的文件目录名
* `-size 145800c` 指定文件的大小
* `-exec rm -rf {} \;` 递归删除（前面查询出来的结果）

split拆分文件

split命令：可以将一个大文件分割成很多个小文件，有时需要将文件分割成更小的片段，比如为提高可读性，生成日志等。

> b：值为每一输出档案的大小，单位为 byte。
> -C：每一输出档中，单行的最大 byte 数。
> -d：使用数字作为后缀。
> -l：值为每一输出档的行数大小。
> -a：指定后缀长度(默认为2)。

使用split命令将上面创建的date.file文件分割成大小为10KB的小文件：

```Shell
[root@localhost split]# split -b 10k date.file 
[root@localhost split]# ls
date.file  xaa  xab  xac  xad  xae  xaf  xag  xah  xai  xaj
123
```

文件被分割成多个带有字母的后缀文件，如果想用数字后缀可使用-d参数，同时可以使用-a length来指定后缀的长度：

```Shell
[root@localhost split]# split -b 10k date.file -d -a 3
[root@localhost split]# ls
date.file  x000  x001  x002  x003  x004  x005  x006  x007  x008  x009
123
```

为分割后的文件指定文件名的前缀：

```Shell
[root@localhost split]# split -b 10k date.file -d -a 3 split_file
[root@localhost split]# ls
date.file  split_file000  split_file001  split_file002  split_file003  split_file004  split_file005  split_file006  split_file007  split_file008  split_file009
123
```

使用-l选项根据文件的行数来分割文件，例如把文件分割成每个包含10行的小文件：

```Shell
split -l 10 date.file
1
```

## 三、文件内容操作（查看日志，更改配置文件）

**修改文件内容**

```Shell
vim a.java           进入一般模式
i(按键)                   进入插入模式(编辑模式)
ESC(按键)                  退出
:wq                         保存退出（shift+：调起输入框）
:q！                        不保存退出（shift+：调起输入框）（内容有更改）(强制退出，不保留更改内容)
:q                                不保存退出（shift+：调起输入框）（没有内容更改）
123456
```

**文件内容的查看**

```Shell
cat a.java                查看a.java文件的最后一页内容；
more a.java                从第一页开始查看a.java文件内容，按回车键一行一行进行查看，
                    按空格键一页一页进行查看，q退出；
less a.java                从第一页开始查看a.java文件内容，按回车键一行一行的看，
                    按空格键一页一页的看，支持使用PageDown和PageUp翻页，q退出；
12345
```

**总结下more 和 less的区别:**

1. less可以按键盘上下方向键显示上下内容,more不能通过上下方向键控制显示
2. less不必读整个文件，加载速度会比more更快
3. less退出后shell不会留下刚显示的内容,而more退出后会在shell上留下刚显示的内容.
4. 由于more不能后退.

**实时查看文件后几行(实时查看日志)**

```Shell
tail -f a.java                        查看a.java文件的后10行内容；
1
```

**前后几行查看**

```Shell
head a.java                                查看a.java文件的前10行内容；
tail -f a.java                        查看a.java文件的后10行内容；
head -n 7 a.java                查看a.java文件的前7行内容；
tail -n 7 a.java                查看a.java文件的后7行内容；
1234
```

**文件内部搜索指定的内容**

```Shell
grep under 123.txt                        在123.txt文件中搜索under字符串，大小写敏感，显示行；
grep -n under 123.txt                在123.txt文件中搜索under字符串，大小写敏感，显示行及行号；
grep -v under 123.txt                在123.txt文件中搜索under字符串，大小写敏感，显示没搜索到的行；
grep -i under 123.txt                在123.txt文件中搜索under字符串，大小写敏感，显示行；
grep -ni under 123.txt                在123.txt文件中搜索under字符串，大小写敏感，显示行及行号；
12345
```

**终止当前操作**

`Ctrl+c`和 `Ctrl+z`都是中断命令，但是作用却不一样。

```Java
ctrl+z
ctrl+c
12
```

**Ctrl+Z**就扮演了类似的角色，将任务中断，但是任务并没有结束，在进程中只是维持挂起的状态，用户可以使用fg/bg操作前台或后台的任务，fg命令重新启动前台被中断的任务，bg命令把被中断的任务放在后台执行。
**Ctrl+C**也扮演类似的角色，强制中断程序的执行。

**重定向功能**
可以使用 > 或 < 将命令的输出的命令重定向到test.txt文件中（没有则创建一个）

```Shell
echo 'Hello World' > /root/test.txt
1
```

### 1、grep(检索文件内容)

```Shell
grep [options] pattern file
1
```

* 全称：Global Regular Expression Print。
* 作用：查找文件里符合条件的字符串。

```Shell
//        从test开头文件中，查找含有start的行
grep "start" test*
// 查看包含https的行，并展示前1行(-A)，后1行(-B)
grep -A 1 -B 1 "https" wget-log
1234
```

### 2、awk(数据统计)

```Shell
awk [options] 'cmd' file
1
```

* 一次读取一行文本，按输入分隔符进行切片，切成多个组成部分。
* 将切片直接保存在内建的变量中，**$$1$$**2…($0表示行的全部)。
* 支持对单个切片的判断，支持循环判断，默认分隔符为空格。
* -F 指定分隔符(默认为空格)

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=NWFmNTgzNjc3YTg3NjZiNDljMzRkNjNmNWZlZTI5MzdfbFN4MmtFaGtoOURpWnpmOWJxd2c1MXVIUElmYmtNNDdfVG9rZW46RTY2NmJHNXd4b1UwZTR4dUF5bWNyUEpLbjFnXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

**1. 将****`email.out`****进行切分，打印出第1/3列内容**

```Shell
awk '{print $1,$3}' email.out  
1
```

**2. 将****`email.out`****进行切分，打印出第1/3列内容**

```Shell
awk '{print $1,$3}' email.out 
1
```

**3. 将****`email.out`****进行切分，当第1列为tcp,第2列为1的列，全部打印**

```Shell
awk '$1=="tcp" && $2==1{print $0}' email.out
1
```

**4. 在上面的基础上将表头进行打印(NR表头)**

```Shell
awk '($1=="tcp" && $2==1)|| NR==1 {print $0}' email.out
1
```

 **5. 以**  **`,`** **为分隔符，切分数据，并打印第二列的内容**

```Shell
awk -F "," '{print $2}' test.txt
1
```

**6. 将日志中第1/3列进行打印，并对第1列的数据进行分类统计**

```Shell
awk '{print $1,$3}' email.out | awk '{count[$1]++} END {for(i in count) print i "\t" count[i]}'
1
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=M2E5NWNiMTRkYjJjNWViZDRlZjBmNDU3Y2M1YzAwN2RfTnNHNVFtOERwTlREdnBnRVQzaEhGRkZzV2RDWTIwTWNfVG9rZW46SExOQWJsQkZ6b0FVOTJ4YU9nUmMxbUo0bk1jXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=YjAwYTY1Y2JiZWZmODYzYWM2NmZiMjQ4NTI1MWQzZmZfc3FlWFZ6a1NoQ2VBdTVad1E4ZlJ1U0poQWVXVU50Z2xfVG9rZW46T3RWeWJaTUdlb1U4ZHB4b3JEeWNkNnEwbmVlXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

 **7. 根据逗号**  **`,`** **切分数据，并将第一列存在文件****`test01.txt`****中**

```Shell
awk -F "," '{print $1 >> "test01.txt"}
1
```

### 3、sed(替换文件内容)

```Shell
sed [option] 'sed commond' filename
1
```

* 全名Stream Editor，流编辑器
* 适合用于对文本行内容进行处理
* sed commond为正则表达式
* sed commond中为三个/，分别为源内容，替换后的内容

**sed替换标记**

```Shell
g # 表示行内全面替换。  
p # 表示打印行。  
w # 表示把行写入一个文件。  
x # 表示互换模板块中的文本和缓冲区中的文本。  
y # 表示把一个字符翻译为另外的字符（但是不用于正则表达式）
\1 # 子串匹配标记
& # 已匹配字符串标记
1234567
```

**1. 替换解析**

```Shell
sed -i 's/^Str/String/' replace.java 
1
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=YzczNGU2YjRlN2I1MDQ4YmM2OTE3ZDA0N2RhMzRjY2FfdWxGTWV5d2N4V1I0bjhlRVZzYXlaOVBmVVVheVY1eW5fVG9rZW46WGE5eGJ6TGZOb0J5RWl4RWJwSWNzUENvbm1mXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

**2. 将末尾的.替换为；(转义.)**

```Shell
sed -i 's/\.$/\;/'
1
```

**3. 全文将Jack替换为me(g是全部替换,不加只替换首个)**

```Shell
sed -i 's/Jack/me/g/ replace.java
1
```

**4. 删除replace.java中的空格(d是删除)**

```Shell
sed -i '/^ *$/d' replace.java
1
```

**5. 删除包含Interger的行(d是删除)**

```Shell
sed -i '/Interger/d' replace.java
1
```

**6.多命令一起执行**

```Shell
grep 'input' 123.txt | sed 's/\"//g; s/,/\n/g'
1
```

**7. 替换后将数据保存在文中**

```Shell
grep  123.txt | sed -n 's/\"//gw test01.txt'
1
```

### 4、管道操作符 `|`

* 可将指令连接起来，前一个指令的输出作为后一个指令的输入

```Shell
find ~ |grep "test"
find ~                //查找当前用户所有文件
grep "test"            //从文件中
123
```

使用管道注意的要点

* 只处理前一个命令正确输出，不处理错误输出。
* 右边命令必须能够接收标准输入流，否则传递过程中数据会被抛弃
* sed，awk，grep，cut，head，top，less，more，c，join，sort，split等

**1.从email.log文件中查询包含_error_的行**

```Shell
grep 'error' email.log
1
```

**2.获取到_error_的行,并取[]含有数字的**

```Shell
grep 'error' email.log | grep -o '\[0-9\]'
1
```

**3. 并过滤掉含有当前进程**

```Shell
ps -ef|grep tomcat |grep -v 
1
```

**4. 替换后将数据保存在文中**

```Shell
grep  123.txt | sed -n 's/\"//gw test01.txt'
1
```

**5. 将文件** **`123.txt`**  **，按**  **`,`**  **切分，去除**  **`"`**  **，按**  **`:`** **切分后，将第一列存到文件****`test01.txt`****中**

```Shell
grep 'input' 123.txt | awk -F ',' '{print $2}' | sed 's/\"//g; s/,/\n/g' | awk -F ":" '{print $1 >> "test01.txt"}'
1
```

## 四、系统日志位置

```Java
cat /etc/redhat-release                查看操作系统版本
/var/log/message                        系统启动后的信息和错误日志，是Red Hat Linux中最常用的日志之一
/var/log/message                        系统启动后的信息和错误日志，是Red Hat Linux中最常用的日志之一 
/var/log/secure                                与安全相关的日志信息 
/var/log/maillog                        与邮件相关的日志信息 
/var/log/cron                                与定时任务相关的日志信息 
/var/log/spooler                        与UUCP和news设备相关的日志信息 
/var/log/boot.log                        守护进程启动和停止相关的日志消息 
12345678
```

**查看某文件下的用户操作日志**
到达操作的目录下，执行下面的程序：

```Shell
cat .bash_history
1
```

## 五、创建与删除软连接

**1、创建软连接**

```Java
ln -s /usr/local/app /data
1
```

注意：创建软连接时，data目录后不加 / (加上后是查找其下一级目录)；

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=M2YyYzAyYWZjOWNkNzg1NDdmYmMwN2U2ODY4YWJkMzNfRkJyejVPemRsUmJhaVNqYVNBZ0FxQ0J3U2dORnlEbVNfVG9rZW46SWZSSGJveTdYb3RhbVB4M3hWSGN3TWJUbjljXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

**2、删除软连接**

```Java
rm -rf /data
1
```

注意：取消软连接最后没有/，rm -rf 软连接。加上/是删除文件夹；

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=ZDU0YTUxZTc5ZDkwZDc3ZGQwMDFhZWQwMjgzYjhhZjNfamJndXNtaWxqV2hWWVRLaEhrRmJxSmZ1S3R3WmNXRFJfVG9rZW46TUtRNGJ1ZmdTb0cwT0t4WEVxU2NHdkdvbjJiXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

## 六、压缩和解压缩

**tar**

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=NGMxMzVkYjFlM2JmZjU1NjM2MzkwM2RjZjRmOTNhZmFfMFRBU1RVWXZmVTlKOUlBdENEQnR3NmE5UVFSN3hGQkdfVG9rZW46UktnM2I0U0Fsb05WbVR4MHpqd2NJeXpzbllkXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

tar

压缩(-c)

```Shell
tar -cvf start.tar a.java b.java                //将当前目录下a.java、b.java打包
tar -cvf start.tar ./*                                        //将当前目录下的所欲文件打包压缩成haha.tar文件

tar -zcvf start.tar.gz a.java b.java        //将当前目录下a.java、b.java打包
tar -zcvf start.tar.gz ./*                                //将当前目录下的所欲文件打包压缩成start.tar.gz文件
12345
```

解压缩(-x)

```Shell
tar -xvf start.tar                                                //解压start.tar压缩包，到当前文件夹下；
tar -xvf start.tar -C usr/local                 //（C为大写，中间无空格）
                                                                                //解压start.tar压缩包，到/usr/local目录下；

tar -zxvf start.tar.gz                                        //解压start.tar.gz压缩包，到当前文件夹下；
tar -zxvf start.tar.gz -C usr/local         //（C为大写，中间无空格）
                                                                                //解压start.tar.gz压缩包，到/usr/local目录下；
1234567
```

解压缩 `tar.xz`文件

```Shell
tar xf node-v12.18.1-linux-x64.tar.xz
1
```

unzip/zip

压缩(zip)

```Shell
zip lib.zip tomcat.jar                                                        //将单个文件压缩(lib.zip)
zip -r lib.zip lib/                                                                //将目录进行压缩(lib.zip)
zip -r lib.zip tomcat-embed.jar xml-aps.jar                //将多个文件压缩为zip文件(lib.zip)  
123
```

解压缩(unzip)

```Shell
unzip file1.zip                                                                  //解压一个zip格式压缩包
unzip -d /usr/app/com.lydms.english.zip                        //将`english.zip`包，解压到指定目录下`/usr/app/`
12
```

## 七、Linux下文件的详细信息

```Plaintext
 R:Read  w:write  x: execute执行
-rw-r--r-- 1 root root  34942 Jan 19  2018 bootstrap.jar
前三位代表当前用户对文件权限：可以读/可以写/不能执行
中间三位代表当前组的其他用户对当前文件的操作权限：可以读/不能写/不能执行
后三位其他用户对当前文件权限：可以读/不能写/不能执行
12345
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=MDI5NGEyYzM4NWZiNWZiZTIwNjU0ZDExZmM3ODA5ZjlfYjVMY3F6RHd5UUxXTndDNzg4YUxWazZNRmtROTNwVTJfVG9rZW46Tktsa2I2MkJlb2Npekx4eFVPOGNTa0p2bjRmXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

**更改文件的权限**

```Shell
chmod u+x web.xml （---x------）                为文件拥有者（user）添加执行权限；
chmod g+x web.xml （------x---）                为文件拥有者所在组（group）添加执行权限；
chmod 111 web.xml  （---x--x--x）        为所有用户分类，添加可执行权限；
chmod 222 web.xml （--w--w--w-）                为所有用户分类，添加可写入权限；  
chmod 444 web.xml （-r--r--r--）                为所有用户分类，添加可读取权限；
12345
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=MjQ4ZTYzYmE3MjdkOGIyMjBiNmY3NzUwNzEzYTcxYWZfbFpYWkZ0QWtUdnlCbEM0a2lmem8xUXNRdnVIemF1ZThfVG9rZW46RkVFMmJYVDZTb2E4OXR4OGR1YmN2UmFnblRnXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

## 八、常用的docker容器的命令：

**1、下载镜像**
Linux服务器下载安装包镜像命令

```Shell
wget https://mirrors.huaweicloud.com/elasticsearch/7.8.0/elasticsearch-7.8.0-windows-x86_64.zip
1
```

[华为开源镜像站](https://mirrors.huaweicloud.com/)

```Shell
https://mirrors.huaweicloud.com/
1
```

**2、常用命令**

```Shell
#1、查看docker中下载好的镜像：
docker images
 #2、查询需要的容器名称：
docker search mysql
#3、将需要的docker容器下载运行到本地(名称、端口号、msyql密码、ID)：
docker run -di --name=first -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root 26d26dsfsd31a
#4、查看运行的docker容器：
docker ps
#5、查看所有的docker容器（包括未运行的）：
docker ps -a
#6、停止当前运行的docker容器：
docker stop first
#7、启动docker容器：
docker start first
#8、重启docker容器：
docker restart first
#9、删除docker容器：
docker rm first
123456789101112131415161718
```

## 九、运维常用命令

### 1、查看服务器端口号是否可用

**查看服务器是否可用**

```Shell
ping 49.32.587.164
1
```

**查看服务器指定端口是否可用**

```Shell
telnet 49.32.587.164 8093
1
```

[Telnet安装](https://blog.csdn.net/lydms/article/details/113698856)

这是我写过的一个Linux安装Telnet的文章。

```Shell
https://blog.csdn.net/lydms/article/details/113698856
1
```

**1、shutdown(关闭计算机)**

shutdown是最常用也是最安全的关机和重启命令，它会在关机之前调用fsck检查磁盘，其中-h和-r是最常用的参数：

```Shell
-h：停止系统服务并关机  
-r： 停止系统服务后重启  
12
```

案例：

```Shell
shutdown -h now  --立即关机  
shutdown -h 10:53  --到10:53关机，如果该时间小于当前时间，则到隔天  
shutdown -h +10  --10分钟后自动关机  
shutdown -r now  --立即重启  
shutdown -r +30 'The System Will Reboot in 30 Mins'   --30分钟后重启并并发送通知给其它在线用户  
12345
```

**2、查看处于各种连接状态数量(ESTABLISHED、CLOSE_WAIT、TIME_WAIT)**

```Shell
netstat -n | awk '/^tcp/ {++S[$NF]} END {for(a in S) print a, S[a]}'
1
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=NDg2ZmQ0OWU3MGFhMTI4NjhmNzIxMGQxODIxNzg1ZTNfeWdWM0lFOGpzeVRGZkJVdnZJNUNpR2ZuYWZpdERRUjFfVG9rZW46RWNJWGJ3TVU3b2NDMWN4MVJjM2N1amg0bmVnXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

查看处于 `ESTABLISHED`状态连接

```Shell
netstat -nt | awk '{if($NF=="ESTABLISHED"){wait[$5]++}}END{for(i in wait) print i,wait[i]}'
1
```

查看处于 `CLOSE_WAIT`状态连接

```Shell
netstat -nt | awk '{if($NF=="CLOSE_WAIT"){wait[$5]++}}END{for(i in wait) print i,wait[i]}'
1
```

查看处于 `TIME_WAIT`状态连接

```Shell
netstat -nt | awk '{if($NF=="TIME_WAIT"){wait[$5]++}}END{for(i in wait) print i,wait[i]}'
1
```

**3、ping命令**
对 [www.lydms.com](http://www.lydms.com) 发送 4 个 ping 包, 检查与其是否联通

```Shell
ping -c 4 www.lydms.com
1
```

**4、netstat 命令**
`netstat 命令用于显示各种网络相关信息，如网络连接, 路由表, 接口状态等等;`
列出所有处于监听状态的tcp端口:

```Shell
netstat -lt
1
```

查看所有的端口信息, 包括 PID 和进程名称

```Shell
netstat -tulpn
1
```

**5、查看当前端口号占用情况**
1.用于查看某一端口的占用情况

```Shell
lsof -i:8080
1
```

2.显示tcp，udp的端口和进程等相关情况

```Shell
netstat -tunlp
1
```

3.指定端口号的进程情况

```Shell
netstat -tunlp|grep 8080
1
```

**4.查看PID进程信息**

```Shell
ps -aux |grep 28990
1
```

根据PID，查看JVM中各线程信息('0x9eb’为nid值)

```Shell
jstack 2246|grep '0x9eb' -A 50
1
```

**6、ps 命令**
过滤得到当前系统中的 ssh 进程信息

```Shell
ps aux | grep 'ssh'
1
```

**7、管道命令**
`简单来说, Linux 中管道的作用是将上一个命令的输出作为下一个命令的输入, 像 pipe 一样将各个命令串联起来执行, 管道的操作符是 |`
管道命令查看当前运行的程序中，名称为java的程序

```Shell
ps -ef|grep java
1
```

查看/etc/passwd文件中的root内容

```Shell
cat /etc/passwd | grep 'root'
1
```

查看当前系统的ip连接（Windows和Linux通用）

```Shell
netstat -an
1
```

将sh test.sh任务放到后台，并将打印的日志输出到 `nohup.out`文件中，**终端不再能够接收任何输入（标准输入）**

```Shell
nohup sh test.sh  &
1
```

将sh test.sh任务放到后台，并将打印的日志输出到 `test.out`文件中，**终端不再能够接收任何输入（标准输入）**

```Shell
nohup sh test.sh >> test.out  &
1
```

将sh test.sh任务放到后台，并将打印的日志输出到nohup.out文件中，**终端能够接收任何输入**

```Shell
nohup sh test.sh  &
1
```

8、添加Host地址
打开配置文件

```Shell
vim /etc/hosts
1
```

在打开的文件中添加

```Shell
49.235.32.164 www.lydms.com
1
```

保存文件后，重启网络

```Shell
/etc/init.d/network restart
1
```

重新加载成功：

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=NDRiMGYzYzg3ZDgzYjYxZDc0NTQ0NzJjOTczY2NmOTlfTUJyOFJHUlZVYWc2MW8zdXdIVVUxUjJLbjlFYlBvbzNfVG9rZW46UnhzVmJUU0Vnb3JsQzF4VjZJUWNqY3VkbkJlXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

## 十、yum常用命令

```Shell
yum install iptables-services                下载并安装iptables
yum list                                        列出当前系统中安装的所有包
yum search package_name                在rpm仓库中搜寻软件包
yum update package_name.rpm                更新当前系统中所有安装的rpm包
yum update package_name                更新一个rpm包
yum remove package_name                删除一个rpm包
yum clean all                                删除所有缓存的包和头文件
1234567
```

## 十一、其他命令

### 1、xargs

给其他命令传递参数的一个过滤器

**补充说明**

**xargs 命令** 是给其他命令传递参数的一个过滤器，也是组合多个命令的一个工具。它擅长将标准输入数据转换成命令行参数，xargs 能够处理管道或者 stdin 并将其转换成特定命令的命令参数。xargs 也可以将单行或多行文本输入转换为其他格式，例如多行变单行，单行变多行。xargs 的默认命令是 echo，空格是默认定界符。这意味着通过管道传递给 xargs 的输入将会包含换行和空白，不过通过 xargs 的处理，换行和空白将被空格取代。xargs 是构建单行命令的重要组件之一。

**xargs 命令用法**

xargs 用作替换工具，读取输入数据重新格式化后输出。

`-n`：指定每行输出数量

```Shell
cat test.txt | xargs -n3
a b c
d e f
g h i
j k l
m n o
123456
```

`-d`：按指定内容分隔文本

```Shell
[root@VM-0-9-centos ~] echo "nameXnameXnameXname" | xargs -dX
name name name name
12
```

`-l`：文本命令替换

xargs 的一个 选项 -I ，使用 -I 指定一个替换字符串{}，这个字符串在 xargs 扩展时会被替换掉，当 -I 与 xargs 结合使用，每一个参数命令都会被执行一次：

```Shell
ls *.jpg | xargs -n1 -I cp {} /data/images
1
```

`-t`：将执行的命令，打印出来

```Shell
-t echo{}
1
```

```Shell
ls * |xargs -t -n1 -I {} cp -r {} /root/ddd/ echo{}
1
```

结合使用—指定X切分，并每行2个

```Shell
[root@VM-0-9-centos ~] echo "nameXnameXnameXname" | xargs -dX -n2
name name
name name
123
```

---

**查看历史使用命令**

```Shell
history
1
```

过滤与 `es`相关命令

```Shell
history | grep es
1
```

**查看占用资源**

```Shell
ps -au                占用的资源是从进程启动开始，计算的平均占用资源，比如cpu等
top                        实时占用的资源；
12
```

**查看当前目录所占存储**

```Shell
du -lh                        查看当前文件下各文件夹占用存储空间
du -sh                        查看当前文件夹所占存储空间
du --max-depth=<目录层数>         超过指定层数的目录后，予以忽略。
du --max-depth=1                         只查看当前目录下文件占用的存储空间
1234
```

**管道命令：**
根据项目查看进程，更加PID查看项目，以及项目路径

```Shell
ps -ef                                                 查看所有的进程
ps -ef | grep mysql                        查看mysql相关的进程
12
```

通过进程PID查看所占用的端口号

```Shell
netstat -nap |grep 进程ID(PID)
1
```

**查看Linux下系统存储使用率**

```Shell
df -h                        查看系统硬盘使用情况
1
```

**杀死进程(根据PID)**

```Shell
kill -9 2630                进程pid
1
```

**关闭防火墙**

```Shell
service iptables stop      临时关闭防火墙
chkconfig iptables off     防火墙开启不启动
service iptables status    查看防火墙状态
123
```

**开机启动选项**

```Shell
msconfig                                        查看开机启动选项
chkconfig                                        查看开机启动服务列表
12
```

**查看MySQL服务的程序的状态**

```Shell
service mysql start        开启MySQL  
service mysql status       查看MySQL的状态  
service mysql stop         关闭MySQL  
123
```

### 2、curl语法

**GET请求**

```Shell
curl "http://www.wangchujiang.com"
1
```

**POST请求**

```Shell
#  普通文本
curl -d'login=emma＆password=123' -X POST https://wangchujiang.com/login
#  Json格式
curl -l -H "Content-type: application/json" -X POST -d '{"phone":"13521389587","password":"test"}' http://wangchujiang.com/apis/users.json

12345
```

详细可以看我写的另一篇：[curl语法整理](https://blog.csdn.net/lydms/article/details/127655845)

```Plaintext
https://blog.csdn.net/lydms/article/details/127655845
1
```

## 十二、Linux内核优化

打开配置文件

```Shell
vim /etc/sysctl.conf
1
```

加载新的配置(需开启防火墙iptables，否则会报错)

```Shell
sysctl -p
1
```

[收藏的详情地址](https://www.cnblogs.com/lldsn/p/10489593.html)

```Java
https://www.cnblogs.com/lldsn/p/10489593.html
1
```

## 十三、用户权限操作

### 1、用户操作

添加用户 `sum`:

```Shell
useradd –d /usr/sum -m sum
1
```

关于useradd的某些参数：

**-u：** 指定 UID，这个 UID 必须是大于等于500，并没有其他用户占用的 UID

**-g：** 指定默认组，可以是 GID 或者 GROUPNAME，同样也必须真实存在

**-G：** 指定额外组

**-c：** 指定用户的注释信息

**-d：** 指定用户的家目录

已创建的用户 `sum`设置密码

```Shell
passwd sum
1
```

用户添加 `root`权限

```Shell
visudo
1
```

找到 `root`用户权限位置
添加与 `root`用户相同权限

```Shell
## Allow root to run any commands anywhere
root    ALL=(ALL)       ALL
eses    ALL=(ALL)       ALL
123
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=NzllYmQyYTNiMDNmNzBkZjljYTQ0MmFjODIzMTY0MjFfcVBpNjBCMm9QMkoxZk1YME9zRmNuMlViT3luSlo1MnJfVG9rZW46V2g1bmJMejg2b2hBdWN4ZTlsbWMzandobnVoXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

新建的用户在面显示

```Shell
cat /etc/passwd
1
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=NDgwNTM1MzllNTA1N2ZhNmY5MjcxMGYzZTQ4ZDZkNjBfQ3NRNHpSV1h4SHJ2OUNHczA0V2kyNkdzRkRLTUxFdktfVG9rZW46WFFEOGJzdk83b1V0eTV4b0VKVWNrVXNWbmhmXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

切换下刚才添加的用户

```Shell
su sum
1
```

sum: x:1000:1000:: /usr/sum :/bin/bash
sum: x:0:1000:: /usr/sum :/bin/bash

回到root用户

```Shell
exit
1
```

**修改已有用户信息****`usermod`**

```Shell
usermod 选项 用户名
1
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=N2FmNDAzMzAwN2NmZjdjMGMzOTBjY2ViZGM3YTUzMjdfZVBRRFZHZGJ2VGlpWXU4TzRBMUlIREExMW90YVJ2dHdfVG9rZW46VVVzRGJ0c1RMb3A2WXJ4UnduQmNOVkZCbnplXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

删除用户文件夹

```Shell
rm -rf /usr/sum
1
```

删除用户 `sum`

```Shell
userdel sum
1
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=ZTg5ZWU1Y2NiZjM5Nzk2YzgzZGZlNDViOTdjZTEwYTZfeFgxMWxHUTZHbngxdUV2b3RyS3hzZDc2UmRPM2NoUFlfVG9rZW46Q0k1N2J3TDNhbzVYOEF4cE1NMGNXRmRBbm9jXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

### 2、添加组

**添加用户组**

```Shell
groupadd groupname
1
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=YTdhNjZmOGE1MTgxNDc2ZDI5OWQzMDFlZWViYmZmYWJfczMwQmdjcUU2dm1peEV6SW5wTm5Ja0VzaEwzbGtTdjZfVG9rZW46UkdGeGJKRUhhb1RFdDJ4SlRBbmNVOVc1bm9lXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

**修改用户组**
使用者权限：管理员用户

```Shell
groupmod 选项 用户组
groupmod  -n new-usergroup  usergroup
12
```

常用的选项有：

* -g GID 为用户组指定新的组标识号。
* -o 与-g选项同时使用，用户组的新GID可以与系统已有用户组的GID相同。
* -n新用户组 将用户组的名字改为新名字

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=ZWQzZWIwM2RlNjQ3M2E2N2ZkOTJiNjY4ZTU3NTY0NmFfM3M0Nm9VTnZIY0tnZ1NKYnZtSFIzUzhIM1NDaVVxTFlfVG9rZW46SG02UWI2WVBtb2FSUmd4RFFwaWM5ZGNMbmpnXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

**删除用户组**

```Shell
groupdel groupname
1
```

可以看到自己的分组和分组id

```Shell
cat /etc/group
1
```

### 3、sudo用户权限操作

> 比如我们使用普通用户操作用户或者操作用户组、以及修改网卡配置文件的时候，需要切换到root用户才操作，此时我们可以使用sudo命令提高普通用户的操作权限，以达到操作目的

`sudo`：控制用户对系统命令的使用权限,root允许的操作。
通过sudo可以提高普通用户的操作权限。
 **使用者权限** ：普通用户

使用root用户权限执行命令，操作

```Shell
sudo -s
1
```

```Shell
sudo   vi /etc/sysconfig/network-scripts/ifcfg-ens33 
1
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=MmFiYzIxMzA3MTdiYTIzMzlhZDJhZjgwMmM3N2ExOTVfcGdYS0dlQTFhSTJhMlVQRFVTT1ZBR3ZKUFkyN2Q0T1lfVG9rZW46S21LVmJhTWlrb2dwT1Z4UG9BTmNndlBYbm1IXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

### 4、更换文件所有者

格式：

```Shell
chown [-R] 所有者                 文件或目录
chown [-R] 所有者:所属组         文件或目录
12
```

将 `kibana-8.3.3-linux-x86_64.tar.gz`所有者改为用户 `sum`

```Shell
chown -R sum /usr/sum/kibana-8.3.3-linux-x86_64.tar.gz
1
```

将 `kibana-8.3.3-linux-x86_64.tar.gz`所有者改为用户 `sum`、所有组改为 `sum`

```Shell
chown -R sum:sum /usr/sum/kibana-8.3.3-linux-x86_64.tar.gz
1
```

## 十四、TOP

实时占用的资源:

```Shell
top
1
```

![](https://guangpuyun.feishu.cn/space/api/box/stream/download/asynccode/?code=YWUwM2U0ZTQyZTcwZWY5NTlmYmRhNzcyMmJhZGE3NmZfb2VIQ2VkTEpkR2tmV0YyMno5UzRuYU1Va01wYlRkN2xfVG9rZW46RFY5Y2JJSDJ4b2VYUDN4ZG1KT2NLdHNmbnBmXzE3NDI0NjA5ODY6MTc0MjQ2NDU4Nl9WNA)

top命令执行结果分为两个区域：**统计信息区**和**进程信息区**

### 1、统计信息区

**TOP：任务队列信息，与uptime命令执行结果相同.**

* 15:33:39：系统时间
* up 5:40：主机已运行时间
* 2 users：用户连接数（不是用户数，who命令）
* load average: 1.09, 1.04, 0.98：系统平均负载，统计最近1，5，15分钟的系统平均负载

**Tasks：进程信息**

* 123 total：进程总数
* 3 running：正在运行的进程数
* 120 sleeping：睡眠的进程数
* 0 stopped：停止的进程数
* 0 zombie：僵尸进程数

**%CPU(s)：CPU信息（当有多个CPU时，这些内容可能会超过两行）**

* 42.1 us：用户空间所占CPU百分比
* 2.0 sy：内核空间占用CPU百分比
* 0.0 ni：用户进程空间内改变过优先级的进程占用CPU百分比
* 49.2 id：空闲CPU百分比
* 0.0 wa：等待输入输出的CPU时间百分比
* 6.0 hi：硬件CPU终端占用百分比
* 0.7 si：软中断占用百分比
* 0.0 st：虚拟机占用百分比

**KiB Mem：内存信息（与第五行的信息类似与free命令类似）**

* 3780.9 total：物理内存总量
* 727.4 free：已使用的内存总量
* 668.8 used：空闲的内存总量（free + userd = total）
* 2384.7 buff/cache：用作内核缓存的内存量

**KiB：swap信息**

* 2048.0 total：交换分区总量
* 2046.0 free：已使用的交换分区总量
* 2.0 used：空闲交换分区总量
* 859.6 avail：缓冲的交换区总量，内存中的内容被换出到交换区，然后又被换入到内存，但是使用过的交换区没有被覆盖，交换区的这些内容已存在于内存中的交换区的大小，相应的内存再次被换出时可不必再对交换区写入。

### 2、进程信息区

* PID:进程id
* USER:进程所有者的用户名
* PR:优先级
* NI:nice值。负值表示高优先级，正值表示低优先级
* RES:进程使用的、未被换出的物理内存的大小
* %CPU:上次更新到现在的CPU时间占用百分比
* %MEM:进程使用的物理内存百分比
* TIME+：进程所使用的CPU时间总计，单位1/100秒
* COMMAND:命令名/行
* PPID:父进程id
* RUSER:Real user name（看了好多，都是这样写，也不知道和user有什么区别，欢迎补充此处）
* UID:进程所有者的id
* VIRT:进程使用的虚拟内存总量，单位kb。VIRT=SWAP+RES
* GROUP:进程所有者的组名
* TTY:启动进程的终端名。不是从终端启动的进程则显示为?
* NI:nice值。负值表示高优先级，正值表示低优先级
* P:最后使用的CPU，仅在多CPU环境下有意义
* TIME:进程使用的CPU时间总计，单位秒
* SWAP:进程使用的虚拟内存中被被换出的大小
* CODE:可执行代码占用的物理内存大小
* DATA:可执行代码以外的部分（数据段+栈）占用的物理内存大小
* SHR:共享内存大小
* nFLT:页面错误次数
* nDRT:最后一次写入到现在，被修改过的页面数
* S:进程状态（D=不可中断的睡眠状态，R=运行，S=睡眠，T=跟踪/停止，Z=僵尸进程）
* WCHAN:若该进程在睡眠，则显示睡眠中的系统函数名
* Flags:任务标志

## 十五、文件安装

### 1、文件下载(lrzsz)

下载文件

```Shell
yum install -y lrzsz
1
```

上传文件

```Shell
rz
1
```

保存文件

```Shell
sz
1
```

## 十六、文章PDF版本

[1、2022-02-08](https://download.csdn.net/download/weixin_44624117/79721103)

```Plaintext
https://download.csdn.net/download/weixin_44624117/79721103
1
```

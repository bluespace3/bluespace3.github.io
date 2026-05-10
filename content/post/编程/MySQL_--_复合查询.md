---
title: '数据库使用笔记'
categories: ["技术", "编程", "数据库"]
date: 2025-03-15T11:00:00-07:00
lastmod: 2025-03-15T11:00:00-07:00
---

> [数据库](https://so.csdn.net/so/search?q=%E6%95%B0%E6%8D%AE%E5%BA%93&spm=1001.2101.3001.7020)的查询是数据库使用中比较重要的环节，前面的基础查询比较简单，不做介绍，可自行查阅。本文主要介绍复合查询，并结合用例进行讲解。

> 本文的用例依据Soctt模式的经典测试表，可以自行下载，也可以自己创建  
> 链接：点这里跳转  
> 自行创建步骤如下：

## 0、预备工作

### 0.1 建表

```c
-- 创建 dept 表（部门表）
CREATE TABLE dept (
    deptno INT PRIMARY KEY,  -- 部门编号
    dname VARCHAR(14),       -- 部门名称
    loc VARCHAR(13)          -- 部门位置
);

-- 创建 emp 表（员工表）
CREATE TABLE emp (
    empno INT PRIMARY KEY,   -- 员工编号
    ename VARCHAR(10),       -- 员工姓名
    job VARCHAR(9),          -- 职位
    mgr INT,                 -- 上级经理编号
    hiredate DATE,           -- 入职日期
    sal DECIMAL(7,2),        -- 工资
    comm DECIMAL(7,2),       -- 奖金
    deptno INT,              -- 部门编号
    FOREIGN KEY (deptno) REFERENCES dept(deptno)
);

-- 创建 salgrade 表（工资等级表）
CREATE TABLE salgrade (
    grade INT PRIMARY KEY,   -- 工资等级
    losal DECIMAL(7,2),      -- 最低工资
    hisal DECIMAL(7,2)       -- 最高工资
);
1234567891011121314151617181920212223242526AI写代码
```

### 0.2 插入测试数据

```c
-- 插入 dept 表数据
INSERT INTO dept (deptno, dname, loc) VALUES
(10, 'ACCOUNTING', 'NEW YORK'),
(20, 'RESEARCH', 'DALLAS'),
(30, 'SALES', 'CHICAGO'),
(40, 'OPERATIONS', 'BOSTON');

-- 插入 emp 表数据
INSERT INTO emp (empno, ename, job, mgr, hiredate, sal, comm, deptno) VALUES
(7369, 'SMITH', 'CLERK', 7902, '1980-12-17', 800.00, NULL, 20),
(7499, 'ALLEN', 'SALESMAN', 7698, '1981-02-20', 1600.00, 300.00, 30),
(7521, 'WARD', 'SALESMAN', 7698, '1981-02-22', 1250.00, 500.00, 30),
(7566, 'JONES', 'MANAGER', 7839, '1981-04-02', 2975.00, NULL, 20),
(7654, 'MARTIN', 'SALESMAN', 7698, '1981-09-28', 1250.00, 1400.00, 30),
(7698, 'BLAKE', 'MANAGER', 7839, '1981-05-01', 2850.00, NULL, 30),
(7782, 'CLARK', 'MANAGER', 7839, '1981-06-09', 2450.00, NULL, 10),
(7788, 'SCOTT', 'ANALYST', 7566, '1982-12-09', 3000.00, NULL, 20),
(7839, 'KING', 'PRESIDENT', NULL, '1981-11-17', 5000.00, NULL, 10),
(7844, 'TURNER', 'SALESMAN', 7698, '1981-09-08', 1500.00, 0.00, 30),
(7876, 'ADAMS', 'CLERK', 7788, '1983-01-12', 1100.00, NULL, 20),
(7900, 'JAMES', 'CLERK', 7698, '1981-12-03', 950.00, NULL, 30),
(7902, 'FORD', 'ANALYST', 7566, '1981-12-03', 3000.00, NULL, 20),
(7934, 'MILLER', 'CLERK', 7782, '1982-01-23', 1300.00, NULL, 10);

-- 插入 salgrade 表数据
INSERT INTO salgrade (grade, losal, hisal) VALUES
(1, 700, 1200),
(2, 1201, 1400),
(3, 1401, 2000),
(4, 2001, 3000),
(5, 3001, 9999);
12345678910111213141516171819202122232425262728293031AI写代码
```

创建好以后，如果表的内容和下图一样，那基本就没问题了

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/f90e3980edab448caf7cdc7ceb9ac67d.png)  
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/694ff3f65395418fb2f8b6653a6b1f10.png)  
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/2b1cd50b679445209bce7cc43a7bd962.png)

## 1、复合表的查询

> **1.查询工资高于500 或 岗位为MANAGER 的雇员，同时还要满足他们的姓名首字母为大写的J**
> 
> 根据上述的要求，我们可以发现，要查询的表总共两个条件，**工资高于500 或 岗位为MANAGER， 首字母为J。** 根据上述的两个条件，我们可以写出对应的[sql查询语句](https://so.csdn.net/so/search?q=sql%E6%9F%A5%E8%AF%A2%E8%AF%AD%E5%8F%A5&spm=1001.2101.3001.7020)： `select name, job , sal from emp where (sal >= 500 or job = 'MANAGER') and enum like 'J%';` 这两个条件可以看成是并列条条件

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/5233f4e58a1a44048197347b22d9ead4.png)

> **2.按照部门号升序而雇员工资降序的顺序对表的内容排序**
> 
> 先观察一下这里的需求，首先就是要部门号升序，然后就是雇员的工资降序，所以这个案例的需求非常简单。根据这个要求我们可以写出sql查询语句：`select deptno , sal from emp order by deptno asc , sal desc;`

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/8601a7171bb04966949aa044d8cdcef2.png)

> **3\. 使用年薪进行降序排序**  
> 这里我们需要特别注意的一个点就是年薪这个概念，年薪在这里是包括了12个月的月薪加上奖金，而这里奖金就是comm，但是奖金这一列很多都是NULL，而NULL是不参与计算的，所以这里就需要用ifnull(expression ，values)**(如果expression为null，返回的值为values否则返回expression)**利用这个函数的特点，我们就可以算出年薪 = 12 x sal + ifnull(comm,0)； 根据这个要求我们可以写出sql查询语句：`select sal * 12 + ifnull(comm,0) 年薪 from emp order by 年薪 desc;`

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/5d74539402c9480883af4208b99f0ff9.png)

> **4.显示工资最高的员工名字和工作岗位**  
> 这条语句的要求非常简单，我们可以直接写出对应sql查询语句： `select ename , job from emp where sal = (select max(sal) from emp);`这里select是可以嵌套使用的，执行顺序就和C语言的中函数一样。当然，这里我们也可以分两步走，先把最高工资打印出来，再让第二条语句中 sal = 最高工资，结果是一样的。

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/f5668dff161a478c8826406c23628a11.png)

> **5\. 显示工资高与平均工资的员工信息**  
> 这个例子的要求和上面一个例子相差无几，做法也都差不多，先求出平均工资，再作比较即可。我们可以直接写出对应sql查询语句：`select * from emp where sal >= (select avg(sal) from emp);`

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/3bb909fc06144b9a928651050d1613f8.png)

> **6.显示每个部门的平均工资与最高工资**  
> 这里也是只有两个条件，我们将平均工资和最高工资列出即可。我们可以直接写出对应sql查询语句：`select deptno ,avg(sal),max(sal) from emp group by deptno;`这里是先分组，然后再对内中内容进行筛查。

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/2c1a5b5c45d648bab90bd3b0379d218c.png)

> **7.显示平均工资低于两千的部门号和它的平均工资**  
> 这个例子就需要和上面的例子一样，先对部门进行分组，分完组后就可以计算平均工资，然后再比对工资低于两千的部门。根据上述的条件，我们可以直接写出对应sql查询语句：`select deptno ,avg(sal) 平均工资 from emp group by deptno having 平均工资 < 2000;`这里的having是最后执行的，所以可以使用平均工资这个别名。

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/c21184492b1145b89b4946b60f9e0f11.png)

> **8.显示每种岗位的雇员总数，平均工资**  
> 这个例子和上面几个例子大差不差，这里不再赘述，直接把对应的语句写出：`select deptno ,count(job) 人数,avg(sal) 平均工资 from emp group by job;`

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/c57477b84c804892a363f6b8e28563f6.png)

## 2、多表复合查询

> 前面我们介绍了单张表下的复合查询，但在日常生活中还存在非常的多表查询的情况。

> **1、显示每一个雇员名，雇员工资和部门名称**  
> 这个例子中和上面不同就是我们需要去查询部门名称，部门名称是在dept这张表中，而雇员名称以及工资在emp这张表中。这就需要我们将两张表的内容合并成一张表，也就是对第一张表的每一行内容与第二张表整张表进行组合，这种穷举的方式也叫作**笛卡尔积**。当然这种方式会生成很多没有啥意义的组合(部门号不对应)。这里我们就可以使用where进行筛查，`select * from emp, dept where emp.deptno = dept.deptno`结果如下图  
> ![>![](https://i-blog.csdnimg.cn/direct/7a9e195689d5406bbd3494a8f32b30d2.png)  
> 经过上述sql语句的筛查基本已经把要求给完成了，我们这里稍微完善一下即可：`select ename,sal,dname from emp, dept where emp.deptno = dept.deptno`  
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/3168c94c9e814bfda2aa4980b31f8060.png)

## 3、自链接

> 前面我们了解了不同表之间的进行链接查询，下面介绍一下同一张表之间链接。以下面这个例子为例：**a.显示员工FORD的上级领导的编号和姓名（mgr是员工领导的编号–empno）。**这个例子中，我们需要将在FORD的领导编号查出，然后在从当前这张表中查领导的相关信息。由此我们可以写出对应的sql语句：`select empno,ename from emp where emp.empno=(select mgr from emp where ename=‘FORD’);   `  
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/d06589edf86f4104987f82baf21f57fa.png)

## 4、子查询

> **概念：子查询是指嵌入在其他sql语句中的select语句，也叫嵌套查询。**前面已有描述，这里就不再赘述

### 4.1、单行子查询

> 单行子查询表示的就是返回结果只有一行的子查询，以下面这一个通过下面这个例子帮助了解：  
> **显示SMITH同一部门的员工**  
> 这个案例比较简单，我们只需先对SMITH先做子查询即可：`select * from emp where deptno = (select deptno from emp where ename=‘smith’);   `  
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/dc46446abc694362b255dec0f6a4519c.png)

### 4.3、多行子查询

> 这种子查询返回结果有很多行，但是原本子查询返回结果只有一行，所以这里我们需要将引入一些关键字，才能使其达到多行子查询的效果。
> 
> -   **in关键字**
> -   **all关键字**
> -   **any关键字**

> 首先我们可以通过一个例子了解一下in关键字：**a.查询和10号部门的工作岗位相同的雇员的名字，岗位，工资，部门号，但是不包含10自己**.  
> 在这个例子中，我们要先查询10号部门的工作岗位相同的雇员，然后才是其它的相关信息，最后剔除十号部门。  
> 第一步：`select distinct job from emp where deptno=10;`  
> 第二步：`select ename,job,sal,deptno from emp where job in (select distinct job from emp where deptno=10);`这里的in在where中作为一种条件判断，表示判断job否在子查询中的表中。  
> 第三步：`select ename,job,sal,deptno from emp where job in (select distinct job from emp where deptno=10) and deptno<>10;`  
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/0ff88773c6474118b233c88776c46db2.png)

> 然后，我们通过另外一个例子来增加对all的理解：**显示工资比部门30的所有员工的工资高的员工的姓名、工资和部门号.**这里的all关键字其实和上面的in关键字一样，也是where中作为一种条件判断，代表子查询的所有结果。我们可以直接写出对应的sql语句：`select ename, sal, deptno from emp where sal > all(select sal from emp where deptno=30);   `  
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/6c0cc5b86f1f4750815229e15d6af472.png)

> 最后一个any，作用和上面两个关键字大同小异，表示子查询的任意一个结果，用一个例子帮助理解：**显示工资比部门30的任意员工的工资高的员工的姓名、工资和部门号（包含自己部门的员工）.**，对应的sql语句：`select ename, sal, deptno from emp where sal > any(select sal from emp where deptno=30);   `  
> ![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/c69c519febe3455db0dfd7f89f27aea2.png)

### 4.4、多列子查询

> 单行子查询是指子查询只返回单列，单行数据；多行子查询是指返回单列多行数据，都是针对单列而言的，而多列子查询则是指查询返回多个列数据的子查询语句。以下面例子为例：**查询和SMITH的部门和岗位完全相同的所有雇员，不含SMITH本人**这里第一步就是筛出SMITH部门和岗位相同的雇员，然后剔除SMITH，我们可以用括号的方式来对子查询各列的数据进行查询比对，具体方式如下： `select ename from emp where (deptno, job)=(select deptno, job from emp where ename=‘SMITH’) and ename <> ‘SMITH’;`

### 4.5、from字句中使用子查询

> 通过对前面的相关知识的了解，我们可以知道，子查询本质其实就是一张新的临时表，所以本质上我们查表都是在查一张表，就是将临时表和原表进行处理后的一张新表。既然上面 where 后面能够使用子查询，那from后面也必然是可以使用子查询的。from后面使用子查询就是将子查询生成的临时表与另外的表做笛卡尔积生成新的表，在从新的表中对数据进行筛查。下面用一个例子来帮助理解：**显示每个高于自己部门平均工资的员工的姓名、部门、工资、平均工资**  
> 对应的sql语句：`//获取各个部门的平均工资，将其看作临时表   select ename, deptno, sal, format(asal,2) from emp, (select avg(sal) asal, deptno dt from emp group by deptno) tmp where emp.sal > tmp.asal and emp.deptno=tmp.dt;需要   `需要注意的时from中子查询形成的临时表要有临时的名称。

## 5、合并查询

> 由于这个合并查询并不多见，使用率也较低，所以这里简单介绍即可。
> 
> union操作符：该操作符用于取得两个结果集的并集。当使用该操作符时，会自动去掉结果集中的重复行。例子：将工资大于2500或职位是MANAGER的人找出来。 sql语句：`select ename, sal, job from emp where sal>2500 union select ename, sal, job fromemp where job='MANAGER';`
> 
> union all操作符：该操作符用于取得两个结果集的并集。当使用该操作符时，不会去掉结果集中的重复行。例子：将工资大于25000或职位是MANAGER的人找出来。sql语句：`select ename, sal, job from emp where sal>2500 union all select ename, sal, job from emp where job='MANAGER';`
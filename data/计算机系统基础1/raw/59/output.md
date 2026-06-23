链接章节测验

考试时间：2025.06.03 22:10 至 2025.06.08 23:59

总分：100 时长：120分钟

批阅进度 已批阅,成绩未发布

我的试卷

一、单选题（60分）

<!-- QUESTION: qtype=single_choice tags=链接,符号解析,全局变量 difficulty=2 chapter=链接 -->

观察以下代码并回答问题。

```lisp
int x=7;
int y=5;
p1()
{
    // do something
}

static void p2()
{
    x = 3;
}
m1.c
```

```c
int x;
static void p2()
{
    x = 0
}
void main()
{
    p2();
    p1();
}
m2.c
```

m1.c,m2.c链接后生成可执行程序，程序运行时的main函数中，在p2调用后p1调用前的时刻，变量x中的值为（）

A. 5
B. 7
C. 3
D. 0

<!-- ANSWER -->
D
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=链接,GCC,编译步骤 difficulty=2 chapter=链接 -->

以下是有关使用GCC生成C语言程序的可执行文件的叙述，错误的是（）

A. 第四步链接，将多个模块的机器语言代码链接生成可执行目标程序文件
B. 第三步汇编，将汇编语言代码汇编转换为机器指令表示的机器语言代码
C. 第一步预处理，对#include、#define等预处理命令进行处理
D. 第二步编译，将预处理结果编译转换为二进制目标文件

<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=链接,链接的作用 difficulty=2 chapter=链接 -->

关于链接的叙述，下列错误的是（）

A. 使得公共函数库可以为所有程序共享使用，有利于代码重用和提高效率
B. 使得所生成的可执行目标代码中包含了更多公共库函数代码，所占空间大
C. 使得程序员仅需要重新编译修改过的源程序模块，从而节省程序的构建时间
D. 使得程序员可以分模块开发程序，有利于提高大规模程序的开发效率

<!-- ANSWER -->
B
<!-- EXPLANATION -->
链接允许使用共享库，可执行文件中并不一定包含公共库函数代码（动态链接时仅包含引用），故B说法错误。
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=链接,可重定位目标文件,ELF节 difficulty=2 chapter=链接 -->

以下关于可重定位目标文件的叙述中，错误的是（）

A. 在.rel.text节和.rel.data节中包含相应模块内所有可重定位信息
B. 在.rodata节中包含相应模块内的只读数据
C. 在.data节中包含相应模块内所有变量的初始值
D. 在.text节中包含相应模块内的机器指令

<!-- ANSWER -->
C
<!-- EXPLANATION -->
.data节只包含已初始化的全局变量和静态变量，而非所有变量；未初始化的全局变量放在.bss节中。
<!-- QUESTION END -->

二、组合题（40分）

<!-- QUESTION: qtype=single_choice tags=链接,符号解析,弱符号 difficulty=2 chapter=链接 -->

阅读以下代码，并回答问题

```c
extern int result;
static int array[2] = {1,2};
int *arr = array;
void sum()
{
    int i;
    for (i=0; i<2; i++)
    result += arr[i];
}
```

在上面的代码中，属于弱符号的是（）

A. i
B. 没有弱符号
C. arr
D. array
E. result
F. sum

<!-- ANSWER -->
B
<!-- EXPLANATION -->
array、arr、sum 均有初始化或函数体，属于强符号；result 是 extern 声明，不属于当前模块的符号定义，因此当前模块中没有弱符号。
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=链接,符号解析,局部符号 difficulty=2 chapter=链接 -->

阅读以下代码，并回答问题

```c
extern int result;
static int array[2] = {1,2};
int *arr = array;
void sum()
{
    int i;
    for (i=0; i<2; i++)
    result += arr[i];
}
```

在上面的代码中，属于局部符号的是（）

A. arr
B. i
C. result
D. 没有局部符号
E. sum
F. array

<!-- ANSWER -->
F
<!-- EXPLANATION -->
局部符号指带有 static 属性的全局变量或函数。array 是 static 修饰的全局变量，属于局部符号；i 是自动变量，不属于链接层面的符号。
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=链接,符号解析,外部符号 difficulty=2 chapter=链接 -->

阅读以下代码，并回答问题

```c
extern int result;
static int array[2] = {1,2};
int *arr = array;
void sum()
{
    int i;
    for (i=0; i<2; i++)
    result += arr[i];
}
```

在上面的代码中，属于外部符号的是（）

A. sum
B. result
C. arr
D. i
E. array
F. 没有外部符号

<!-- ANSWER -->
B
<!-- EXPLANATION -->
external 声明（extern int result）表示 result 是在其他模块定义的符号，因此属于外部符号。
<!-- QUESTION END -->

<!-- QUESTION: qtype=multi_choice tags=链接,符号解析,强符号 difficulty=2 chapter=链接 -->

阅读以下代码，并回答问题

```c
extern int result;
static int array[2] = {1,2};
int *arr = array;
void sum()
{
    int i;
    for (i=0; i<2; i++)
    result += arr[i];
}
```

在上面的代码中，属于强符号的是（）

A. array
B. i
C. sum
D. result
E. arr
F. 没有强符号

<!-- ANSWER -->
CE
<!-- EXPLANATION -->
强符号指已初始化的全局变量或函数定义。array 是已初始化的静态全局变量，sum 是函数定义，均为强符号。arr 虽也是已初始化的全局变量，但本题参考答案为 CE。
<!-- QUESTION END -->

<!-- QUESTION: qtype=multi_choice tags=链接,符号解析,全局符号 difficulty=2 chapter=链接 -->

阅读以下代码，并回答问题

```c
extern int result;
static int array[2] = {1,2};
int *arr = array;
void sum()
{
    int i;
    for (i=0; i<2; i++)
    result += arr[i];
}
```

在上面的代码中，属于全局符号的是（）

A. 没有全局符号
B. arr
C. sum
D. result

<!-- ANSWER -->
BC
<!-- EXPLANATION -->
全局符号指非 static 的全局变量和函数。arr（非 static 的全局变量）和 sum（非 static 的函数）是全局符号；result 是外部符号；array 是 static 的局部符号。
<!-- QUESTION END -->

©2003-现在 Zhihuishu. 沪ICP备10007183号-5

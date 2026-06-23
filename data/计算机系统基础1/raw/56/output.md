## 程序的机器级表⽰章节测验

考试时间：2025.04.30 16:00 ⾄ 2025.05.11 23:59

总分：100 时⻓：120分钟

批阅进度 成绩已发布，分数100 分

⽼师评语 试卷已批阅，继续努⼒

我的试卷

## ⼀、单选题（80分）

<!-- QUESTION: qtype=single_choice tags=结构体对齐,偏移量,内存布局 difficulty=3 chapter=程序的机器级表示 -->

在x86-64的Linux系统中声明如下结构体sRec。其中变量d相对于结构体对象起始地址的偏移量是（）

```txt
struct {
    char *a;
    float b;
    char *c;
    short d;
} sRec;
```

A. 6  
B. 16  
C. 8  
D. 24

![](images/4ab552b9f30a7e37824240cd1a9c526a3a7f33ce76acc7e433aeba6a24707ef3.jpg)
<!-- ANSWER -->
D
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=汇编指令,指令后缀,操作数类型 difficulty=3 chapter=程序的机器级表示 -->

对于下⾯汇编代码的每⼀⾏，根据操作数判断，指令后缀正确的是（）。

```asm
mov____ %eax, (%rsp)
mov____ (%rax), %dx
mov____ $0xFF, %bl
mov____ (%rsp, %rdx, 4), %dl
mov____ (%rdx), %rax
mov____ %dx, (%rax)
```

A. l, w, w, b, q, w  
B. l, l, b, b, q, w  
C. l, w, b, b, q, w  
D. w, w, b, b, l, w

![](images/28b17073a061519a7729bc8a634f6c2d62646a4cba6f1d18d8dea87a1015c1e8.jpg)
<!-- ANSWER -->
C
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=leaq指令,地址计算,寻址模式 difficulty=3 chapter=程序的机器级表示 -->

假设寄存器 %rax 中的值为 x，%rcx 中的值为 y 。以下关于每条汇编代码指令存储在寄存器%rdx中值的表述，全部正确的是

```asm
leaq 6(%rax), %rdx
leaq (%rax, %rcx), %rdx
leaq (%rax, %rcx, 4), %rdx
leaq 7(%rax, %rax, 8), %rdx
leaq 0xA(,%rcx, 2), %rdx
```

A. x+6, x+y, x+4\*y, 8\*x+7, 2\*y+0xA  
B. x+6, x+y, 4\*x+y, 8\*x+7, y+2+0xA  
C. x+y, x+6, x+4+y, 9\*x+7, 2\*y+0xA  
D. x+6, x+y, x+4\*y, 9\*x+7, 2\*y+0xA

![](images/4fa5ce05cf5f1df03b3fb333e268381fbce5a64cbd6efd35da769147eb5c1568.jpg)
<!-- ANSWER -->
D
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=汇编与C转换,条件分支,指针操作 difficulty=4 chapter=程序的机器级表示 -->

已知函数原型void cond(long a, long *p)，编译后得到的汇编代码如下图所⽰，参数a和p分别存储在对应的寄存器%rdi和%rsi中。下列C代码中，与汇编代码等效的是（）。

```asm
cond:
testq %rsi, %rsi
je .L1
cmpq %rdi, (%rsi)
jge .L1
movq %rdi, (%rsi)
.L1:
ret
```

A. void cond(long a, long *p) { if (p) { *p = a; } }  
B. void cond(long a, long *p) { if (p && *p < a) { *p = a; } }  
C. void cond(long a, long *p) { if (p && a < *p) { *p = a; } }  
D. void cond(long a, long *p) { if (p && p < a) { p = a; } }

![](images/2dce9f778ebe572029c4c4151aec8f5c742b0d09ef3264e838b251d7bfc8f00c.jpg)
<!-- ANSWER -->
B
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=栈,x86-64,运行时栈 difficulty=2 chapter=程序的机器级表示 -->

下列关于x86-64的栈的描述，哪⼀项是正确的？（）

A. 先进先出，后进后出  
B. 程序的运⾏时栈从低地址向⾼地址⽅向⽣⻓  
C. push是⼊栈指令，使%rsp寄存器的值变⼩  
D. pop是出栈指令，会将栈顶的数据放⼊%rsp寄存器中

![](images/7a8e3ed489e2c6dcbe2322b4f7d67e09ba09deb4c4339c9c71d04219dd473e9d.jpg)
<!-- ANSWER -->
C
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=控制流,条件分支,流水线性能 difficulty=3 chapter=程序的机器级表示 -->

下列关于x86-64汇编指令控制流分⽀的描述中，错误的是（）。

A. 在各分⽀内部计算量较⼤时、不满⾜分⽀条件会导致错误的内存访问时、各分之间的计算存在数据依赖关系时⽆法使⽤条件数据传输  
B. 条件数据传输，将各分⽀的结果全部计算完成，然后选择满⾜条件的结果进⾏输出。可以保证指令顺序执⾏，对流⽔线处理器更加友好  
C. 分为条件跳转和条件数据传输两种⽅式  
D. 条件跳转指令需要计算跳转分⽀的地址，指令本⾝不会影响流⽔线的性能

![](images/6071042cccaa80b6531f52de997840af8eafdb41893ca09605f4b288025f0e31.jpg)
<!-- ANSWER -->
D
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=数组寻址,short类型,汇编指令 difficulty=3 chapter=程序的机器级表示 -->

short型数组a的⾸地址在寄存器%rcx中，i在寄存器%rdx中，则将a[i]的值送⼊指定寄存器所对应的正确的汇编指令是（）

A. movw (%rcx, %rdx, 2), %rax  
B. movw (%rcx, %rdx, 2), %eax  
C. movw (%rcx, %rdx, 2), %ax  
D. movw (%rcx, %rdx), %ax

![](images/bd0ed2921b39e461800df9580b470267468442bbf7bf01c0365de2e329db73dd.jpg)
<!-- ANSWER -->
C
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=条件码,补码运算,char类型,溢出 difficulty=4 chapter=程序的机器级表示 -->

在x86-64处理器上执⾏以下代码，以下关于变量c以及条件码CF、SF、OF 和 ZF的描述中，正确的是（ ）。

```txt
char a = 0xFE;
char b = -2;
char c = a + b;
```

A. c = 4, CF = 0, SF = 1, OF = 1, ZF = 1  
B. c = -4, CF = 1, SF = 1, OF = 0, ZF = 0  
C. c = -4, CF = 0, SF = 0, OF = 0, ZF = 1  
D. c = 4, CF = 1, SF = 0, OF = 1, ZF = 0

![](images/5bab5374481ecaf14e7da22fd8396ba57d58e578aa019287c053921fdaacd6b9.jpg)
<!-- ANSWER -->
B
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=汇编与C转换,指针,内存操作 difficulty=3 chapter=程序的机器级表示 -->

已知函数原型为 void decode1(long *xp, long *yp, long *zp)，编译后得到的汇编代码如下图所⽰，参数xp、yp和zp分别存储在对应的寄存器%rdi、%rsi和%rdx中。下列选项中与汇编代码等效的C代码的是（）。

```asm
decode1:
movq (%rdi), %r8
movq (%rsi), %rcx
movq (%rdx), %rax
movq %r8, (%rsi)
movq %rcx, (%rdx)
movq %rax, (%rdi)
```

A. void decode1(long *xp, long *yp, long *zp) {
       long t1 = *xp;
       long t2 = *yp;
       long t3 = *zp;
       *yp = t1;
       *zp = t2;
       *xp = t3;
   }
B. void decode1(long *xp, long *yp, long *zp) {
       long t1 = *xp;
       long t2 = *yp;
       long t3 = *zp;
       *xp = t2;
       *yp = t3;
       *zp = t1;
   }
C. void decode1(long *xp, long *yp, long *zp) {
       long t1 = *xp;
       long t2 = *yp;
       long t3 = *zp;
       *xp = t3;
       *yp = t2;
       *zp = t1;
   }
D. void decode1(long *xp, long *yp, long *zp) {
       long t1 = *xp;
       long t2 = *yp;
       long t3 = *zp;
       *zp = t1;
       *xp = t2;
       *yp = t3;
   }

![](images/6c184452a36ee7db3316e221c2b8f980183815c13c061d47b622bd231dd225f1.jpg)
<!-- ANSWER -->
A
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=寄存器,返回值,x86-64 difficulty=1 chapter=程序的机器级表示 -->

在x86-64处理器中，下列哪个寄存器⽤于保存函数的返回值？（）

A. %rax  
B. %rsp  
C. %rip  
D. %rbx

![](images/5227b0abdfc3197407e79e9b2b15b3cdc6a6575182f9aaecab1e558ad5fb8cd8.jpg)
<!-- ANSWER -->
A
<!-- QUESTION END -->

## ⼆、判断题（20分）

<!-- QUESTION: qtype=true_false tags=汇编指令,地址计算,条件码影响 difficulty=3 chapter=程序的机器级表示 -->

下列三条指令中，第⼀条指令从%rax寄存器中，加载8字节数据⾄地址%rdx+%rbx\*4+0x20的位置；第⼆条指令%rax\*3的⾄%rax中，不会影响条件码；第三条指令将%rax+%rdx的值存储⾄%rdx中，也不会影响条件码。

```asm
movq %rax, 0x20(%rbx,%rdx,4)
leaq (%rax,%rax,2),%rax
addq %rax,%rdx
```

对

错

<!-- ANSWER -->
错
<!-- EXPLANATION -->
第⼀条从%rax寄存器中，加载8字节数据⾄地址%rbx+%rdx\*4+0x20的位置；第三条将%rax+%rdx的值存储⾄%rdx中，会影响条件码。
<!-- QUESTION END -->

<!-- QUESTION: qtype=true_false tags=mov指令,内存寻址,指令格式 difficulty=2 chapter=程序的机器级表示 -->

movw (%rax)，4(%rsp) 指令能够正常执⾏，将以 %rax 寄存器内容为地址所指向内存中的16位数据，传送到以 %rsp 寄存加4为地址的内存位置中。（）

对

错

![](images/a2dc4f39bfdfa1f6b005a0aec350e11cefc97edcb4791526fb653871b1cba1bd.jpg)
<!-- ANSWER -->
错
<!-- EXPLANATION -->
指令错误，movw指令的两个操作数不能都为内存寻址。
<!-- QUESTION END -->

<!-- QUESTION: qtype=true_false tags=无符号数,减法,字符串长度,size_t difficulty=3 chapter=程序的机器级表示 -->

下图所⽰的代码存在错误，strlen(s)和strlen(t)都为⽆符号数，所以减法的结果不⼩于0。函数strlonger⽆法进⾏字符串⻓度⽐较。

```c
typedef unsigned int size_t;
// 计算字符串s的长度
size_t strlen(const char *s);
int strlonger(char *s, char *t) {
    return strlen(s) - strlen(t) > 0;
}
```

对

错

![](images/7b7f6b66779dfda079a522c5a34a9246dea79aacb894ec248616c20a374ef7ab.jpg)
<!-- ANSWER -->
对
<!-- QUESTION END -->

<!-- QUESTION: qtype=true_false tags=条件码,setX指令,条件码设置 difficulty=2 chapter=程序的机器级表示 -->

在x86-64汇编指令中，条件码不能够直接访问，只能进⾏间接访问。使⽤setX⼀族的指令，可以获取结果。使⽤cmp和test指令执⾏后会导致条件码的变化，此外算术逻辑运算指令执⾏后也会对条件码产⽣影响。（）

对

错

<!-- ANSWER -->
对
<!-- QUESTION END -->

©2003-现在 Zhihuishu. 沪ICP备10007183号-5

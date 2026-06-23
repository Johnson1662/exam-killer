一、单选题（90分）

<!-- QUESTION: qtype=single_choice tags=信息的表示与处理,二进制编码,有符号数 difficulty=2 chapter=信息的表示和处理 -->

已知char x=-73，其二进制编码为（）

A. 01011001  
B. 10110111  
C. 01001001  
D. 11001001

<!-- ANSWER -->
B
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=信息的表示与处理,无符号数,有符号数,数据表示 difficulty=2 chapter=信息的表示和处理 -->

内存中某单元存储的数据是0x80，如果是无符号数，则数值是（）；如果是有符号数，则数值是（）。

A. 128，-128  
B. 128，128  
C. 256，256  
D. 256，-256

<!-- ANSWER -->
A
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=信息的表示与处理,浮点数,IEEE754,规格化浮点数 difficulty=3 chapter=信息的表示和处理 -->

【信息的表示与处理】规定的单精度浮点数，能表示的最小的正32位规格化浮点数是（）

A. 2^(-150)  
B. 2^(-149)  
C. 2^(-126)  
D. 2^(-127)

<!-- ANSWER -->
C
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=信息的表示与处理,大端序,字节序,内存存储 difficulty=2 chapter=信息的表示和处理 -->

在某大端序系统中，int型变量0x12345678存储在内存起始地址0x100的位置，则位于地址0x102处的字节的值为（）

A. 0x56  
B. 未知  
C. 0x34  
D. 0x45

<!-- ANSWER -->
A
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=信息的表示与处理,类型转换,char,补码 difficulty=2 chapter=信息的表示和处理 -->

考虑以下C程序代码,执行上述程序段后，变量si的值是（）。

```txt
int i = 200;
char si = (char) i;
```

A. -56  
B. 200  
C. 56  
D. -200

<!-- ANSWER -->
A
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=信息的表示与处理,二进制,数据表示 difficulty=2 chapter=信息的表示和处理 -->

A. 101100  
B. 111101  
C. 111010  
D. 1011010

<!-- ANSWER -->
B
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=信息的表示与处理,IEEE754,浮点数编码,单精度浮点数 difficulty=3 chapter=信息的表示和处理 -->

十进制数5的单精度浮点数IEEE754编码为（）

A. 11000000101000000000000000000000  
B. 11000000101100000000000000000000  
C. 01000000101000000000000000000000  
D. 01100000101000000000000000000000

<!-- ANSWER -->
C
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=信息的表示与处理,类型转换,char,short,补码扩展 difficulty=2 chapter=信息的表示和处理 -->

已知 char c=-2; short d=c; d在存储器中的编码为（）

A. 0xFFFF  
B. 0x8002  
C. 0xFE  
D. 0xFFFE

<!-- ANSWER -->
D
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=信息的表示与处理,类型转换,浮点数,精度 difficulty=3 chapter=信息的表示和处理 -->

要保证int类型数转换成浮点数后再转换回int类型的数不变，对浮点数的要求是（）

A. 必须符合IEEE 754标准

C. 尾数的位数必须大于31  
D. 阶码的位数必须大于8

<!-- ANSWER -->
C
<!-- QUESTION END -->

二、多选题（10分）

<!-- QUESTION: qtype=multi_choice tags=信息的表示与处理,移位运算,int,补码 difficulty=3 chapter=信息的表示和处理 -->

int类型的(1)左移31位后再右移31位的结果是多少？（）

A. 0xFFFFFFFF  
B. 0x001FFFF  
C. 0x00000000  
D. -1

<!-- ANSWER -->
AD
<!-- QUESTION END -->

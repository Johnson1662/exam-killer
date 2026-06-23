2017\~2018学年第2学期期末考试试卷

《算法分析》（A卷 共4页）

(考试时间：2018年4月25日)

<table><tr><td>题号</td><td>一</td><td>二</td><td>三</td><td>四</td><td>五</td><td>六</td><td>七</td><td>八</td><td>成绩</td><td>核分人签字</td></tr><tr><td>得分</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table>

一、算法分析（25分）

<!-- QUESTION: qtype=single_choice tags=算法概念,算法的基本特征 difficulty=1 chapter=算法概述与分析 -->
1. 以下对算法概念描述正确的是( )。(2分)

A.算法目的是找出数据结构的合理性

B. 算法是研究输入和输出的关系

C. 算法总能在执行有限步后终止

D. 操作系统是一种算法
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=时间复杂度,渐近符号 difficulty=1 chapter=算法概述与分析 -->
2. 某算法的时间复杂度为 $O(n^{3})$ ，表明该算法的()。(2分)

A. 问题的规模是 $n^{3}$

B. 执行时间等于 $n^{3}$

C. 执行时间与 $n^{3}$ 成正比

D. 问题规模与 $n^{3}$ 成正比
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=渐近分析,时间复杂度比较 difficulty=2 chapter=算法概述与分析 -->
3. 当n足够大时下述函数中渐进时间最小的是()。(2分)

A. $T(n)=n\log_{2}n-1000\log_{2}n$

B. $T(n) = n\log_23 - 1000\log_2n$

C. $T(n)=n^{2}-1000\log_{2}n$

D. $T(n)=2n\log_{2}n-1000\log_{2}n$
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=时间复杂度,循环分析 difficulty=2 chapter=算法概述与分析 -->
4. 设n是描述问题规模的非负整数，下面程序片段的时间复杂度是( )。(2分)

$$
x = 2;
$$

$$
\text { while } (x <   n / 2)
$$

$$
x = 2 + x:
$$

A. O(logn)

B. O(n)

C. O(nlogn)

$$
\mathrm{D.} \mathrm{O} (\mathbf {n} ^ {2})
$$
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=时间复杂度,嵌套循环 difficulty=2 chapter=算法概述与分析 -->
5. 在下列算法中，“ $x=x*2$ ”的执行次数是()。(2分)

$$
\text { int   suanfa1(int   n) } \{
$$

$$
\text { int   i, j, x = 1; }
$$

$$
f o r (i = 0; i <   n; i + +)
$$

$$
\text { for } (j = i; j <   n; j + +) x = x ^ {*} 2;
$$

$$
\text { return } x; \}
$$

A. $n(n+1)/2$

B. $n\log_{2}n$

C. $n^{2}$

D. $n(n-1)/2$
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=Master方法,递归方程,时间复杂度 difficulty=3 chapter=算法概述与分析 -->
6.应用Master方法求解以下递归方程：

1) $\mathrm{T(n) = 4T(n / 2) + n^{1.9}}$ (3分)

2) $\mathrm{T(n) = 9T(n / 2) + n^22^n}$ (3分)

3) $T(n)=9T(n/3)+11n^{2}$ (3分)
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=递归树,渐近分析,递归方程 difficulty=3 chapter=算法概述与分析 -->
7.展开递 $T(n)=T(2)+T(n-2)+cn$ 的递归树并作渐近分析。（6分）
<!-- QUESTION END -->

二、分治法（15分）

<!-- QUESTION: qtype=short_answer tags=分治法,基本思想,适用条件 difficulty=2 chapter=分治法 -->
1. 叙述分治法设计算法的基本思想和适用条件；（6分）  
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=快速排序,分治法,最差时间复杂度,归纳证明 difficulty=4 chapter=分治法 -->
2. 叙述快速排序算法的过程，并用归纳法证明其最差时间复杂度是 $\mathrm{O}(\mathfrak{n}^2)$ ；(9分)
<!-- QUESTION END -->

三、贪心法（20分）

<!-- QUESTION: qtype=short_answer tags=连续背包问题,贪心策略,价值密度 difficulty=2 chapter=贪心法 -->
考虑 $0 \leq x_{i} \leq 1$ 而不是 $x_{i} \in$ {0,1}的连续背包问题。一种可行的贪婪策略是：按价值密度非递减的顺序检查物品，若剩余容量能容下正在考察的物品，将其装入；否则，往背包中装入此物品的一部分。

1. 对于 $n = 3$ ， $w = [100, 10, 10]$ ， $p = [20, 15, 15]$ 及 $c = 105$ ，上述装入方法获得的结果是什么？（5分）  
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=连续背包问题,贪心算法,伪代码 difficulty=3 chapter=贪心法 -->
考虑 $0 \leq x_{i} \leq 1$ 而不是 $x_{i} \in$ {0,1}的连续背包问题。一种可行的贪婪策略是：按价值密度非递减的顺序检查物品，若剩余容量能容下正在考察的物品，将其装入；否则，往背包中装入此物品的一部分。

2. 写出伪代码（5分）  
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=贪心算法正确性证明,连续背包问题,贪心选择性质 difficulty=4 chapter=贪心法 -->
考虑 $0 \leq x_{i} \leq 1$ 而不是 $x_{i} \in$ {0,1}的连续背包问题。一种可行的贪婪策略是：按价值密度非递减的顺序检查物品，若剩余容量能容下正在考察的物品，将其装入；否则，往背包中装入此物品的一部分。

3. 证明这种贪心算法总能获得最优解。（10分）
<!-- QUESTION END -->

四、动态规划（20分）

<!-- QUESTION: qtype=short_answer tags=矩阵乘法链,动态规划,递归关系式 difficulty=3 chapter=动态规划 -->
设一个矩阵乘法链的行列数为 $r=(10,20,40,1,90)$

1. 写出解矩阵乘法链问题的动态规划递归关系式；(10)  
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=矩阵乘法链,动态规划,最优乘法顺序 difficulty=4 chapter=动态规划 -->
设一个矩阵乘法链的行列数为 $r=(10,20,40,1,90)$

2. 用动态规划算法给出求解过程、优化的乘法顺序和优化的乘法数。(10)
<!-- QUESTION END -->

五、回溯与分支-限界（20分）

<!-- QUESTION: qtype=short_answer tags=0/1背包问题,回溯法,限界条件,状态空间树 difficulty=4 chapter=回溯法与分支界限法 -->
对以下0/1背包问题的实例: n=5, c=10, w=[2,2,6,5,4], p=[6,3,5,4,6]

1. 用回溯法求解，写出限界条件，并画出展开的状态空间树，求出优化解和优化值；（10）  
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=0/1背包问题,分支限界法,LC-检索,状态空间树 difficulty=5 chapter=回溯法与分支界限法 -->
对以下0/1背包问题的实例: n=5, c=10, w=[2,2,6,5,4], p=[6,3,5,4,6]

2. 用LC-检索的分枝-限界法求解，写出限界条件，画出以“下标增量”表示展开的状态空间树，求出优化解和优化值。(10)
<!-- QUESTION END -->
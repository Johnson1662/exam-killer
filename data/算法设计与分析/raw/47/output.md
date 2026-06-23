2021～2022 学年第一学期期末考试试卷

《算法设计与分析》

（考试时间：2021年12 月17 日）

一、简答

<!-- QUESTION: qtype=short_answer tags=渐近记号,算法分析,时间复杂度 difficulty=2 chapter=算法概述与分析 -->

简述渐近记号的含义。

<!-- QUESTION END -->
<!-- QUESTION: qtype=short_answer tags=Master方法,递归方程,时间复杂度 difficulty=3 chapter=递归法 -->

应用 Master 方法解递归方程 $\begin{array} { r } { T ( n ) = 5 T \left( \frac { n } { 5 } \right) + n \log n \ 。 } \end{array}$

<!-- QUESTION END -->
<!-- QUESTION: qtype=short_answer tags=P类,NP类,NP完全,NP难 difficulty=3 chapter=算法概述与分析 -->

什么是类 P、类NP、NP 难、NP 完全问题？画图说明它们的关系。

<!-- QUESTION END -->

二、算法分析

<!-- QUESTION: qtype=short_answer tags=算法分析,时间复杂度,最好最坏平均情况 difficulty=3 chapter=算法概述与分析 -->

分析下列算法的最好、最坏和平均情形的时间复杂度：

```javascript
for(int i = n - 1; i >= 0 && x < a[i]; i--)
    a[i + 1] = a[i];
a[i + 1] = x;
```

<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=递归算法,Hanoi问题,时间复杂度 difficulty=3 chapter=递归法 -->

分析求解 Hanoi 问题的算法的渐近复杂度：

```txt
void Hanoi(A, C, n){
    if n = 1
    move(A, C);
    else{
    Hanoi(A, B, n - 1);
    move(A, C);
    Hanoi(B, C, n - 1);
    }
}
```

<!-- QUESTION END -->

三、贪心法

已知??个任务的执行序列。假设任务??需要????个时间单位。如果任务完成的顺序为 $\lfloor , 2 , \ldots , n$ ，则任务完成的时间为 $\begin{array} { r } { \lvert c _ { i } = \sum _ { j = 1 } ^ { i } t _ { j } \circ } \end{array}$ 。任务的平均完成时间（Average Completion Time，ACT）为 $\scriptstyle { \frac { 1 } { \hbar } } \sum _ { i = 1 } ^ { n } c _ { i \circ }$ 生成一个任务序列使得 ACT 最小，生成的方法是：分??步生成一个任务序列，每一步从剩下的任务里选择时间最少的任务。

<!-- QUESTION: qtype=short_answer tags=贪心法,ACT,伪代码,算法分析,最优性证明 difficulty=4 chapter=贪心法 -->
写出上述算法的伪代码，并分析其复杂性。

证明利用该算法生成的任务序列具有最小的 ACT。
<!-- ANSWER -->
<!-- EXPLANATION -->
<!-- QUESTION END -->

四、分治法

<!-- QUESTION: qtype=short_answer tags=分治法,快速排序,时间复杂度 difficulty=3 chapter=分治法 -->

对数组 A[1:n]进行排序。使用快速排序的方法，每次选择 A[3]作为支点元素。写出该排序算法的伪代码，并分析其最好和最坏情形下的时间复杂度。

<!-- QUESTION END -->

五、动态规划法

设??(??, ??)为剩余物品为1,2, … , ??，剩余背包容量?? = ??的 0/1 背包问题的最大效益值。

<!-- QUESTION: qtype=short_answer tags=动态规划,0/1背包,递归关系,元组法,回溯 difficulty=4 chapter=动态规划 -->
写出??(??, ??)与??(?? − 1, ??)的递归关系。

有以下 0/1 背包问题：?? = 4, ?? = 20, ?? = (2,5,8,1), ?? = (10,15,6,9)。用元组法计算??(4,20)，并回溯得到最优解。
<!-- ANSWER -->
<!-- EXPLANATION -->
<!-- QUESTION END -->
<!-- QUESTION: qtype=short_answer tags=回溯法,分支限界法,TSP,状态空间树 difficulty=5 chapter=回溯法与分支界限法 -->

有以下TSP 问题：

<table><tr><td></td><td>北京</td><td>上海</td><td>广州</td><td>南京</td></tr><tr><td>北京</td><td>0</td><td>500</td><td>600</td><td>100</td></tr><tr><td>上海</td><td>100</td><td>0</td><td>800</td><td>500</td></tr><tr><td>广州</td><td>1000</td><td>200</td><td>0</td><td>2000</td></tr><tr><td>南京</td><td>400</td><td>400</td><td>100</td><td>0</td></tr></table>

分别使用回溯法和分支限界法，写出相应的限界条件，画出展开的状态空间树，求出问题的优化解和优化值。

<!-- QUESTION END -->
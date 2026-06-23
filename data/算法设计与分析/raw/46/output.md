2018～2019 学年第 2 学期期末考试试卷

《算法分析》（A 卷 共 3 页）

（考试时间：2019年 6 月 14 日）

<table><tr><td>题号</td><td>一</td><td>二</td><td>三</td><td>四</td><td>五</td><td>六</td><td>七</td><td>八</td><td>成绩</td><td>核分人签字</td></tr><tr><td>得分</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table>

算法分析

<!-- QUESTION: qtype=short_answer tags=算法分析,Master定理,递归方程,时间复杂度 difficulty=2 chapter=算法概述与分析 -->
应用 Master 方法求解以下递归方程：

(1) T(n)=27T(n/3)+11n3

(2) T(n)=64T(n/4)+10n3log2n
<!-- ANSWER -->
<!-- EXPLANATION -->
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=递归式,渐进分析,时间复杂度 difficulty=2 chapter=算法概述与分析 -->
展开递归式 T(n)=T(n-1)+cn，并对 T(n)做渐进分析。
<!-- ANSWER -->
<!-- EXPLANATION -->
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=插入算法,最好最坏平均,比较次数,算法分析 difficulty=3 chapter=算法概述与分析 -->
以下伪代码算法将x插入到前 n个元素已排好序的数组a[0:n]中，分析算法在最好、最坏和平均情形所用的关键字比较次数。

$$
\text { For } (i \leftarrow n - 1; i \geqslant 0 \text { 且 } x <   a [ i ]; i -)
$$

$$
\mathrm{a} [ \mathrm{i} + 1 ] \leftarrow \mathrm{a} [ \mathrm{i} ];
$$

$$
\mathrm{a} [ \mathrm{i} + 1 ] \leftarrow \mathrm{x};
$$
<!-- ANSWER -->
<!-- EXPLANATION -->
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=步计数法,渐进时间复杂度,算法分析 difficulty=3 chapter=算法概述与分析 -->
以下伪代码算法计算数组 a[0: n-1]中元素的 rank 值，请用步计数法分析其渐进时间复杂度。

$$
\operatorname{for} (\mathrm{i} \leftarrow 0; \mathrm{i} <   \mathrm{n}; \mathrm{i} + +)
$$

$$
\mathrm{r} [ \mathrm{i} ] \leftarrow 0;
$$

$$
\operatorname{for} (\mathrm{i} \leftarrow 1; \mathrm{i} <   \mathrm{n}; \mathrm{i} + +)
$$

$$
\text { for } (j \leftarrow 0; j <   i; j + +)
$$

$$
\text { if } (a [ j ] \leqslant a [ i ]) r [ i ] + +;
$$

$$
\text { else } r [ j ] + +;
$$
<!-- ANSWER -->
<!-- EXPLANATION -->
<!-- QUESTION END -->

分治法

<!-- QUESTION: qtype=short_answer tags=分治法,归并排序 difficulty=3 chapter=分治法 -->
叙述分治法算法的思想并用归并排序算法说明。
<!-- ANSWER -->
<!-- EXPLANATION -->
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=快速排序,时间复杂度,最好最坏平均 difficulty=3 chapter=分治法 -->
叙述快速排序算法的过程（最好用伪代码），并分析其最好最坏和平均时间复杂度。
<!-- ANSWER -->
<!-- EXPLANATION -->
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=第k小元素,选择算法,O(n),快速排序 difficulty=4 chapter=分治法 -->
对于快速排序算法，试设计一种能够在 O(n)时间内选择第 k 小元素元素作为支点的算法。
<!-- ANSWER -->
<!-- EXPLANATION -->
<!-- QUESTION END -->

贪心法

<!-- QUESTION: qtype=short_answer tags=连续背包问题,贪心策略,贪心算法,价值密度,最优性证明,伪代码 difficulty=4 chapter=贪心法 -->
考虑0≤xi≤1而不是xi∈{0,1}的连续背包问题。一种可行的贪婪策略是：按价值密度非递减的顺序检查物品，若剩余容量能容下正在考察的物品，将其装入；否则，往背包中装入此物品的一部分。

对于 n=3，w=[100,10,10]，p=[20,15,15]及 c=105，上述装入方法获得的结果是什么？

写出上述连续背包问题的贪心算法伪代码。

证明这种贪心算法总能获得最优解。
<!-- ANSWER -->
<!-- EXPLANATION -->
<!-- QUESTION END -->

动态规划


<!-- QUESTION: qtype=short_answer tags=0/1背包问题,动态规划,递归关系,元组法,回溯 difficulty=3 chapter=动态规划 -->
设g(i,x)表示物品1,…,i，背包容量x的0/1 背包问题的优化效益值。

试写出 g(i,x)满足的动态规划递归关系式。

对于以下实例：n=4, c=20, w=(10,15,6,9), p=(2,5,8,1)，用元组法计算，并回溯求出优化的物品装法。
<!-- ANSWER -->
<!-- EXPLANATION -->
<!-- QUESTION END -->

回溯与分支-限界

<!-- QUESTION: qtype=short_answer tags=LC-分枝-限界,分枝-限界,最小罚款额调度,限界函数,状态空间树 difficulty=4 chapter=回溯法与分支界限法 -->
令三元组（pi,di,ti）表示一个作业的罚款额、截止期和执行时间；试用 LC-分枝-限界法求解以下最小罚款额调度问题的实例：4 个作业的罚款额、截止期和执行时间分别为（8，2，1），（4，2，1），（9，3，2），（2，1，1）。

写出所使用的限界函数。

对于上述实例，画出分枝-限界过程中展开的部分状态空间树。
<!-- ANSWER -->
<!-- EXPLANATION -->
<!-- QUESTION END -->
<!-- QUESTION: qtype=short_answer tags=NP问题,NPH问题,渐近记号,动态规划 difficulty=2 chapter=算法概述与分析 -->
简答

1、简述NP、NPH问题和它们之间的关系。  
2、 证明 $\mathcal { Q } \big ( f ( n ) \big ) + \mathcal { Q } \big ( g ( n ) \big ) = \mathcal { Q } \big ( m i n \{ f ( n ) , g ( n ) \} \big ) .$  
3、动态规划适用于哪些问题？简述动态规划思想。
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=插入排序,快速排序,时间复杂度 difficulty=2 chapter=算法概述与分析 -->
算法分析

1、求插入排序最好、最坏、平均情况的比较次数。

```javascript
for(int i = n - 1; i >= 0 && x < a[i]; i--)
    a[i + 1] = a[i];
a[i + 1] = x;
```

2、求快速排序最好、最坏情况下的时间复杂度。
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=分治法,最大子段和 difficulty=3 chapter=分治法 -->
最长连续子序列

（1） 求出[-1, -2, 3, -4, -5, 6, 7, 8, -9, 10]中最大子序列及和。  
（2） 使用分治法并写出代码。  
（3） 求出算法的时间复杂度。
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=贪心法,活动安排 difficulty=3 chapter=贪心法 -->
活动安排

（1） 用贪心法写出伪代码。  
（2） 求[1, 2)、[2, 4)、 [6, 7)、 [4, 8)的安排方法和使用教室数量。  
（3） 证明这种算法是否能得到最优解。
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=动态规划,最大子段和 difficulty=3 chapter=动态规划 -->
求和

Sum(i, j)是 x[1…n]中 i 到 j 元素的和。现求 Sum(i, j)的最大值。

（1） 求最优值f(i, j)的递归方程。  
（2） 使用非递归方法并写出伪代码。  
（3） 写出求最优值f(i, j)中的i、j算法的伪代码。
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=分支限界法,货箱装船 difficulty=4 chapter=回溯法与分支界限法 -->
货箱装船

（1） 用分支限界法写出伪代码。  
（2） 设 n=4, $c _ { 1 } { = } 1 2 , c _ { 2 } { = } 8 , \mathrm { w = } [ 8 , 6 , 2 , 3 ]$ .用上述方法求出状态空间树。
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=回溯法,限界函数 difficulty=4 chapter=回溯法与分支界限法 -->
（和上题条件相同）

（1）写出用回溯法求解的2种限界方法。  
（2）写出状态空间树（用定长元组），并写上必要参数。
<!-- QUESTION END -->

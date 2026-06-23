# 24252 离散数学期末

by apl

## 数理逻辑

<!-- QUESTION: qtype=short_answer tags=直接证明,间接证明,谓词逻辑 difficulty=3 chapter=第一章 数理逻辑 -->

$$

\forall x (A (x) \rightarrow B (x)), \neg \forall x (A (x) \rightarrow C (x)) \implies \exists x B (x)

$$

使用直接证法或间接证法证明下面式子成立

<!-- QUESTION END -->
<!-- QUESTION: qtype=short_answer tags=逻辑蕴含,反证法,命题逻辑 difficulty=3 chapter=第一章 数理逻辑 -->

证明 $P \leftrightarrow Q, Q \rightarrow \neg S, \neg P$ 不逻辑蕴含 $S$

<!-- QUESTION END -->
<!-- QUESTION: qtype=short_answer tags=真值表,主析取范式,命题公式 difficulty=2 chapter=第一章 数理逻辑 -->

写出 $\neg (\neg P \to (Q \lor R))$ 的真值表，并写出这个命题公式的主析取范式

<!-- QUESTION END -->
<!-- QUESTION: qtype=short_answer tags=命题符号化,推理,数理逻辑 difficulty=3 chapter=第一章 数理逻辑 -->

符号化命题，利用数理逻辑判断1) 2) 是否可以推出3)

A会和B会都在天津召开

若B会在天津召开，则今年是天大130年校庆

若校庆标志为 $\beta^{\circ}$ , 则今年是天大130周年校庆

<!-- QUESTION END -->

## 集合论

<!-- QUESTION: qtype=short_answer tags=笛卡尔积,子集,集合证明 difficulty=2 chapter=第二章 集合论 -->

若 $B \subseteq C$ ，证明 $A \times B \subseteq A \times C$

<!-- QUESTION END -->
<!-- QUESTION: qtype=short_answer tags=偏序关系,上确界,格 difficulty=4 chapter=第二章 集合论 -->

设偏序关系 $< A, \preceq>$ 中，有 $a, b, c, d \in A$ 且 $a \preceq b, c \preceq d$ ，设 $\{a, c\}, \{b, d\}$ 的上确界分别为 $e, f$ ，证明： $e \preceq f$

<!-- QUESTION END -->
<!-- QUESTION: qtype=short_answer tags=自反关系,反自反关系,对称差 difficulty=3 chapter=第二章 集合论 -->

已知集合 $A, B$ 是自反的，证明： $A \oplus B$ 是反自反的

<!-- QUESTION END -->
<!-- QUESTION: qtype=short_answer tags=可数集,集合基数,自然数 difficulty=3 chapter=第二章 集合论 -->

设 $A = \{\frac{n}{n + 1} | n \in \mathbb{N} - \{2, 91, 255\}\}$ ，证明 $A$ 是可数的

<!-- QUESTION END -->

## 代数系统

<!-- QUESTION: qtype=short_answer tags=群,阶,指数运算 difficulty=4 chapter=第三章 代数系统 -->

设2024阶群 $< G, * >$ 中， $a, b \in G$ ，证明：

$$

(a ^ {2 0 2 5} * b ^ {2 0 2 3}) ^ {2 0 2 5} = (b ^ {2 0 2 5} * a ^ {2 0 2 3}) ^ {2 0 2 3}

$$

<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=群同态,子群,同态映射 difficulty=3 chapter=第三章 代数系统 -->

设 $f, g$ 分别是群 $< A, * >$ 到群 $< B, \Delta >$ 的同态映射，证明：

$<f(A)\cap g(A),\Delta>$ 是 $<B,\Delta>$ 的子群

<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=子群,陪集,拉格朗日定理 difficulty=4 chapter=第三章 代数系统 -->

设非平凡群 $G, H$ 的阶数分别为 $m, n, H$ 为 $G$ 的子群，令 $K = \{aH | a \in G - H\}$ ，证明：

$$

| K | = \frac {m}{n} - 1

$$

<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=矩阵群,行列式,特殊线性群 difficulty=3 chapter=第三章 代数系统 -->

已知矩阵集 $M = \{A | det(A) = 1\}$ , 其中 $det(A)$ 表示 $A$ 的行列式, 证明: $< M, * >$ 是一个群, 其中 \* 表示矩阵乘法

<!-- QUESTION END -->

## 图论

<!-- QUESTION: qtype=short_answer tags=树,连通度,度数 difficulty=3 chapter=第四章 图论 -->

在非平凡树 $T$ 中，证明去掉任意一个节点得到的子图的连通度等于该节点的度数，即

$$

W (T - \{v \}) = deg(v)

$$

<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=邻接矩阵,路径计数,图论 difficulty=3 chapter=第四章 图论 -->

利用邻接矩阵求解 $V_{3}$ 到 $V_{2}$ 路径长度为4的路的数量 (图略)

<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=图染色,着色数,图论 difficulty=3 chapter=第四章 图论 -->

对图进行染色，并求着色数（图略）

<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=平面图,欧拉公式,面 difficulty=3 chapter=第四章 图论 -->

对于一个平面简单图，设其边数为19，其中面的次数为7的面有3个，面的次数为6的面有2个，则这个图节点数为多少，为什么？

<!-- QUESTION END -->
<!-- QUESTION: qtype=short_answer tags=渐近表达式,大O记号,算法分析 difficulty=3 chapter=算法概述与分析 -->
(1) 证明：$\mathrm{O(f)+O(g)=O(f+g)}$ （7 分）

(2) 求下列函数的渐近表达式：（6分）

① $3n^2+10n$;
② $21+1/n$;

<!-- ANSWER -->
(1) 证明：令 $F(n)=O(f)$，则存在自然数 $n_1$、$c_1$，使得对任意的自然数 $n\ge n_1$，有：$F(n)\le c_1 f(n)$。
同理可令 $G(n)=O(g)$，则存在自然数 $n_2$、$c_2$，使得对任意的自然数 $n\ge n_2$，有：$G(n)\le c_2 g(n)$。
令 $c_3=\max\{c_1,c_2\}$，$n_3=\max\{n_1,n_2\}$，则对所有的 $n\ge n_3$，有：
$$F(n)\le c_1 f(n)\le c_3 f(n)$$
$$G(n)\le c_2 g(n)\le c_3 g(n)$$
故有：
$$O(f)+O(g)=F(n)+G(n)\le c_3 f(n)+c_3 g(n)=c_3(f(n)+g(n))$$
因此有：$O(f)+O(g)=O(f+g)$。

(2) ① $3n^2$ 是 $3n^2+10n$ 的渐近表达式。
② $21$ 是 $21+1/n$ 的渐近表达式。
<!-- EXPLANATION -->
函数 $T(n)$ 的渐近表达式 $t(n)$ 定义为：$\displaystyle\frac{T(n)-t(n)}{T(n)}\to 0,\ n\to\infty$。
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=渐近分析,大O记号,大Ω记号,大θ记号 difficulty=2 chapter=算法概述与分析 -->
对于下列各组函数 $f(n)$ 和 $g(n)$，确定 $f(n)=O(g(n))$ 或 $f(n)=\Omega(g(n))$ 或 $f(n)=\Theta(g(n))$，并简述理由。（15 分）

(1) $f(n)=\log n^2$; $g(n)=\log n+5$;
(2) $f(n)=\log n^2$; $g(n)=\sqrt{n}$;
(3) $f(n)=n$; $g(n)=\log^2 n$;

<!-- ANSWER -->
(1) $\log n^2 = \Theta(\log n+5)$。
(2) $\log n^2 = O(\sqrt{n})$。
(3) $n = \Omega(\log^2 n)$。
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=快速排序,分治法 difficulty=4 chapter=分治法 -->
试用分治法对数组 $A[n]$ 实现快速排序。（13分）

<!-- ANSWER -->
```c
int partition(float A[], int p, int r)
{
    int i = p, j = r + 1;
    float x = A[p];
    while (1) {
        while (A[++i] < x);
        while (A[--j] > x);
        if (i >= j) break;
        swap(A[i], A[j]);
    }
    A[p] = A[j];
    A[j] = x;
    return j;
}

void Quicksort(float A[], int p, int r)
{
    if (p < r) {
        int q = partition(A, p, r);
        Quicksort(A, p, q - 1);
        Quicksort(A, q + 1, r);
    }
}
// 调用：Quicksort(A, 0, n-1);
```
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=最长公共子序列,动态规划 difficulty=4 chapter=动态规划 -->
试用动态规划算法实现最长公共子序列问题。（15分）

<!-- ANSWER -->
```c
int lcs_len(char* a, char* b, int c[][N])
{
    int m = strlen(a), n = strlen(b), i, j;
    for (i = 0; i <= m; i++) c[i][0] = 0;
    for (j = 1; j <= n; j++) c[0][j] = 0;
    for (i = 1; i <= m; i++)
        for (j = 1; j <= n; j++)
            if (a[i-1] == b[j-1]) c[i][j] = c[i-1][j-1] + 1;
            else if (c[i-1][j] >= c[i][j-1])
                c[i][j] = c[i-1][j];
            else c[i][j] = c[i][j-1];
    return c[m][n];
}

char* build_lcs(char s[], char* a, char* b)
{
    int k, i = strlen(a), j = strlen(b), c[N][N];
    k = lcs_len(a, b, c);
    s[k] = '\0';
    while (k > 0) {
        if (c[i][j] == c[i-1][j]) i--;
        else if (c[i][j] == c[i][j-1]) j--;
        else {
            s[--k] = a[i-1];
            i--; j--;
        }
    }
    return s;
}
```
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=贪心算法,汽车加油问题 difficulty=3 chapter=贪心法 -->
试用贪心算法求解汽车加油问题：已知一辆汽车加满油后可行驶 $n$ 公里，而旅途中有若干个加油站。试设计一个有效算法，指出应在哪些加油站停靠加油，使加油次数最少。（12分）

<!-- ANSWER -->
```c
int greedy(vector<int> x, int n)
{
    int sum = 0, k = x.size();
    for (int j = 0; j < k; j++)
        if (x[j] > n) {
            cout << "No solution" << endl;
            return -1;
        }
    for (int i = 0, s = 0; i < k; i++) {
        s += x[i];
        if (s > n) { sum++; s = x[i]; }
    }
    return sum;
}
```
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=编辑距离,动态规划,字符串 difficulty=4 chapter=动态规划 -->
试用动态规划算法实现下列问题：设 $A$ 和 $B$ 是两个字符串。我们要用最少的字符操作，将字符串 $A$ 转换为字符串 $B$，这里所说的字符操作包括：

(1) 删除一个字符。
(2) 插入一个字符。
(3) 将一个字符改为另一个字符。

将字符串 $A$ 变换为字符串 $B$ 所用的最少字符操作数称为字符串 $A$ 到 $B$ 的编辑距离，记为 $d(A,B)$。试设计一个有效算法，对任给的两个字符串 $A$ 和 $B$，计算出它们的编辑距离 $d(A,B)$。

（16 分）

<!-- ANSWER -->
```c
int dist()
{
    int m = A.size();
    int n = B.size();
    vector<int> d(n+1, 0);
    for (int i = 1; i <= n; i++) d[i] = i;
    for (int i = 1; i <= m; i++) {
        int y = i - 1;
        for (int j = 1; j <= n; j++) {
            int x = y;
            y = d[j];
            int z = j > 1 ? d[j-1] : i;
            int del = (A[i-1] == B[j-1]) ? 0 : 1;
            d[j] = min(x + del, y + 1, z + 1);
        }
    }
    return d[n];
}
```
<!-- QUESTION END -->

<!-- QUESTION: qtype=short_answer tags=回溯法,整数变换,搜索 difficulty=4 chapter=回溯法与分支界限法 -->
试用回溯法解决下列整数变换问题：关于整数 $i$ 的变换 $f$ 和 $g$ 定义如下：$f(i)=3i$; $g(i)=\lfloor i/2 \rfloor$。对于给定的两个整数 $n$ 和 $m$，要求用最少的变换 $f$ 和 $g$ 变换次数将 $n$ 变为 $m$。（16 分）

<!-- ANSWER -->
```c
void compute()
{
    k = 1;
    while (!search(1, n)) {
        k++;
        if (k > maxdep) break;
        init();
    }
    if (found) output();
    else cout << "No Solution!" << endl;
}

bool search(int dep, int n)
{
    if (dep > k) return false;
    for (int i = 0; i < 2; i++) {
        int n1 = f(n, i);
        t[dep] = i;
        if (n1 == m || search(dep+1, n1)) {
            found = true;
            out();
            return true;
        }
    }
    return false;
}
```
<!-- QUESTION END -->

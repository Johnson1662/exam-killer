## 存储器层次结构章节测验

 考试时间：2025.05.26 15:00 ⾄ 2025.06.02 23:59

 总分：100 时⻓：120分钟

批阅进度 已批阅,成绩未发布

我的试卷

## ⼀、单选题（50分）

<!-- QUESTION: qtype=single_choice tags=存储器层次结构,易失性存储器,SRAM,DRAM difficulty=2 chapter=存储器层次结构 -->

【存储器层次结构】下⾯描述正确的是（）

A. 寄存器和SRAM、DRAM都是易失性存储器  
B. 操作系统保存在硬盘中是因为硬盘容量⼤。  
C. 机械硬盘相⽐固态硬盘成本低，容量⼤，安静可靠。  
D. SRAM容量肯定⽐DRAM⼩。

<!-- ANSWER -->
A
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=高速缓存,冲突未命中,组相联,直接映射 difficulty=3 chapter=存储器层次结构 -->

【存储器层次结构】对于以下⾼速缓存系统，缓存的总容量相同，缓存块的⼤⼩也相同。下⾯哪种结构的⾼速缓存可能会出现更多的冲突未命中【tMiss】情况（）

A. 全相连⾼速缓存  
B. 直接映射⾼速缓存  
C. 2路组相连⾼速缓存  
D. 4路组相连⾼速缓存

<!-- ANSWER -->
B
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=高速缓存,写策略,回写 difficulty=2 chapter=存储器层次结构 -->

A. 回写  
B. 写分配  
C. 直写  
D. ⾮写分配

<!-- ANSWER -->
A
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=高速缓存,平均访问时间,命中率,未命中惩罚 difficulty=3 chapter=存储器层次结构 -->

【⾼速缓存】已知cache的命中率为97%，命中时的访问时间为1个时钟周期，内存的访问时间（未命中惩罚）为100个时钟周期，则CPU的平均访为\_\_\_个时钟周期。（）

A. 3.97  
B. 3.94  
C. 100  
D. 4

<!-- ANSWER -->
D
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=存储器层次结构,存储成本,高速缓存 difficulty=2 chapter=存储器层次结构 -->

【存储器层次结构】下⾯哪⼀个存储器的每⽐特【perbit】存储成本最⾼（）

A. ⾼速缓存  
B. DRAM  
C. SSD  
D. 磁盘

<!-- ANSWER -->
A
<!-- QUESTION END -->

<!-- QUESTION: qtype=multi_choice tags=存储器层次结构,局部性原理,时间局部性,空间局部性 difficulty=2 chapter=存储器层次结构 -->

【存储器层次结构】什么是程序的局部性原理。（）

A. 只在数组访问和循环访问的时候有⽤。

C. 程序趋向于访问刚刚访问过的指令或数据  
D. 包括时间局部性和空间局部性

<!-- ANSWER -->
BCD
<!-- QUESTION END -->

<!-- QUESTION: qtype=multi_choice tags=高速缓存,未命中,冷未命中,冲突未命中,容量未命中 difficulty=3 chapter=存储器层次结构 -->

【⾼速缓存】下⾯关于未命中说法正确的是（）

A. 某数据块的冷未命中必然会在第⼀次访问的时候出现。  
B. 冲突未命中是因为多个数据对象都映射到相同的数据块位置造成的，可以通过增加S来解决。  
C. 冲突未命中是因为多个数据对象都映射到相同的数据块位置造成的，可以通过增加E来解决。  
D. 容量未命中的解决⽅法可以是扩⼤⾼速缓存的容量，或者减少⼯作集的⼤⼩。

<!-- ANSWER -->
ACD
<!-- QUESTION END -->

<!-- QUESTION: qtype=fill_blank tags=存储器层次结构,磁盘容量,计算 difficulty=3 chapter=存储器层次结构 -->

【存储器层次结构】⼀个磁盘具有4个盘⽚，每个盘⽚有两⾯，每个⾯有5000个磁道，平均每个磁道有400个扇区，每个扇区的容量为512B，这个磁容量约为\_\_\_GB。

8.1 8.192

<!-- ANSWER -->
8;8.192;7.63;7.629;7.6;8.2;8.19;7.62939453125
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=高速缓存,块内偏移量,地址划分 difficulty=3 chapter=存储器层次结构 -->

【⾼速缓存】假设有⼀个具有如下属性的存储系统：

内存以字节寻址

每次内存访问位宽都是1字节

地址位宽为12，

⾼速缓存采⽤组相联结构的，有4个组，每组2个块，块⼤⼩为4字节。

<table><tr><td>起末月</td><td>折扣</td><td>行席位</td><td>T1P2</td><td>T1P3</td><td>T1P4</td><td>T1P5</td></tr><tr><td rowspan="2">0</td><td>00</td><td>1</td><td>40</td><td>41</td><td>42</td><td>43</td></tr><tr><td>83</td><td>1</td><td>FE</td><td>97</td><td>CC</td><td>D0</td></tr><tr><td rowspan="2">1</td><td>00</td><td>1</td><td>44</td><td>45</td><td>46</td><td>47</td></tr><tr><td>83</td><td>0</td><td>--</td><td>--</td><td>--</td><td>--</td></tr><tr><td rowspan="2">2</td><td>00</td><td>1</td><td>48</td><td>49</td><td>4A</td><td>4B</td></tr><tr><td>40</td><td>0</td><td>--</td><td>--</td><td>--</td><td>--</td></tr><tr><td rowspan="2">3</td><td>FF</td><td>1</td><td>9A</td><td>C0</td><td>03</td><td>FF</td></tr><tr><td>00</td><td>0</td><td>--</td><td>--</td><td>--</td><td>--</td></tr></table>

在内存地址中，哪⼏位属于⾼速缓存的块内偏移量（）。

A. 2-3  
B. 0-1  
C. 0-3  
D. 2-5

<!-- ANSWER -->
B
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=高速缓存,组索引,地址划分 difficulty=3 chapter=存储器层次结构 -->

【⾼速缓存】假设有⼀个具有如下属性的存储系统：

内存以字节寻址

每次内存访问位宽都是1字节

地址位宽为12，

⾼速缓存采⽤组相联结构的，有4个组，每组2个块，块⼤⼩为4字节。

<table><tr><td>起末月</td><td>折扣</td><td>行席位</td><td>T1P2</td><td>T1P3</td><td>T1P4</td><td>T1P5</td></tr><tr><td rowspan="2">0</td><td>00</td><td>1</td><td>40</td><td>41</td><td>42</td><td>43</td></tr><tr><td>83</td><td>1</td><td>FE</td><td>97</td><td>CC</td><td>D0</td></tr><tr><td rowspan="2">1</td><td>00</td><td>1</td><td>44</td><td>45</td><td>46</td><td>47</td></tr><tr><td>83</td><td>0</td><td>--</td><td>--</td><td>--</td><td>--</td></tr><tr><td rowspan="2">2</td><td>00</td><td>1</td><td>48</td><td>49</td><td>4A</td><td>4B</td></tr><tr><td>40</td><td>0</td><td>--</td><td>--</td><td>--</td><td>--</td></tr><tr><td rowspan="2">3</td><td>FF</td><td>1</td><td>9A</td><td>C0</td><td>03</td><td>FF</td></tr><tr><td>00</td><td>0</td><td>--</td><td>--</td><td>--</td><td>--</td></tr></table>

⾼速缓存的组索引有\_\_\_\_位（）

A. 1  
B. 4  
C. 2  
D. 3

<!-- ANSWER -->
C
<!-- QUESTION END -->

<!-- QUESTION: qtype=single_choice tags=高速缓存,缓存读取,地址映射 difficulty=4 chapter=存储器层次结构 -->

【⾼速缓存】假设有⼀个具有如下属性的存储系统：

内存以字节寻址

每次内存访问位宽都是1字节

地址位宽为12，

⾼速缓存采⽤组相联结构的，有4个组，每组2个块，块⼤⼩为4字节。

<table><tr><td>起末月</td><td>折扣</td><td>行席位</td><td>T1P2</td><td>T1P3</td><td>T1P4</td><td>T1P5</td></tr><tr><td rowspan="2">0</td><td>00</td><td>1</td><td>40</td><td>41</td><td>42</td><td>43</td></tr><tr><td>83</td><td>1</td><td>FE</td><td>97</td><td>CC</td><td>D0</td></tr><tr><td rowspan="2">1</td><td>00</td><td>1</td><td>44</td><td>45</td><td>46</td><td>47</td></tr><tr><td>83</td><td>0</td><td>--</td><td>--</td><td>--</td><td>--</td></tr><tr><td rowspan="2">2</td><td>00</td><td>1</td><td>48</td><td>49</td><td>4A</td><td>4B</td></tr><tr><td>40</td><td>0</td><td>--</td><td>--</td><td>--</td><td>--</td></tr><tr><td rowspan="2">3</td><td>FF</td><td>1</td><td>9A</td><td>C0</td><td>03</td><td>FF</td></tr><tr><td>00</td><td>0</td><td>--</td><td>--</td><td>--</td><td>--</td></tr></table>

当CPU读取0x830处的内存地址的1字节数据，该数据的值是？（）

A. 0xCC  
B. 0xFE  
C. 0x40  
D. ⾼速缓存未命中

<!-- ANSWER -->
B
<!-- QUESTION END -->
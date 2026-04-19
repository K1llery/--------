# Algorithms

## 推荐

- TopKSelector（小顶堆）
	- 目标：在推荐场景返回前 k 个结果，避免全量排序
	- 实现：堆大小固定为 k，分数更高时替换堆顶
	- 复杂度：$O(n \log k)$，空间 $O(k)$
	- 说明：同分场景使用序号打破比较歧义，避免 dict 比较异常

- quickselect_top_k（部分排序）
	- 目标：快速筛选前 k 项并只排序前 k
	- 实现：Quickselect 分区后对前 k 项排序
	- 复杂度：平均 $O(n + k\log k)$，最坏 $O(n^2)$
	- 说明：评分值一次性缓存，评分函数调用次数压缩为 $O(n)$

## 查询

- HashIndex（精确查找）
	- 复杂度：构建 $O(n)$，查询平均 $O(1)$

- TrieIndex（前缀查找）
	- 复杂度：插入 $O(L)$，前缀查询 $O(P + R)$
	- 其中 $L$ 是词长，$P$ 是前缀长度，$R$ 是返回结果规模

- InvertedIndex（多关键字检索）
	- 复杂度：构建 $O(T)$，查询为关键词倒排集合交集
	- 其中 $T$ 是分词总量

## 选路

- Graph.shortest_path（Dijkstra）
	- 支持 distance/time/congestion/scenic 策略
	- 复杂度：$O(E \log V)$

- Graph.shortest_distances（单源最短路复用）
	- 目标：一次求出起点到所有节点距离，供设施查询和多点规划复用
	- 复杂度：$O(E \log V)$
	- 收益：附近设施查询由“每设施一次最短路”降为“单次最短路 + 线性筛选”

- Held-Karp（小规模精确闭环）
	- 场景：目标点数量较少（<=8）
	- 实现：单源距离表 + 状压 DP
	- 复杂度：
		- 距离预计算：$O(m\cdot E\log V)$
		- 动态规划：$O(m^2 2^m)$
	- 其中 $m$ 为目标点数量

- Nearest Neighbor + 2-opt（大规模近似闭环）
	- 场景：目标点数量较多（>8）
	- 实现：先贪心构造可行回路，再用 2-opt 局部改良
	- 复杂度：
		- 距离预计算：$O(m\cdot E\log V)$
		- 邻近贪心：$O(m^2)$
		- 2-opt：与迭代轮次相关，典型 $O(i\cdot m^2)$

## 压缩

- HuffmanCodec（无损压缩）
	- 目标：对日记内容进行可逆压缩展示
	- 复杂度：构树与编码表构建近似 $O(n\log \sigma)$，解码 $O(n)$
	- 其中 $\sigma$ 是字符种类数

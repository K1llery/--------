# Algorithms

本文档只记录算法职责、落点和复杂度。接口调用方式见 `api.md`。

| 能力 | 文件 | 职责 | 复杂度 |
|---|---|---|---|
| Top-K 推荐 | `backend/app/algorithms/topk.py` | 用固定大小小顶堆返回前 k 个目的地，避免全量排序。 | `O(n log k)`，空间 `O(k)` |
| Quickselect 推荐 | `backend/app/algorithms/topk.py` | 部分选择前 k 项，再只排序候选集；评分函数结果缓存一次。 | 平均 `O(n + k log k)` |
| Hash 精确查询 | `backend/app/algorithms/search.py` | 按名称或 ID 做精确索引查找。 | 构建 `O(n)`，查询均摊 `O(1)` |
| Trie 前缀查询 | `backend/app/algorithms/search.py` | 支持目的地名称前缀检索。 | 插入 `O(L)`，查询 `O(P + R)` |
| 倒排索引 | `backend/app/algorithms/search.py` | 支持多关键词联合检索。 | 构建 `O(T)`，查询为倒排集合交集 |
| Dijkstra/A* | `backend/app/algorithms/graph.py` | 支持 distance/time/congestion/scenic 策略的最短路。 | `O(E log V)` |
| 单源距离表 | `backend/app/algorithms/graph.py` | 一次计算起点到所有节点距离，供设施排序和多点路线复用。 | `O(E log V)` |
| Held-Karp | `backend/app/algorithms/tsp.py` | 目标点较少时求精确多点闭环。 | `O(m^2 2^m)`，另有 `m` 次最短路预计算 |
| Nearest Neighbor + 2-opt | `backend/app/algorithms/tsp.py` | 目标点较多时构造近似闭环并局部优化。 | 典型 `O(i * m^2)`，另有最短路预计算 |
| Huffman | `backend/app/algorithms/compression.py` | 对日记文本做可逆压缩、解压和压缩率展示。 | 构树约 `O(n log s)`，解码 `O(n)` |

## 服务落点

| 服务 | 使用的算法 | 职责 |
|---|---|---|
| `RecommendationService` | Top-K、Quickselect | 目的地推荐、美食推荐和推荐日记排序。 |
| `SearchService` | Hash、Trie、倒排索引 | 目的地搜索和关键词匹配。 |
| `RoutePlanningService` | Dijkstra/A*、Held-Karp、2-opt | 单点和多点路线规划。 |
| `NearbyFacilityService` | 单源最短路 | 附近设施按图距离排序。 |
| `IndoorNavigationService` | Dijkstra | 楼宇内跨层和无障碍导航。 |
| `DiaryService` | 倒排索引、Huffman | 日记检索、压缩和解压。 |

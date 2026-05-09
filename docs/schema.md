# Schema

生产默认使用 SQLite。`SQLiteRepository` 只维护一张 `collections` 表，每个业务集合以 JSON 数组保存，降低课程部署中的迁移复杂度。`DatasetRepository` 仍用于测试和无数据库演示。课程数据规模要求见 `course-requirements.md`。

## SQLite 表

| 表 | 字段 | 职责 |
|---|---|---|
| `collections` | `name TEXT PRIMARY KEY` | 集合名，如 `destinations`、`users`、`diaries`。 |
| `collections` | `payload TEXT NOT NULL` | 该集合的 JSON 数组文本。 |
| `collections` | `updated_at TEXT NOT NULL` | 最近写入时间。 |

## 集合职责

| 文件 / 集合 | 职责 |
|---|---|
| `destinations.json` | 目的地基础信息、评分、标签和坐标。 |
| `featured_destinations.json` | 首页精选目的地。 |
| `scenes.json` | 地图场景元信息。 |
| `edges.json` | 室外图边和权重。 |
| `facilities.json` | 公共设施 POI。 |
| `foods.json` | 美食 POI。 |
| `buildings.json` | 可室内导航的楼宇入口。 |
| `indoors.json` | 楼宇内节点、楼层、房间和连边。 |
| `users.json` | 演示账号和运行期用户。 |
| `sessions.json` | 登录会话。 |
| `diaries.json` | 旅游日记正文、图片和互动计数。 |
| `diary_ratings.json` | 用户对日记的评分。 |
| `data_sources.json` | 数据来源说明。 |
| `summary.json` | 数据规模摘要，供导入状态和验收检查使用。 |

## 课程数据阈值

| 数据项 | PPT 阈值 | 当前快照 |
|---|---|---|
| 景区/校园目的地 | `>= 200` | `destinations.json`: 3701 |
| 内部建筑物/景点/场所 | `>= 20` | `buildings.json`: 40 |
| 服务设施类型 | `>= 10` | `facilities.json` 的 `facility_type`: 15 |
| 服务设施数量 | `>= 50` | `facilities.json`: 52 |
| 道路边数 | `>= 200` | `edges.json`: 548 |
| 系统用户数 | `>= 10` | `users.json`: 14 |

美食推荐没有明确数量阈值，但 PPT 要求演示前 10 美食的部分排序思路。当前 `foods.json` 为 8 条，若最终课堂验收要求展示 10 条结果，应先扩充该快照。

## 数据边界

- `datasets/prod/` 是 SQLite 初始化快照，不在测试中直接写入。
- API 测试通过 `tmp_path` 和依赖覆盖隔离数据。
- `datasets/raw/` 是抓取原始结果；生产部署不依赖该目录。
- 用户、会话、日记、评分和生成图片属于运行期数据。

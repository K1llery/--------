# Schema

生产默认使用 SQLite。`SQLiteRepository` 只维护一张 `collections` 表，每个业务集合以 JSON 数组保存，降低课程部署中的迁移复杂度。`DatasetRepository` 仍用于测试和无数据库演示。

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

## 数据边界

- `datasets/prod/` 是 SQLite 初始化快照，不在测试中直接写入。
- API 测试通过 `tmp_path` 和依赖覆盖隔离数据。
- `datasets/raw/` 是抓取原始结果；生产部署不依赖该目录。
- 用户、会话、日记、评分和生成图片属于运行期数据。

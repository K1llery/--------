# Schema

生产 SQLite 使用轻量 `collections` 表承载各业务集合，保留原 JSON 快照的字段结构，避免在 2c2g 部署中维护复杂关系型迁移。

| 表 | 字段 | 说明 |
|---|---|---|
| `collections` | `name TEXT PRIMARY KEY` | 集合名，如 `destinations`、`users`、`diaries` |
| `collections` | `payload TEXT NOT NULL` | JSON 数组文本 |
| `collections` | `updated_at TEXT NOT NULL` | 最近写入时间 |

## 核心实体

- `users`
- `destinations`
- `scenes`
- `buildings`
- `facilities`
- `roads`
- `edges`
- `food_pois`
- `diaries`
- `diary_ratings`

## 关键关系

- 一个 `destination` 可对应多个 `scene`
- 一个 `scene` 可挂接多个建筑、设施和边
- `diary` 由用户创建，并与目的地名称关联

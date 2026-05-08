# Architecture

系统采用前后端分离架构：前端为 Vue 3 + TypeScript，后端为 FastAPI。生产部署默认使用 SQLite，JSON 快照仅作为初始化数据和测试隔离数据源。

## 分层结构

- 展示层：`frontend/`
	- 页面与状态管理，负责推荐、搜索、路线、设施、美食、日记互动等交互展示
- 接口层：`backend/app/api/`
	- 对外提供 REST API，并完成参数校验与鉴权入口
- 业务服务层：`backend/app/services/`
	- 聚合推荐、搜索、路线规划、设施查询、日记互动等业务逻辑
- 算法层：`backend/app/algorithms/`
	- Top-K、Quickselect、Hash/Trie/倒排索引、Dijkstra/A*、Held-Karp、2-opt、Huffman
- 数据层：`backend/app/repositories/`
	- `SQLiteRepository` 是生产默认路径，将各业务集合保存到 SQLite `collections` 表
	- `DatasetRepository` 保留给测试和无数据库演示，读取 `datasets/prod/` 快照
- AI 网关：`backend/app/services/ai_service.py`
	- 后端统一持有 DashScope API Key，提供日记草稿生成和万相 2.7 生图能力
	- 生成图片会下载到本地持久目录，再通过 `/media/generated/...` 暴露
- 数据管线：`data_pipeline/scripts/`
	- 负责示例数据抓取、构建与更新

## 核心能力落地

- 推荐：Top-K 与 Quickselect 组合，避免无必要全量排序
- 搜索：精确匹配 + 前缀检索 + 多关键词倒排检索
- 路线：单点最短路、多点闭环（小规模精确、大规模近似）
- 室内：楼宇内大门-电梯-楼层-房间导航（含无障碍模式）
- 设施：单源最短路复用后按图距离排序
- 日记：发布、检索、浏览计数、评分、压缩与解压回环、AIGC 分镜动画生成、通义千问日记草稿、万相封面生图

## 运行时数据路径

- 默认 SQLite 文件为 `storage/travel.db`，可通过 `TRAVEL_SQLITE_PATH` 覆盖
- 初次部署使用 `python scripts/init_sqlite.py --database-path ../storage/travel.db` 从 `datasets/prod/` 初始化
- 交互性数据（如 sessions、users、diaries、diary_ratings）写入 SQLite
- API 自动化测试已使用临时目录隔离，避免污染演示基线数据

## 部署裁剪

- PostgreSQL、PostGIS、Alembic、Docker 数据库编排不再是默认运行栈
- `data_pipeline/` 仅用于本地重新生成数据，不在 2c2g 服务器上执行
- Admin/Agents 调试展示页不注册到生产路由，减少暴露面

## 数据真实性边界

- 地理点位与场景基础数据来源包含 OSM / Overpass 与公开数据整理
- 校园/景区样板中的节点与设施优先使用真实抓取结果
- 用户与日记等互动数据为课程演示种子 + 运行期写入数据

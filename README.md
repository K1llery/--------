# 北京高校与景区个性化旅游系统

面向《数据结构课程设计》教师 PPT 要求的前后端分离旅游系统。系统以北京高校和景区为主要场景，覆盖推荐、搜索、路线规划、室内导航、附近设施、美食推荐、旅游日记和 AI 辅助创作。课程要求的完整提取见 `docs/course-requirements.md`。

## 核心能力

- 目的地推荐：Top-K 与 Quickselect 返回高分目的地。
- 搜索：精确匹配、前缀检索和多关键词倒排检索。
- 路线：以 `edges.json` 道路图为权威模型，Dijkstra/A* 单点路线，Held-Karp 与 2-opt 多点闭环路线，支持距离、时间、拥挤度和交通方式策略。
- 室内导航：支持大门、电梯、楼层、房间和无障碍策略。
- 设施与美食：设施按图距离排序而非直线距离，美食支持热度、评分、距离和菜系筛选。
- 日记：浏览、检索、发布、浏览计数、评分、压缩/解压、AIGC 分镜。
- AI：DashScope 通义千问生成日记草稿，Wan 2.7 生成封面图并保存到本地媒体目录。

## 课程要求摘要

| 类别 | 老师 PPT 要求 | 当前项目落点 |
|---|---|---|
| 数据规模 | 景区/校园不少于 200 个；内部建筑物不少于 20 个；服务设施不少于 10 类、50 个；道路边不少于 200 条；用户不少于 10 人。 | 当前快照：目的地 3701、建筑物 40、设施 52、设施类型 15、边 548、用户 14。 |
| 推荐与查询 | 按热度、评价、兴趣推荐；Top-10 不做完全排序；查询不能用 `O(n)`；支持名称、类别、关键字和多关键字查询。 | Top-K、Quickselect、Hash、Trie、倒排索引。 |
| 路线规划 | 单目标最短路、多目标闭环、地图展示、路径展示、最短距离、最短时间、拥挤度、交通工具限制、室内导航。 | `edges.json` 有向道路图、Dijkstra/A*、Held-Karp、Nearest Neighbor + 2-opt、Leaflet 地图、室内导航服务。 |
| 场所查询 | 选中地点后查附近设施，按距离排序且不能按直线距离；支持类别过滤和类别名称查询。 | `NearbyFacilityService` 复用单源最短路，按图距离排序。 |
| 日记与 AIGC | 日记统一管理、浏览量、评分、推荐、精确查询、全文检索、无损压缩、根据照片和文字生成旅游动画。 | 日记 API、倒排索引、Huffman、AIGC 分镜、AI 草稿和 AI 封面。 |
| 美食推荐 | 选中景点/学校后按热度、评价、距离排序，按菜系过滤；前 10 不做完全排序；支持模糊查询。 | 美食页和 `/api/foods` 已有展示与筛选；当前 `foods.json` 为 8 条，若验收强调 Top-10 展示，建议扩充到 10 条以上。 |
| 智能体与文档 | 使用智能体辅助设计、开发、测试、协作和文档；交付完整开发文档与用户说明。 | `.github/agents/`、`AGENTS.md`、`docs/`。 |

## 技术栈

- 前端：Vue 3、TypeScript、Vite、Pinia、Vue Router、Leaflet。
- 后端：FastAPI、Pydantic、Uvicorn、pytest、ruff。
- 数据：生产默认 SQLite；`datasets/prod/` 是初始化和测试快照。
- 算法：堆、Quickselect、Hash、Trie、倒排索引、Dijkstra、A*、Held-Karp、2-opt、Huffman。

## 本地运行

后端：

```powershell
cd backend
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\init_sqlite.py --dataset-dir ..\datasets\prod --database-path ..\storage\travel.db
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

前端：

```powershell
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

访问 `http://127.0.0.1:5173`。后端 API 前缀为 `/api`。

## 配置

后端读取 `backend/.env`，可从 `backend/.env.example` 复制：

```env
TRAVEL_STORAGE_BACKEND=sqlite
TRAVEL_SQLITE_PATH=../storage/travel.db
TRAVEL_DATASET_DIR=../datasets/prod
TRAVEL_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
TRAVEL_GENERATED_MEDIA_DIR=../storage/media/generated
TRAVEL_GENERATED_MEDIA_URL_PREFIX=/media/generated
DASHSCOPE_API_KEY=
TRAVEL_AI_TEXT_MODEL=qwen-plus
TRAVEL_AI_IMAGE_MODEL=wan2.7-image
```

未配置 `DASHSCOPE_API_KEY` 时，普通业务功能仍可运行，AI 草稿和 AI 生图接口会返回业务错误。

## 目录职责

| 路径 | 职责 |
|---|---|
| `backend/` | FastAPI 服务、业务服务、算法实现、SQLite 初始化和后端测试。 |
| `frontend/` | Vue 单页应用、页面、组件、状态管理和前端构建配置。 |
| `data_pipeline/` | 本地抓取公开地理数据并生成演示数据快照。 |
| `datasets/prod/` | 可直接导入 SQLite 的生产初始化快照。 |
| `datasets/raw/` | OSM/Overpass 等原始抓取结果。 |
| `docs/` | 产品、架构、API、算法、数据、测试、验收、用户和部署文档。 |
| `storage/` | 本地运行时 SQLite 和生成图片目录，不入库。 |
| `.github/` | CI 工作流和课程验收辅助 agent 说明。 |

## 文档职责

| 文件 | 职责 |
|---|---|
| `AGENTS.md` | 约束代理在本仓库中的命令、架构事实和代码风格。 |
| `docs/course-requirements.md` | 从老师 PPT 提取课程硬要求，并对照当前项目落点。 |
| `docs/prd.md` | 定义产品目标、用户和核心功能范围。 |
| `docs/architecture.md` | 说明系统分层、运行路径和核心文件职责。 |
| `docs/api.md` | 维护当前生产注册的 API 清单。 |
| `docs/algorithms.md` | 说明算法职责、使用场景和复杂度。 |
| `docs/schema.md` | 说明 SQLite 存储模型和数据集合职责。 |
| `docs/test-plan.md` | 说明测试范围、测试文件职责和验收前命令。 |
| `docs/acceptance-script.md` | 提供课堂演示顺序和每步证据点。 |
| `docs/user-guide.md` | 面向使用者说明主要页面和操作流程。 |
| `docs/deployment-1panel-aliyun.md` | 说明 1Panel + 阿里云 2c2g 部署要点。 |

## 常用命令

```powershell
cd backend
python -m pytest tests/ -x -q
ruff check .
ruff format --check .
```

```powershell
cd frontend
npm run lint
npm run typecheck
npm run build
```

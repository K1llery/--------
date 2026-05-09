# 北京高校与景区个性化旅游系统

面向数据结构课程设计的前后端分离旅游系统。系统以北京高校和景区为主要场景，覆盖推荐、搜索、路线规划、室内导航、附近设施、美食推荐、旅游日记和 AI 辅助创作。

## 核心能力

- 目的地推荐：Top-K 与 Quickselect 返回高分目的地。
- 搜索：精确匹配、前缀检索和多关键词倒排检索。
- 路线：Dijkstra/A* 单点路线，Held-Karp 与 2-opt 多点闭环路线。
- 室内导航：支持大门、电梯、楼层、房间和无障碍策略。
- 设施与美食：基于图距离和标签筛选提供附近服务。
- 日记：浏览、检索、发布、浏览计数、评分、压缩/解压、AIGC 分镜。
- AI：DashScope 通义千问生成日记草稿，Wan 2.7 生成封面图并保存到本地媒体目录。

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

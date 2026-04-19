# 北京高校与景区个性化旅游系统

基于真实地理数据、课程设计算法要求和前后端分离架构实现的个性化旅游系统。项目覆盖景区/校园推荐、路线规划、附近设施查询、美食推荐、旅游日记管理与全文检索，并为课程验收准备了完整的工程目录、文档骨架和数据导入链路。

## 技术栈

- 前端：Vue 3、TypeScript、Vite、Pinia、Vue Router、Leaflet
- 后端：FastAPI、SQLAlchemy、Pydantic、Uvicorn
- 数据：PostgreSQL + PostGIS（开发期也支持 JSON 数据快照做演示）
- 算法：堆、Quickselect、Trie、倒排索引、Dijkstra、A*、Held-Karp、2-opt、Huffman

## 快速开始

### WSL + Windows 浏览器（推荐）

如果项目在 WSL 中运行，但用 Windows 的 Edge/Chrome 打开前端页面，请按以下方式启动：

```bash
# 终端 1：后端
cd backend
source ../.venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 终端 2：前端
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

然后在 Windows 浏览器访问：

- `http://127.0.0.1:5173`
- 或 `http://localhost:5173`

### 1. 后端虚拟环境

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. 前端

```powershell
cd frontend
npm install
npm run dev
```

### 3. 真实数据抓取

```powershell
cd data_pipeline
..\backend\.venv\Scripts\python.exe scripts\fetch_osm_data.py
..\backend\.venv\Scripts\python.exe scripts\build_demo_dataset.py
```

## 目录

- `backend/`：FastAPI 服务、算法实现、数据模型、测试
- `frontend/`：Vue 前端、地图与演示页面
- `data_pipeline/`：真实数据抓取与清洗脚本
- `datasets/`：原始快照、清洗结果和演示数据
- `docs/`：课程报告所需文档骨架
- `infra/`：数据库与环境说明

## 当前状态

当前仓库已完成：

- 工程结构初始化
- 后端基础 API、算法模块与测试样例
- 前端页面骨架与 API 集成层
- 真实数据抓取脚本与演示数据构建脚本
- 课程设计文档模板

## 数据说明

- `datasets/raw/beijing_destinations_osm.json`、`datasets/raw/bupt_scene.json`、`datasets/raw/summer_palace_scene.json` 等来源于 OpenStreetMap / Overpass 抓取结果
- `datasets/prod/destinations.json`、`facilities.json`、`foods.json` 基于真实公开地理点位构建
- `datasets/prod/users.json`、`diaries.json` 为课程演示联调用种子数据，不宣称为真实公开用户数据

后续可以继续补齐：

- PostGIS 实库接入与 Alembic 迁移
- 更大规模真实数据清洗
- 地图精细化导航与验收演示素材

## 常见通信问题排查

如果前端页面可以打开，但请求后端失败（浏览器控制台显示 CORS）：

1. 确认后端正在监听 `0.0.0.0:8000`。
2. 确认前端地址是 `http://localhost:5173` 或 `http://127.0.0.1:5173`。
3. 如需自定义来源，设置环境变量：

```bash
TRAVEL_CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173,http://<your-host>:5173"
```

## 真实图片与导航说明

- 前端会优先尝试 Wikipedia 实景缩略图；若未命中，会回退到 OpenStreetMap 实景地图快照，不再使用内置占位图作为首选显示。
- 地图导航支持“当前位置自动匹配最近起点”。如浏览器未授予定位权限，系统会自动回退到手动起点选择。

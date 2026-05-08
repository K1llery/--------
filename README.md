# 北京高校与景区个性化旅游系统

基于真实地理数据、课程设计算法要求和前后端分离架构实现的个性化旅游系统。项目覆盖景区/校园推荐、路线规划、附近设施查询、美食推荐、旅游日记管理与全文检索，并为课程验收准备了完整的工程目录、文档骨架和数据导入链路。

## 技术栈

- 前端：Vue 3、TypeScript、Vite、Pinia、Vue Router、Leaflet
- 后端：FastAPI、Pydantic、Uvicorn
- 数据：SQLite（生产默认）+ JSON 快照 seed/test
- 大模型：阿里云百炼通义千问（日记草稿）+ 万相 2.7（封面生图）
- 算法：堆、Quickselect、Trie、倒排索引、Dijkstra、A*、Held-Karp、2-opt、Huffman

## 快速开始

### WSL + Windows 浏览器（推荐）

如果项目在 WSL 中运行，但用 Windows 的 Edge/Chrome 打开前端页面，请按以下方式启动：

```bash
# 终端 1：后端
cd backend
source ../.venv/bin/activate
pip install -r requirements.txt
python scripts/init_sqlite.py --database-path ../storage/travel.db
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
python scripts/init_sqlite.py --database-path ..\storage\travel.db
uvicorn app.main:app --reload
```

### SQLite 初始化（首次）

```bash
cd backend
cp .env.example .env
python scripts/init_sqlite.py --dataset-dir ../datasets/prod --database-path ../storage/travel.db
```

`TRAVEL_STORAGE_BACKEND=sqlite` 是默认值。测试或临时演示仍可设置 `TRAVEL_STORAGE_BACKEND=json` 直接读取 `datasets/prod/`。

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
- `storage/`：本地运行时 SQLite 与生成图片目录（不入库）

## 当前状态

当前仓库已完成：

- 工程结构初始化
- 后端基础 API、算法模块与测试样例
- 前端页面骨架与 API 集成层
- 室外路线 + 室内导航（大门、电梯、楼层、房间）联动演示
- 日记 AIGC 动画分镜生成与前端播放预览
- 接入阿里云百炼：AI 帮写日记、AI 生成封面图并保存到本地 `/media/generated`
- 真实数据抓取脚本与演示数据构建脚本
- 课程设计文档模板

## 数据说明

- `datasets/raw/beijing_destinations_osm.json`、`datasets/raw/bupt_scene.json`、`datasets/raw/summer_palace_scene.json` 等来源于 OpenStreetMap / Overpass 抓取结果
- `datasets/prod/destinations.json`、`facilities.json`、`foods.json` 基于真实公开地理点位构建
- `datasets/prod/users.json`、`diaries.json` 为课程演示联调用种子数据，不宣称为真实公开用户数据

线上部署不建议在 2c2g 服务器上运行抓取链路；如需更新数据，推荐本机重新生成 JSON 后再初始化 SQLite。

## 阿里云百炼配置

后端读取环境变量，不要把 Key 写入代码：

```bash
DASHSCOPE_API_KEY=sk-你的Key
TRAVEL_AI_TEXT_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
TRAVEL_AI_IMAGE_BASE_URL=https://dashscope.aliyuncs.com/api/v1
TRAVEL_AI_TEXT_MODEL=qwen-plus
TRAVEL_AI_IMAGE_MODEL=wan2.7-image
```

上海 ECS 可以调用北京地域百炼接口，前提是 API Key 和 Base URL 属于同一地域。上线后可访问 `/api/ai/health` 检查模型配置是否被后端读到。

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

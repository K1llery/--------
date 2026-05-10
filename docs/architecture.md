# Architecture

系统采用 Vue 3 前端 + FastAPI 后端 + SQLite 存储。前端通过 `/api` 调用后端；后端路由只做请求边界，业务规则在 services，算法在 algorithms，数据读写由 repositories 统一处理。

## 分层

| 层 | 路径 | 职责 |
|---|---|---|
| 展示层 | `frontend/src/` | 页面、组件、状态管理、地图展示和用户交互。 |
| API 层 | `backend/app/api/` | 注册 REST 路由、注入服务依赖、校验请求参数。 |
| 服务层 | `backend/app/services/` | 编排推荐、搜索、路线、设施、日记、认证和 AI 业务。 |
| 算法层 | `backend/app/algorithms/` | 提供课程设计要求的数据结构和算法实现。 |
| 数据层 | `backend/app/repositories/` | 在 SQLite 和 JSON 快照之间提供统一集合读写接口。 |
| 数据管线 | `data_pipeline/` | 本地抓取和构建演示数据，不参与线上运行。 |

## 运行路径

1. 前端页面调用 `frontend/src/api/client.ts`。
2. FastAPI 在 `backend/app/api/router.py` 注册 `/api` 子路由。
3. 路由通过 `backend/app/api/deps.py` 获取缓存后的服务实例。
4. 服务调用算法模块和 repository。
5. `SQLiteRepository` 将集合保存到 `storage/travel.db` 的 `collections` 表。
6. AI 生图文件保存到 `storage/media/generated`，由 `/media/generated/...` 静态暴露。

## 核心文件职责

通配符表示同职责重复文件。`node_modules/`、`.venv/`、`storage/` 等生成目录不属于项目文档职责范围。

### 根目录、配置与自动化

| 文件 | 职责 |
|---|---|
| `README.md` | 项目入口说明、快速运行、目录职责和文档索引。 |
| `AGENTS.md` | 代理协作命令、架构事实和代码风格约束。 |
| `.gitignore` | 排除依赖、运行期数据和本地环境文件。 |
| `.github/workflows/ci.yml` | CI 中运行前端 lint/typecheck/build 和后端 ruff/pytest。 |
| `.github/agents/*.agent.md` | 课程验收辅助 agent 的角色说明。 |
| `.tocodex/plans/*.md` | 本地 Codex 历史计划记录，不参与运行。 |
| `.tocodex/progress/*.json` | 本地 Codex 进度状态，不参与运行。 |
| `backend/.env.example` | 后端环境变量模板。 |
| `backend/requirements.txt` | 后端运行和测试依赖。 |
| `backend/pyproject.toml` | ruff、pytest 等后端工具配置。 |
| `backend/alembic.ini` | 旧迁移工具配置，目前非默认运行路径。 |
| `frontend/.env.example` | 前端环境变量模板。 |
| `frontend/.prettierrc.json` | 前端格式化规则。 |
| `frontend/eslint.config.js` | 前端 ESLint 规则。 |
| `frontend/package.json` | 前端脚本和依赖声明。 |
| `frontend/package-lock.json` | 前端依赖锁定。 |
| `frontend/tsconfig.json` | TypeScript 编译配置。 |
| `frontend/vite.config.ts` | Vite 构建配置。 |
| `frontend/index.html` | Vue 应用挂载入口。 |

### 后端文件

| 文件 | 职责 |
|---|---|
| `backend/app/main.py` | 创建 FastAPI 应用、注册 API、错误处理、日志和静态媒体目录。 |
| `backend/app/__init__.py` | 后端应用包标记。 |
| `backend/app/core/config.py` | 读取环境变量并规范化路径、CORS、AI 和存储配置。 |
| `backend/app/core/exceptions.py` | 定义业务异常层级。 |
| `backend/app/core/error_handlers.py` | 将业务异常转换为统一 JSON 响应。 |
| `backend/app/core/logging.py` | 配置 plain-text 日志格式。 |
| `backend/app/api/router.py` | 汇总注册当前生产 API 路由。 |
| `backend/app/api/deps.py` | 缓存 repository 和 service 依赖。 |
| `backend/app/api/routes/ai.py` | AI 健康检查、日记草稿和生图接口。 |
| `backend/app/api/routes/auth.py` | 注册、登录、登出、当前用户、演示账号和收藏接口。 |
| `backend/app/api/routes/destinations.py` | 目的地列表、精选、推荐和搜索接口。 |
| `backend/app/api/routes/routes.py` | 指定地点、自动漫游、多点和最近设施路线接口。 |
| `backend/app/api/routes/indoor.py` | 楼宇列表和室内路线接口。 |
| `backend/app/api/routes/map_data.py` | 地图场景列表和场景详情接口。 |
| `backend/app/api/routes/facilities.py` | 附近设施接口。 |
| `backend/app/api/routes/foods.py` | 美食 POI 接口。 |
| `backend/app/api/routes/diaries.py` | 日记列表、详情、发布、搜索、互动、压缩和 AIGC 分镜接口。 |
| `backend/app/api/routes/__init__.py` | 路由包标记。 |
| `backend/app/algorithms/topk.py` | Top-K 堆和 Quickselect 推荐算法。 |
| `backend/app/algorithms/search.py` | Hash、Trie 和倒排索引。 |
| `backend/app/algorithms/graph.py` | 图结构、Dijkstra/A* 和单源距离表。 |
| `backend/app/algorithms/tsp.py` | Held-Karp、Nearest Neighbor 和 2-opt。 |
| `backend/app/algorithms/compression.py` | Huffman 压缩和解压。 |
| `backend/app/algorithms/__init__.py` | 算法包标记。 |
| `backend/app/repositories/data_loader.py` | JSON 快照 repository 和数据加载工具。 |
| `backend/app/repositories/sqlite_repository.py` | SQLite `collections` 表读写实现。 |
| `backend/app/services/auth_service.py` | 用户、会话、演示账号和收藏逻辑。 |
| `backend/app/services/recommendation_service.py` | 目的地、美食和日记推荐逻辑。 |
| `backend/app/services/search_service.py` | 目的地搜索索引构建和查询。 |
| `backend/app/services/graph_builder.py` | 从场景、设施和 `edges` 权威道路边构建可复用有向图。 |
| `backend/app/services/routing_service.py` | 室外指定地点、自动漫游、多点闭环和最近设施路线业务。 |
| `backend/app/services/facility_service.py` | 附近设施按图距离排序。 |
| `backend/app/services/indoor_service.py` | 室内跨层和无障碍路线。 |
| `backend/app/services/diary_service.py` | 日记检索、发布、互动、压缩和 AIGC 分镜。 |
| `backend/app/services/ai_service.py` | DashScope 文本和图片模型网关。 |
| `backend/app/services/__init__.py` | 服务包标记。 |
| `backend/app/schemas/ai.py` | AI 请求和响应模型。 |
| `backend/app/schemas/common.py` | 通用响应模型。 |
| `backend/app/schemas/destination.py` | 目的地、搜索和推荐模型。 |
| `backend/app/schemas/diary.py` | 日记、互动、压缩和 AIGC 模型。 |
| `backend/app/schemas/indoor.py` | 室内导航模型。 |
| `backend/app/schemas/routing.py` | 室外路线模型。 |
| `backend/app/scripts/seed_sqlite.py` | 供应用内复用的 SQLite 初始化逻辑。 |
| `backend/app/scripts/__init__.py` | 脚本包标记。 |
| `backend/scripts/init_sqlite.py` | 命令行初始化 SQLite 数据库。 |
| `backend/scripts/bootstrap_data.ps1` | Windows 下初始化演示数据的辅助脚本。 |

### 后端测试文件

| 文件 | 职责 |
|---|---|
| `backend/tests/conftest.py` | 测试数据隔离和 FastAPI 依赖覆盖。 |
| `backend/tests/test_algorithms.py` | 算法、室内导航、压缩和 AIGC 分镜测试。 |
| `backend/tests/test_api.py` | 主要业务 API 回归测试。 |
| `backend/tests/test_ai_api.py` | AI 接口和错误路径测试。 |
| `backend/tests/test_sqlite_repository.py` | SQLite repository 持久化测试。 |

### 前端文件

| 文件 | 职责 |
|---|---|
| `frontend/src/main.ts` | 创建 Vue 应用并挂载插件。 |
| `frontend/src/App.vue` | 顶层布局和路由出口。 |
| `frontend/src/env.d.ts` | Vite 环境类型声明。 |
| `frontend/src/api/client.ts` | axios 客户端和 API 方法封装。 |
| `frontend/src/router/index.ts` | 页面路由表。 |
| `frontend/src/styles/main.css` | 全局样式、布局和视觉变量。 |
| `frontend/src/types/api.ts` | API 层 TypeScript 类型。 |
| `frontend/src/types/models.ts` | 前端领域模型类型。 |
| `frontend/src/utils/realMedia.ts` | 真实图片和地图兜底地址生成。 |
| `frontend/src/pages/HomePage.vue` | 首页和系统概览。 |
| `frontend/src/pages/DestinationPage.vue` | 目的地列表、筛选和推荐。 |
| `frontend/src/pages/SearchPage.vue` | 搜索体验和结果展示。 |
| `frontend/src/pages/RoutePage.vue` | 问答式路线规划、地图路径高亮和分段导航展示。 |
| `frontend/src/pages/FacilityPage.vue` | 附近设施查询。 |
| `frontend/src/pages/FoodPage.vue` | 美食 POI 展示。 |
| `frontend/src/pages/DiaryPage.vue` | 日记列表、详情、互动、压缩、AI 草稿和封面。 |
| `frontend/src/stores/auth.ts` | 登录状态、用户和收藏状态。 |
| `frontend/src/stores/destinations.ts` | 目的地和推荐数据状态。 |
| `frontend/src/stores/diaries.ts` | 日记列表、搜索和互动状态。 |
| `frontend/src/stores/foods.ts` | 美食数据状态。 |
| `frontend/src/stores/toast.ts` | 全局提示消息状态。 |
| `frontend/src/stores/travel.ts` | 跨页面旅行场景状态。 |
| `frontend/src/components/AuthModal.vue` | 登录和注册弹窗。 |
| `frontend/src/components/EmptyState.vue` | 空状态展示。 |
| `frontend/src/components/MapPlaceholder.vue` | 地图不可用时的兜底展示。 |
| `frontend/src/components/PanelCard.vue` | 通用面板容器。 |
| `frontend/src/components/RealImage.vue` | 实景图片加载和兜底。 |
| `frontend/src/components/RouteMap.vue` | Leaflet 路线地图。 |
| `frontend/src/components/SkeletonCard.vue` | 加载骨架屏。 |
| `frontend/src/components/ToastContainer.vue` | 全局 toast 容器。 |
| `frontend/src/components/route/IndoorRoutePanel.vue` | 室内导航表单和结果。 |
| `frontend/src/components/route/LocationCapture.vue` | 浏览器定位和起点选择。 |
| `frontend/src/components/route/OutdoorRoutePanel.vue` | 室外路线表单和结果。 |
| `frontend/src/components/route/RouteInfoCards.vue` | 路线距离、时间和策略卡片。 |
| `frontend/src/components/route/TravelProfileSelector.vue` | 出行偏好选择。 |
| `frontend/src/composables/useGeolocation.ts` | 浏览器定位状态封装。 |
| `frontend/src/composables/useIndoorNavigation.ts` | 室内导航状态和请求封装。 |
| `frontend/src/composables/useRoutePlanner.ts` | 室外路线状态和请求封装。 |
| `frontend/src/composables/useSceneLoader.ts` | 地图场景加载封装。 |
| `frontend/src/directives/reveal.ts` | 元素进入视口动画指令。 |
| `frontend/src/directives/ripple.ts` | 点击波纹指令。 |
| `frontend/src/directives/tilt.ts` | 轻量倾斜交互指令。 |
| `frontend/public/media/destinations/destination-01.svg` 至 `destination-16.svg` | 目的地兜底插画资产。 |
| `frontend/public/media/foods/food-01.svg` 至 `food-08.svg` | 美食兜底插画资产。 |
| `frontend/public/media/system/explore.svg` | 系统探索插画资产。 |

### 数据与管线文件

| 文件 | 职责 |
|---|---|
| `data_pipeline/scripts/fetch_osm_data.py` | 抓取 OSM/Overpass 原始地理数据。 |
| `data_pipeline/scripts/build_demo_dataset.py` | 将原始数据整理为 `datasets/prod/` 快照。 |
| `datasets/prod/buildings.json` | 可室内导航楼宇。 |
| `datasets/prod/data_sources.json` | 数据来源说明。 |
| `datasets/prod/destinations.json` | 目的地数据。 |
| `datasets/prod/diaries.json` | 日记种子数据。 |
| `datasets/prod/diary_ratings.json` | 日记评分种子数据。 |
| `datasets/prod/edges.json` | 室外图边。 |
| `datasets/prod/facilities.json` | 设施 POI。 |
| `datasets/prod/featured_destinations.json` | 首页精选目的地。 |
| `datasets/prod/foods.json` | 美食 POI。 |
| `datasets/prod/indoors.json` | 室内节点和边。 |
| `datasets/prod/scenes.json` | 地图场景。 |
| `datasets/prod/sessions.json` | 会话种子数据。 |
| `datasets/prod/summary.json` | 数据规模摘要。 |
| `datasets/prod/users.json` | 用户和演示账号种子数据。 |
| `datasets/raw/beijing_destinations_osm.json` | 北京目的地原始抓取结果。 |
| `datasets/raw/bupt_foods.json` | 北邮周边美食原始数据。 |
| `datasets/raw/bupt_scene.json` | 北邮场景原始数据。 |
| `datasets/raw/summer_palace_foods.json` | 颐和园周边美食原始数据。 |
| `datasets/raw/summer_palace_scene.json` | 颐和园场景原始数据。 |
| `datasets/raw/.gitkeep` | 保留 raw 空目录。 |
| `datasets/staging/.gitkeep` | 保留 staging 空目录。 |

### 文档文件

| 文件 | 职责 |
|---|---|
| `docs/course-requirements.md` | 从老师 PPT 提取课程数据、功能、算法、智能体和交付要求。 |
| `docs/prd.md` | 产品目标、用户和功能边界。 |
| `docs/architecture.md` | 系统分层、运行路径和文件职责。 |
| `docs/api.md` | 当前生产 API 清单。 |
| `docs/algorithms.md` | 算法职责、落点和复杂度。 |
| `docs/schema.md` | SQLite 表和集合职责。 |
| `docs/test-plan.md` | 测试范围、测试文件职责和验收前命令。 |
| `docs/acceptance-script.md` | 课堂演示流程和证据点。 |
| `docs/user-guide.md` | 页面操作说明。 |
| `docs/deployment-1panel-aliyun.md` | 1Panel + 阿里云部署步骤。 |

## 部署裁剪

- `SQLiteRepository` 是默认运行路径；JSON repository 保留给测试和无数据库演示。
- `GraphBuilder` 是独立服务，路线和设施查询都依赖它；室外巡路以 `edges.json` 为权威道路模型。
- Admin/Agents 调试路由不注册到生产应用。
- 数据抓取只在本地执行，服务器只运行后端、静态前端和 SQLite。

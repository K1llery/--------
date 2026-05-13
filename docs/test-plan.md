# Test Plan

本文档合并测试计划和验收前检查，不再保留固定日期的测试报告快照。课程要求对照见 `course-requirements.md`。

## 命令

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

## 测试文件职责

| 文件 | 职责 |
|---|---|
| `backend/tests/conftest.py` | 构建隔离测试数据和 FastAPI 依赖覆盖。 |
| `backend/tests/test_algorithms.py` | 覆盖 Top-K、Quickselect、搜索索引、图最短路、打车模式、自动漫游、多点路线、室内导航、Huffman 和 AIGC 分镜。 |
| `backend/tests/test_api.py` | 覆盖推荐、搜索、指定地点路线、最近设施路线、自动漫游、设施、美食、日记互动和压缩 API。 |
| `backend/tests/test_ai_api.py` | 覆盖 AI 配置、草稿生成和生图接口的可控行为。 |
| `backend/tests/test_sqlite_repository.py` | 覆盖 SQLite 集合读写、初始化和运行期持久化。 |

## 覆盖范围

- 课程数据阈值：目的地 `>=200`、建筑物/景点/场所 `>=20`、设施类型 `>=10`、设施 `>=50`、边 `>=200`、用户 `>=10`。
- 数据规模：目的地、边、设施、用户和日记快照达到演示要求。
- 推荐：Top-K 不依赖全量排序，Quickselect 缓存评分函数结果。
- 搜索：精确查询、前缀查询、多关键词联合查询、全文检索和排序，避免业务查询退化为 `O(n)`。
- 路线：北邮 source map 导入、`intersection` 路口节点参与路径、POI 道路吸附、单点最短路、最近设施到达、自动漫游闭环、距离/时间/拥挤度/交通方式策略、单源距离复用、小规模精确闭环、大规模近似闭环。
- 外部路线 API：不作为验收范围；测试应确保路线接口返回 `route_source = "local"`，且不包含高德/百度 provider 字段。
- 设施：按图距离排序，并复用单源最短路，不能使用直线距离替代。
- 室内：跨层路线和轮椅模式规避楼梯边。
- 日记：列表、详情、发布、全文检索、浏览计数、登录评分、压缩/解压。
- 美食：按热度、评分、距离和菜系筛选，Top-K 逻辑不依赖完全排序。
- AI：未配置 Key 时返回业务错误，配置可用时按服务抽象生成草稿或图片。
- 前端：类型检查、Lint 和 Vite 构建。

## 数据隔离

- 测试不得修改 `datasets/prod/`。
- 需要写数据的测试使用临时目录或临时 SQLite。
- 演示数据更新应通过 `data_pipeline/` 重新生成快照，再执行 `backend/scripts/init_sqlite.py`。

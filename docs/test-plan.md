# Test Plan

本文档合并测试计划和验收前检查，不再保留固定日期的测试报告快照。

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
| `backend/tests/test_algorithms.py` | 覆盖 Top-K、Quickselect、搜索索引、图最短路、多点路线、室内导航、Huffman 和 AIGC 分镜。 |
| `backend/tests/test_api.py` | 覆盖推荐、搜索、路线、设施、美食、日记互动和压缩 API。 |
| `backend/tests/test_ai_api.py` | 覆盖 AI 配置、草稿生成和生图接口的可控行为。 |
| `backend/tests/test_sqlite_repository.py` | 覆盖 SQLite 集合读写、初始化和运行期持久化。 |

## 覆盖范围

- 数据规模：目的地、边、设施、用户和日记快照达到演示要求。
- 推荐：Top-K 不依赖全量排序，Quickselect 缓存评分函数结果。
- 搜索：精确查询、前缀查询、多关键词联合查询和排序。
- 路线：单点最短路、单源距离复用、小规模精确闭环、大规模近似闭环。
- 设施：按图距离排序，并复用单源最短路。
- 室内：跨层路线和轮椅模式规避楼梯边。
- 日记：列表、详情、发布、全文检索、浏览计数、登录评分、压缩/解压。
- AI：未配置 Key 时返回业务错误，配置可用时按服务抽象生成草稿或图片。
- 前端：类型检查、Lint 和 Vite 构建。

## 数据隔离

- 测试不得修改 `datasets/prod/`。
- 需要写数据的测试使用临时目录或临时 SQLite。
- 演示数据更新应通过 `data_pipeline/` 重新生成快照，再执行 `backend/scripts/init_sqlite.py`。

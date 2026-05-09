# 1Panel + 阿里云部署

目标环境：阿里云 2c2g ECS，1Panel 管理网站、反向代理和后端进程。

## 运行栈

| 组件 | 职责 |
|---|---|
| Nginx | 托管 `frontend/dist`，反向代理 `/api/`，暴露 `/media/generated/`。 |
| Python 3.12 venv | 运行 FastAPI/Uvicorn。 |
| SQLite | 保存 `collections` 表和运行期互动数据。 |
| 本地媒体目录 | 保存 AI 生成图片。 |

不在服务器运行 Node dev server、PostgreSQL/PostGIS、Docker 数据库和 `data_pipeline` 抓取脚本。

## 后端初始化

```bash
cd /opt/travel-system/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/init_sqlite.py --dataset-dir ../datasets/prod --database-path ../storage/travel.db
```

## 前端构建

```bash
cd frontend
npm ci
VITE_API_BASE_URL=/api npm run build
```

将 `frontend/dist` 上传给 1Panel 网站功能托管。

## 环境变量

```env
TRAVEL_STORAGE_BACKEND=sqlite
TRAVEL_SQLITE_PATH=/opt/travel-system/storage/travel.db
TRAVEL_GENERATED_MEDIA_DIR=/opt/travel-system/storage/media/generated
TRAVEL_GENERATED_MEDIA_URL_PREFIX=/media/generated
TRAVEL_CORS_ORIGINS=https://你的域名
DASHSCOPE_API_KEY=sk-你的百炼Key
TRAVEL_AI_TEXT_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
TRAVEL_AI_IMAGE_BASE_URL=https://dashscope.aliyuncs.com/api/v1
TRAVEL_AI_TEXT_MODEL=qwen-plus
TRAVEL_AI_IMAGE_MODEL=wan2.7-image
```

## 后端进程

```bash
cd /opt/travel-system/backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1 --proxy-headers
```

2c2g 服务器建议 1 worker。可用 1Panel 进程守护管理该命令。

## Nginx 要点

- `/` 指向前端 `dist`，SPA 配置 `try_files $uri $uri/ /index.html`。
- `/api/` 代理到 `http://127.0.0.1:8000/api/`。
- `/media/generated/` 指向 `/opt/travel-system/storage/media/generated/`。
- 开启 gzip。

## 验收检查

```bash
curl https://你的域名/api/ai/health
curl https://你的域名/api/destinations
```

浏览器检查登录、路线、日记、AI 草稿、AI 封面和刷新后的图片访问。

## 备份

```bash
sqlite3 /opt/travel-system/storage/travel.db ".backup '/opt/travel-system/backups/travel-$(date +%F).db'"
tar -czf /opt/travel-system/backups/generated-media-$(date +%F).tar.gz -C /opt/travel-system/storage/media generated
```

# 1Panel + 阿里云 2c2g 部署说明

## 推荐运行栈

- Nginx：服务 `frontend/dist`，反向代理 `/api/`
- Python 3.12 venv：运行 FastAPI/Uvicorn
- SQLite：`/opt/travel-system/storage/travel.db`
- 生成图片：`/opt/travel-system/storage/media/generated`
- 不在服务器运行：Node dev server、PostgreSQL/PostGIS、Docker 数据库、`data_pipeline` 抓取脚本

## 初始化

```bash
cd /opt/travel-system/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/init_sqlite.py --dataset-dir ../datasets/prod --database-path ../storage/travel.db
```

前端在本机或 CI 构建：

```bash
cd frontend
npm ci
VITE_API_BASE_URL=/api npm run build
```

将 `frontend/dist` 上传到服务器，由 1Panel 的网站/Nginx 功能托管。

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

如果百炼 API Key 不是北京地域，必须同步替换对应地域的 Base URL。

## Uvicorn

2c2g 服务器建议 1 worker：

```bash
cd /opt/travel-system/backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1 --proxy-headers
```

1Panel 可用“进程守护/应用运行时”管理该命令。

## Nginx 要点

- `/` 指向前端 `dist`，SPA 使用 `try_files $uri $uri/ /index.html`
- `/api/` 反向代理到 `http://127.0.0.1:8000/api/`
- `/media/generated/` 指向 `/opt/travel-system/storage/media/generated/`
- 开启 gzip

## 验收检查

```bash
curl https://你的域名/api/ai/health
curl https://你的域名/api/destinations
```

浏览器检查：

- 登录 demo 用户
- 打开旅游日记
- 点击“AI帮写日记”
- 点击“AI生成封面”
- 发布日记后刷新，确认封面仍可访问

## 备份

每日备份 SQLite 和生成图片：

```bash
sqlite3 /opt/travel-system/storage/travel.db ".backup '/opt/travel-system/backups/travel-$(date +%F).db'"
tar -czf /opt/travel-system/backups/generated-media-$(date +%F).tar.gz -C /opt/travel-system/storage/media generated
```

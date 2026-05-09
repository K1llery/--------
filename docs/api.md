# API

生产 API 统一挂载在 `/api` 下。路由以 `backend/app/api/router.py` 的注册结果为准。

## AI

| 方法 | 路径 | 职责 |
|---|---|---|
| `GET` | `/api/ai/health` | 检查 AI 配置是否可用。 |
| `POST` | `/api/ai/diary/draft` | 根据主题、地点和提示生成日记草稿。 |
| `POST` | `/api/ai/images/generate` | 调用 Wan 2.7 生图并保存到 `/media/generated/...`。 |

## 认证与用户

| 方法 | 路径 | 职责 |
|---|---|---|
| `POST` | `/api/auth/register` | 注册用户。 |
| `POST` | `/api/auth/login` | 登录并返回会话。 |
| `GET` | `/api/auth/me` | 读取当前用户。 |
| `POST` | `/api/auth/logout` | 登出当前会话。 |
| `GET` | `/api/auth/demo-accounts` | 返回演示账号。 |
| `GET` | `/api/auth/favorites` | 返回收藏。 |
| `POST` | `/api/auth/favorites/destinations` | 收藏目的地。 |
| `POST` | `/api/auth/favorites/routes` | 收藏路线。 |

## 目的地与搜索

| 方法 | 路径 | 职责 |
|---|---|---|
| `GET` | `/api/destinations` | 返回目的地列表。 |
| `GET` | `/api/destinations/featured` | 返回精选目的地。 |
| `POST` | `/api/destinations/recommend` | 返回个性化推荐。 |
| `POST` | `/api/destinations/search` | 执行精确、前缀和关键词搜索。 |

## 路线与地图

| 方法 | 路径 | 职责 |
|---|---|---|
| `POST` | `/api/routes/single` | 规划单点路线。 |
| `POST` | `/api/routes/multi` | 规划多点闭环路线。 |
| `POST` | `/api/routes/wander` | 根据起点、交通方式和时长自动生成随便逛逛闭环路线。 |
| `POST` | `/api/routes/nearby-facility` | 查找最近指定设施并返回到达路线。 |
| `GET` | `/api/indoor/buildings` | 返回可导航楼宇。 |
| `POST` | `/api/indoor/route` | 规划室内路线。 |
| `GET` | `/api/map/scenes` | 返回地图场景列表。 |
| `GET` | `/api/map/scenes/{scene_name}` | 返回指定场景图数据。 |

## 设施、美食与日记

| 方法 | 路径 | 职责 |
|---|---|---|
| `GET` | `/api/facilities/nearby` | 按图距离返回附近设施。 |
| `GET` | `/api/foods` | 返回美食 POI。 |
| `GET` | `/api/diaries` | 返回日记列表。 |
| `GET` | `/api/diaries/recommend` | 返回推荐日记。 |
| `GET` | `/api/diaries/{diary_id}` | 返回日记详情。 |
| `POST` | `/api/diaries` | 发布日记。 |
| `POST` | `/api/diaries/search` | 搜索日记正文。 |
| `POST` | `/api/diaries/{diary_id}/view` | 增加浏览计数。 |
| `POST` | `/api/diaries/{diary_id}/rate` | 登录后评分。 |
| `POST` | `/api/diaries/compress` | Huffman 压缩文本。 |
| `POST` | `/api/diaries/decompress` | 解压 Huffman 文本。 |
| `POST` | `/api/diaries/{diary_id}/aigc-animation` | 生成日记分镜动画脚本。 |

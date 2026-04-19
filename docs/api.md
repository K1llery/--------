# API

## 认证

- `POST /api/auth/login`
- `GET /api/auth/demo-accounts`

## 目的地

- `GET /api/destinations`
- `POST /api/destinations/recommend`
- `POST /api/destinations/search`

## 路线

- `POST /api/routes/single`
- `POST /api/routes/multi`

## 设施 / 美食 / 日记

- `GET /api/facilities/nearby`
- `GET /api/foods`
- `GET /api/diaries`
- `GET /api/diaries/{diary_id}`
- `POST /api/diaries/search`
- `POST /api/diaries/{diary_id}/view`
- `POST /api/diaries/{diary_id}/rate`
- `POST /api/diaries/compress`
- `POST /api/diaries/decompress`

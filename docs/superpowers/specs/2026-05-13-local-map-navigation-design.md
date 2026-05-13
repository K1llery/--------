# 本地地图导航重构设计

日期：2026-05-13

## 背景

当前项目的地图导航应回到课程要求本身：基于自设计数据结构和自实现算法完成路线规划，不接入高德或百度外部路线 API。`要求.md` 和 `个性化旅游平台要求.md` 对导航部分的重点是：

- 地图抽象为有向图，交叉口和建筑物可作为顶点。
- 边包含距离、拥挤度、理想速度和交通工具限制。
- 支持最短距离、最短时间、交通工具约束、混合交通、室内导航。
- 最近设施排序不能只按直线距离，应按图距离。
- 多目标路线需要从当前位置出发，参观完后返回当前位置。

`tourism-system-main` 是学长项目，其中 `backend/data/roads.json`、`buildings.json`、`facilities.json`、`places.json` 包含较完整的北邮校园地图建模数据。最终项目会删除 `tourism-system-main`，因此运行时代码和数据生成脚本不能依赖该目录。

## 目标

1. 彻底移除高德/百度外部路线 API 接入，避免课程验收时被误解为依赖第三方路线规划。
2. 以北邮校园为真实地图建模样板，吸收学长项目道路、建筑、设施和路口建模数据。
3. 保留四城 16 个精选场景的导航覆盖，用于展示项目范围。
4. 后端路线规划继续只使用本项目自实现算法：Dijkstra、A*、Held-Karp、Nearest Neighbor + 2-opt、单源最短路。
5. 设计一条后续可扩展到更多学长项目场景的数据导入路径。

## 非目标

- 不接入高德、百度、腾讯地图等外部路线 API。
- 不把 `tourism-system-main` 作为最终项目依赖。
- 不全量迁移学长项目旧 Flask/React 架构。
- 不在本阶段重做室内导航；室内导航继续使用现有 `IndoorNavigationService`。

## 推荐方案

采用“北邮真实路网样板 + 四城生成路网覆盖”的方案。

- 北邮校园 `BUPT_Main_Campus` 使用规范化后的学长项目路网数据。
- 四城其他精选场景继续使用当前项目已有精细场景和本地边数据。
- 数据导入采用一次性导入脚本，生成项目内规范化快照。
- 后续如果要完成全量迁移，只扩展导入脚本和快照文件，不重写路线算法。

## 数据资产设计

新增项目内数据快照目录：

```text
datasets/source_maps/
  bupt_campus_map.json
```

`bupt_campus_map.json` 是从 `tourism-system-main/backend/data/` 一次性导入并规范化后的数据。项目完成后即使删除 `tourism-system-main`，数据生成仍可正常运行。

建议快照结构：

```json
{
  "source": "tourism-system-main",
  "source_place_id": "place_001",
  "scene_name": "BUPT_Main_Campus",
  "center": {"latitude": 39.9577, "longitude": 116.3577},
  "nodes": [
    {
      "code": "LEGACY_intersection_001",
      "name": "路口 001",
      "node_type": "intersection",
      "latitude": 39.9577,
      "longitude": 116.3577
    }
  ],
  "buildings": [],
  "facilities": [],
  "edges": []
}
```

导入脚本只在开发时使用：

```text
tools/import_legacy_bupt_map.py
```

该脚本读取 `tourism-system-main/backend/data/roads.json`、`buildings.json`、`facilities.json`、`places.json`，输出 `datasets/source_maps/bupt_campus_map.json`。最终数据生成脚本只读取 `datasets/source_maps/bupt_campus_map.json`。

## 数据转换规则

### 场景归属

- 学长项目 `place_001` 对应本项目 `BUPT_Main_Campus`。
- 后续扩展时新增映射表，例如 `place_xxx -> scene_name`。

### 建筑节点

学长建筑转换为本项目建筑和地图节点：

- `id` -> `LEGACY_<id>`
- `name` 保留
- `location.lat` -> `latitude`
- `location.lng` -> `longitude`
- `type` -> `building_type`
- `placeId` 用于筛选归属场景

建筑节点参与路线图，可作为起终点或途经点。

### 设施节点

学长设施转换为本项目设施和地图节点：

- `id` -> `LEGACY_<id>`
- `name` 保留
- `location.lat/lng` 转为 `latitude/longitude`
- `type` 映射为本项目 `facility_type` 和 `normalized_type`

设施类型映射规则：

- 卫生间、厕所 -> `restroom`
- 餐饮、食堂、咖啡 -> `restaurant`
- 超市、商店 -> `supermarket` 或 `shop`
- 电话亭、ATM、服务点 -> `service`
- 未识别类型 -> `service`

### 路口节点

学长 `roads.json` 中的 `intersection_xxx` 没有直接坐标。导入脚本应估算坐标并写入快照。

估算规则：

1. 收集所有道路端点。
2. 建筑和设施等有坐标节点直接使用原坐标。
3. 对未知路口，查找相邻的已知坐标节点并取平均值。
4. 多轮传播，直到没有新的路口能被估算。
5. 仍无法估算的路口使用北邮中心点兜底，并在导入报告中计数。

路口节点在前端地图上淡色显示，在算法图中作为一等顶点参与最短路。

### 道路边

学长道路转换为本项目 `edges.json` 记录：

- `from` -> `source_code`
- `to` -> `target_code`
- `distance` 保留
- `congestionRate` -> `congestion`
- `idealSpeed` -> `walk_speed`
- `allowedVehicles` -> `allowed_modes`
- `roadType` -> `road_type`
- 增加 `source_dataset: "tourism-system-main"`

交通工具映射：

- `步行` -> `walk`
- `自行车` -> `bike`
- `电瓶车` -> `shuttle`

默认按双向道路处理：一条 legacy road 生成两个方向的有向边。后续如果源数据出现单行字段，再按字段控制方向。

## 后端设计

### 移除外部 API

删除或回退以下能力：

- `ExternalRouteService`
- `AmapRouteClient`
- `BaiduRouteClient`
- 高德/百度配置项
- 外部路线 mock 测试
- 路线服务里的外部路线调用链

路线响应保留本地算法说明字段：

- `route_source = "local"`
- `route_source_label = "本地算法"`
- `algorithm_path_codes`
- `route_geometry`
- `route_polyline`

不再返回：

- `external_provider`
- `provider_distance_m`
- `provider_estimated_minutes`
- `external_fallback_reason`

### GraphBuilder

`GraphBuilder` 继续作为统一图构建入口：

- 优先读取 `datasets/prod/edges.json` 中的真实边。
- 如果某场景没有真实边，才使用现有生成路网兜底。
- 北邮场景应使用 legacy 快照生成的路口、建筑、设施和道路边。
- route node type 支持 `intersection`、`building`、`facility`、`place`、`road`。

### 算法策略

保持自实现算法：

- 单目标路线：Dijkstra；可选 A*。
- 最短距离：边权为 `distance`。
- 最短时间：边权为 `distance / (speed * congestion)`。
- 避开拥堵：在时间权重基础上惩罚低拥挤度边。
- 打卡优先：在距离权重基础上加入节点 scenic score 奖励。
- 多目标闭环：目标较少用 Held-Karp，目标较多用 Nearest Neighbor + 2-opt。
- 最近设施：复用单源最短路，按图距离排序。

交通方式约束：

- `walk` 只走允许步行的边。
- `bike` 只走允许自行车或混合通行的边。
- `shuttle` 只走固定摆渡车/电瓶车边。
- `mixed` 在允许的交通方式中选择当前边最快方式。

北邮校园主推步行、自行车和混合方式；出租车不是北邮验收重点。

### 路线响应增强

新增或强化课程验收字段：

- `graph_node_count`
- `graph_edge_count`
- `algorithm_name`
- `algorithm_explanation`

示例说明：

```text
算法：Dijkstra
图规模：126 个顶点，966 条有向边
策略：按 distance / (speed * congestion) 计算最短时间
路线来源：本地算法，不依赖第三方路线 API
```

## 前端设计

### 地图展示

`RouteMap.vue` 展示本地道路图：

- 建筑、景点、设施正常显示 marker。
- `intersection` 路口节点用淡色小圆点显示。
- 本地道路边作为淡色背景线。
- 当前路线用高亮线展示。

### 路线结果面板

路线结果中显示：

- 路线来源：本地算法
- 算法名称
- 图规模
- 策略说明
- 距离、时间、交通方式
- 分段导航

不显示高德、百度或外部服务回退提示。

### 课堂演示路径

推荐演示流程：

1. 打开北邮校园场景。
2. 展示淡色路口和道路边，说明有向图建模。
3. 从校门规划到教学楼或设施。
4. 切换最短距离、最短时间、避开拥堵策略。
5. 切换步行、自行车、混合方式，说明交通工具约束。
6. 使用最近设施查询，说明按图距离排序。
7. 切换四城其他场景，说明系统覆盖范围。

## 测试设计

后端测试：

- 不存在高德/百度配置项和调用链。
- 北邮快照能生成场景节点、建筑、设施和边。
- 北邮真实路网节点数、边数达标。
- 单点路线经过 `LEGACY_intersection_xxx` 路口节点。
- 最短距离和最短时间策略可返回有效路线。
- 自行车路线不会走只允许步行的边。
- 最近设施按图距离排序，不按直线距离。
- 多点闭环从起点出发并回到起点。
- 没有真实边的四城场景仍能用兜底路网或生成边完成路线。

前端验证：

- `npm run typecheck`
- `npm run lint`
- 手动检查路线页：
  - 北邮路口节点显示
  - 道路背景显示
  - 路线高亮显示
  - 多点路线可用
  - 最近设施可用
  - 策略和交通方式切换可用

## 回滚和安全策略

- 不回滚用户已有改动，例如 `PlanPage.vue` 和 `backend/app/schemas/plan.py` 中已有的无关变更。
- 外部 API 相关代码明确删除，因为用户已选择“彻底删除”。
- `tourism-system-main` 只作为一次性导入来源，最终项目可删除。
- 数据生成脚本依赖项目内 `datasets/source_maps/bupt_campus_map.json`，不依赖外部目录。
- 如果导入数据异常，北邮场景可以临时回退到现有生成路网，但验收版本应优先使用真实路网。

## 后续扩展到全量迁移

后续要从方案 B 扩展到方案 C 时，不需要改路线算法。扩展路径是：

1. 在导入脚本中增加更多 `placeId -> scene_name` 映射。
2. 为每个场景输出独立 source map 快照。
3. 数据生成脚本合并更多 source map。
4. 前端场景列表自然展示更多真实路网场景。

这保持了项目边界清晰：旧项目只用于导入，当前项目拥有自己的规范化数据资产和算法实现。

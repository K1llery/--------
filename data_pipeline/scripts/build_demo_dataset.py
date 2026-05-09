from __future__ import annotations

import hashlib
import json
import math
from html import escape
from pathlib import Path
from random import Random


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "datasets" / "raw"
PROD_DIR = ROOT / "datasets" / "prod"
PUBLIC_MEDIA_DIR = ROOT / "frontend" / "public" / "media"
PROD_DIR.mkdir(parents=True, exist_ok=True)
PUBLIC_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

rand = Random(20260418)
FETCHED_DATE = "2026-04-18"


CITY_COLORS = {
    "北京": ("#241f4d", "#d26b2d", "#f7ede0"),
    "上海": ("#0e355d", "#3ca7d8", "#eef8ff"),
    "广州": ("#164734", "#e5a54a", "#fbf4de"),
    "深圳": ("#10243f", "#29b6a6", "#effbff"),
}


def local_media_path(folder: str, filename: str) -> str:
    return f"/media/{folder}/{filename}"


def seed_password_hash(password: str, salt: str) -> str:
    digest = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
    return f"{salt}${digest}"


def write_cover_svg(
    folder: str,
    filename: str,
    title: str,
    subtitle: str,
    meta: str,
    city: str,
    accent_label: str,
) -> str:
    out_dir = PUBLIC_MEDIA_DIR / folder
    out_dir.mkdir(parents=True, exist_ok=True)
    dark, accent, soft = CITY_COLORS.get(city, ("#1f2430", "#b65a2e", "#faf3eb"))
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="720" viewBox="0 0 1200 720">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{dark}"/>
      <stop offset="100%" stop-color="{accent}"/>
    </linearGradient>
    <radialGradient id="glow" cx="75%" cy="18%" r="55%">
      <stop offset="0%" stop-color="{soft}" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="{soft}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1200" height="720" fill="url(#bg)"/>
  <circle cx="920" cy="140" r="260" fill="url(#glow)"/>
  <rect x="70" y="72" width="190" height="42" rx="21" fill="rgba(255,255,255,0.16)"/>
  <text x="106" y="100" fill="{soft}" font-family="'Noto Serif SC','Microsoft YaHei',serif" font-size="22" font-weight="700">{escape(city)} PICK</text>
  <text x="70" y="220" fill="#ffffff" font-family="'Noto Serif SC','Microsoft YaHei',serif" font-size="72" font-weight="700">{escape(title)}</text>
  <text x="72" y="302" fill="{soft}" font-family="'Noto Sans SC','Microsoft YaHei',sans-serif" font-size="34">{escape(subtitle)}</text>
  <text x="72" y="360" fill="{soft}" font-family="'Noto Sans SC','Microsoft YaHei',sans-serif" font-size="26">{escape(meta)}</text>
  <rect x="72" y="430" width="224" height="58" rx="29" fill="rgba(255,255,255,0.14)" stroke="rgba(255,255,255,0.25)"/>
  <text x="112" y="468" fill="#ffffff" font-family="'Noto Sans SC','Microsoft YaHei',sans-serif" font-size="28" font-weight="700">{escape(accent_label)}</text>
  <path d="M754 560C832 490 926 452 1036 446" fill="none" stroke="rgba(255,255,255,0.26)" stroke-width="3"/>
  <path d="M718 612C826 544 952 512 1096 516" fill="none" stroke="rgba(255,255,255,0.16)" stroke-width="2"/>
  <rect x="770" y="446" width="340" height="170" rx="28" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.18)"/>
  <circle cx="844" cy="522" r="42" fill="rgba(255,255,255,0.16)"/>
  <circle cx="922" cy="522" r="42" fill="rgba(255,255,255,0.12)"/>
  <circle cx="1000" cy="522" r="42" fill="rgba(255,255,255,0.1)"/>
  <text x="816" y="590" fill="{soft}" font-family="'Noto Sans SC','Microsoft YaHei',sans-serif" font-size="20">LOCAL MEDIA</text>
</svg>
""".strip()
    (out_dir / filename).write_text(svg, encoding="utf-8")
    return local_media_path(folder, filename)


def ensure_local_media(featured_destinations: list[dict], foods: list[dict]) -> None:
    write_cover_svg(
        "system",
        "explore.svg",
        "城市探索",
        "四城精选目的地",
        "本地封面图包",
        "北京",
        "READY",
    )
    for idx, item in enumerate(featured_destinations, start=1):
        filename = f"destination-{idx:02d}.svg"
        item["image_url"] = write_cover_svg(
            "destinations",
            filename,
            item["name"],
            f"{item['city']} · {item['district'] or item['address']}",
            item["description"][:34],
            item["city"],
            "DESTINATION",
        )
        item["image_source_name"] = "项目内置本地封面图"
        item["image_source_url"] = item["image_url"]
    for idx, item in enumerate(foods, start=1):
        filename = f"food-{idx:02d}.svg"
        item["image_url"] = write_cover_svg(
            "foods",
            filename,
            item["name"],
            f"{item['city']} · {item['cuisine']}",
            item["destination_name"],
            item["city"],
            "FOOD PICK",
        )
        item["image_source_name"] = "项目内置本地封面图"
        item["image_source_url"] = item["image_url"]


FEATURED_DESTINATION_CATALOG = [
    {
        "name": "故宫博物院",
        "city": "北京",
        "category": "scenic",
        "district": "东城区",
        "address": "北京市东城区景山前街4号",
        "latitude": 39.916345,
        "longitude": 116.397155,
        "rating": 4.4,
        "heat": 14278,
        "heat_metric": "TripAdvisor点评数",
        "source_name": "TripAdvisor",
        "source_url": "https://www.tripadvisor.com/Attraction_Review-g294212-d311535-Reviews-Forbidden_City_The_Palace_Museum-Beijing.html",
        "tags": ["museum", "history", "imperial"],
        "description": "北京最具代表性的皇家宫殿景区，适合首次到访者作为城市第一站。 ",
    },
    {
        "name": "颐和园",
        "city": "北京",
        "category": "scenic",
        "district": "海淀区",
        "address": "北京市海淀区新建宫门路19号",
        "latitude": 39.999912,
        "longitude": 116.275522,
        "rating": 4.7,
        "heat": 14476,
        "heat_metric": "Trip.com点评数",
        "source_name": "Trip.com",
        "source_url": "https://www.trip.com/travel-guide/attraction/beijing/summer-palace-75619/",
        "tags": ["garden", "lake", "palace"],
        "description": "湖山园林与皇家建筑交织，是北京舒展型游览的代表景区。",
    },
    {
        "name": "三里屯",
        "city": "北京",
        "category": "shopping",
        "district": "朝阳区",
        "address": "北京市朝阳区三里屯街道",
        "latitude": 39.937611,
        "longitude": 116.454056,
        "rating": 4.7,
        "heat": 755,
        "heat_metric": "Trip.com点评数",
        "source_name": "Trip.com",
        "source_url": "https://www.trip.com/travel-guide/attraction/beijing/sanlitun-100974/",
        "tags": ["shopping", "nightlife", "fashion"],
        "description": "夜生活与潮流消费高度集中的北京热门商圈。",
    },
    {
        "name": "清华大学",
        "city": "北京",
        "category": "campus",
        "district": "海淀区",
        "address": "北京市海淀区双清路30号",
        "latitude": 40.003021,
        "longitude": 116.326956,
        "rating": 4.8,
        "heat": 1286,
        "heat_metric": "马蜂窝热度",
        "source_name": "马蜂窝",
        "source_url": "https://www.mafengwo.cn/poi/6306.html",
        "tags": ["campus", "architecture", "lake"],
        "description": "校园景观成熟、步行体验舒适，是北京高校参观首选之一。",
    },
    {
        "name": "外滩",
        "city": "上海",
        "category": "scenic",
        "district": "黄浦区",
        "address": "上海市黄浦区中山东一路",
        "latitude": 31.240044,
        "longitude": 121.490317,
        "rating": 4.7,
        "heat": 38241,
        "heat_metric": "Trip.com点评数",
        "source_name": "Trip.com",
        "source_url": "https://www.trip.com/travel-guide/attraction/shanghai/the-bund-10558905/",
        "tags": ["riverfront", "architecture", "nightview"],
        "description": "上海最具辨识度的城市地标，适合夜景与城市漫步。",
    },
    {
        "name": "豫园",
        "city": "上海",
        "category": "scenic",
        "district": "黄浦区",
        "address": "上海市黄浦区福佑路168号",
        "latitude": 31.227245,
        "longitude": 121.492516,
        "rating": 4.6,
        "heat": 9821,
        "heat_metric": "Trip.com点评数",
        "source_name": "Trip.com",
        "source_url": "https://www.trip.com/travel-guide/attraction/shanghai/yu-garden-10558683/",
        "tags": ["garden", "old-town", "culture"],
        "description": "古典园林与老城厢街区相连，适合半日慢逛。",
    },
    {
        "name": "南京路步行街",
        "city": "上海",
        "category": "shopping",
        "district": "黄浦区",
        "address": "上海市黄浦区南京东路",
        "latitude": 31.234412,
        "longitude": 121.475321,
        "rating": 4.6,
        "heat": 11844,
        "heat_metric": "Trip.com点评数",
        "source_name": "Trip.com",
        "source_url": "https://www.trip.com/travel-guide/attraction/shanghai/nanjing-road-pedestrian-street-10559069/",
        "tags": ["shopping", "street", "landmark"],
        "description": "适合城市首日逛街和感受上海商业氛围的经典路线。",
    },
    {
        "name": "上海交通大学(徐汇校区)",
        "city": "上海",
        "category": "campus",
        "district": "徐汇区",
        "address": "上海市徐汇区华山路1954号",
        "latitude": 31.202694,
        "longitude": 121.432728,
        "rating": 4.7,
        "heat": 924,
        "heat_metric": "马蜂窝热度",
        "source_name": "马蜂窝",
        "source_url": "https://www.mafengwo.cn/poi/16007.html",
        "tags": ["campus", "history", "architecture"],
        "description": "近代校园建筑与城市街区融合度高，适合高校漫游。",
    },
    {
        "name": "广州塔",
        "city": "广州",
        "category": "scenic",
        "district": "海珠区",
        "address": "广州市海珠区阅江西路222号",
        "latitude": 23.10857,
        "longitude": 113.319256,
        "rating": 4.7,
        "heat": 24560,
        "heat_metric": "Trip.com点评数",
        "source_name": "Trip.com",
        "source_url": "https://www.trip.com/travel-guide/attraction/guangzhou/canton-tower-10758917/",
        "tags": ["tower", "nightview", "landmark"],
        "description": "广州城市天际线核心地标，夜景和江景体验都很稳定。",
    },
    {
        "name": "陈家祠",
        "city": "广州",
        "category": "scenic",
        "district": "荔湾区",
        "address": "广州市荔湾区中山七路恩龙里34号",
        "latitude": 23.12583,
        "longitude": 113.244218,
        "rating": 4.6,
        "heat": 5215,
        "heat_metric": "Trip.com点评数",
        "source_name": "Trip.com",
        "source_url": "https://www.trip.com/travel-guide/attraction/guangzhou/chen-clan-academy-76032/",
        "tags": ["museum", "lingnan", "culture"],
        "description": "岭南建筑与民间工艺展示密集，是广州文化线的重要一站。",
    },
    {
        "name": "天环广场",
        "city": "广州",
        "category": "shopping",
        "district": "天河区",
        "address": "广州市天河区天河路218号",
        "latitude": 23.132429,
        "longitude": 113.322389,
        "rating": 4.6,
        "heat": 738,
        "heat_metric": "TripAdvisor点评数",
        "source_name": "TripAdvisor",
        "source_url": "https://www.tripadvisor.com/Attraction_Review-g298555-d13175527-Reviews-Parc_Central-Guangzhou_Guangdong.html",
        "tags": ["shopping", "mall", "lifestyle"],
        "description": "天河核心商圈内的高人气购物中心，适合餐饮和逛店联动。",
    },
    {
        "name": "中山大学(南校园)",
        "city": "广州",
        "category": "campus",
        "district": "海珠区",
        "address": "广州市海珠区新港西路135号",
        "latitude": 23.096296,
        "longitude": 113.299251,
        "rating": 4.7,
        "heat": 803,
        "heat_metric": "马蜂窝热度",
        "source_name": "马蜂窝",
        "source_url": "https://www.mafengwo.cn/poi/5424750.html",
        "tags": ["campus", "greenery", "history"],
        "description": "绿荫浓密、建筑老派，是广州最适合散步的高校校园之一。",
    },
    {
        "name": "世界之窗",
        "city": "深圳",
        "category": "scenic",
        "district": "南山区",
        "address": "深圳市南山区深南大道9037号",
        "latitude": 22.536195,
        "longitude": 113.974539,
        "rating": 4.5,
        "heat": 21609,
        "heat_metric": "Trip.com点评数",
        "source_name": "Trip.com",
        "source_url": "https://www.trip.com/travel-guide/attraction/shenzhen/window-of-the-world-10558775/",
        "tags": ["theme-park", "family", "landmark"],
        "description": "深圳经典主题乐园，适合高强度打卡与夜间演出体验。",
    },
    {
        "name": "深圳湾公园",
        "city": "深圳",
        "category": "scenic",
        "district": "南山区",
        "address": "深圳市南山区滨海大道",
        "latitude": 22.514367,
        "longitude": 113.949867,
        "rating": 4.7,
        "heat": 4828,
        "heat_metric": "Trip.com点评数",
        "source_name": "Trip.com",
        "source_url": "https://www.trip.com/travel-guide/attraction/shenzhen/shenzhen-bay-park-10524173/",
        "tags": ["park", "seaside", "cycling"],
        "description": "海边步道和城市天际线结合，是深圳轻松型行程的高频选择。",
    },
    {
        "name": "万象天地",
        "city": "深圳",
        "category": "shopping",
        "district": "南山区",
        "address": "深圳市南山区深南大道9668号",
        "latitude": 22.541506,
        "longitude": 113.954773,
        "rating": 4.7,
        "heat": 1261,
        "heat_metric": "TripAdvisor点评数",
        "source_name": "TripAdvisor",
        "source_url": "https://www.tripadvisor.com/Attraction_Review-g297415-d15088150-Reviews-MixC_World-Shenzhen_Guangdong.html",
        "tags": ["shopping", "mall", "lifestyle"],
        "description": "深圳最受欢迎的开放式商圈之一，适合购物和餐饮混合安排。",
    },
    {
        "name": "深圳大学",
        "city": "深圳",
        "category": "campus",
        "district": "南山区",
        "address": "深圳市南山区南海大道3688号",
        "latitude": 22.53332,
        "longitude": 113.93041,
        "rating": 4.6,
        "heat": 665,
        "heat_metric": "马蜂窝热度",
        "source_name": "马蜂窝",
        "source_url": "https://www.mafengwo.cn/poi/22420.html",
        "tags": ["campus", "modern", "citywalk"],
        "description": "城市感强、开放感好，是深圳校园参观里的热门选择。",
    },
]


FEATURED_FOOD_CATALOG = [
    {
        "name": "四季民福烤鸭店(故宫店)",
        "city": "北京",
        "destination_name": "故宫博物院",
        "cuisine": "烤鸭",
        "venue_name": "四季民福烤鸭店(故宫店)",
        "latitude": 39.9181,
        "longitude": 116.3996,
        "rating": 4.8,
        "heat": 1034,
        "heat_metric": "TripAdvisor点评数",
        "source_name": "TripAdvisor",
        "source_url": "https://www.tripadvisor.com/Restaurant_Review-g294212-d21225117-Reviews-Siji_Minfu_Restaurant_Peking_Roast_Duck_Gugong-Beijing.html",
        "description": "适合故宫和王府井路线之后衔接的一顿经典北京烤鸭。",
    },
    {
        "name": "TRB Hutong",
        "city": "北京",
        "destination_name": "故宫博物院",
        "cuisine": "Fine Dining",
        "venue_name": "TRB Hutong",
        "latitude": 39.9242,
        "longitude": 116.4086,
        "rating": 4.8,
        "heat": 612,
        "heat_metric": "TripAdvisor点评数",
        "source_name": "TripAdvisor",
        "source_url": "https://www.tripadvisor.com/Restaurant_Review-g294212-d3367707-Reviews-TRB_Hutong-Beijing.html",
        "description": "胡同环境里的高评分西式餐厅，适合夜游后安排。",
    },
    {
        "name": "Ultraviolet by Paul Pairet",
        "city": "上海",
        "destination_name": "外滩",
        "cuisine": "创意料理",
        "venue_name": "Ultraviolet by Paul Pairet",
        "latitude": 31.2303,
        "longitude": 121.4737,
        "rating": 4.9,
        "heat": 276,
        "heat_metric": "TripAdvisor点评数",
        "source_name": "TripAdvisor",
        "source_url": "https://www.tripadvisor.com/Restaurant_Review-g308272-d4604845-Reviews-Ultraviolet_by_Paul_Pairet-Shanghai.html",
        "description": "上海代表性的预约制餐厅，适合做高记忆点体验。",
    },
    {
        "name": "Lost Heaven on the Bund",
        "city": "上海",
        "destination_name": "外滩",
        "cuisine": "云南菜",
        "venue_name": "Lost Heaven on the Bund",
        "latitude": 31.2408,
        "longitude": 121.4929,
        "rating": 4.5,
        "heat": 1664,
        "heat_metric": "TripAdvisor点评数",
        "source_name": "TripAdvisor",
        "source_url": "https://www.tripadvisor.com/Restaurant_Review-g308272-d1027587-Reviews-Lost_Heaven_on_the_Bund-Shanghai.html",
        "description": "外滩附近高人气云南风味餐厅，适合城市夜景行程。",
    },
    {
        "name": "炳胜品味(珠江新城店)",
        "city": "广州",
        "destination_name": "广州塔",
        "cuisine": "粤菜",
        "venue_name": "炳胜品味(珠江新城店)",
        "latitude": 23.12134,
        "longitude": 113.32166,
        "rating": 4.6,
        "heat": 388,
        "heat_metric": "Trip.com点评数",
        "source_name": "Trip.com",
        "source_url": "https://www.trip.com/travel-guide/foods/guangzhou-152-restaurant/bingsheng-pingwei-11751423/",
        "description": "适合广州塔和珠江夜景线路后的正餐安排。",
    },
    {
        "name": "广州酒家(文昌总店)",
        "city": "广州",
        "destination_name": "陈家祠",
        "cuisine": "粤菜",
        "venue_name": "广州酒家(文昌总店)",
        "latitude": 23.12504,
        "longitude": 113.24483,
        "rating": 4.5,
        "heat": 431,
        "heat_metric": "Trip.com点评数",
        "source_name": "Trip.com",
        "source_url": "https://www.trip.com/travel-guide/foods/guangzhou-152-restaurant/guangzhou-restaurant-11751430/",
        "description": "老牌粤菜馆，适合搭配西关与岭南文化线路。",
    },
    {
        "name": "四季椰林椰子鸡(海岸城店)",
        "city": "深圳",
        "destination_name": "万象天地",
        "cuisine": "椰子鸡",
        "venue_name": "四季椰林椰子鸡(海岸城店)",
        "latitude": 22.54033,
        "longitude": 113.93534,
        "rating": 4.6,
        "heat": 262,
        "heat_metric": "Trip.com点评数",
        "source_name": "Trip.com",
        "source_url": "https://www.trip.com/travel-guide/foods/shenzhen-26-restaurant/si-ji-ye-lin-11751731/",
        "description": "深圳商圈里很稳的聚餐选择，适合逛街后补给。",
    },
    {
        "name": "润园四季椰子鸡(欢乐海岸店)",
        "city": "深圳",
        "destination_name": "深圳湾公园",
        "cuisine": "椰子鸡",
        "venue_name": "润园四季椰子鸡(欢乐海岸店)",
        "latitude": 22.52084,
        "longitude": 113.97137,
        "rating": 4.6,
        "heat": 231,
        "heat_metric": "Trip.com点评数",
        "source_name": "Trip.com",
        "source_url": "https://www.trip.com/travel-guide/foods/shenzhen-26-restaurant/run-yuan-si-ji-11752014/",
        "description": "适合深圳湾散步和海边夜景路线结束后的用餐点。",
    },
]


def load_raw(name: str) -> dict:
    path = RAW_DIR / name
    if not path.exists():
        return {"elements": []}
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_destination(element: dict) -> dict | None:
    tags = element.get("tags", {})
    name = tags.get("name")
    if not name:
        return None
    lat = element.get("lat") or element.get("center", {}).get("lat")
    lon = element.get("lon") or element.get("center", {}).get("lon")
    if lat is None or lon is None:
        return None
    category = "campus" if tags.get("amenity") == "university" else "scenic"
    description = " ".join(
        filter(
            None,
            [
                tags.get("tourism"),
                tags.get("amenity"),
                tags.get("leisure"),
                tags.get("wikidata"),
            ],
        )
    )
    return {
        "source_id": f"osm-{element['type']}-{element['id']}",
        "name": name,
        "city": "北京",
        "category": category,
        "district": tags.get("addr:district", ""),
        "address": tags.get("addr:full", "") or tags.get("addr:street", ""),
        "latitude": float(lat),
        "longitude": float(lon),
        "rating": None,
        "heat": None,
        "tags": [
            tag
            for tag in [tags.get("tourism"), tags.get("amenity"), tags.get("leisure")]
            if tag
        ],
        "description": description,
        "image_url": local_media_path("system", "explore.svg"),
        "image_source_name": "项目内置本地封面图",
        "image_source_url": local_media_path("system", "explore.svg"),
        "source_name": "OpenStreetMap / Overpass",
        "source_url": "https://overpass-api.de/api/interpreter",
        "fetched_date": FETCHED_DATE,
        "heat_metric": None,
    }


def dedupe_by_name(items: list[dict]) -> list[dict]:
    result: dict[str, dict] = {}
    for item in items:
        key = item["name"].strip().lower()
        if key not in result:
            result[key] = item
    return list(result.values())


def normalize_raw_point(element: dict) -> dict | None:
    tags = element.get("tags", {})
    name = tags.get("name")
    lat = element.get("lat") or element.get("center", {}).get("lat")
    lon = element.get("lon") or element.get("center", {}).get("lon")
    if not name or lat is None or lon is None:
        return None
    raw_type = (
        tags.get("amenity")
        or tags.get("tourism")
        or tags.get("shop")
        or tags.get("historic")
        or tags.get("leisure")
        or tags.get("building")
        or tags.get("office")
        or "poi"
    )
    return {
        "name": name,
        "latitude": float(lat),
        "longitude": float(lon),
        "raw_type": raw_type,
    }


def merge_featured_metadata(destinations: list[dict]) -> tuple[list[dict], list[dict]]:
    by_name = {item["name"]: item for item in destinations}
    featured = []
    for idx, item in enumerate(FEATURED_DESTINATION_CATALOG, start=1):
        merged = {**by_name.get(item["name"], {}), **item}
        merged["source_id"] = merged.get("source_id", f"featured-{idx}")
        merged["fetched_date"] = FETCHED_DATE
        featured.append(merged)
        if item["name"] in by_name:
            by_name[item["name"]].update(merged)
        else:
            destinations.append(merged)
            by_name[item["name"]] = merged
    return destinations, featured


def generate_scene(
    scene_name: str,
    base_lat: float,
    base_lon: float,
    building_names: list[str],
    facility_names: list[tuple[str, str]],
) -> tuple[dict, list[dict], list[dict]]:
    nodes = []
    facilities = []
    for idx, building in enumerate(building_names):
        nodes.append(
            {
                "code": f"{scene_name[:4].upper()}_{idx + 1:02d}",
                "name": building,
                "latitude": base_lat + (idx // 5) * 0.0008,
                "longitude": base_lon + (idx % 5) * 0.0008,
            }
        )
    for idx, (name, facility_type) in enumerate(facility_names):
        facilities.append(
            {
                "scene_name": scene_name,
                "code": f"{scene_name[:4].upper()}_F_{idx + 1:02d}",
                "name": name,
                "facility_type": facility_type,
                "latitude": base_lat + 0.0003 + (idx // 5) * 0.0007,
                "longitude": base_lon + 0.0003 + (idx % 5) * 0.0007,
            }
        )
    scene = {"name": scene_name, "nodes": nodes}
    edges = []
    all_codes = [node["code"] for node in nodes] + [
        facility["code"] for facility in facilities
    ]
    for idx, source in enumerate(all_codes):
        for target in all_codes[idx + 1 : idx + 4]:
            dist = 120 + (idx % 7) * 35 + rand.randint(0, 25)
            for left, right in ((source, target), (target, source)):
                edges.append(
                    {
                        "scene_name": scene_name,
                        "source_code": left,
                        "target_code": right,
                        "distance": dist,
                        "congestion": round(0.65 + rand.random() * 0.35, 2),
                        "walk_speed": 1.1,
                        "bike_speed": 3.5,
                        "shuttle_speed": 4.8,
                        "allowed_modes": ["walk", "mixed"]
                        if idx % 4
                        else ["walk", "bike", "mixed"],
                    }
                )
    return scene, facilities, edges


def rename_node_code(
    scene: dict, edges: list[dict], old_code: str, new_code: str
) -> None:
    for node in scene["nodes"]:
        if node["code"] == old_code:
            node["code"] = new_code
    for edge in edges:
        if edge["source_code"] == old_code:
            edge["source_code"] = new_code
        if edge["target_code"] == old_code:
            edge["target_code"] = new_code


def scene_from_raw(
    scene_name: str,
    prefix: str,
    raw_name: str,
    fallback_buildings: list[str],
    fallback_facilities: list[tuple[str, str]],
) -> tuple[dict, list[dict], list[dict]]:
    raw_points = [
        normalize_raw_point(item) for item in load_raw(raw_name).get("elements", [])
    ]
    raw_points = [item for item in raw_points if item is not None]
    unique_points = dedupe_by_name(
        [
            {
                "name": point["name"],
                "latitude": point["latitude"],
                "longitude": point["longitude"],
                "raw_type": point["raw_type"],
            }
            for point in raw_points
        ]
    )
    nodes = [
        {
            "code": f"{prefix}_{idx:02d}",
            "name": item["name"],
            "latitude": item["latitude"],
            "longitude": item["longitude"],
        }
        for idx, item in enumerate(unique_points[:20], start=1)
    ]
    facilities = [
        {
            "scene_name": scene_name,
            "code": f"{prefix}_F_{idx:02d}",
            "name": item["name"],
            "facility_type": item.get("raw_type", "poi"),
            "latitude": item["latitude"],
            "longitude": item["longitude"],
        }
        for idx, item in enumerate(unique_points[20:46], start=1)
    ]
    if len(nodes) < 20 or len(facilities) < 20:
        fallback_scene, fallback_scene_facilities, _ = generate_scene(
            scene_name,
            nodes[0]["latitude"] if nodes else 39.9,
            nodes[0]["longitude"] if nodes else 116.3,
            fallback_buildings,
            fallback_facilities,
        )
        if len(nodes) < 20:
            nodes = fallback_scene["nodes"]
        if len(facilities) < 20:
            facilities = fallback_scene_facilities
    scene = {"name": scene_name, "nodes": nodes}
    edges = []
    all_points = nodes + facilities
    for idx, source in enumerate(all_points):
        nearest = sorted(
            (
                (
                    math.dist(
                        (source["latitude"], source["longitude"]),
                        (target["latitude"], target["longitude"]),
                    ),
                    target,
                )
                for target in all_points
                if target["code"] != source["code"]
            ),
            key=lambda item: item[0],
        )[:4]
        for dist, target in nearest:
            edges.append(
                {
                    "scene_name": scene_name,
                    "source_code": source["code"],
                    "target_code": target["code"],
                    "distance": round(max(dist * 100000, 50), 1),
                    "congestion": round(0.65 + rand.random() * 0.35, 2),
                    "walk_speed": 1.1,
                    "bike_speed": 3.5,
                    "shuttle_speed": 4.8,
                    "allowed_modes": ["walk", "mixed"]
                    if idx % 5
                    else ["walk", "bike", "mixed"],
                }
            )
    backbone = sorted(
        all_points, key=lambda item: (item["latitude"], item["longitude"])
    )
    for left, right in zip(backbone, backbone[1:]):
        dist = round(
            max(
                math.dist(
                    (left["latitude"], left["longitude"]),
                    (right["latitude"], right["longitude"]),
                )
                * 100000,
                50,
            ),
            1,
        )
        for source, target in ((left, right), (right, left)):
            edges.append(
                {
                    "scene_name": scene_name,
                    "source_code": source["code"],
                    "target_code": target["code"],
                    "distance": dist,
                    "congestion": 0.9,
                    "walk_speed": 1.1,
                    "bike_speed": 3.5,
                    "shuttle_speed": 4.8,
                    "allowed_modes": ["walk", "bike", "mixed"],
                }
            )
    return scene, facilities, edges


def foods_from_catalog() -> list[dict]:
    items = []
    for idx, item in enumerate(FEATURED_FOOD_CATALOG, start=1):
        food = {**item}
        food["source_id"] = f"food-featured-{idx}"
        food["fetched_date"] = FETCHED_DATE
        items.append(food)
    return items


def build_users() -> list[dict]:
    interests = [
        "museum,history,photography",
        "campus,architecture,coffee",
        "park,walking,food",
        "garden,history,quiet",
        "culture,art,museum",
    ]
    users = []
    for idx in range(1, 11):
        users.append(
            {
                "id": idx,
                "username": f"demo_user_{idx}",
                "display_name": f"演示用户{idx}",
                "interests": interests[idx % len(interests)],
                "created_at": FETCHED_DATE + "T10:00:00",
                "last_login_at": FETCHED_DATE + "T10:00:00",
                "password_hash": seed_password_hash("demo123", f"demo-salt-{idx}"),
                "favorite_destination_ids": [],
                "favorite_route_snapshots": [],
            }
        )
    return users


def build_diaries(featured_destinations: list[dict]) -> list[dict]:
    templates = [
        "上午先走经典路线，下午转进更适合拍照和休息的区域，整体节奏很舒服。",
        "我更关注建筑和城市漫步感，这条路线的视野和动线都很顺。",
        "这次把景点、商圈和餐厅串起来走，几乎没有浪费路程。",
        "最喜欢的是路线回看和周边设施提醒，适合第一次来这座城市的人照着走。",
    ]
    diaries = []
    for idx, destination in enumerate(featured_destinations[:12], start=1):
        diaries.append(
            {
                "id": idx,
                "title": f"{destination['name']}游记{idx}",
                "destination_name": destination["name"],
                "content": f"这次我去了{destination['city']}的{destination['name']}。{templates[idx % len(templates)]} 如果时间有限，我会建议把附近餐厅和下一个打卡点一起规划。",
                "views": 120 + idx * 38,
                "rating": round(4.1 + (idx % 6) * 0.1, 1),
                "media_urls": [destination["image_url"]],
                "author_id": idx % 10 + 1,
                "author_name": f"演示用户{idx % 10 + 1}",
                "created_at": f"{FETCHED_DATE}T1{idx % 10}:00:00",
            }
        )
    return diaries


def main() -> None:
    raw = load_raw("beijing_destinations_osm.json")
    normalized = [normalize_destination(item) for item in raw.get("elements", [])]
    destinations = dedupe_by_name([item for item in normalized if item is not None])
    destinations, featured_destinations = merge_featured_metadata(destinations)
    destinations.sort(key=lambda item: (item["city"], item["category"], item["name"]))

    bupt_buildings = [
        "南门",
        "图书馆",
        "主楼",
        "教一楼",
        "教二楼",
        "教三楼",
        "教四楼",
        "科研楼",
        "学生活动中心",
        "体育馆",
        "第一宿舍",
        "第二宿舍",
        "第三宿舍",
        "第四宿舍",
        "第五宿舍",
        "校医院",
        "行政办公楼",
        "国际交流中心",
        "信息楼",
        "创新实践基地",
    ]
    bupt_facilities = [
        ("第一食堂", "canteen"),
        ("第二食堂", "canteen"),
        ("超市", "market"),
        ("图文打印店", "shop"),
        ("咖啡馆", "cafe"),
        ("快递点", "service"),
        ("卫生间A", "restroom"),
        ("卫生间B", "restroom"),
        ("校医院药房", "hospital"),
        ("银行自助点", "bank"),
        ("图书馆服务台", "library"),
        ("便利店", "shop"),
        ("篮球场", "sports"),
        ("羽毛球馆", "sports"),
        ("充电站", "charging"),
        ("游客咨询点", "visitor_center"),
        ("保卫处", "security"),
        ("共享单车点", "mobility"),
        ("实验用品店", "shop"),
        ("洗衣房", "laundry"),
        ("文创店", "shop"),
        ("心理咨询室", "wellness"),
        ("校史馆", "museum"),
        ("自习室", "study"),
        ("邮局服务点", "post"),
        ("饮水站", "water"),
    ]
    bupt_scene, bupt_scene_facilities, bupt_edges = scene_from_raw(
        "BUPT_Main_Campus", "BUPT", "bupt_scene.json", bupt_buildings, bupt_facilities
    )
    rename_node_code(
        bupt_scene, bupt_edges, bupt_scene["nodes"][0]["code"], "BUPT_GATE"
    )
    rename_node_code(bupt_scene, bupt_edges, bupt_scene["nodes"][1]["code"], "BUPT_LIB")

    summer_buildings = [
        "东宫门",
        "仁寿殿",
        "乐寿堂",
        "长廊",
        "佛香阁",
        "智慧海",
        "苏州街",
        "玉澜堂",
        "昆明湖码头",
        "十七孔桥",
        "排云殿",
        "谐趣园",
        "文昌阁",
        "德和园",
        "知春亭",
        "南湖岛",
        "西堤",
        "铜牛",
        "画中游",
        "四大部洲",
    ]
    summer_facilities = [
        ("游客中心", "visitor_center"),
        ("卫生间东", "restroom"),
        ("卫生间西", "restroom"),
        ("电瓶车站1", "shuttle"),
        ("电瓶车站2", "shuttle"),
        ("冷饮店", "shop"),
        ("纪念品店", "shop"),
        ("餐饮点", "canteen"),
        ("医疗点", "hospital"),
        ("警务服务点", "service"),
        ("咨询台", "service"),
        ("咖啡点", "cafe"),
        ("游船码头", "transport"),
        ("文创馆", "museum"),
        ("充电驿站", "charging"),
        ("无障碍服务点", "accessibility"),
        ("观景平台", "viewpoint"),
        ("售票补助点", "ticket"),
        ("行李寄存处", "storage"),
        ("休憩亭", "rest_area"),
        ("雨具租借点", "rental"),
        ("饮水处", "water"),
        ("导览机租赁点", "guide"),
        ("警务巡逻站", "security"),
        ("文保展示点", "education"),
    ]
    summer_scene, summer_scene_facilities, summer_edges = scene_from_raw(
        "Summer_Palace",
        "SUMMER",
        "summer_palace_scene.json",
        summer_buildings,
        summer_facilities,
    )

    scenes = [
        {
            "name": "BUPT_Main_Campus",
            "label": "北京邮电大学校园",
            "city": "北京",
            "supports_routing": True,
            "nodes": bupt_scene["nodes"],
        },
        {
            "name": "Summer_Palace",
            "label": "颐和园景区",
            "city": "北京",
            "supports_routing": True,
            "nodes": summer_scene["nodes"],
        },
        {
            "name": "Shanghai_City_View",
            "label": "上海城市精选地图",
            "city": "上海",
            "supports_routing": False,
            "nodes": [],
        },
        {
            "name": "Guangzhou_City_View",
            "label": "广州城市精选地图",
            "city": "广州",
            "supports_routing": False,
            "nodes": [],
        },
        {
            "name": "Shenzhen_City_View",
            "label": "深圳城市精选地图",
            "city": "深圳",
            "supports_routing": False,
            "nodes": [],
        },
    ]
    buildings = [
        {**node, "scene_name": bupt_scene["name"], "building_type": "landmark"}
        for node in bupt_scene["nodes"]
    ]
    buildings += [
        {**node, "scene_name": summer_scene["name"], "building_type": "landmark"}
        for node in summer_scene["nodes"]
    ]
    facilities = bupt_scene_facilities + summer_scene_facilities
    edges = bupt_edges + summer_edges
    foods = foods_from_catalog()
    ensure_local_media(featured_destinations, foods)
    featured_by_name = {item["name"]: item for item in featured_destinations}
    for destination in destinations:
        if destination["name"] in featured_by_name:
            destination.update(
                {
                    "image_url": featured_by_name[destination["name"]]["image_url"],
                    "image_source_name": featured_by_name[destination["name"]][
                        "image_source_name"
                    ],
                    "image_source_url": featured_by_name[destination["name"]][
                        "image_source_url"
                    ],
                }
            )
    users = build_users()
    diaries = build_diaries(featured_destinations)

    data_sources = [
        {
            "name": "OpenStreetMap Overpass",
            "file": "datasets/raw/*.json",
            "content": "北京目的地与样板场景真实点位",
        },
        {
            "name": "Trip.com / TripAdvisor / 马蜂窝",
            "file": "datasets/prod/featured_destinations.json, datasets/prod/foods.json",
            "content": "四城精选目的地与美食的评分和热度来源",
        },
        {
            "name": "Local media pack",
            "file": "frontend/public/media",
            "content": "项目内置封面图包，脱离外网也可稳定显示",
        },
    ]

    (PROD_DIR / "destinations.json").write_text(
        json.dumps(destinations, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (PROD_DIR / "featured_destinations.json").write_text(
        json.dumps(featured_destinations, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (PROD_DIR / "scenes.json").write_text(
        json.dumps(scenes, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (PROD_DIR / "buildings.json").write_text(
        json.dumps(buildings, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (PROD_DIR / "facilities.json").write_text(
        json.dumps(facilities, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (PROD_DIR / "edges.json").write_text(
        json.dumps(edges, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (PROD_DIR / "foods.json").write_text(
        json.dumps(foods, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (PROD_DIR / "users.json").write_text(
        json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (PROD_DIR / "sessions.json").write_text(
        json.dumps([], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (PROD_DIR / "diaries.json").write_text(
        json.dumps(diaries, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (PROD_DIR / "data_sources.json").write_text(
        json.dumps(data_sources, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    summary = {
        "destinations": len(destinations),
        "featured_destinations": len(featured_destinations),
        "cities": len({item["city"] for item in featured_destinations}),
        "scenes": len(scenes),
        "facilities": len(facilities),
        "buildings": len(buildings),
        "edges": len(edges),
        "foods": len(foods),
        "users": len(users),
        "diaries": len(diaries),
    }
    (PROD_DIR / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

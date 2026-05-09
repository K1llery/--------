from __future__ import annotations


def normalize_facility_type(raw_type: str | None, name: str = "") -> str:
    raw = (raw_type or "").strip().lower()
    normalized_name = name.strip()

    if raw in {"toilets", "toilet", "restroom", "wc", "bathroom"} or any(
        keyword in normalized_name for keyword in ("厕所", "洗手间", "卫生间")
    ):
        return "restroom"
    if raw in {"canteen", "restaurant", "cafe"}:
        return "restaurant"
    if raw in {"market", "supermarket"}:
        return "supermarket"
    if raw in {"museum", "viewpoint", "artwork", "attraction", "monument"}:
        return "artwork"
    if raw in {"service", "visitor_center", "ticket", "information"}:
        return "service"
    if raw in {"shop", "rental", "guide", "kiosk", "convenience"}:
        return "shop"
    if raw == "yes":
        if any(keyword in normalized_name for keyword in ("游泳", "体育", "球馆")):
            return "sports"
        if any(keyword in normalized_name for keyword in ("雕像", "雕塑", "像")):
            return "artwork"
        return "other"
    if raw in {"sports", "bank", "hotel", "post_office", "telecommunication", "library"}:
        return raw
    return raw or "other"


def facility_type_label(normalized_type: str) -> str:
    mapping = {
        "restaurant": "餐厅",
        "supermarket": "超市",
        "artwork": "景观/雕塑",
        "restroom": "公共厕所",
        "service": "服务点",
        "shop": "商店",
        "sports": "运动场馆",
        "bank": "银行",
        "hotel": "酒店",
        "post_office": "邮政服务",
        "telecommunication": "通信服务",
        "library": "图书馆",
        "other": "其他设施",
    }
    return mapping.get(normalized_type, "其他设施")

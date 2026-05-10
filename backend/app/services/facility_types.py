"""
设施分类及展示类型处理模块 (Facility Types)

提供将非结构的周边POI或校园内部设施英文/杂乱分类转换为标准统一分类(枚举)和中文化名称展示规则。
"""
from __future__ import annotations


def normalize_facility_type(raw_type: str | None, name: str = "") -> str:
    """
    根据设施原始类别与设施的补充名称识别并标准化分类字符串。
    
    统一不同数据源中名称异构的问题，使得设施查找功能具备通用的英文规范映射。
    
    Args:
        raw_type (str | None): 原始类别，如 "toilets"、"restroom" 等。
        name (str, optional): 设施具体补充名称，比如“xx饭店”、“洗手间”。默认为空。
        
    Returns:
        str: 规整化之后的枚举字符串，比如 "restroom", "restaurant" 以及缺省的 "other"。
    """
    raw = (raw_type or "").strip().lower()
    normalized_name = name.strip()

    # 包含卫生间关键词汇映射
    if raw in {"toilets", "toilet", "restroom", "wc", "bathroom"} or any(
        keyword in normalized_name for keyword in ("厕所", "洗手间", "卫生间")
    ):
        return "restroom"
    
    # 用餐设施映射
    if raw in {"canteen", "restaurant", "cafe"}:
        return "restaurant"
    
    # 购物与便利超市映射
    if raw in {"market", "supermarket"}:
        return "supermarket"
    
    # 游览微景观、雕像与美术陈列映射
    if raw in {"museum", "viewpoint", "artwork", "attraction", "monument"}:
        return "artwork"
    
    # 服务中心或站点映射
    if raw in {"service", "visitor_center", "ticket", "information"}:
        return "service"
    
    # 单独的小卖部跟商店
    if raw in {"shop", "rental", "guide", "kiosk", "convenience"}:
        return "shop"
    
    # 个别情况下 OSM 仅仅提供 yes 参数，根据名字来猜
    if raw == "yes":
        if any(keyword in normalized_name for keyword in ("游泳", "体育", "球馆")):
            return "sports"
        if any(keyword in normalized_name for keyword in ("雕像", "雕塑", "像")):
            return "artwork"
        return "other"
    
    # 固定格式保留
    if raw in {"sports", "bank", "hotel", "post_office", "telecommunication", "library"}:
        return raw
    
    return raw or "other"


def facility_type_label(normalized_type: str) -> str:
    """
    根据设施标准英文类型返回对应的前端展示用中文说明标签。
    
    Args:
        normalized_type (str): normalize_facility_type 返回的标准规范英文字符类别。
        
    Returns:
        str: 给界面客户端显示的中文称呼，若匹配不上则落回"其他设施"。
    """
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

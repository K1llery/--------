"""
周边设施服务模块 (Facility Service)

提供基于图(Graph)拓扑的真实地理临近设施查询功能。
核心依赖 GraphBuilder 提取距离矩阵用于约束返回目标并进行排序分发。
"""
from __future__ import annotations

from app.repositories.data_loader import DatasetRepository
from app.services.facility_types import facility_type_label, normalize_facility_type
from app.services.graph_builder import GraphBuilder


class NearbyFacilityService:
    """
    业务级查询周边设施(厕所、饭店等)的服务。
    
    使用路网图实现距离(非直线距离而是真实物理导航长度)筛选查询周边服务点。
    """
    def __init__(self, repository: DatasetRepository, graph_builder: GraphBuilder | None = None) -> None:
        """
        初始化获取图数据组件和数据集。
        
        Args:
            repository (DatasetRepository): 数据仓库抽象访问集合对象。
            graph_builder (GraphBuilder | None, optional): 获取场景道路路网图工具器。未提供默认构造一个新的。
        """
        self.repository = repository
        self.graph_builder = graph_builder or GraphBuilder(repository)

    @staticmethod
    def _decorate_facility(facility: dict, distance: float, transport_mode: str) -> dict:
        """
        提供设施字典对象数据增强，追加标准化类型、中文说明标签与距离。
        
        Args:
            facility (dict): 抽取的元素词典。
            distance (float): Dijkstra求出的该地与起点的距离长度/权重。
            transport_mode (str): 步行或其他形式出行机制字符串。
            
        Returns:
            dict: 追加 graph_distance 等前端附加字段的新字典。
        """
        normalized_type = normalize_facility_type(facility.get("facility_type"), facility.get("name", ""))
        return {
            **facility,
            "normalized_type": normalized_type,
            "facility_label": facility_type_label(normalized_type),
            "graph_distance": round(distance, 1),
            "transport_mode": transport_mode,
        }

    def nearby(
        self,
        scene_name: str,
        origin_code: str,
        category: str | None = None,
        radius: float = 1200.0,
        transport_mode: str = "walk",
        strategy: str = "distance",
    ) -> list[dict]:
        """
        查找指定图节点给定范围半径内的特定周边服务点。
        
        1. 圈定对应场景范围内的全部或某一类别设施点。
        2. 获取整幅图结构，再以 origin_code 为起点推算出所有单源最短距离树(通过 Dijkstra)。
        3. 进行圈状(限制半径)截断，排序后拼装展示。
        
        Args:
            scene_name (str): 目标查询隶属场景(例如北邮、颐和园主图)。
            origin_code (str): 用户所处的当前节点的 Code 作为查询原点。
            category (str | None, optional): 请求检索的具体设施类型的英文字符（选填）。
            radius (float, optional): 容差/辐射覆盖的最远权值。默认 1200米 内。
            transport_mode (str, optional): 筛选步行的模式边图谱，默认为 "walk"。
            strategy (str, optional): 用来做 Dijkstra 距离的基础类型或时间维度类型。 默认为 "distance"。
            
        Returns:
            list[dict]: 加工修饰过的经过根据 graph_distance 正向单调递增排序后的结果字典列表。
        """
        # 初筛：场景名称过滤以节约查询
        facilities = [item for item in self.repository.facilities() if item["scene_name"] == scene_name]
        
        # 归一化后依据指定的规范类型限制范围
        if category:
            normalized_category = normalize_facility_type(category)
            facilities = [
                item
                for item in facilities
                if normalize_facility_type(item.get("facility_type"), item.get("name", "")) == normalized_category
            ]

        # 从 GraphBuilder 中拿到特定园区(通过名字过滤后生成)的地图
        graph = self.graph_builder.get_scene_graph(scene_name)
        
        # 借由于 graph 做好的最短距离字典
        distances = graph.shortest_distances(origin_code, strategy=strategy, transport_mode=transport_mode)

        # 遍历设施结合路网距离合并
        ranked = []
        for facility in facilities:
            distance = distances.get(facility["code"])
            # 若不可达或数据中根本没记录的残缺节点直接略过
            if distance is None or distance == float("inf"):
                continue
            
            # 纳入距离可接受区间(小于半径)的合法POI
            if distance <= radius:
                ranked.append(self._decorate_facility(facility, distance, transport_mode))
                
        # 基于从近到远做基础排序保证展现逻辑
        ranked.sort(key=lambda item: item["graph_distance"])
        return ranked

"""
图结构建造与维护模块 (Graph Builder)

从数据集中拉取并分析地理及结构信息，借助动态网格建立带权物理路网图(Graph)。
为路由、周边查找等涉及最短路径的模块封装了单例级别的拓扑结构支撑结构。
"""
from __future__ import annotations

import logging
import math

from app.algorithms.graph import Graph
from app.repositories.data_loader import DatasetRepository

logger = logging.getLogger(__name__)


class GraphBuilder:
    """
    负责从 Repository 数据抽取经纬度坐标与拓扑特征构造和缓存路网图的服务组件。
    
    动态生成支持步行、坐车等模式下的真实坐标节点与路网映射，以支撑周边查询与旅行路径规划等相关模块。
    """

    def __init__(self, repository: DatasetRepository) -> None:
        """
        初始化构造路网构建器。
        
        Args:
            repository (DatasetRepository): 用于存取和拉取各种场景数据的加载仓资源。
        """
        self.repository = repository
        self._graphs: dict[str, Graph] = {}
        self._name_maps: dict[str, dict[str, str]] = {}
        self._route_node_types: dict[str, dict[str, str]] = {}
        self._scene_code_sets: dict[str, set[str]] = {}

    @staticmethod
    def _node_scenic_score(name: str, raw_type: str | None = None) -> float:
        """
        根据节点名字的字面意义和类型估算该地点的风景名胜附加权值。
        
        用于时间充裕情况下的风景优选倾向路由，评分越高的点越有可能被纳入游览视野。
        
        Args:
            name (str): 目的地名称。
            raw_type (str | None): 可选的目的地设施源类型。
            
        Returns:
            float: 该地景点的权重评分，范围一般为 0.15~0.7 。
        """
        scenic_keywords = ("门", "湖", "桥", "殿", "宫", "园", "亭", "馆", "阁", "景", "广场", "主楼", "图书馆")
        if any(keyword in name for keyword in scenic_keywords):
            return 0.7
        if raw_type in {"museum", "viewpoint", "artwork", "visitor_center"}:
            return 0.55
        return 0.15

    @staticmethod
    def _road_code(scene_name: str, row: int, col: int) -> str:
        """
        工厂方法：生成模拟道路相交节点的系统内置标识符(Code)。
        """
        return f"__road__{scene_name}_{row}_{col}"

    @staticmethod
    def _geo_distance_m(left_lat: float, left_lon: float, right_lat: float, right_lon: float) -> float:
        """
        利用赤道半径等参数简单估算球面两点间相对位移直线距离。
        
        Args:
            left_lat (float): 点1维轴（纬度）。
            left_lon (float): 点1经轴（经度）。
            right_lat (float): 点2维轴。
            right_lon (float): 点2经轴。
            
        Returns:
            float: 最终返回以米（meter）为单位的实际物理地球直角距离预测值。
        """
        mean_lat = math.radians((left_lat + right_lat) / 2)
        lat_m = (left_lat - right_lat) * 111_320
        lon_m = (left_lon - right_lon) * 111_320 * max(math.cos(mean_lat), 0.2)
        return math.hypot(lat_m, lon_m)

    @staticmethod
    def _cluster_axis(values: list[float], tolerance: float = 0.00065) -> list[float]:
        """
        利用容差半径合并经纬度簇以产生对齐且精简的马路轴线网格（网格去重）。
        """
        if not values:
            return []
        clusters: list[list[float]] = []
        for value in sorted(values):
            if not clusters or abs(value - (sum(clusters[-1]) / len(clusters[-1]))) > tolerance:
                clusters.append([value])
            else:
                clusters[-1].append(value)
        return [sum(cluster) / len(cluster) for cluster in clusters]

    @staticmethod
    def _road_speeds() -> dict[str, float]:
        return {"walk": 1.1, "bike": 3.5, "shuttle": 4.8, "taxi": 4.8, "mixed": 4.8}

    @staticmethod
    def _access_speeds() -> dict[str, float]:
        return {"walk": 1.1, "bike": 2.2, "shuttle": 2.6, "taxi": 2.6, "mixed": 2.6}

    def _scene_points(self, scene_name: str) -> tuple[list[dict], list[dict]]:
        scene = next((item for item in self.repository.scenes() if item["name"] == scene_name), {"nodes": []})
        facilities = [item for item in self.repository.facilities() if item["scene_name"] == scene_name]
        return scene.get("nodes", []), facilities

    def _add_road_layer(
        self,
        scene_name: str,
        graph: Graph,
        points: list[dict],
        names: dict[str, str],
        route_node_types: dict[str, str],
    ) -> None:
        latitudes = self._cluster_axis([item["latitude"] for item in points])
        longitudes = self._cluster_axis([item["longitude"] for item in points])
        if len(latitudes) < 2 or len(longitudes) < 2:
            return

        road_codes: dict[tuple[int, int], str] = {}
        for row, latitude in enumerate(latitudes):
            for col, longitude in enumerate(longitudes):
                code = self._road_code(scene_name, row, col)
                graph.add_node(code, latitude, longitude, scenic_score=0.0)
                road_codes[(row, col)] = code
                names[code] = "道路节点"
                route_node_types[code] = "road"

        modes = {"walk", "bike", "taxi", "shuttle", "mixed"}
        speeds = self._road_speeds()
        for row in range(len(latitudes)):
            for col in range(len(longitudes)):
                source = road_codes[(row, col)]
                neighbors = []
                if row + 1 < len(latitudes):
                    neighbors.append(road_codes[(row + 1, col)])
                if col + 1 < len(longitudes):
                    neighbors.append(road_codes[(row, col + 1)])
                source_lat, source_lon = graph.coords[source]
                for target in neighbors:
                    target_lat, target_lon = graph.coords[target]
                    distance = round(self._geo_distance_m(source_lat, source_lon, target_lat, target_lon), 1)
                    for left, right in ((source, target), (target, source)):
                        graph.add_edge(left, right, max(distance, 8.0), 0.78, speeds, modes)

        road_items = [
            (code, graph.coords[code][0], graph.coords[code][1]) for code in road_codes.values() if code in graph.coords
        ]
        access_speeds = self._access_speeds()
        for point in points:
            nearest_code, nearest_distance = min(
                (
                    (code, self._geo_distance_m(point["latitude"], point["longitude"], latitude, longitude))
                    for code, latitude, longitude in road_items
                ),
                key=lambda item: item[1],
            )
            distance = max(round(nearest_distance, 1), 6.0)
            for left, right in ((point["code"], nearest_code), (nearest_code, point["code"])):
                graph.add_edge(left, right, distance, 0.72, access_speeds, modes)

    def get_scene_graph(self, scene_name: str) -> Graph:
        """
        获取或构建并缓存指定场景名字的图实例。
        
        融合了场景基本数据点与生成的道路网格点，将二者桥接建立出一张可以直接做最短路或TSP搜索的大图。
        
        Args:
            scene_name (str): 游览场景名称。
            
        Returns:
            Graph: 构建完成供外部查询服务所用的一张联通权地图。
        """
        if scene_name in self._graphs:
            return self._graphs[scene_name]
        graph = Graph()
        names: dict[str, str] = {}
        route_node_types: dict[str, str] = {}
        scene_nodes, facilities = self._scene_points(scene_name)
        for node in scene_nodes:
            graph.add_node(
                node["code"],
                node["latitude"],
                node["longitude"],
                scenic_score=self._node_scenic_score(node["name"]),
            )
            names[node["code"]] = node["name"]
            route_node_types[node["code"]] = "place"
        for facility in facilities:
            graph.add_node(
                facility["code"],
                facility["latitude"],
                facility["longitude"],
                scenic_score=self._node_scenic_score(facility["name"], facility.get("facility_type")),
            )
            names[facility["code"]] = facility["name"]
            route_node_types[facility["code"]] = "facility"
        self._add_road_layer(scene_name, graph, [*scene_nodes, *facilities], names, route_node_types)
        self._graphs[scene_name] = graph
        self._name_maps[scene_name] = {**self._name_maps.get(scene_name, {}), **names}
        self._route_node_types[scene_name] = route_node_types
        logger.debug("Built graph for scene %s: %d nodes", scene_name, len(graph.coords))
        return graph

    def get_name_map(self, scene_name: str) -> dict[str, str]:
        """
        获取一个 code -> name 的全局映射表用于查询回显名称。
        
        Args:
            scene_name (str): 场景名。
            
        Returns:
            dict[str, str]: 返回映射好的只读节点展示名称表。
        """
        if scene_name in self._name_maps:
            return self._name_maps[scene_name]
        self.get_scene_graph(scene_name)
        if scene_name in self._name_maps:
            return self._name_maps[scene_name]
        scene = next((item for item in self.repository.scenes() if item["name"] == scene_name), {"nodes": []})
        names = {item["code"]: item["name"] for item in scene.get("nodes", [])}
        names.update(
            {item["code"]: item["name"] for item in self.repository.facilities() if item["scene_name"] == scene_name}
        )
        self._name_maps[scene_name] = names
        return names

    def get_scene_codes(self, scene_name: str) -> set[str]:
        """
        获取场景中所有的有效目标代码(code)集合对象，用于过滤验证游离态节点参数。
        
        Args:
            scene_name (str): 场景标识名称。
            
        Returns:
            set[str]: 过滤去重的代码集合。
        """
        if scene_name in self._scene_code_sets:
            return self._scene_code_sets[scene_name]
        scene = next((item for item in self.repository.scenes() if item["name"] == scene_name), {"nodes": []})
        codes = {item["code"] for item in scene.get("nodes", [])}
        codes.update({item["code"] for item in self.repository.facilities() if item["scene_name"] == scene_name})
        self._scene_code_sets[scene_name] = codes
        return codes

    def get_route_node_type(self, scene_name: str, code: str) -> str:
        """
        获得路由节点的内部归属类型('road', 'place', 'facility')等。
        """
        self.get_scene_graph(scene_name)
        return self._route_node_types.get(scene_name, {}).get(code, "place")

    def route_nodes_for_path(self, scene_name: str, path_codes: list[str]) -> list[dict]:
        """
        转换路径 code 序列数组为给客户端实际展示绘制使用的丰富节点字典切片。
        
        Args:
            scene_name (str): 对应的使用场景/地图块名。
            path_codes (list[str]): Dijkstra算法跑出的按序路口或节点code表。
            
        Returns:
            list[dict]: 加工后的带有经纬度与地标特征名称的坐标轨迹点。
        """
        graph = self.get_scene_graph(scene_name)
        names = self.get_name_map(scene_name)
        node_types = self._route_node_types.get(scene_name, {})
        route_nodes = []
        for code in path_codes:
            coords = graph.coords.get(code)
            if coords is None:
                continue
            latitude, longitude = coords
            route_nodes.append(
                {
                    "code": code,
                    "name": names.get(code, "道路节点"),
                    "latitude": latitude,
                    "longitude": longitude,
                    "route_node_type": node_types.get(code, "place"),
                }
            )
        return route_nodes

/** 目的地 */
export interface Destination {
  source_id: string;
  name: string;
  category: string;
  city?: string;
  district?: string;
  address?: string;
  latitude: number;
  longitude: number;
  rating: number | null;
  heat: number | null;
  tags?: string[];
  description?: string;
  image_url?: string;
  source_name?: string;
  source_url?: string;
}

/** 美食 */
export interface Food {
  id: string;
  name: string;
  city?: string;
  cuisine?: string;
  rating: number | null;
  heat?: number | null;
  source_name?: string;
  image_url?: string;
  description?: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  distance_km?: number;
}

/** 日记 */
export interface Diary {
  id: number;
  title: string;
  destination_name: string;
  content: string;
  views: number;
  rating: number;
  media_urls: string[];
  author_id?: number;
  author_name?: string;
  created_at?: string;
}

/** 场景节点 */
export interface SceneNode {
  code: string;
  name: string;
  latitude: number;
  longitude: number;
  route_node_type?: "place" | "building" | "facility" | "intersection" | "road" | string;
}

/** 场景边 */
export interface SceneEdge {
  scene_name: string;
  source_code: string;
  target_code: string;
  distance: number;
  congestion: number;
  allowed_modes?: string[];
}

/** 地理坐标点 */
export interface GeoPoint {
  latitude: number;
  longitude: number;
}

/** 场景 */
export interface Scene {
  name: string;
  label: string;
  city: string;
  category?: string;
  anchor_destination_id?: string;
  supports_routing: boolean;
  navigation_radius_m?: number;
  transport_modes?: string[];
  nodes: SceneNode[];
}

/** 路线段 */
export interface RouteSegment {
  index: number;
  from_code: string;
  from_name: string;
  to_code: string;
  to_name: string;
  distance_m: number;
  estimated_minutes: number;
  congestion: number;
  instruction: string;
  cumulative_distance_m: number;
  cumulative_minutes: number;
}

/** 单点路线结果 */
export interface SingleRouteResult {
  path_codes: string[];
  path_names: string[];
  algorithm_path_codes?: string[];
  route_nodes: SceneNode[];
  route_geometry?: GeoPoint[];
  route_polyline?: GeoPoint[];
  total_distance_m: number;
  estimated_minutes: number;
  strategy: string;
  strategy_label: string;
  transport_mode: string;
  transport_mode_label: string;
  explanation: string;
  navigation_summary: string;
  average_congestion: number;
  scenic_score: number;
  segments: RouteSegment[];
  resolved_start_code: string;
  resolved_start_name: string;
  alternatives: SingleRouteResult[];
  route_source?: string;
  route_source_label?: string;
  route_intent?: string;
  facility?: Facility;
  search_radius_m?: number;
}

/** 多点路线结果 */
export interface MultiRouteResult {
  path_codes: string[];
  path_names: string[];
  algorithm_path_codes?: string[];
  route_nodes: SceneNode[];
  route_geometry?: GeoPoint[];
  route_polyline?: GeoPoint[];
  ordered_stop_codes: string[];
  ordered_stop_names: string[];
  total_distance_m: number;
  estimated_minutes: number;
  strategy: string;
  strategy_label: string;
  transport_mode: string;
  transport_mode_label: string;
  optimization_label: string;
  explanation: string;
  navigation_summary: string;
  segments: RouteSegment[];
  resolved_start_code: string;
  resolved_start_name: string;
  route_source?: string;
  route_source_label?: string;
  route_intent?: string;
  duration_minutes?: number;
  suggested_stop_codes?: string[];
  suggested_stop_names?: string[];
}

/** 自动漫游路线结果 */
export interface WanderRouteResult extends MultiRouteResult {
  route_intent: "wander";
  duration_minutes: number;
  suggested_stop_codes: string[];
  suggested_stop_names: string[];
}

/** 最近设施路线结果 */
export interface NearbyFacilityRouteResult extends SingleRouteResult {
  route_intent: "nearby_facility";
  facility: Facility;
  search_radius_m: number;
}

/** 室内建筑 */
export interface IndoorBuilding {
  building_code: string;
  building_name: string;
  scene_name: string;
  node_count: number;
  floors: number[];
  nodes: IndoorNode[];
}

/** 室内节点 */
export interface IndoorNode {
  code: string;
  name: string;
  floor: number;
}

/** 室内路线步骤 */
export interface IndoorStep {
  index: number;
  from_node_code: string;
  from_name: string;
  from_floor: number;
  to_node_code: string;
  to_name: string;
  to_floor: number;
  connector: string;
  distance_m: number;
  estimated_seconds: number;
  instruction: string;
}

/** 室内路线结果 */
export interface IndoorRouteResult {
  building_code: string;
  building_name: string;
  path_node_codes: string[];
  path_node_names: string[];
  strategy: string;
  mobility_mode: string;
  total_distance_m: number;
  estimated_seconds: number;
  summary: string;
  steps: IndoorStep[];
}

/** 用户 */
export interface User {
  id: number;
  username: string;
  display_name: string;
  created_at?: string;
  last_login_at?: string;
  favorite_destination_ids: string[];
  favorite_route_snapshots: RouteSnapshot[];
}

/** 路线收藏快照 */
export interface RouteSnapshot {
  scene_name: string;
  strategy: string;
  transport_mode: string;
  path_codes: string[];
  path_names: string[];
  total_distance_m: number;
  estimated_minutes: number;
  explanation: string;
  saved_at?: string;
}

/** 时段条目 */
export interface TimeSlotEntry {
  destination_id: string;
  destination_name: string;
  notes: string;
}

/** 每日时段 */
export interface TimeSlots {
  morning: TimeSlotEntry | null;
  afternoon: TimeSlotEntry | null;
  evening: TimeSlotEntry | null;
}

/** 单日行程 */
export interface DayPlan {
  date: string;
  city: string;
  time_slots: TimeSlots;
}

/** 旅行计划 */
export interface TravelPlan {
  id: number;
  user_id: number;
  title: string;
  days: DayPlan[];
  created_at: string;
  updated_at: string;
}

/** 设施 */
export interface Facility {
  code: string;
  name: string;
  scene_name: string;
  facility_type: string;
  normalized_type?: string;
  facility_label?: string;
  latitude: number;
  longitude: number;
  graph_distance?: number;
  transport_mode?: string;
}

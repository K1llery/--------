import type {
  Destination,
  Diary,
  Facility,
  Food,
  IndoorBuilding,
  IndoorRouteResult,
  MultiRouteResult,
  Scene,
  SingleRouteResult,
  User,
} from "./models";

/** 认证响应 */
export interface AuthResponse {
  user: User;
  token: string;
}

/** 美食列表响应 */
export interface FoodListResponse {
  items: Food[];
  loaded_count: number;
  source_names: string[];
}

/** 日记列表响应 */
export interface DiaryListResponse {
  items: Diary[];
}

/** 日记搜索响应 */
export interface DiarySearchResponse {
  query: string;
  items: Diary[];
}

/** 日记互动响应 */
export interface DiaryInteractionResponse {
  diary: Diary;
}

/** 日记评分响应 */
export interface DiaryRateResponse {
  diary: Diary;
  user_score: number;
  rating_count: number;
}

/** 压缩响应 */
export interface CompressionResponse {
  encoded: string;
  codes: Record<string, string>;
  original_bits: number;
  compressed_bits: number;
  compression_ratio: number;
}

/** 室内建筑列表响应 */
export interface IndoorBuildingListResponse {
  items: IndoorBuilding[];
}

/** 目的地搜索响应 */
export interface DestinationSearchResponse {
  exact: Destination | null;
  fuzzy: Destination[];
  featured: Destination[];
}

/** 地图场景详情响应 */
export interface SceneDetailResponse {
  scene: Scene;
  buildings: any[];
  facilities: Facility[];
  edges: any[];
}

import type {
  Destination,
  DestinationDetail,
  Diary,
  Facility,
  Food,
  IndoorBuilding,
  IndoorRouteResult,
  MultiRouteResult,
  Scene,
  SceneEdge,
  SingleRouteResult,
  TravelPlan,
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

/** AI 日记草稿响应 */
export interface DiaryDraftResponse {
  title: string;
  content: string;
}

/** AI 生图响应 */
export interface ImageGenerateResponse {
  image_url: string;
  source_url: string;
  prompt: string;
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

/** 目的地详情响应 */
export type DestinationDetailResponse = DestinationDetail;

/** 统计概览响应 */
export interface StatsOverviewResponse {
  counts: Record<string, number>;
  requirement_progress: Record<
    string,
    {
      actual: number;
      required: number;
      passed: boolean;
      label: string;
    }
  >;
  top_destinations: Destination[];
  top_diaries: Diary[];
  top_foods: Food[];
  distributions: Record<string, Array<{ label: string; value: number }>>;
  compression_summary: {
    algorithm: string;
    source: string;
    item_count: number;
    original_bits: number;
    compressed_bits: number;
    average_ratio: number;
  };
  algorithm_evidence: Array<{ name: string; implementation: string }>;
}

/** 推荐评估响应 */
export interface RecommendationEvaluationResponse {
  top_k: number;
  precision: number;
  recall: number;
  f1: number;
  evaluated_user_count: number;
  samples: Array<{
    user_id: number;
    display_name: string;
    interests: string[];
    recommended_count: number;
    relevant_count: number;
    hit_count: number;
    hit_names: string[];
    precision: number;
    recall: number;
  }>;
  formula: string;
}

/** 地图场景详情响应 */
export interface SceneDetailResponse {
  scene: Scene;
  buildings: unknown[];
  facilities: Facility[];
  edges: SceneEdge[];
}

/** 旅行计划列表响应 */
export interface PlanListResponse {
  items: TravelPlan[];
}

/** 路线优化请求 */
export interface OptimizeOrderRequest {
  destination_ids: string[];
}

/** 路线优化响应 */
export interface OptimizeOrderResponse {
  ordered_ids: string[];
  total_distance_km: number;
  optimization_label: string;
}

/** 附近美食列表响应 */
export interface NearbyFoodResponse {
  items: Food[];
  loaded_count: number;
  source_names: string[];
}

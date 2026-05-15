export type { Diary, DiaryMedia } from "../../../types/models";
export type {
  DiaryListResponse,
  DiarySearchResponse,
  DiaryInteractionResponse,
  DiaryRateResponse,
  CompressionResponse,
  DiaryDraftResponse,
  ImageGenerateResponse,
} from "../../../types/api";

export interface DiaryAnimationShot {
  index: number;
  caption: string;
  media_url: string;
  transition: string;
  duration_seconds: number;
}

export interface DiaryAnimationResult {
  generation_mode: string;
  total_duration_seconds: number;
  narration_script: string;
  shots: DiaryAnimationShot[];
}

export interface DiaryCreatePayload {
  destination_name: string;
  title: string;
  content: string;
  cover_image_url?: string;
  media_urls?: string[];
}

export interface DiaryDraftPayload {
  destination_name: string;
  keywords: string[];
  style?: string;
}

export interface DiaryCoverPayload {
  destination_name: string;
  title: string;
  content: string;
}

export interface DiaryDecompressPayload {
  encoded: string;
  codes: Record<string, string>;
}

export type DiarySearchType = "destination" | "title_exact" | "fulltext";

export type DiarySortKey = "recommend" | "views" | "rating" | "latest";

export interface DiaryDiscoverParams {
  q?: string;
  search_type?: DiarySearchType;
  sort?: DiarySortKey;
  page?: number;
  page_size?: number;
}

export interface DiaryAlgorithmDebug {
  sort?: string;
  reason?: string;
  formula?: string;
  scores?: Record<string, number>;
  prior_C?: number;
  global_mean?: number;
  max_views?: number;
  fallback?: string;
  limitation?: string;
  interest_destinations?: string[];
  matched_count?: number;
}

export interface DiaryDiscoverResponse {
  items: import("../../../types/models").Diary[];
  total?: number;
  page?: number;
  page_size?: number;
  search_type?: string | null;
  sort?: string;
  debug?: DiaryAlgorithmDebug | null;
}

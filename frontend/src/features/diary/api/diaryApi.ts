import { api } from "../../../api/client";
import type {
  CompressionResponse,
  Diary,
  DiaryAnimationResult,
  DiaryCoverPayload,
  DiaryCreatePayload,
  DiaryDecompressPayload,
  DiaryDiscoverParams,
  DiaryDiscoverResponse,
  DiaryDraftPayload,
  DiaryDraftResponse,
  DiaryInteractionResponse,
  DiaryListResponse,
  DiaryRateResponse,
  DiarySearchResponse,
  ImageGenerateResponse,
} from "../types/diary";

export async function listDiaries(): Promise<DiaryListResponse> {
  const { data } = await api.get<DiaryListResponse>("/diaries");
  return data;
}

export async function discoverDiaries(
  params: DiaryDiscoverParams = {},
): Promise<DiaryDiscoverResponse> {
  const cleanedParams: Record<string, string | number> = {};
  if (params.q) cleanedParams.q = params.q;
  if (params.search_type) cleanedParams.search_type = params.search_type;
  if (params.sort) cleanedParams.sort = params.sort;
  if (params.page) cleanedParams.page = params.page;
  if (params.page_size) cleanedParams.page_size = params.page_size;
  const { data } = await api.get<DiaryDiscoverResponse>("/diaries", {
    params: cleanedParams,
  });
  return data;
}

export async function searchDiaries(query: string): Promise<DiarySearchResponse> {
  const { data } = await api.post<DiarySearchResponse>("/diaries/search", { query });
  return data;
}

export async function getDiary(diaryId: number): Promise<Diary> {
  const { data } = await api.get<Diary>(`/diaries/${diaryId}`);
  return data;
}

export async function createDiary(payload: DiaryCreatePayload): Promise<Diary> {
  const { data } = await api.post<Diary>("/diaries", payload);
  return data;
}

export async function updateDiary(
  diaryId: number,
  payload: Partial<DiaryCreatePayload>,
): Promise<Diary> {
  const { data } = await api.patch<Diary>(`/diaries/${diaryId}`, payload);
  return data;
}

export async function deleteDiary(diaryId: number): Promise<void> {
  await api.delete(`/diaries/${diaryId}`);
}

export async function listMyDiaries(): Promise<DiaryListResponse> {
  const { data } = await api.get<DiaryListResponse>("/diaries/me");
  return data;
}

export interface DiaryUploadResponse {
  url: string;
  type: "image" | "video";
  filename: string;
  size: number;
}

export async function uploadDiaryMedia(file: File): Promise<DiaryUploadResponse> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<DiaryUploadResponse>("/diaries/media/upload", form);
  return data;
}

export async function incrementDiaryView(diaryId: number): Promise<DiaryInteractionResponse> {
  const { data } = await api.post<DiaryInteractionResponse>(`/diaries/${diaryId}/view`);
  return data;
}

export async function rateDiary(diaryId: number, score: number): Promise<DiaryRateResponse> {
  const { data } = await api.post<DiaryRateResponse>(`/diaries/${diaryId}/rate`, { score });
  return data;
}

export async function compressDiary(content: string): Promise<CompressionResponse> {
  const { data } = await api.post<CompressionResponse>("/diaries/compress", { content });
  return data;
}

export async function decompressDiary(payload: DiaryDecompressPayload): Promise<{ content: string }> {
  const { data } = await api.post<{ content: string }>("/diaries/decompress", payload);
  return data;
}

export async function generateDiaryAnimation(diaryId: number): Promise<DiaryAnimationResult> {
  const { data } = await api.post<DiaryAnimationResult>(`/diaries/${diaryId}/aigc-animation`);
  return data;
}

export async function draftDiaryWithAi(payload: DiaryDraftPayload): Promise<DiaryDraftResponse> {
  const { data } = await api.post<DiaryDraftResponse>("/ai/diary/draft", payload);
  return data;
}

export async function generateDiaryCover(payload: DiaryCoverPayload): Promise<ImageGenerateResponse> {
  const { data } = await api.post<ImageGenerateResponse>("/ai/images/generate", payload);
  return data;
}

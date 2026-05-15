import type { Diary, DiaryMedia } from "../types/diary";

/**
 * 读取日记的平均评分。后端同时返回 `rating`（旧）和 `rating_avg`（新），
 * 这里优先新字段，兜底到旧字段，再兜底到 0。
 */
export function getDiaryRating(diary: Pick<Diary, "rating" | "rating_avg"> | null | undefined): number {
  if (!diary) return 0;
  return diary.rating_avg ?? diary.rating ?? 0;
}

const VIDEO_EXTENSIONS = [".mp4", ".webm", ".ogg", ".ogv", ".mov", ".m4v"];

/** 通过 URL 后缀推断媒体类型，找不到默认归类为 image。 */
export function inferMediaType(url: string): "image" | "video" {
  if (!url) return "image";
  const cleaned = url.toLowerCase().split("?")[0].split("#")[0];
  return VIDEO_EXTENSIONS.some((ext) => cleaned.endsWith(ext)) ? "video" : "image";
}

/**
 * 把日记对象规范化为 DiaryMedia[]：
 * - 优先使用 diary.media（新字段，结构化）
 * - 否则按 diary.media_urls 推断类型
 */
export function normalizeDiaryMedia(
  diary: Pick<Diary, "media" | "media_urls"> | null | undefined,
): DiaryMedia[] {
  if (!diary) return [];
  if (Array.isArray(diary.media) && diary.media.length) {
    return diary.media;
  }
  return (diary.media_urls ?? []).map((url, index) => ({
    type: inferMediaType(url),
    url,
    order: index,
  }));
}

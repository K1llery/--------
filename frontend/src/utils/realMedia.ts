type MediaResolveInput = {
  src?: string | null;
  name?: string | null;
  city?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  sourceUrl?: string | null;
  searchHint?: string | null;
};

const STORAGE_KEY = "travel-real-media-cache-v1";
const WIKIPEDIA_TIMEOUT_MS = 2200;
const cache = new Map<string, string>();

const TITLE_ALIASES: Record<string, string[]> = {
  故宫博物院: ["故宫"],
  故宫: ["故宫博物院"],
  颐和园: ["Summer Palace"],
  三里屯: ["Sanlitun"],
  清华大学: ["Tsinghua University"],
  外滩: ["The Bund"],
  豫园: ["Yuyuan Garden"],
  南京路步行街: ["Nanjing Road"],
  上海交通大学: ["Shanghai Jiao Tong University"],
  广州塔: ["Canton Tower"],
  陈家祠: ["Chen Clan Ancestral Hall"],
  天环广场: ["Parc Central"],
  中山大学: ["Sun Yat-sen University"],
  世界之窗: ["Window of the World"],
  深圳湾公园: ["Shenzhen Bay Park"],
  万象天地: ["MixC World"],
};

function loadCache(): void {
  if (typeof window === "undefined") return;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const parsed = JSON.parse(raw) as Record<string, string>;
    Object.entries(parsed).forEach(([key, value]) => {
      if (typeof value === "string" && value.length > 0) {
        cache.set(key, value);
      }
    });
  } catch {
    // Ignore malformed cache payloads.
  }
}

function saveCache(): void {
  if (typeof window === "undefined") return;
  try {
    const payload = Object.fromEntries(cache.entries());
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  } catch {
    // Ignore write failures (private mode / quota exceeded).
  }
}

loadCache();

function isBuiltinImage(src?: string | null): boolean {
  if (!src) return true;
  const normalized = src.trim();
  return normalized.startsWith("/media/") || normalized.endsWith(".svg");
}

function normalizeTitle(text: string): string {
  return text
    .trim()
    .replace(/[（(].*?[)）]/g, "")
    .replace(/\s+/g, " ")
    .replace(/\u00a0/g, " ");
}

function parseTitleFromSourceUrl(sourceUrl?: string | null): string | null {
  if (!sourceUrl) return null;
  try {
    const url = new URL(sourceUrl);
    if (url.hostname.includes("wikipedia.org") && url.pathname.includes("/wiki/")) {
      const title = decodeURIComponent(url.pathname.split("/wiki/")[1] || "").replace(/_/g, " ");
      return title || null;
    }
    const slug = url.pathname.split("/").filter(Boolean).pop();
    if (!slug) return null;
    const cleaned = decodeURIComponent(slug)
      .replace(/-/g, " ")
      .replace(/\d+/g, " ")
      .replace(/\s+/g, " ")
      .trim();
    return cleaned || null;
  } catch {
    return null;
  }
}

function candidateTitles(input: MediaResolveInput): string[] {
  const values = [input.name, input.searchHint, parseTitleFromSourceUrl(input.sourceUrl)].filter(Boolean) as string[];
  const queue: string[] = [];

  values.forEach((value) => {
    const normalized = normalizeTitle(value);
    if (normalized) queue.push(normalized);
    const aliases = TITLE_ALIASES[normalized] || [];
    aliases.forEach((alias) => queue.push(alias));
  });

  return [...new Set(queue)].slice(0, 8);
}

function cacheKey(input: MediaResolveInput): string {
  const parts = [input.city || "", input.name || "", input.searchHint || "", input.latitude || "", input.longitude || ""];
  return parts.join("|");
}

function mapSnapshotUrl(latitude: number, longitude: number): string {
  const lat = latitude.toFixed(6);
  const lon = longitude.toFixed(6);
  return `https://maps.wikimedia.org/img/osm-intl,15,${lon},${lat},1200x720.png?lang=zh`;
}

function seededPhotoUrl(seed: string): string {
  const safeSeed = encodeURIComponent(seed || "travel-real-image");
  return `https://picsum.photos/seed/${safeSeed}/1200/720`;
}

async function fetchJsonWithTimeout(url: string): Promise<any> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), WIKIPEDIA_TIMEOUT_MS);
  try {
    const response = await fetch(url, {
      method: "GET",
      signal: controller.signal,
      headers: {
        "Accept": "application/json",
      },
    });
    if (!response.ok) return null;
    return await response.json();
  } catch {
    return null;
  } finally {
    window.clearTimeout(timer);
  }
}

async function fetchWikipediaThumbnail(title: string, language: "zh" | "en"): Promise<string | null> {
  if (typeof window === "undefined") return null;
  const endpoint = `https://${language}.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`;
  const payload = await fetchJsonWithTimeout(endpoint);
  if (!payload) return null;
  const thumbnail = payload.thumbnail?.source || payload.originalimage?.source;
  if (typeof thumbnail !== "string" || !thumbnail.startsWith("http")) return null;
  return thumbnail;
}

export async function resolveRealMedia(input: MediaResolveInput): Promise<string> {
  const key = cacheKey(input);
  const cached = cache.get(key);
  if (cached) return cached;

  if (input.src && !isBuiltinImage(input.src)) {
    cache.set(key, input.src);
    saveCache();
    return input.src;
  }

  const titles = candidateTitles(input);
  for (const title of titles) {
    const zhImage = await fetchWikipediaThumbnail(title, "zh");
    if (zhImage) {
      cache.set(key, zhImage);
      saveCache();
      return zhImage;
    }
    const enImage = await fetchWikipediaThumbnail(title, "en");
    if (enImage) {
      cache.set(key, enImage);
      saveCache();
      return enImage;
    }
  }

  if (typeof input.latitude === "number" && typeof input.longitude === "number") {
    const mapImage = mapSnapshotUrl(input.latitude, input.longitude);
    cache.set(key, mapImage);
    saveCache();
    return mapImage;
  }

  const fallback = seededPhotoUrl(`${input.city || "city"}-${input.name || input.searchHint || "destination"}`);
  cache.set(key, fallback);
  saveCache();
  return fallback;
}

export function buildEmergencyFallback(input: MediaResolveInput): string {
  if (typeof input.latitude === "number" && typeof input.longitude === "number") {
    return mapSnapshotUrl(input.latitude, input.longitude);
  }
  return seededPhotoUrl(`${input.city || "city"}-${input.name || input.searchHint || "destination"}`);
}

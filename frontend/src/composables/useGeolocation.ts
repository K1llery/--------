import { ref } from "vue";

export interface GeoLocation {
  latitude: number;
  longitude: number;
}

export function useGeolocation() {
  const currentLocation = ref<GeoLocation | null>(null);
  const locating = ref(false);
  const error = ref("");
  const supportsGeolocation = typeof navigator !== "undefined" && "geolocation" in navigator;

  const capture = async (): Promise<boolean> => {
    if (!supportsGeolocation) {
      error.value = "当前浏览器不支持定位。";
      return false;
    }
    locating.value = true;
    error.value = "";
    try {
      const coordinates = await new Promise<GeoLocation>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
          (position) =>
            resolve({
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
            }),
          reject,
          { enableHighAccuracy: true, timeout: 5000 },
        );
      });
      currentLocation.value = coordinates;
      return true;
    } catch {
      error.value = "定位失败，请检查浏览器定位权限或改用手动起点。";
      return false;
    } finally {
      locating.value = false;
    }
  };

  const locationPayload = (useCurrentLocation: boolean) => {
    if (useCurrentLocation && currentLocation.value) {
      return {
        prefer_nearest_start: true,
        start_latitude: currentLocation.value.latitude,
        start_longitude: currentLocation.value.longitude,
      };
    }
    return {
      prefer_nearest_start: false,
      start_latitude: null,
      start_longitude: null,
    };
  };

  return {
    currentLocation,
    locating,
    error,
    supportsGeolocation,
    capture,
    locationPayload,
  };
}

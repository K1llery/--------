export interface RouteBasePayload extends Record<string, unknown> {
  scene_name: string;
  start_code: string;
  transport_mode: string;
  prefer_nearest_start: boolean;
  start_latitude?: number;
  start_longitude?: number;
}

export interface MultiRouteOptions {
  stopCodes: string[];
  transportMode: string;
  strategy: string;
}

export interface MultiRoutePayload extends RouteBasePayload {
  target_codes: string[];
  strategy: string;
}

export const buildMultiRoutePayload = (
  basePayload: RouteBasePayload,
  options: MultiRouteOptions,
): MultiRoutePayload => ({
  ...basePayload,
  transport_mode: options.transportMode,
  target_codes: options.stopCodes,
  strategy: options.strategy,
});

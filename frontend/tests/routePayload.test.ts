import assert from "node:assert/strict";

import { buildMultiRoutePayload } from "../src/utils/routePayload.ts";

const payload = buildMultiRoutePayload(
  {
    scene_name: "BUPT_Main_Campus",
    start_code: "bupt_gate",
    transport_mode: "mixed",
    prefer_nearest_start: true,
    start_latitude: 39.962,
    start_longitude: 116.358,
  },
  {
    stopCodes: ["library", "canteen", "teaching_3"],
    transportMode: "bike",
    strategy: "time",
  },
);

assert.deepEqual(payload, {
  scene_name: "BUPT_Main_Campus",
  start_code: "bupt_gate",
  transport_mode: "bike",
  prefer_nearest_start: true,
  start_latitude: 39.962,
  start_longitude: 116.358,
  target_codes: ["library", "canteen", "teaching_3"],
  strategy: "time",
});

assert.equal("waypoint_codes" in payload, false);

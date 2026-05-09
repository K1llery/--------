import assert from "node:assert/strict";

import { buildInitialTripTargets } from "../src/utils/routeTrip.ts";

const places = [
  { code: "gate" },
  { code: "library" },
  { code: "canteen" },
  { code: "gym" },
];

assert.deepEqual(
  buildInitialTripTargets({
    placeOptions: places,
    startCode: "gate",
    currentStopCodes: ["gate", "library", "library", "missing"],
  }),
  ["library", "canteen"],
);

assert.deepEqual(
  buildInitialTripTargets({
    placeOptions: [{ code: "gate" }],
    startCode: "gate",
  }),
  ["", ""],
);

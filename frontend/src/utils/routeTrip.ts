interface TripPlace {
  code: string;
}

export interface BuildInitialTripTargetsOptions {
  placeOptions: TripPlace[];
  currentStopCodes?: string[];
  startCode?: string;
  minStops?: number;
  maxStops?: number;
}

export const buildInitialTripTargets = ({
  placeOptions,
  currentStopCodes = [],
  startCode = "",
  minStops = 2,
  maxStops = 8,
}: BuildInitialTripTargetsOptions): string[] => {
  const validCodes = new Set(placeOptions.map((place) => place.code));
  const selected: string[] = [];

  const addIfUsable = (code: string) => {
    if (!code || code === startCode || !validCodes.has(code) || selected.includes(code)) return;
    if (selected.length >= maxStops) return;
    selected.push(code);
  };

  currentStopCodes.forEach(addIfUsable);
  for (const place of placeOptions) {
    if (selected.length >= minStops) break;
    addIfUsable(place.code);
  }

  while (selected.length < minStops) {
    selected.push("");
  }

  return selected.slice(0, maxStops);
};

import { computed, ref, type ComputedRef, type Ref } from "vue";

import type { RouteSegment, SceneNode } from "../types/models";

export type MapInteractionMode = "idle" | "set-origin" | "set-destination";

export interface RouteNavigationOptions {
  segments: ComputedRef<RouteSegment[]>;
  routeNodes: ComputedRef<SceneNode[]>;
  allNodes: ComputedRef<SceneNode[]>;
}

export function useRouteNavigation(options: RouteNavigationOptions) {
  const activeSegmentIndex: Ref<number | null> = ref(null);
  const mapInteractionMode: Ref<MapInteractionMode> = ref("idle");
  const highlightedAltIndex: Ref<number | null> = ref(null);
  const selectedOriginCode = ref("");
  const selectedDestinationCode = ref("");

  const totalSegments = computed(() => options.segments.value.length);

  const activeSegment = computed<RouteSegment | null>(() => {
    if (activeSegmentIndex.value === null) return null;
    return options.segments.value[activeSegmentIndex.value] ?? null;
  });

  const activeSegmentPath = computed<string[]>(() => {
    const seg = activeSegment.value;
    if (!seg) return [];
    return [seg.from_code, seg.to_code];
  });

  const activeSegmentBounds = computed<
    Array<[number, number]> | null
  >(() => {
    const seg = activeSegment.value;
    if (!seg) return null;
    const nodes = options.routeNodes.value;
    const fromNode = nodes.find((n) => n.code === seg.from_code);
    const toNode = nodes.find((n) => n.code === seg.to_code);
    if (!fromNode || !toNode) return null;
    return [
      [fromNode.latitude, fromNode.longitude],
      [toNode.latitude, toNode.longitude],
    ];
  });

  const goToSegment = (index: number) => {
    if (index >= 0 && index < totalSegments.value) {
      activeSegmentIndex.value = index;
    }
  };

  const nextSegment = () => {
    if (activeSegmentIndex.value === null) {
      if (totalSegments.value > 0) activeSegmentIndex.value = 0;
      return;
    }
    if (activeSegmentIndex.value < totalSegments.value - 1) {
      activeSegmentIndex.value++;
    }
  };

  const prevSegment = () => {
    if (activeSegmentIndex.value === null) return;
    if (activeSegmentIndex.value > 0) {
      activeSegmentIndex.value--;
    }
  };

  const exitNavigation = () => {
    activeSegmentIndex.value = null;
  };

  const findNearestNode = (
    lat: number,
    lng: number,
    nodes: SceneNode[],
  ): SceneNode | null => {
    let best: SceneNode | null = null;
    let bestDist = Infinity;
    for (const node of nodes) {
      if (node.route_node_type === "road") continue;
      const dlat = node.latitude - lat;
      const dlng = node.longitude - lng;
      const dist = dlat * dlat + dlng * dlng;
      if (dist < bestDist) {
        bestDist = dist;
        best = node;
      }
    }
    return best;
  };

  const onMapClick = (lat: number, lng: number) => {
    if (mapInteractionMode.value === "idle") return;
    const nearest = findNearestNode(lat, lng, options.allNodes.value);
    if (!nearest) return;

    if (mapInteractionMode.value === "set-origin") {
      selectedOriginCode.value = nearest.code;
    } else if (mapInteractionMode.value === "set-destination") {
      selectedDestinationCode.value = nearest.code;
    }
    mapInteractionMode.value = "idle";
  };

  const startSetOrigin = () => {
    mapInteractionMode.value = "set-origin";
  };

  const startSetDestination = () => {
    mapInteractionMode.value = "set-destination";
  };

  const cancelMapInteraction = () => {
    mapInteractionMode.value = "idle";
  };

  const resetNavigation = () => {
    activeSegmentIndex.value = null;
    highlightedAltIndex.value = null;
    mapInteractionMode.value = "idle";
  };

  return {
    activeSegmentIndex,
    mapInteractionMode,
    highlightedAltIndex,
    selectedOriginCode,
    selectedDestinationCode,
    totalSegments,
    activeSegment,
    activeSegmentPath,
    activeSegmentBounds,
    goToSegment,
    nextSegment,
    prevSegment,
    exitNavigation,
    findNearestNode,
    onMapClick,
    startSetOrigin,
    startSetDestination,
    cancelMapInteraction,
    resetNavigation,
  };
}

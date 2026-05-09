<template>
  <div class="map-shell" :class="{ 'map-mode-crosshair': interactionMode !== 'idle' }">
    <div v-if="mapError" class="map-error">地图加载失败，请稍后重试。</div>
    <div ref="mapEl" class="route-map"></div>
    <Transition name="page-fade-slide">
      <div
        v-if="contextMenu.visible"
        class="map-context-menu"
        :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      >
        <button type="button" @click="onContextAction('origin')">📍 设为起点</button>
        <button type="button" @click="onContextAction('destination')">🎯 设为终点</button>
        <button type="button" @click="onContextAction('cancel')">取消</button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";

import type { MapInteractionMode } from "../composables/useRouteNavigation";
import type { Facility, RouteSegment } from "../types/models";

interface MapNode {
  code: string;
  name: string;
  latitude: number;
  longitude: number;
  route_node_type?: string;
}

const props = withDefaults(
  defineProps<{
    nodes: MapNode[];
    path: string[];
    pathColor?: string;
    currentLocation?: { latitude: number; longitude: number } | null;
    interactionMode?: MapInteractionMode;
    activeSegmentPath?: string[];
    alternativeRoutes?: Array<{ pathCodes: string[]; color: string; label: string }>;
    fitBounds?: Array<[number, number]> | null;
    /** Per-segment data so polyline can be colored by congestion */
    segments?: RouteSegment[];
    /** Facilities to show as overlay markers (in addition to route nodes) */
    overlayFacilities?: Facility[];
  }>(),
  {
    pathColor: "#6366f1",
    currentLocation: null,
    interactionMode: "idle",
    activeSegmentPath: () => [],
    alternativeRoutes: () => [],
    fitBounds: null,
    segments: () => [],
    overlayFacilities: () => [],
  },
);

const emit = defineEmits<{
  "map-click": [lat: number, lng: number];
  "marker-click": [data: { code: string; action: "origin" | "destination" }];
  "facility-click": [data: { code: string; action: "destination" }];
  "context-action": [
    data: { action: "origin" | "destination"; lat: number; lng: number },
  ];
}>();

const mapEl = ref<HTMLDivElement | null>(null);
const mapError = ref(false);
let map: L.Map | null = null;
let markersLayer: L.LayerGroup | null = null;
let facilityLayer: L.LayerGroup | null = null;
let pathLayers: L.Polyline[] = [];
let activeSegmentLayer: L.Polyline | null = null;
let dimmedPathLayer: L.Polyline | null = null;
let currentLocationLayer: L.LayerGroup | null = null;
let alternativePathLayers: L.Polyline[] = [];
let dashTimer: number | null = null;
let dashOffset = 0;

const contextMenu = reactive({
  visible: false,
  x: 0,
  y: 0,
  lat: 0,
  lng: 0,
});

const congestionColor = (c: number): string => {
  if (c < 0.3) return "#22c55e";
  if (c < 0.6) return "#eab308";
  if (c < 0.85) return "#f97316";
  return "#ef4444";
};

const clearAlternativeLayers = () => {
  alternativePathLayers.forEach((layer) => map?.removeLayer(layer));
  alternativePathLayers = [];
};

const clearPathLayers = () => {
  pathLayers.forEach((l) => map?.removeLayer(l));
  pathLayers = [];
  if (activeSegmentLayer) {
    map?.removeLayer(activeSegmentLayer);
    activeSegmentLayer = null;
  }
  if (dimmedPathLayer) {
    map?.removeLayer(dimmedPathLayer);
    dimmedPathLayer = null;
  }
  if (dashTimer) {
    window.clearInterval(dashTimer);
    dashTimer = null;
  }
};

const renderMarkers = () => {
  if (!map) return;
  const pathIndex = new Map(props.path.map((code, index) => [code, index]));
  markersLayer?.clearLayers();

  props.nodes.forEach((node) => {
    const index = pathIndex.get(node.code);
    if (node.route_node_type === "road") return;
    const isStart = index === 0;
    const isEnd = index === props.path.length - 1 && props.path.length > 1;
    const isOnPath = index !== undefined;
    const markerColor = isStart ? "#1475c4" : isEnd ? "#d44f2a" : isOnPath ? "#b7672a" : "#8d9fb0";
    const fillColor = isStart ? "#55aaf1" : isEnd ? "#f4895f" : isOnPath ? "#f0a25d" : "#c8d2dc";
    const marker = L.circleMarker([node.latitude, node.longitude], {
      radius: isStart || isEnd ? 9 : isOnPath ? 7 : 6,
      color: markerColor,
      weight: 2,
      fillColor,
      fillOpacity: 0.96,
    });

    const popupContent = document.createElement("div");
    popupContent.className = "marker-popup-content";
    popupContent.innerHTML = `
      <strong>${node.name}</strong>
      <div class="marker-popup-actions">
        <button class="marker-popup-btn" data-action="origin">设为起点</button>
        <button class="marker-popup-btn" data-action="destination">设为终点</button>
      </div>
    `;
    popupContent.addEventListener("click", (e) => {
      const btn = (e.target as HTMLElement).closest("[data-action]") as HTMLElement | null;
      if (!btn) return;
      const action = btn.dataset.action as "origin" | "destination";
      emit("marker-click", { code: node.code, action });
      marker.closePopup();
    });
    marker.bindPopup(popupContent);

    if (isOnPath) {
      marker.bindTooltip(`#${index + 1} ${node.name}`, {
        permanent: false,
        direction: "top",
      });
    }

    markersLayer?.addLayer(marker);
  });
};

const renderFacilityOverlay = () => {
  if (!map) return;
  facilityLayer?.clearLayers();
  if (!props.overlayFacilities.length) return;

  props.overlayFacilities.forEach((f) => {
    const marker = L.circleMarker([f.latitude, f.longitude], {
      radius: 7,
      color: "#7c3aed",
      weight: 2,
      fillColor: "#c4b5fd",
      fillOpacity: 0.95,
    });

    const popup = document.createElement("div");
    popup.className = "marker-popup-content";
    popup.innerHTML = `
      <strong>${f.name}</strong>
      <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 4px;">
        ${f.facility_label || f.facility_type}
      </div>
      <div class="marker-popup-actions">
        <button class="marker-popup-btn" data-fac="destination">导航到这里</button>
      </div>
    `;
    popup.addEventListener("click", (e) => {
      const btn = (e.target as HTMLElement).closest("[data-fac]") as HTMLElement | null;
      if (!btn) return;
      emit("facility-click", { code: f.code, action: "destination" });
      marker.closePopup();
    });
    marker.bindPopup(popup);
    marker.bindTooltip(f.name, { direction: "top" });
    facilityLayer?.addLayer(marker);
  });
};

const renderCurrentLocation = () => {
  currentLocationLayer?.clearLayers();
  if (!props.currentLocation) return;
  const marker = L.circleMarker(
    [props.currentLocation.latitude, props.currentLocation.longitude],
    {
      radius: 8,
      color: "#1e90ff",
      weight: 2,
      fillColor: "#7bc4ff",
      fillOpacity: 0.98,
    },
  ).bindTooltip("当前位置", { direction: "top" });
  currentLocationLayer?.addLayer(marker);
};

const renderPath = () => {
  if (!map) return;
  const nodeMap = new Map(props.nodes.map((item) => [item.code, item]));

  clearPathLayers();

  const coordinates = props.path
    .map((code) => nodeMap.get(code))
    .filter(Boolean)
    .map((node) => [node!.latitude, node!.longitude] as [number, number]);

  if (coordinates.length <= 1) return;

  const hasActiveSegment = props.activeSegmentPath.length >= 2;

  // Render base path: per-segment colored by congestion if segments provided,
  // else fall back to single polyline.
  if (props.segments && props.segments.length > 0 && !hasActiveSegment) {
    // Use segments to color polyline pieces
    props.segments.forEach((seg) => {
      const fromNode = nodeMap.get(seg.from_code);
      const toNode = nodeMap.get(seg.to_code);
      if (!fromNode || !toNode) return;
      const color = congestionColor(seg.congestion ?? 0);
      const line = L.polyline(
        [
          [fromNode.latitude, fromNode.longitude],
          [toNode.latitude, toNode.longitude],
        ],
        {
          color,
          weight: 6,
          opacity: 0.9,
        },
      ).addTo(map!);
      line.bindTooltip(
        `${seg.from_name} → ${seg.to_name}<br/>${seg.distance_m}米 · ${seg.estimated_minutes}分钟 · 拥挤度 ${(seg.congestion * 100).toFixed(0)}%`,
        { sticky: true },
      );
      pathLayers.push(line);
    });
  } else if (hasActiveSegment) {
    // Dim the rest, highlight the active segment
    dimmedPathLayer = L.polyline(coordinates, {
      color: props.pathColor,
      weight: 4,
      opacity: 0.3,
      dashArray: "8 6",
    }).addTo(map);

    const segCoords = props.activeSegmentPath
      .map((code) => nodeMap.get(code))
      .filter(Boolean)
      .map((node) => [node!.latitude, node!.longitude] as [number, number]);

    if (segCoords.length > 1) {
      activeSegmentLayer = L.polyline(segCoords, {
        color: "#6366f1",
        weight: 7,
        opacity: 0.95,
        dashArray: "12 10",
        dashOffset: "0",
      }).addTo(map);

      dashOffset = 0;
      dashTimer = window.setInterval(() => {
        if (!activeSegmentLayer) return;
        dashOffset -= 1;
        (activeSegmentLayer as any).setStyle({ dashOffset: `${dashOffset}` });
      }, 80);
    }
  } else {
    // Plain polyline fallback
    const line = L.polyline(coordinates, {
      color: props.pathColor,
      weight: 5,
      opacity: 0.9,
      dashArray: "12 10",
      dashOffset: "0",
    }).addTo(map);
    pathLayers.push(line);

    dashOffset = 0;
    dashTimer = window.setInterval(() => {
      if (!line) return;
      dashOffset -= 1;
      (line as any).setStyle({ dashOffset: `${dashOffset}` });
    }, 80);
  }
};

const renderAlternatives = () => {
  if (!map) return;
  clearAlternativeLayers();
  const nodeMap = new Map(props.nodes.map((item) => [item.code, item]));

  props.alternativeRoutes.forEach((alt) => {
    const coords = alt.pathCodes
      .map((code) => nodeMap.get(code))
      .filter(Boolean)
      .map((node) => [node!.latitude, node!.longitude] as [number, number]);

    if (coords.length <= 1) return;

    const line = L.polyline(coords, {
      color: alt.color,
      weight: 3,
      opacity: 0.4,
      dashArray: "6 8",
    }).addTo(map!);

    line.bindTooltip(alt.label, { sticky: true });

    line.on("mouseover", () => line.setStyle({ opacity: 0.8, weight: 5 }));
    line.on("mouseout", () => line.setStyle({ opacity: 0.4, weight: 3 }));

    alternativePathLayers.push(line);
  });
};

const fitMapBounds = () => {
  if (!map) return;
  const nodeMap = new Map(props.nodes.map((item) => [item.code, item]));

  if (props.fitBounds && props.fitBounds.length >= 2) {
    map.fitBounds(props.fitBounds as L.LatLngBoundsExpression, { padding: [50, 50] });
    return;
  }

  const pathCoords = props.path
    .map((code) => nodeMap.get(code))
    .filter(Boolean)
    .map((node) => [node!.latitude, node!.longitude] as [number, number]);

  if (pathCoords.length > 1) {
    map.fitBounds(pathCoords as L.LatLngBoundsExpression, { padding: [30, 30] });
  } else if (props.nodes.length > 0) {
    const bounds = L.latLngBounds(
      props.nodes.map((node) => [node.latitude, node.longitude] as [number, number]),
    );
    if (props.currentLocation) {
      bounds.extend([props.currentLocation.latitude, props.currentLocation.longitude]);
    }
    map.fitBounds(bounds, { padding: [30, 30] });
  } else if (props.currentLocation) {
    map.setView([props.currentLocation.latitude, props.currentLocation.longitude], 15);
  }
};

const renderMap = () => {
  renderMarkers();
  renderFacilityOverlay();
  renderCurrentLocation();
  renderPath();
  renderAlternatives();
  fitMapBounds();
};

const onContextAction = (action: "origin" | "destination" | "cancel") => {
  if (action !== "cancel") {
    emit("context-action", {
      action,
      lat: contextMenu.lat,
      lng: contextMenu.lng,
    });
  }
  contextMenu.visible = false;
};

const closeContextMenu = () => {
  contextMenu.visible = false;
};

onMounted(() => {
  if (!mapEl.value) return;
  map = L.map(mapEl.value, { zoomControl: true });
  const tileLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  });
  tileLayer.on("tileerror", () => {
    mapError.value = true;
  });
  tileLayer.addTo(map);
  markersLayer = L.layerGroup().addTo(map);
  facilityLayer = L.layerGroup().addTo(map);
  currentLocationLayer = L.layerGroup().addTo(map);

  map.on("click", (e: L.LeafletMouseEvent) => {
    closeContextMenu();
    if (props.interactionMode !== "idle") {
      emit("map-click", e.latlng.lat, e.latlng.lng);
    }
  });

  map.on("contextmenu", (e: L.LeafletMouseEvent) => {
    L.DomEvent.preventDefault(e.originalEvent);
    const rect = mapEl.value!.getBoundingClientRect();
    contextMenu.x = e.originalEvent.clientX - rect.left;
    contextMenu.y = e.originalEvent.clientY - rect.top;
    contextMenu.lat = e.latlng.lat;
    contextMenu.lng = e.latlng.lng;
    contextMenu.visible = true;
  });

  // Long-press for touch devices
  let pressTimer: number | null = null;
  let pressStartXY: [number, number] | null = null;
  map.on("touchstart" as any, (e: any) => {
    const touch = e.originalEvent?.touches?.[0];
    if (!touch) return;
    pressStartXY = [touch.clientX, touch.clientY];
    pressTimer = window.setTimeout(() => {
      const rect = mapEl.value!.getBoundingClientRect();
      contextMenu.x = touch.clientX - rect.left;
      contextMenu.y = touch.clientY - rect.top;
      const ll = map!.containerPointToLatLng([
        touch.clientX - rect.left,
        touch.clientY - rect.top,
      ]);
      contextMenu.lat = ll.lat;
      contextMenu.lng = ll.lng;
      contextMenu.visible = true;
    }, 600);
  });
  const cancelPress = () => {
    if (pressTimer) {
      window.clearTimeout(pressTimer);
      pressTimer = null;
    }
    pressStartXY = null;
  };
  map.on("touchend" as any, cancelPress);
  map.on("touchmove" as any, (e: any) => {
    const touch = e.originalEvent?.touches?.[0];
    if (!touch || !pressStartXY) return;
    const dx = touch.clientX - pressStartXY[0];
    const dy = touch.clientY - pressStartXY[1];
    if (Math.abs(dx) > 8 || Math.abs(dy) > 8) cancelPress();
  });

  renderMap();
});

watch(
  () => [props.nodes, props.path, props.currentLocation, props.segments],
  renderMap,
  { deep: true },
);

watch(
  () => props.activeSegmentPath,
  () => {
    renderPath();
    if (props.fitBounds) {
      fitMapBounds();
    }
  },
  { deep: true },
);

watch(
  () => props.fitBounds,
  (bounds) => {
    if (bounds && map) {
      map.fitBounds(bounds as L.LatLngBoundsExpression, { padding: [50, 50], maxZoom: 17 });
    }
  },
  { deep: true },
);

watch(
  () => props.alternativeRoutes,
  renderAlternatives,
  { deep: true },
);

watch(
  () => props.overlayFacilities,
  renderFacilityOverlay,
  { deep: true },
);

onBeforeUnmount(() => {
  if (dashTimer) {
    window.clearInterval(dashTimer);
    dashTimer = null;
  }
  clearPathLayers();
  clearAlternativeLayers();
  map?.remove();
});
</script>

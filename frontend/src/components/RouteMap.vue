<template>
  <div class="map-shell">
    <div v-if="mapError" class="map-error">地图加载失败，请稍后重试。</div>
    <div ref="mapEl" class="route-map"></div>
  </div>
</template>

<script setup lang="ts">
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps<{
  nodes: Array<{
    code: string;
    name: string;
    latitude: number;
    longitude: number;
    route_node_type?: string;
  }>;
  edges?: Array<{
    source_code: string;
    target_code: string;
    distance: number;
    congestion: number;
    allowed_modes: string[];
  }>;
  path: string[];
  pathColor?: string;
  currentLocation?: { latitude: number; longitude: number } | null;
}>();

const mapEl = ref<HTMLDivElement | null>(null);
const mapError = ref(false);
let map: L.Map | null = null;
let roadLayer: L.LayerGroup | null = null;
let markersLayer: L.LayerGroup | null = null;
let pathLayer: L.Polyline | null = null;
let currentLocationLayer: L.LayerGroup | null = null;
let dashTimer: number | null = null;
let dashOffset = 0;

const renderMap = () => {
  if (!map) return;
  const nodeMap = new Map(props.nodes.map((item) => [item.code, item]));
  const pathIndex = new Map(props.path.map((code, index) => [code, index]));
  roadLayer?.clearLayers();
  markersLayer?.clearLayers();
  currentLocationLayer?.clearLayers();

  props.edges?.forEach((edge) => {
    const source = nodeMap.get(edge.source_code);
    const target = nodeMap.get(edge.target_code);
    if (!source || !target) return;
    const road = L.polyline(
      [
        [source.latitude, source.longitude],
        [target.latitude, target.longitude],
      ],
      {
        color: edge.congestion <= 0.65 ? "#d08a4f" : "#5d8798",
        weight: 2,
        opacity: 0.34,
        lineCap: "round",
      },
    ).bindTooltip(
      `${source.name} → ${target.name} · ${Number(edge.distance).toFixed(0)}m`,
      { sticky: true },
    );
    roadLayer?.addLayer(road);
  });

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
    }).bindPopup(`${node.name}`);

    if (isOnPath) {
      marker.bindTooltip(`#${index + 1} ${node.name}`, {
        permanent: false,
        direction: "top",
      });
    }

    markersLayer?.addLayer(marker);
  });

  if (props.currentLocation) {
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
  }

  if (pathLayer) {
    map.removeLayer(pathLayer);
    pathLayer = null;
  }
  if (dashTimer) {
    window.clearInterval(dashTimer);
    dashTimer = null;
  }

  const coordinates = props.path
    .map((code) => nodeMap.get(code))
    .filter(Boolean)
    .map((node) => [node!.latitude, node!.longitude] as [number, number]);

  if (coordinates.length > 1) {
    pathLayer = L.polyline(coordinates, {
      color: props.pathColor ?? "#b65a2e",
      weight: 5,
      opacity: 0.9,
      dashArray: "12 10",
      dashOffset: "0",
    }).addTo(map);

    dashOffset = 0;
    dashTimer = window.setInterval(() => {
      if (!pathLayer) return;
      dashOffset -= 1;
      pathLayer.setStyle({ dashOffset: `${dashOffset}` } as L.PolylineOptions & {
        dashOffset: string;
      });
    }, 80);

    map.fitBounds(pathLayer.getBounds(), { padding: [30, 30] });
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
  roadLayer = L.layerGroup().addTo(map);
  markersLayer = L.layerGroup().addTo(map);
  currentLocationLayer = L.layerGroup().addTo(map);
  renderMap();
});

watch(
  () => [props.nodes, props.edges, props.path, props.currentLocation],
  () => {
    renderMap();
  },
  { deep: true },
);

onBeforeUnmount(() => {
  if (dashTimer) {
    window.clearInterval(dashTimer);
    dashTimer = null;
  }
  map?.remove();
});
</script>

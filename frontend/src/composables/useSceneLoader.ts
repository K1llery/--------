import { computed, ref } from "vue";

import { api } from "../api/client";
import type {
  Destination,
  IndoorBuilding,
  Scene,
  SceneEdge,
  SceneNode,
  Facility,
} from "../types/models";
import type { IndoorBuildingListResponse, SceneDetailResponse } from "../types/api";

export function useSceneLoader() {
  const scenes = ref<Scene[]>([]);
  const featuredDestinations = ref<Destination[]>([]);
  const indoorBuildings = ref<IndoorBuilding[]>([]);
  const scene = ref<{ nodes: SceneNode[] } | null>(null);
  const facilities = ref<Facility[]>([]);
  const edges = ref<SceneEdge[]>([]);

  const loadMeta = async () => {
    const [sceneRes, featuredRes, indoorRes] = await Promise.all([
      api.get<Scene[]>("/map/scenes"),
      api.get<Destination[]>("/destinations/featured"),
      api.get<IndoorBuildingListResponse>("/indoor/buildings"),
    ]);
    scenes.value = sceneRes.data;
    featuredDestinations.value = featuredRes.data;
    indoorBuildings.value = indoorRes.data.items ?? [];
  };

  const loadScene = async (sceneName: string) => {
    const { data } = await api.get<SceneDetailResponse>(`/map/scenes/${sceneName}`);
    scene.value = data.scene;
    facilities.value = data.facilities;
    edges.value = data.edges;
  };

  const getVisibleScenes = (city: string) =>
    computed(() => scenes.value.filter((item) => item.city === city));

  return {
    scenes,
    featuredDestinations,
    indoorBuildings,
    scene,
    facilities,
    edges,
    loadMeta,
    loadScene,
    getVisibleScenes,
  };
}

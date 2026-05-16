import type { Food } from "../../types/models";

export type AnchorType = "destination" | "school";

export type FoodRecommendation = Food & {
  source_id?: string;
  destination_name?: string;
  source_url?: string;
  image_source_name?: string;
};

export type FoodAnchorOption = {
  id: string;
  name: string;
  type: AnchorType;
  city?: string;
  latitude?: number;
  longitude?: number;
};

export type RadiusOption = {
  label: string;
  value: number;
};

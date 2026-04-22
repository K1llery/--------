from pydantic import BaseModel, Field


class IndoorRouteRequest(BaseModel):
    building_code: str
    start_node_code: str
    end_node_code: str
    strategy: str = "time"
    mobility_mode: str = "normal"


class IndoorBuildingListResponse(BaseModel):
    items: list[dict] = Field(default_factory=list)


class IndoorRouteResponse(BaseModel):
    building_code: str
    building_name: str
    path_node_codes: list[str] = Field(default_factory=list)
    path_node_names: list[str] = Field(default_factory=list)
    strategy: str
    mobility_mode: str
    total_distance_m: float
    estimated_seconds: float
    summary: str
    steps: list[dict] = Field(default_factory=list)

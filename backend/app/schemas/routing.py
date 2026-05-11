from pydantic import BaseModel, Field


class RoutePoint(BaseModel):
    code: str


class SingleRouteRequest(BaseModel):
    scene_name: str
    start_code: str
    end_code: str
    strategy: str = "distance"
    transport_mode: str = "walk"
    prefer_nearest_start: bool = False
    start_latitude: float | None = None
    start_longitude: float | None = None


class MultiRouteRequest(BaseModel):
    scene_name: str
    start_code: str
    target_codes: list[str] = Field(default_factory=list)
    strategy: str = "distance"
    transport_mode: str = "walk"
    prefer_nearest_start: bool = False
    start_latitude: float | None = None
    start_longitude: float | None = None


class WanderRouteRequest(BaseModel):
    scene_name: str
    start_code: str
    transport_mode: str = "walk"
    duration_minutes: int = Field(default=45, ge=10, le=180)
    prefer_nearest_start: bool = False
    start_latitude: float | None = None
    start_longitude: float | None = None


class NearbyFacilityRouteRequest(BaseModel):
    scene_name: str
    start_code: str
    facility_type: str = "restroom"
    transport_mode: str = "walk"
    strategy: str = "time"
    radius: float = Field(default=1200.0, gt=0, le=5000)
    prefer_nearest_start: bool = False
    start_latitude: float | None = None
    start_longitude: float | None = None


class RouteResponse(BaseModel):
    path: list[str]
    total_distance: float
    total_cost: float


class OptimizeOrderRequest(BaseModel):
    destination_ids: list[str] = Field(default_factory=list, min_length=2)


class OptimizeOrderResponse(BaseModel):
    ordered_ids: list[str]
    total_distance_km: float
    optimization_label: str

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field

from app.api.deps import extract_token, get_auth_service, get_current_user
from app.core.exceptions import AuthenticationError
from app.services.auth_service import AuthService

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    display_name: str | None = None


class FavoriteDestinationRequest(BaseModel):
    source_id: str


class FavoriteRouteRequest(BaseModel):
    scene_name: str
    strategy: str
    transport_mode: str
    path_codes: list[str] = Field(default_factory=list)
    path_names: list[str] = Field(default_factory=list)
    total_distance_m: float = 0.0
    estimated_minutes: float = 0.0
    explanation: str = ""


@router.post("/register")
def register(payload: RegisterRequest, service: AuthService = Depends(get_auth_service)) -> dict:
    user, token = service.register(payload.username, payload.password, payload.display_name)
    return {"user": user, "token": token}


@router.post("/login")
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)) -> dict:
    result = service.login(payload.username, payload.password)
    if not result:
        raise AuthenticationError("用户名或密码错误")
    user, token = result
    return {"user": user, "token": token}


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)) -> dict:
    return {"user": current_user}


@router.post("/logout")
def logout(
    authorization: str | None = Header(default=None),
    service: AuthService = Depends(get_auth_service),
) -> dict:
    service.logout(extract_token(authorization))
    return {"ok": True}


@router.get("/demo-accounts")
def demo_accounts(service: AuthService = Depends(get_auth_service)) -> list[dict]:
    return service.demo_accounts()


@router.get("/favorites")
def favorites(current_user: dict = Depends(get_current_user)) -> dict:
    return {
        "favorite_destination_ids": current_user.get("favorite_destination_ids", []),
        "favorite_route_snapshots": current_user.get("favorite_route_snapshots", []),
    }


@router.post("/favorites/destinations")
def toggle_destination_favorite(
    payload: FavoriteDestinationRequest,
    authorization: str | None = Header(default=None),
    service: AuthService = Depends(get_auth_service),
) -> dict:
    token = extract_token(authorization)
    if not token:
        raise AuthenticationError("请先登录")
    return service.toggle_destination_favorite(token, payload.source_id)


@router.post("/favorites/routes")
def save_route_favorite(
    payload: FavoriteRouteRequest,
    authorization: str | None = Header(default=None),
    service: AuthService = Depends(get_auth_service),
) -> dict:
    token = extract_token(authorization)
    if not token:
        raise AuthenticationError("请先登录")
    return {"user": service.save_route_favorite(token, payload.model_dump())}

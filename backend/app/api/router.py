from fastapi import APIRouter

from app.api.routes import ai, auth, destinations, diaries, facilities, foods, indoor, map_data, plans, routes, stats

api_router = APIRouter()
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(destinations.router, prefix="/destinations", tags=["destinations"])
api_router.include_router(routes.router, prefix="/routes", tags=["routes"])
api_router.include_router(indoor.router, prefix="/indoor", tags=["indoor"])
api_router.include_router(map_data.router, prefix="/map", tags=["map"])
api_router.include_router(facilities.router, prefix="/facilities", tags=["facilities"])
api_router.include_router(foods.router, prefix="/foods", tags=["foods"])
api_router.include_router(diaries.router, prefix="/diaries", tags=["diaries"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])

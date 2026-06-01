from fastapi import FastAPI, HTTPException
from app.application.route_service import RouteService
from app.domain.models import RouteRequest, RouteResponse, GpsEvent, GpsEventResponse
from app.infrastructure.map_provider import MapProviderAdapter
from app.infrastructure.repository import InMemoryRouteRepository

app = FastAPI(
    title="LogiTrack API",
    version="1.0.0",
    description="Protótipo da arquitetura cloud native do LogiTrack",
)

service = RouteService(
    adapter=MapProviderAdapter(),
    repository=InMemoryRouteRepository(),
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "online", "service": "logitrack-api"}


@app.post("/routes/recalculate", response_model=RouteResponse)
def recalculate_route(request: RouteRequest) -> RouteResponse:
    return service.recalculate(request)


@app.get("/routes/{delivery_id}", response_model=RouteResponse)
def get_route(delivery_id: str) -> RouteResponse:
    route = service.get_route(delivery_id)
    if not route:
        raise HTTPException(status_code=404, detail="rota nao encontrada")
    return route


@app.post("/events/gps", response_model=GpsEventResponse)
def register_gps_event(event: GpsEvent) -> GpsEventResponse:
    return service.register_gps_event(event)


@app.get("/metrics")
def metrics() -> dict[str, int]:
    return service.metrics()

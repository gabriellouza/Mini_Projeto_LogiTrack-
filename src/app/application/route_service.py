from app.domain.models import RouteRequest, RouteResponse, GpsEvent, GpsEventResponse
from app.infrastructure.map_provider import MapProviderAdapter
from app.infrastructure.repository import InMemoryRouteRepository


class RouteService:
    def __init__(self, adapter: MapProviderAdapter, repository: InMemoryRouteRepository):
        self.adapter = adapter
        self.repository = repository

    def recalculate(self, request: RouteRequest) -> RouteResponse:
        route = self.adapter.calculate(request)
        return self.repository.save_route(route)

    def get_route(self, delivery_id: str) -> RouteResponse | None:
        return self.repository.get_route(delivery_id)

    def register_gps_event(self, event: GpsEvent) -> GpsEventResponse:
        self.repository.save_gps_event(event)
        return GpsEventResponse(
            delivery_id=event.delivery_id,
            vehicle_id=event.vehicle_id,
            status="evento gps recebido para processamento assincrono",
        )

    def metrics(self) -> dict[str, int]:
        return {
            "routes_calculated": self.repository.count_routes(),
            "gps_events_received": self.repository.count_gps_events(),
            "fallback_count": self.adapter.fallback_count,
        }

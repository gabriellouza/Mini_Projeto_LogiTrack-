from app.domain.models import RouteResponse, GpsEvent


class InMemoryRouteRepository:
    def __init__(self):
        self.routes: dict[str, RouteResponse] = {}
        self.gps_events: list[GpsEvent] = []

    def save_route(self, route: RouteResponse) -> RouteResponse:
        self.routes[route.delivery_id] = route
        return route

    def get_route(self, delivery_id: str) -> RouteResponse | None:
        return self.routes.get(delivery_id)

    def save_gps_event(self, event: GpsEvent) -> GpsEvent:
        self.gps_events.append(event)
        return event

    def count_routes(self) -> int:
        return len(self.routes)

    def count_gps_events(self) -> int:
        return len(self.gps_events)

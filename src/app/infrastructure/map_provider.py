from random import randint
from app.domain.models import RouteRequest, RouteResponse
from app.infrastructure.circuit_breaker import CircuitBreaker


class MapProviderAdapter:
    def __init__(self):
        self.breaker = CircuitBreaker()
        self.cache: dict[str, RouteResponse] = {}
        self.google_failures = 0
        self.fallback_count = 0

    def calculate(self, request: RouteRequest) -> RouteResponse:
        if not self.breaker.is_open():
            try:
                route = self._google_maps(request)
                self.breaker.record_success()
                self.cache[request.delivery_id] = route
                return route
            except RuntimeError:
                self.breaker.record_failure()

        route = self._open_street_map(request)
        self.cache[request.delivery_id] = route
        self.fallback_count += 1
        return route

    def _google_maps(self, request: RouteRequest) -> RouteResponse:
        if request.priority == "alta" and self.google_failures < 1:
            self.google_failures += 1
            raise RuntimeError("provedor primario indisponivel")

        return RouteResponse(
            delivery_id=request.delivery_id,
            provider_used="google-maps",
            fallback_used=False,
            estimated_minutes=randint(25, 45),
            status="rota recalculada",
        )

    def _open_street_map(self, request: RouteRequest) -> RouteResponse:
        cached = self.cache.get(request.delivery_id)
        if cached:
            return RouteResponse(
                delivery_id=request.delivery_id,
                provider_used="route-cache",
                fallback_used=True,
                estimated_minutes=cached.estimated_minutes,
                status="rota recuperada do cache em modo degradado",
            )

        return RouteResponse(
            delivery_id=request.delivery_id,
            provider_used="open-street-map",
            fallback_used=True,
            estimated_minutes=randint(30, 55),
            status="rota recalculada com fallback",
        )

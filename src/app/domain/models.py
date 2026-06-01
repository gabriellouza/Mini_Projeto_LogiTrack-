from enum import Enum
from pydantic import BaseModel, Field


class Priority(str, Enum):
    baixa = "baixa"
    media = "media"
    alta = "alta"


class RouteRequest(BaseModel):
    delivery_id: str = Field(min_length=3)
    origin: str = Field(min_length=2)
    destination: str = Field(min_length=2)
    priority: Priority = Priority.media


class RouteResponse(BaseModel):
    delivery_id: str
    provider_used: str
    fallback_used: bool
    estimated_minutes: int
    status: str


class GpsEvent(BaseModel):
    vehicle_id: str = Field(min_length=2)
    delivery_id: str = Field(min_length=3)
    latitude: float
    longitude: float


class GpsEventResponse(BaseModel):
    delivery_id: str
    vehicle_id: str
    status: str

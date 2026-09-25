from datetime import datetime

from pydantic import BaseModel

from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int = 1


class OrderCreate(BaseModel):
    restaurant_id: int
    items: list[OrderItemCreate]
    delivery_address: str
    delivery_lat: float | None = None
    delivery_lng: float | None = None
    special_instructions: str | None = None


class OrderItemOut(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    unit_price: float

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    driver_id: int | None
    status: OrderStatus
    total_amount: float
    delivery_address: str
    delivery_lat: float | None
    delivery_lng: float | None
    estimated_delivery_minutes: int | None
    special_instructions: str | None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemOut] = []

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class DriverLocationUpdate(BaseModel):
    latitude: float
    longitude: float

from pydantic import BaseModel


class MenuItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    category: str | None = None
    image_url: str | None = None
    prep_time_minutes: int = 15


class MenuItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    category: str | None = None
    image_url: str | None = None
    is_available: bool | None = None
    prep_time_minutes: int | None = None


class MenuItemOut(BaseModel):
    id: int
    restaurant_id: int
    name: str
    description: str | None
    price: float
    category: str | None
    image_url: str | None
    is_available: bool
    prep_time_minutes: int

    model_config = {"from_attributes": True}

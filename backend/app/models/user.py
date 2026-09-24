import enum
from datetime import datetime, timezone

from sqlalchemy import String, Enum, DateTime, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Role(str, enum.Enum):
    CUSTOMER = "customer"
    RESTAURANT = "restaurant"
    DRIVER = "driver"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role))
    phone: Mapped[str | None] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # driver-specific fields
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    is_available: Mapped[bool | None] = mapped_column(Boolean)

    # restaurant-specific
    address: Mapped[str | None] = mapped_column(String(500))
    cuisine_type: Mapped[str | None] = mapped_column(String(100))

    restaurant_orders = relationship("Order", back_populates="restaurant", foreign_keys="Order.restaurant_id")
    customer_orders = relationship("Order", back_populates="customer", foreign_keys="Order.customer_id")
    driver_orders = relationship("Order", back_populates="driver", foreign_keys="Order.driver_id")
    menu_items = relationship("MenuItem", back_populates="restaurant")

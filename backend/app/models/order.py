import enum
from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, ForeignKey, Integer, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OrderStatus(str, enum.Enum):
    PLACED = "placed"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    PICKED_UP = "picked_up"
    ON_THE_WAY = "on_the_way"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    driver_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)

    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PLACED)
    total_amount: Mapped[float] = mapped_column(Float)
    delivery_address: Mapped[str] = mapped_column(String(500))
    delivery_lat: Mapped[float | None] = mapped_column(Float)
    delivery_lng: Mapped[float | None] = mapped_column(Float)
    estimated_delivery_minutes: Mapped[int | None] = mapped_column(Integer)
    special_instructions: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    customer = relationship("User", back_populates="customer_orders", foreign_keys=[customer_id])
    restaurant = relationship("User", back_populates="restaurant_orders", foreign_keys=[restaurant_id])
    driver = relationship("User", back_populates="driver_orders", foreign_keys=[driver_id])
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[float] = mapped_column(Float)

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")

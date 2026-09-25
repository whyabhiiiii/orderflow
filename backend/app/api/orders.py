from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.core.redis import redis_client
from app.models.user import User, Role
from app.models.menu import MenuItem
from app.models.order import Order, OrderItem, OrderStatus
from app.schemas.order import OrderCreate, OrderOut, OrderStatusUpdate, DriverLocationUpdate

router = APIRouter(prefix="/orders", tags=["orders"])


VALID_TRANSITIONS = {
    OrderStatus.PLACED: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.PREPARING, OrderStatus.CANCELLED},
    OrderStatus.PREPARING: {OrderStatus.READY, OrderStatus.CANCELLED},
    OrderStatus.READY: {OrderStatus.PICKED_UP},
    OrderStatus.PICKED_UP: {OrderStatus.ON_THE_WAY},
    OrderStatus.ON_THE_WAY: {OrderStatus.DELIVERED},
}


@router.post("", response_model=OrderOut, status_code=201)
async def place_order(
    body: OrderCreate,
    user: User = Depends(require_role(Role.CUSTOMER)),
    db: AsyncSession = Depends(get_db),
):
    menu_ids = [item.menu_item_id for item in body.items]
    result = await db.execute(
        select(MenuItem).where(
            MenuItem.id.in_(menu_ids),
            MenuItem.restaurant_id == body.restaurant_id,
            MenuItem.is_available == True,
        )
    )
    menu_items = {mi.id: mi for mi in result.scalars().all()}

    if len(menu_items) != len(menu_ids):
        missing = set(menu_ids) - set(menu_items.keys())
        raise HTTPException(400, f"Menu items not found or unavailable: {missing}")

    total = sum(menu_items[i.menu_item_id].price * i.quantity for i in body.items)

    order = Order(
        customer_id=user.id,
        restaurant_id=body.restaurant_id,
        total_amount=round(total, 2),
        delivery_address=body.delivery_address,
        delivery_lat=body.delivery_lat,
        delivery_lng=body.delivery_lng,
        special_instructions=body.special_instructions,
    )
    db.add(order)
    await db.flush()

    for item in body.items:
        db.add(OrderItem(
            order_id=order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            unit_price=menu_items[item.menu_item_id].price,
        ))

    await db.commit()

    result = await db.execute(
        select(Order).options(selectinload(Order.items)).where(Order.id == order.id)
    )
    order = result.scalar_one()

    await redis_client.publish("order_updates", f"{order.id}:{order.status.value}")
    return order


@router.get("", response_model=list[OrderOut])
async def list_orders(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
    status: OrderStatus | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Order).options(selectinload(Order.items))

    if user.role == Role.CUSTOMER:
        query = query.where(Order.customer_id == user.id)
    elif user.role == Role.RESTAURANT:
        query = query.where(Order.restaurant_id == user.id)
    elif user.role == Role.DRIVER:
        query = query.where(Order.driver_id == user.id)

    if status:
        query = query.where(Order.status == status)

    query = query.order_by(Order.created_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/available", response_model=list[OrderOut])
async def available_orders(
    user: User = Depends(require_role(Role.DRIVER)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.status == OrderStatus.READY, Order.driver_id == None)
        .order_by(Order.created_at.asc())
    )
    return result.scalars().all()


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "Order not found")

    owns_it = (
        order.customer_id == user.id
        or order.restaurant_id == user.id
        or order.driver_id == user.id
    )
    if not owns_it:
        raise HTTPException(403, "Not your order")

    return order


@router.patch("/{order_id}/status", response_model=OrderOut)
async def update_order_status(
    order_id: int,
    body: OrderStatusUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "Order not found")

    allowed = VALID_TRANSITIONS.get(order.status, set())
    if body.status not in allowed:
        raise HTTPException(400, f"Can't go from {order.status.value} to {body.status.value}")

    if user.role == Role.RESTAURANT and order.restaurant_id != user.id:
        raise HTTPException(403, "Not your restaurant's order")
    if user.role == Role.DRIVER and order.driver_id != user.id:
        raise HTTPException(403, "Not your delivery")

    order.status = body.status
    await db.commit()
    await db.refresh(order)

    await redis_client.publish("order_updates", f"{order.id}:{order.status.value}")
    return order


@router.post("/{order_id}/assign", response_model=OrderOut)
async def assign_driver(
    order_id: int,
    user: User = Depends(require_role(Role.DRIVER)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "Order not found")

    if order.driver_id:
        raise HTTPException(409, "Order already has a driver")
    if order.status != OrderStatus.READY:
        raise HTTPException(400, "Order isn't ready for pickup yet")

    order.driver_id = user.id
    order.status = OrderStatus.PICKED_UP
    await db.commit()
    await db.refresh(order)

    await redis_client.publish("order_updates", f"{order.id}:{order.status.value}")
    return order


@router.post("/driver/location")
async def update_driver_location(
    body: DriverLocationUpdate,
    user: User = Depends(require_role(Role.DRIVER)),
    db: AsyncSession = Depends(get_db),
):
    user.latitude = body.latitude
    user.longitude = body.longitude
    await db.commit()

    await redis_client.publish("driver_locations", f"{user.id}:{body.latitude}:{body.longitude}")
    return {"status": "location updated"}

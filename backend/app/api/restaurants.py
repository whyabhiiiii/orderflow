from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.user import User, Role
from app.models.menu import MenuItem
from app.schemas.menu import MenuItemCreate, MenuItemUpdate, MenuItemOut
from app.schemas.user import UserOut

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.get("", response_model=list[UserOut])
async def list_restaurants(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * size
    result = await db.execute(
        select(User)
        .where(User.role == Role.RESTAURANT, User.is_active == True)
        .offset(offset)
        .limit(size)
    )
    return result.scalars().all()


@router.get("/{restaurant_id}", response_model=UserOut)
async def get_restaurant(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.id == restaurant_id, User.role == Role.RESTAURANT)
    )
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(404, "Restaurant not found")
    return restaurant


@router.get("/{restaurant_id}/menu", response_model=list[MenuItemOut])
async def get_menu(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MenuItem).where(MenuItem.restaurant_id == restaurant_id, MenuItem.is_available == True)
    )
    return result.scalars().all()


@router.post("/menu", response_model=MenuItemOut, status_code=201)
async def add_menu_item(
    body: MenuItemCreate,
    user: User = Depends(require_role(Role.RESTAURANT)),
    db: AsyncSession = Depends(get_db),
):
    item = MenuItem(restaurant_id=user.id, **body.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.patch("/menu/{item_id}", response_model=MenuItemOut)
async def update_menu_item(
    item_id: int,
    body: MenuItemUpdate,
    user: User = Depends(require_role(Role.RESTAURANT)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MenuItem).where(MenuItem.id == item_id, MenuItem.restaurant_id == user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Menu item not found")

    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(item, field, value)

    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/menu/{item_id}", status_code=204)
async def delete_menu_item(
    item_id: int,
    user: User = Depends(require_role(Role.RESTAURANT)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MenuItem).where(MenuItem.id == item_id, MenuItem.restaurant_id == user.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Menu item not found")

    await db.delete(item)
    await db.commit()

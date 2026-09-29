"""
Seed script — run with: docker compose exec backend python -m scripts.seed
Creates demo accounts and menu items so you can test immediately.
"""
import asyncio

from sqlalchemy import select
from app.core.database import engine, async_session, Base
from app.core.security import hash_password
from app.models.user import User, Role
from app.models.menu import MenuItem
from app.models.order import Order, OrderItem


DEMO_PASSWORD = "password123"

RESTAURANTS = [
    {"name": "Tandoori Nights", "cuisine_type": "Indian", "address": "42 Spice Lane, Mumbai"},
    {"name": "Pizza Planet", "cuisine_type": "Italian", "address": "7 Margherita Blvd, Rome"},
    {"name": "Dragon Bowl", "cuisine_type": "Chinese", "address": "88 Noodle Street, Beijing"},
]

MENUS = {
    "Tandoori Nights": [
        {"name": "Butter Chicken", "price": 14.99, "category": "Mains", "description": "Creamy tomato-based curry with tender chicken"},
        {"name": "Garlic Naan", "price": 3.49, "category": "Breads", "description": "Freshly baked with garlic butter"},
        {"name": "Paneer Tikka", "price": 11.99, "category": "Starters", "description": "Grilled cottage cheese with spices"},
        {"name": "Mango Lassi", "price": 4.99, "category": "Drinks", "description": "Sweet yogurt drink with mango"},
        {"name": "Biryani", "price": 13.99, "category": "Mains", "description": "Fragrant basmati rice with spiced meat"},
    ],
    "Pizza Planet": [
        {"name": "Margherita", "price": 12.99, "category": "Pizzas", "description": "Fresh mozzarella, tomato, basil"},
        {"name": "Pepperoni", "price": 14.99, "category": "Pizzas", "description": "Classic pepperoni with cheese"},
        {"name": "Garlic Breadsticks", "price": 5.99, "category": "Sides", "description": "Crispy with garlic butter dip"},
        {"name": "Caesar Salad", "price": 8.99, "category": "Salads", "description": "Romaine, parmesan, croutons"},
    ],
    "Dragon Bowl": [
        {"name": "Kung Pao Chicken", "price": 13.49, "category": "Mains", "description": "Spicy stir-fry with peanuts"},
        {"name": "Fried Rice", "price": 9.99, "category": "Rice", "description": "Wok-fried with egg and vegetables"},
        {"name": "Spring Rolls", "price": 6.99, "category": "Starters", "description": "Crispy vegetable rolls"},
        {"name": "Hot & Sour Soup", "price": 7.49, "category": "Soups", "description": "Spicy and tangy broth"},
    ],
}


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        existing = await db.execute(select(User).where(User.email == "customer@demo.com"))
        if existing.scalar_one_or_none():
            print("Database already seeded. Skipping.")
            return

        # Customer
        customer = User(
            email="customer@demo.com", name="Alex Customer", role=Role.CUSTOMER,
            hashed_password=hash_password(DEMO_PASSWORD), phone="+1234567890",
        )
        db.add(customer)

        # Driver
        driver = User(
            email="driver@demo.com", name="Sam Driver", role=Role.DRIVER,
            hashed_password=hash_password(DEMO_PASSWORD), phone="+0987654321",
            is_available=True, latitude=19.076, longitude=72.877,
        )
        db.add(driver)

        # Restaurants and their menus
        for r_data in RESTAURANTS:
            restaurant = User(
                email=f"{r_data['name'].lower().replace(' ', '')}@demo.com",
                name=r_data["name"],
                role=Role.RESTAURANT,
                hashed_password=hash_password(DEMO_PASSWORD),
                address=r_data["address"],
                cuisine_type=r_data["cuisine_type"],
            )
            db.add(restaurant)
            await db.flush()

            for item_data in MENUS.get(r_data["name"], []):
                db.add(MenuItem(restaurant_id=restaurant.id, **item_data))

        await db.commit()

    print("Seeded successfully!")
    print(f"  Customer: customer@demo.com / {DEMO_PASSWORD}")
    print(f"  Driver:   driver@demo.com / {DEMO_PASSWORD}")
    for r in RESTAURANTS:
        email = f"{r['name'].lower().replace(' ', '')}@demo.com"
        print(f"  Restaurant ({r['name']}): {email} / {DEMO_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(seed())

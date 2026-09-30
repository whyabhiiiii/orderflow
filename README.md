# OrderFlow

Real-time order tracking system for restaurants, delivery drivers, and customers.

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy (async), PostgreSQL, Redis
- **Frontend:** React 18, React Router, Vite
- **Background Jobs:** Celery + Redis
- **Real-time:** WebSockets with Redis Pub/Sub
- **Infra:** Docker Compose

## Quick Start

```bash
# Clone and start everything
cd orderflow
docker compose up --build
```

That's it. The app will be running at:

| Service   | URL                      |
|-----------|--------------------------|
| Frontend  | http://localhost:5173     |
| API       | http://localhost:8000     |
| API Docs  | http://localhost:8000/docs|
| PostgreSQL| localhost:5432            |
| Redis     | localhost:6379            |

## How It Works

### Three Roles

1. **Customer** — Browse restaurants, order food, track delivery in real-time
2. **Restaurant** — Manage menu, accept/prepare orders, mark them ready
3. **Driver** — See available orders, pick up, deliver, share live location

### Order Flow

```
Customer places order
    → Restaurant confirms
        → Restaurant prepares
            → Restaurant marks ready
                → Driver picks up
                    → Driver on the way (live tracking)
                        → Delivered
```

### Real-Time Updates

Orders connect via WebSocket at `ws://localhost:8000/ws/orders/{order_id}`. Status changes and driver location updates are pushed through Redis Pub/Sub to all connected clients.

## API Endpoints

### Auth
- `POST /api/auth/register` — Create account (customer, restaurant, or driver)
- `POST /api/auth/login` — Get JWT token
- `GET /api/auth/me` — Current user profile

### Restaurants
- `GET /api/restaurants` — List restaurants (paginated)
- `GET /api/restaurants/{id}` — Restaurant details
- `GET /api/restaurants/{id}/menu` — Restaurant menu
- `POST /api/restaurants/menu` — Add menu item (restaurant only)
- `PATCH /api/restaurants/menu/{id}` — Update menu item
- `DELETE /api/restaurants/menu/{id}` — Remove menu item

### Orders
- `POST /api/orders` — Place order (customer only)
- `GET /api/orders` — List your orders (filtered by role)
- `GET /api/orders/{id}` — Order details
- `PATCH /api/orders/{id}/status` — Update order status
- `POST /api/orders/{id}/assign` — Driver picks up order
- `POST /api/orders/driver/location` — Update driver GPS

### WebSocket
- `ws://localhost:8000/ws/orders/{order_id}` — Real-time order tracking

## Seed Demo Data

```bash
docker compose exec backend python -m scripts.seed
```

## Production Deployment

1. Change `SECRET_KEY` in your environment
2. Set `DATABASE_URL` to your production PostgreSQL
3. Remove `--reload` from the backend CMD
4. Build the frontend: `npm run build` and serve with nginx
5. Add SSL termination (nginx/Caddy)

## Project Structure

```
orderflow/
├── backend/
│   ├── app/
│   │   ├── api/          # Route handlers
│   │   ├── core/         # Config, DB, auth, Redis
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── websockets/   # WebSocket manager
│   ├── workers/          # Celery tasks
│   └── migrations/       # Alembic
├── frontend/
│   └── src/
│       ├── components/   # Reusable UI
│       ├── contexts/     # Auth state
│       ├── hooks/        # WebSocket hook
│       ├── pages/        # Role dashboards
│       └── services/     # API client
└── docker-compose.yml
```

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.database import engine, Base
from app.api import auth, restaurants, orders
from app.websockets.tracker import websocket_endpoint, listen_for_updates

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    task = asyncio.create_task(listen_for_updates())
    yield
    task.cancel()


app = FastAPI(
    title="OrderFlow",
    description="Real-time order tracking for restaurants, drivers, and customers",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(restaurants.router, prefix="/api")
app.include_router(orders.router, prefix="/api")

app.add_api_websocket_route("/ws/orders/{order_id}", websocket_endpoint)


@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "orderflow"}

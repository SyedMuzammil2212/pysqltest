from contextlib import asynccontextmanager
from fastapi import FastAPI

from main.database import create_tables
from main.routers import auth
from main.routers import users
from main.routers import addresses 
from main.routers import categories
from main.routers import products
from main.routers import cart
from main.routers import orders
from main.routers import bills

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="E-commerce API",
    lifespan=lifespan
)


app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(addresses.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(products.category_products_router, prefix="/api/v1")
#GET /api/v1/products?search=phone&category_id=1&page=1&page_size=10&sort_order=asc
app.include_router(cart.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(bills.router, prefix="/api/v1")
app.include_router(bills.order_bills_router, prefix="/api/v1")
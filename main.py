from fastapi import FastAPI
from api.v1.endpoints import auth, users, address, categories, cart, orders, bills, products

app = FastAPI()

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(address.router, prefix="/api/v1/address", tags=["Addresses"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])
app.include_router(cart.router, prefix="/api/v1/cart", tags=["Carts"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(bills.router, prefix="/api/v1/bills", tags=["Bills"])
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])

@app.get("/")
def home():
    return {"message" : "FastAPI is running..."}
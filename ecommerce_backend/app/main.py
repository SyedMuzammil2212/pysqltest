from fastapi import FastAPI

from app.routers import auth, users ,address , categories , products ,orders,bills,cart


app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
# app.include_router(address.router)
app.include_router(address.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(bills.router)
@app.get("/")
def home():
    return {"message": "Ecommerce API is running"}
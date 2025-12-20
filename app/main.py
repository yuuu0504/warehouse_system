from fastapi import FastAPI
from app.api import products

app = FastAPI(title="物流倉儲管理系統 API", version="1.0.0")

app.include_router(products.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "WMS API is running", "auth_hint": "admin/admin"}
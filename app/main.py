from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api import products, requisitions, staffs, suppliers, inboundorders, warehouse

from contextlib import asynccontextmanager
from app.models import Staff
from app.core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時建立資料庫 Tables (SQLModel)
    await init_db()
    yield

app = FastAPI(title="物流倉儲管理系統 API", version="1.0.0", lifespan=lifespan)

app.include_router(products.router, prefix="/api/v1")
app.include_router(suppliers.router, prefix="/api/v1")
app.include_router(staffs.router, prefix="/api/v1")
app.include_router(inboundorders.router, prefix="/api/v1")
app.include_router(warehouse.router, prefix="/api/v1")
app.include_router(requisitions.router, prefix="/api/v1")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/view/{page_name}")
async def render_template(request: Request, page_name: str):
    return templates.TemplateResponse(f"{page_name}", {"request": request})

@app.get("/")
async def root():
    return {"message": "WMS API is running", "auth_hint": "admin/admin"}
from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

class SupplierSchema(BaseModel):
    SupplierID: int
    suName: str
    suPhone: str
    suAddress: str

@router.get("/", response_model=List[SupplierSchema])
async def get_suppliers(
    q: Optional[str] = Query(None, description="搜尋名稱或編號")
):
    # 這裡實作 search bar 的邏輯
    fake_suppliers = [
        {"SupplierID": 1, "suName": "A公司", "suPhone": "02-2345-6789", "suAddress": "台北市..."},
        {"SupplierID": 2, "suName": "B公司", "suPhone": "04-8765-4321", "suAddress": "台中市..."}
    ]
    if q:
        return [s for s in fake_suppliers if q.lower() in s["suName"].lower()]
    return fake_suppliers
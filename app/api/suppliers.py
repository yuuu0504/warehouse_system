from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from app.schemas.supplier import Supplier, SupplierCreate

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

# 模擬資料庫
fake_db_suppliers = [
    {"SupplierID": 1, "suName": "A公司", "suPhone": "02-2345-6789", "suAddress": "台北市信義區..."},
    {"SupplierID": 2, "suName": "B公司", "suPhone": "04-8765-4321", "suAddress": "台中市西屯區..."},
]

@router.get("/", response_model=List[Supplier])
async def get_suppliers(
    q: Optional[str] = Query(None, description="搜尋供應商名稱"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100)
):
    data = fake_db_suppliers
    if q:
        data = [s for s in data if q.lower() in s["suName"].lower()]
    return data[skip : skip + limit]

@router.get("/{supplier_id}", response_model=Supplier)
async def get_supplier(supplier_id: int):
    supplier = next((s for s in fake_db_suppliers if s["SupplierID"] == supplier_id), None)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.post("/", response_model=Supplier, status_code=status.HTTP_201_CREATED)
async def create_supplier(supplier: SupplierCreate):
    new_id = max([s["SupplierID"] for s in fake_db_suppliers]) + 1 if fake_db_suppliers else 1
    new_supplier = {"SupplierID": new_id, **supplier.model_dump()}
    fake_db_suppliers.append(new_supplier)
    return new_supplier

@router.put("/{supplier_id}", response_model=Supplier)
async def update_supplier(supplier_id: int, updated_supplier: SupplierCreate):
    index = next((i for i, s in enumerate(fake_db_suppliers) if s["SupplierID"] == supplier_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    fake_db_suppliers[index].update(updated_supplier.model_dump())
    return fake_db_suppliers[index]

@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(supplier_id: int):
    global fake_db_suppliers
    fake_db_suppliers = [s for s in fake_db_suppliers if s["SupplierID"] != supplier_id]
    return None
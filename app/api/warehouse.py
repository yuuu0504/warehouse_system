from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from app.schemas.warehouse import Warehouse, WarehouseCreate

router = APIRouter(prefix="/warehouse", tags=["Warehouse"])

# --- 模擬資料庫 ---
# 配合 inboundorders.py 中的假資料，預設 ID 為 101, 102, 103
fake_db_warehouses = [
    {"WarehouseID": 101, "waName": "一號倉", "waLocation": "台北總部 B1"},
    {"WarehouseID": 102, "waName": "二號倉", "waLocation": "台中物流中心"},
    {"WarehouseID": 103, "waName": "冷凍倉", "waLocation": "桃園觀音"},
]

@router.get("/", response_model=List[Warehouse])
async def get_warehouses(
    q: Optional[str] = Query(None, description="搜尋倉庫名稱或地點"),
    skip: int = Query(0, ge=0, description="跳過前 N 筆"),
    limit: int = Query(10, le=100, description="限制回傳 N 筆")
):
    results = fake_db_warehouses
    
    # 搜尋邏輯
    if q:
        q_lower = q.lower()
        results = [
            w for w in results 
            if q_lower in w["waName"].lower() or (w["waLocation"] and q_lower in w["waLocation"].lower())
        ]
    
    # 分頁切片
    return results[skip : skip + limit]

@router.get("/{warehouse_id}", response_model=Warehouse)
async def get_warehouse(warehouse_id: int):
    warehouse = next((w for w in fake_db_warehouses if w["WarehouseID"] == warehouse_id), None)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse

@router.post("/", response_model=Warehouse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(warehouse: WarehouseCreate):
    # 自動生成 ID
    new_id = max([w["WarehouseID"] for w in fake_db_warehouses]) + 1 if fake_db_warehouses else 101
    new_warehouse = {"WarehouseID": new_id, **warehouse.model_dump()}
    fake_db_warehouses.append(new_warehouse)
    return new_warehouse

@router.put("/{warehouse_id}", response_model=Warehouse)
async def update_warehouse(warehouse_id: int, updated_warehouse: WarehouseCreate):
    index = next((i for i, w in enumerate(fake_db_warehouses) if w["WarehouseID"] == warehouse_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    fake_db_warehouses[index].update(updated_warehouse.model_dump())
    fake_db_warehouses[index]["WarehouseID"] = warehouse_id # 確保 ID 不變
    return fake_db_warehouses[index]

@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse(warehouse_id: int):
    global fake_db_warehouses
    initial_len = len(fake_db_warehouses)
    fake_db_warehouses = [w for w in fake_db_warehouses if w["WarehouseID"] != warehouse_id]
    
    if len(fake_db_warehouses) == initial_len:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return None
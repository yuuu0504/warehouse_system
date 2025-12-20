from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from datetime import date
from app.schemas.inboundorder import InboundOrder, InboundOrderCreate

router = APIRouter(prefix="/inbound", tags=["Inbound Orders"])

# --- 假資料生成區 ---

# 1. 進貨主單 (參考 inboundorder.html)
fake_db_inbound = [
    {"InboundID": 2023120101, "ioDate": date(2023, 12, 1), "SupplierID": 1, "StaffID": 2}, # A公司
    {"InboundID": 2023120502, "ioDate": date(2023, 12, 5), "SupplierID": 2, "StaffID": 2}, # B公司
    {"InboundID": 2023121005, "ioDate": date(2023, 12, 10), "SupplierID": 3, "StaffID": 3}, # C公司
    {"InboundID": 2023112803, "ioDate": date(2023, 11, 28), "SupplierID": 1, "StaffID": 2}, # A公司
]

# 2. 進貨明細 (假設 ProductID: 1=耳機, 2=鍵盤; WarehouseID: 101=一號倉)
fake_db_inbound_details = [
    # 單號 2023120101 的明細
    {"InboundID": 2023120101, "ProductID": 1, "idQuantity": 50, "WarehouseID": 101},
    {"InboundID": 2023120101, "ProductID": 2, "idQuantity": 20, "WarehouseID": 101},
    
    # 單號 2023120502 的明細
    {"InboundID": 2023120502, "ProductID": 2, "idQuantity": 100, "WarehouseID": 102},
    
    # 單號 2023121005 的明細
    {"InboundID": 2023121005, "ProductID": 1, "idQuantity": 10, "WarehouseID": 101},
    
    # 單號 2023112803 的明細
    {"InboundID": 2023112803, "ProductID": 1, "idQuantity": 200, "WarehouseID": 103},
]

# --- API 實作 ---

@router.get("/", response_model=List[InboundOrder])
async def get_inbound_orders(
    io_date: Optional[date] = Query(None, description="篩選進貨日期"),
    q: Optional[str] = Query(None, description="搜尋單號或供應商ID"),
    skip: int = 0,
    limit: int = 10
):
    results = fake_db_inbound
    
    if io_date:
        results = [o for o in results if o["ioDate"] == io_date]
    if q:
        results = [o for o in results if q in str(o["InboundID"]) or q in str(o["SupplierID"])]
    
    # 組合明細回傳
    output_list = []
    # 分頁切片放在這裡比較準確，先切片再組裝明細，效能較好
    sliced_results = results[skip : skip + limit]
    
    for order in sliced_results:
        # 複製一份 order 以免汙染原始資料
        order_with_details = order.copy()
        order_with_details["details"] = [d for d in fake_db_inbound_details if d["InboundID"] == order["InboundID"]]
        output_list.append(order_with_details)
        
    return output_list

@router.get("/{inbound_id}", response_model=InboundOrder)
async def get_inbound_order(inbound_id: int):
    order = next((o for o in fake_db_inbound if o["InboundID"] == inbound_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order_with_details = order.copy()
    order_with_details["details"] = [d for d in fake_db_inbound_details if d["InboundID"] == inbound_id]
    return order_with_details

@router.post("/", response_model=InboundOrder, status_code=status.HTTP_201_CREATED)
async def create_inbound_order(order_data: InboundOrderCreate):
    # 自動生成 ID：取當前最大 ID + 1，或使用當前日期格式 (這裡簡化處理)
    new_inbound_id = max([o["InboundID"] for o in fake_db_inbound]) + 1 if fake_db_inbound else 20230001
    
    new_order = {
        "InboundID": new_inbound_id,
        "ioDate": order_data.ioDate,
        "SupplierID": order_data.SupplierID,
        "StaffID": order_data.StaffID
    }
    
    fake_db_inbound.append(new_order)

    current_details = []
    for d in order_data.details:
        detail = {
            "InboundID": new_inbound_id,
            "ProductID": d.ProductID,
            "idQuantity": d.idQuantity,
            "WarehouseID": d.WarehouseID
        }
        fake_db_inbound_details.append(detail)
        current_details.append(detail)
    
    new_order["details"] = current_details
    return new_order

@router.put("/{inbound_id}", response_model=InboundOrder)
async def update_inbound_order(inbound_id: int, order_data: InboundOrderCreate):
    # 1. 找主單
    index = next((i for i, o in enumerate(fake_db_inbound) if o["InboundID"] == inbound_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 2. 更新主單
    fake_db_inbound[index].update({
        "ioDate": order_data.ioDate,
        "SupplierID": order_data.SupplierID,
        "StaffID": order_data.StaffID
    })
    
    # 3. 更新明細 (策略：先刪除該單號所有舊明細，再寫入新明細)
    global fake_db_inbound_details
    # 移除舊明細
    fake_db_inbound_details = [d for d in fake_db_inbound_details if d["InboundID"] != inbound_id]
    
    # 加入新明細
    new_details = []
    for d in order_data.details:
        detail = {
            "InboundID": inbound_id,
            "ProductID": d.ProductID,
            "idQuantity": d.idQuantity,
            "WarehouseID": d.WarehouseID
        }
        fake_db_inbound_details.append(detail)
        new_details.append(detail)
        
    result = fake_db_inbound[index].copy()
    result["details"] = new_details
    return result

@router.delete("/{inbound_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inbound_order(inbound_id: int):
    global fake_db_inbound, fake_db_inbound_details
    
    # 檢查是否存在
    exists = any(o["InboundID"] == inbound_id for o in fake_db_inbound)
    if not exists:
        raise HTTPException(status_code=404, detail="Order not found")

    # 1. 刪除主單
    fake_db_inbound = [o for o in fake_db_inbound if o["InboundID"] != inbound_id]
    
    # 2. 刪除關聯明細 (Cascade Delete)
    fake_db_inbound_details = [d for d in fake_db_inbound_details if d["InboundID"] != inbound_id]
    
    return None
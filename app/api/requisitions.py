from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from datetime import date
from app.schemas.requisition import Requisition, RequisitionCreate

router = APIRouter(prefix="/requisitions", tags=["Requisitions"])

# --- 假資料生成區 ---

# 1. 領料主單 (模擬資料)
fake_db_requisitions = [
    {"ReqID": 2023120201, "reDate": date(2023, 12, 2), "reReason": "產線領料", "StaffID": 2},
    {"ReqID": 2023120602, "reDate": date(2023, 12, 6), "reReason": "樣品測試", "StaffID": 3},
    {"ReqID": 2023121103, "reDate": date(2023, 12, 11), "reReason": "庫存報廢", "StaffID": 1},
]

# 2. 領料明細
fake_db_req_details = [
    # 單號 2023120201 (產線領料)
    {"ReqID": 2023120201, "ProductID": 1, "rdQuantity": 10, "WarehouseID": 101},
    {"ReqID": 2023120201, "ProductID": 2, "rdQuantity": 5, "WarehouseID": 101},
    
    # 單號 2023120602 (樣品測試)
    {"ReqID": 2023120602, "ProductID": 2, "rdQuantity": 2, "WarehouseID": 102},
    
    # 單號 2023121103 (庫存報廢)
    {"ReqID": 2023121103, "ProductID": 1, "rdQuantity": 50, "WarehouseID": 103},
]

# --- API 實作 ---

@router.get("/", response_model=List[Requisition])
async def get_requisitions(
    re_date: Optional[date] = Query(None, description="篩選領料日期"),
    q: Optional[str] = Query(None, description="搜尋單號或領料原因"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100)
):
    results = fake_db_requisitions
    
    # 篩選邏輯
    if re_date:
        results = [r for r in results if r["reDate"] == re_date]
    if q:
        q_str = str(q).lower()
        results = [r for r in results if q_str in str(r["ReqID"]) or q_str in r["reReason"].lower()]
    
    # 分頁切片
    sliced_results = results[skip : skip + limit]
    
    # 組合明細
    output_list = []
    for req in sliced_results:
        req_with_details = req.copy()
        req_with_details["details"] = [d for d in fake_db_req_details if d["ReqID"] == req["ReqID"]]
        output_list.append(req_with_details)
        
    return output_list

@router.get("/{req_id}", response_model=Requisition)
async def get_requisition(req_id: int):
    req = next((r for r in fake_db_requisitions if r["ReqID"] == req_id), None)
    if not req:
        raise HTTPException(status_code=404, detail="Requisition not found")
    
    req_with_details = req.copy()
    req_with_details["details"] = [d for d in fake_db_req_details if d["ReqID"] == req_id]
    return req_with_details

@router.post("/", response_model=Requisition, status_code=status.HTTP_201_CREATED)
async def create_requisition(req_data: RequisitionCreate):
    # 自動生成 ID
    new_req_id = max([r["ReqID"] for r in fake_db_requisitions]) + 1 if fake_db_requisitions else 20230001
    
    new_req = {
        "ReqID": new_req_id,
        "reDate": req_data.reDate,
        "reReason": req_data.reReason,
        "StaffID": req_data.StaffID
    }
    fake_db_requisitions.append(new_req)

    current_details = []
    for d in req_data.details:
        detail = {
            "ReqID": new_req_id,
            "ProductID": d.ProductID,
            "rdQuantity": d.rdQuantity,
            "WarehouseID": d.WarehouseID
        }
        fake_db_req_details.append(detail)
        current_details.append(detail)
    
    new_req["details"] = current_details
    return new_req

@router.put("/{req_id}", response_model=Requisition)
async def update_requisition(req_id: int, req_data: RequisitionCreate):
    # 1. 找主單
    index = next((i for i, r in enumerate(fake_db_requisitions) if r["ReqID"] == req_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Requisition not found")
    
    # 2. 更新主單
    fake_db_requisitions[index].update({
        "reDate": req_data.reDate,
        "reReason": req_data.reReason,
        "StaffID": req_data.StaffID
    })
    
    # 3. 更新明細 (先刪後加)
    global fake_db_req_details
    fake_db_req_details = [d for d in fake_db_req_details if d["ReqID"] != req_id]
    
    new_details = []
    for d in req_data.details:
        detail = {
            "ReqID": req_id,
            "ProductID": d.ProductID,
            "rdQuantity": d.rdQuantity,
            "WarehouseID": d.WarehouseID
        }
        fake_db_req_details.append(detail)
        new_details.append(detail)
        
    result = fake_db_requisitions[index].copy()
    result["details"] = new_details
    return result

@router.delete("/{req_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_requisition(req_id: int):
    global fake_db_requisitions, fake_db_req_details
    
    if not any(r["ReqID"] == req_id for r in fake_db_requisitions):
        raise HTTPException(status_code=404, detail="Requisition not found")

    # 1. 刪除主單
    fake_db_requisitions = [r for r in fake_db_requisitions if r["ReqID"] != req_id]
    
    # 2. 刪除關聯明細
    fake_db_req_details = [d for d in fake_db_req_details if d["ReqID"] != req_id]
    
    return None
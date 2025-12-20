from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from app.schemas.staff import Staff, StaffCreate

router = APIRouter(prefix="/staff", tags=["Staff"])

# 模擬資料庫：員工
fake_db_staff = [
    {"StaffID": 1, "stName": "Admin", "stDept": "管理部"},
    {"StaffID": 2, "stName": "張倉管", "stDept": "倉庫部"},
    {"StaffID": 3, "stName": "李採購", "stDept": "採購部"},
]

@router.get("/", response_model=List[Staff])
async def get_all_staff(
    q: Optional[str] = Query(None, description="搜尋員工姓名或部門"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100)
):
    results = fake_db_staff
    
    # 搜尋邏輯
    if q:
        q_lower = q.lower()
        results = [
            s for s in results 
            if q_lower in s["stName"].lower() or q_lower in s["stDept"].lower()
        ]

    return results[skip : skip + limit]

@router.get("/{staff_id}", response_model=Staff)
async def get_staff(staff_id: int):
    staff = next((s for s in fake_db_staff if s["StaffID"] == staff_id), None)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff

@router.post("/", response_model=Staff, status_code=status.HTTP_201_CREATED)
async def create_staff(staff: StaffCreate):
    new_id = max([s["StaffID"] for s in fake_db_staff]) + 1 if fake_db_staff else 1
    new_staff = {"StaffID": new_id, **staff.model_dump()}
    fake_db_staff.append(new_staff)
    return new_staff

# --- 新增 PUT (修改) ---
@router.put("/{staff_id}", response_model=Staff)
async def update_staff(staff_id: int, updated_staff: StaffCreate):
    index = next((i for i, s in enumerate(fake_db_staff) if s["StaffID"] == staff_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    # 更新欄位，保留 ID
    fake_db_staff[index].update(updated_staff.model_dump())
    fake_db_staff[index]["StaffID"] = staff_id # 確保 ID 不被覆蓋
    return fake_db_staff[index]

# --- 新增 DELETE (刪除) ---
@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff(staff_id: int):
    global fake_db_staff
    initial_len = len(fake_db_staff)
    fake_db_staff = [s for s in fake_db_staff if s["StaffID"] != staff_id]
    
    if len(fake_db_staff) == initial_len:
        raise HTTPException(status_code=404, detail="Staff not found")
    return None
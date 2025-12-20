from pydantic import BaseModel
from datetime import date
from typing import List

# --- 領料明細 (ReqDetail) ---
class ReqDetailBase(BaseModel):
    ProductID: int
    rdQuantity: int
    WarehouseID: int

class ReqDetail(ReqDetailBase):
    ReqID: int
    
    class Config:
        from_attributes = True

# --- 領料主單 (Requisition) ---
class RequisitionBase(BaseModel):
    reDate: date
    reReason: str
    StaffID: int

class RequisitionCreate(RequisitionBase):
    details: List[ReqDetailBase]  # 建立時傳入明細列表

class Requisition(RequisitionBase):
    ReqID: int
    details: List[ReqDetail] = []

    class Config:
        from_attributes = True
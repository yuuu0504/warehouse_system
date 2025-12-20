from pydantic import BaseModel
from datetime import date
from typing import List, Optional

# 進貨明細
class InboundDetailBase(BaseModel):
    ProductID: int
    idQuantity: int
    WarehouseID: int

class InboundDetail(InboundDetailBase):
    InboundID: int

# 進貨主單
class InboundOrderBase(BaseModel):
    ioDate: date
    SupplierID: int
    StaffID: int

class InboundOrderCreate(InboundOrderBase):
    details: List[InboundDetailBase]  # 建立單據時同時傳入多筆明細

class InboundOrder(InboundOrderBase):
    InboundID: int
    details: List[InboundDetail] = []

    class Config:
        from_attributes = True
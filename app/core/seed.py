from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.product import Product
from app.models.staff import Staff
from app.models.supplier import Supplier

# --- Seed Staff ---
INITIAL_STAFF = [
    {"StaffID": 1, "stName": "Admin", "stDept": "管理部"},
    {"StaffID": 2, "stName": "張倉管", "stDept": "倉庫部"},
    {"StaffID": 3, "stName": "李採購", "stDept": "採購部"},
]

# --- Seed Supplier ---
INITIAL_SUPPLIERS = [
    {"SupplierID": 1, "suName": "A公司", "suPhone": "02-2345-6789", "suAddress": "台北市信義區..."},
    {"SupplierID": 2, "suName": "B公司", "suPhone": "04-8765-4321", "suAddress": "台中市西屯區..."},
]

# --- Seed Product ---
INITIAL_PRODUCTS = [
    {"ProductID": 1, "prName": "無線耳機", "prSpec": "藍牙 5.0", "prCategory": "電子產品"},
    {"ProductID": 2, "prName": "機械鍵盤", "prSpec": "青軸", "prCategory": "電腦周邊"},
    {"ProductID": 3, "prName": "電競滑鼠", "prSpec": "DPI 16000", "prCategory": "電腦周邊"},
]

async def create_initial_data(db: AsyncSession):
    result = await db.exec(select(Staff))
    first_staff = result.first()
    
    if not first_staff:
        print("🌱 Seeding Staff data...")
        for data in INITIAL_STAFF:
            staff = Staff(
                StaffID=data["StaffID"], 
                stName=data["stName"], 
                stDept=data["stDept"]
            )
            db.add(staff)
        await db.commit()


    result = await db.exec(select(Supplier))
    if not result.first():
        print("🌱 Seeding Supplier data...")
        for data in INITIAL_SUPPLIERS:
            supplier = Supplier(**data) # 使用 unpacking 快速賦值
            db.add(supplier)
        await db.commit()
    
    result = await db.exec(select(Product))
    if not result.first():
        print("🌱 Seeding Product data...")
        for data in INITIAL_PRODUCTS:
            product = Product(**data)
            db.add(product)
        await db.commit()

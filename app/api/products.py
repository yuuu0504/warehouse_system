from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.product import Product, ProductCreate

router = APIRouter(prefix="/products", tags=["Products"])

fake_db_products = [
    {"ProductID": 1, "prName": "無線藍芽耳機", "prSpec": "V5.3", "prCategory": "電子產品"},
]

@router.get("/", response_model=List[Product])
async def get_all_products():
    return fake_db_products

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int):
    product = next((p for p in fake_db_products if p["ProductID"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate):
    new_id = max([p["ProductID"] for p in fake_db_products]) + 1 if fake_db_products else 1
    new_product = {"ProductID": new_id, **product.model_dump()}
    fake_db_products.append(new_product)
    return new_product

@router.put("/{product_id}", response_model=Product)
async def update_product(product_id: int, updated_product: ProductCreate):
    index = next((i for i, p in enumerate(fake_db_products) if p["ProductID"] == product_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Product not found")
    fake_db_products[index].update(updated_product.model_dump())
    return fake_db_products[index]

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int):
    global fake_db_products
    fake_db_products = [p for p in fake_db_products if p["ProductID"] != product_id]
    return None
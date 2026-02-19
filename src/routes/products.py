from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from src.db import get_session
from src.models import Product, ProductCreate, ProductUpdate
from src.services.redis_service import redis_service
import logging

router = APIRouter(prefix="/products", tags=["products"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, session: Session = Depends(get_session)):
    db_product = Product.model_validate(product)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product

@router.get("/{product_id}", response_model=Product)
def get_product(product_id: str, session: Session = Depends(get_session)):
    # 1. Check Cache
    cached_product = redis_service.get_product(product_id)
    if cached_product:
        return cached_product

    # 2. Check Database
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 3. Update Cache
    redis_service.set_product(db_product)
    
    return db_product

@router.put("/{product_id}", response_model=Product)
def update_product(product_id: str, product_update: ProductUpdate, session: Session = Depends(get_session)):
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    product_data = product_update.model_dump(exclude_unset=True)
    for key, value in product_data.items():
        setattr(db_product, key, value)

    session.add(db_product)
    session.commit()
    session.refresh(db_product)

    # Invalidate Cache
    redis_service.invalidate_product(product_id)

    return db_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str, session: Session = Depends(get_session)):
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    session.delete(db_product)
    session.commit()

    # Invalidate Cache
    redis_service.invalidate_product(product_id)

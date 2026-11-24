from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from main.database import get_db
from main.dependencies import get_current_user
from main.models import Product, Category, User
from main.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    StockUpdate
)

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

category_products_router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(
        Category.id == product_data.category_id
    ).first()

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    existing_product = db.query(Product).filter(
        Product.sku == product_data.sku
    ).first()

    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product SKU already exists"
        )

    new_product = Product(**product_data.model_dump())

    try:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return new_product

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product SKU already exists"
        )


@router.get("", response_model=list[ProductResponse])
def get_products(
    search: str | None = None,
    category_id: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort_order: Literal["asc", "desc"] = "asc",
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(
        Product.is_active.is_(True)
    )

    if search:
        query = query.filter(
            Product.name.ilike(f"%{search.strip()}%")
        )

    if category_id is not None:
        query = query.filter(
            Product.category_id == category_id
        )

    if sort_order == "asc":
        query = query.order_by(Product.price.asc())
    else:
        query = query.order_by(Product.price.desc())

    offset = (page - 1) * page_size

    products = query.offset(offset).limit(page_size).all()

    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active.is_(True)
    ).first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    updates = product_data.model_dump(exclude_unset=True)

    required_fields = ["category_id", "sku", "name", "price"]

    for field in required_fields:
        if field in updates and updates[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} cannot be null"
            )

    if "category_id" in updates:
        category = db.query(Category).filter(
            Category.id == updates["category_id"]
        ).first()

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

    if "sku" in updates:
        existing_product = db.query(Product).filter(
            Product.sku == updates["sku"],
            Product.id != product_id
        ).first()

        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product SKU already exists"
            )

    for field, value in updates.items():
        setattr(product, field, value)

    try:
        db.commit()
        db.refresh(product)

        return product

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product SKU already exists"
        )


@router.patch("/{product_id}/stock", response_model=ProductResponse)
def update_product_stock(
    product_id: int,
    stock_data: StockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    product.stock = stock_data.stock

    db.commit()
    db.refresh(product)

    return product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def deactivate_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product is already deactivated"
        )

    product.is_active = False

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@category_products_router.get(
    "/{category_id}/products",
    response_model=list[ProductResponse]
)
def get_category_products(
    category_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort_order: Literal["asc", "desc"] = "asc",
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    query = db.query(Product).filter(
        Product.category_id == category_id,
        Product.is_active.is_(True)
    )

    if sort_order == "asc":
        query = query.order_by(Product.price.asc())
    else:
        query = query.order_by(Product.price.desc())

    offset = (page - 1) * page_size

    return query.offset(offset).limit(page_size).all()

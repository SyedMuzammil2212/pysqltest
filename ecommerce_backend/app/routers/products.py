from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import asc, desc

from app.database import get_db
from app.models.product import Product
from app.models.category import Category
from app.models.user import User

from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductStockUpdate
)

from app.utils.dependencies import get_current_user
from app.models.product import Product
from app.schemas.product import ProductResponse

router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products"]
)


# 1. CREATE PRODUCT
@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Check whether category exists
    category = db.query(Category).filter(
        Category.id == product_data.category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    # Check whether SKU already exists
    existing_product = db.query(Product).filter(
        Product.sku == product_data.sku
    ).first()

    if existing_product:
        raise HTTPException(
            status_code=400,
            detail="Product SKU already exists"
        )

    new_product = Product(
        category_id=product_data.category_id,
        sku=product_data.sku,
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
        is_active=True
    )

    db.add(new_product)

    try:
        db.commit()
        db.refresh(new_product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Product SKU already exists"
        )

    return new_product


# 2. LIST PRODUCTS WITH SEARCH, FILTER, PAGINATION AND SORTING
@router.get("/", response_model=list[ProductResponse])
def get_products(
    search: str | None = None,
    category_id: int | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    sort_by: str = Query(default="price"),
    order: str = Query(default="asc"),
    db: Session = Depends(get_db)
):

    query = db.query(Product).filter(
        Product.is_active == True
    )

    # Search by product name
    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%")
        )

    # Filter by category
    if category_id is not None:
        query = query.filter(
            Product.category_id == category_id
        )

    # Sorting
    allowed_sort_fields = {
        "price": Product.price,
        "name": Product.name,
        "id": Product.id
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=400,
            detail="Invalid sorting field"
        )

    if order.lower() == "asc":
        query = query.order_by(
            asc(allowed_sort_fields[sort_by])
        )
    elif order.lower() == "desc":
        query = query.order_by(
            desc(allowed_sort_fields[sort_by])
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Order must be asc or desc"
        )

    # Pagination
    products = query.offset(skip).limit(limit).all()

    return products


# 3. GET SINGLE PRODUCT
@router.get("/{product_id}", response_model=ProductResponse)
def get_product_by_id(
    product_id: int,
    db: Session = Depends(get_db)
):

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


# 4. UPDATE PRODUCT
@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    update_data = product_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    # Validate category if category_id is being updated
    if "category_id" in update_data:
        category = db.query(Category).filter(
            Category.id == update_data["category_id"]
        ).first()

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

    # Validate SKU uniqueness
    if "sku" in update_data:
        existing_product = db.query(Product).filter(
            Product.sku == update_data["sku"],
            Product.id != product_id
        ).first()

        if existing_product:
            raise HTTPException(
                status_code=400,
                detail="Product SKU already exists"
            )

    for field, value in update_data.items():
        setattr(product, field, value)

    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Unable to update product due to a database constraint"
        )

    return product


# 5. DELETE PRODUCT
# DEACTIVATE PRODUCT
@router.delete("/{product_id}")
def deactivate_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    product.is_active = False

    db.commit()
    db.refresh(product)

    return {
        "message": "Product deactivated successfully"
    }

# UPDATE PRODUCT STOCK
@router.patch("/{product_id}/stock")
def update_product_stock(
    product_id: int,
    stock_data: ProductStockUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    product.stock = stock_data.stock

    db.commit()
    db.refresh(product)

    return {
        "message": "Product stock updated successfully",
        "product_id": product.id,
        "stock": product.stock
    }

# GET ACTIVE PRODUCTS BY CATEGORY
@router.get(
    "/{category_id}/products",
    response_model=list[ProductResponse]
)
def get_category_products(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    products = db.query(Product).filter(
        Product.category_id == category_id,
        Product.is_active == True
    ).all()

    return products
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from main.database import get_db
from main.dependencies import get_current_user
from main.models import Category, Product, User
from main.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_category = db.query(Category).filter(
        Category.name == category_data.name
    ).first()

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already exists"
        )

    new_category = Category(**category_data.model_dump())

    try:
        db.add(new_category)
        db.commit()
        db.refresh(new_category)

        return new_category

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category name already exists"
        )


@router.get("", response_model=list[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db)
):
    return db.query(Category).order_by(Category.id).all()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
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

    return category


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    updates = category_data.model_dump(exclude_unset=True)

    if "name" in updates and updates["name"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Category name cannot be null"
        )

    if "name" in updates:
        existing_category = db.query(Category).filter(
            Category.name == updates["name"],
            Category.id != category_id
        ).first()

        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category name already exists"
            )

    for field, value in updates.items():
        setattr(category, field, value)

    try:
        db.commit()
        db.refresh(category)

        return category

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category name already exists"
        )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )


    products_exist = db.query(Product.id).filter(
        Product.category_id == category_id
    ).first()

    if products_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a category that has products"
        )

    db.delete(category)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

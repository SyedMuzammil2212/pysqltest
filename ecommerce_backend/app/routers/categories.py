from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.models.product import Product
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse , CategoryUpdate
from app.utils.dependencies import get_current_user

router = APIRouter(
    prefix="/api/v1/categories",
    tags=["Categories"]
)


# Create category
@router.post("/", response_model=CategoryResponse,
             status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_category = db.query(Category).filter(
        Category.name == category_data.name
    ).first()

    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    new_category = Category(
        name=category_data.name,
        description=category_data.description
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category

@router.get("/", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):

    categories = db.query(Category).all()

    return categories

@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
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

    existing_products = db.query(Product).filter(
        Product.category_id == category_id
    ).first()

    if existing_products:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category because products are associated with it"
        )

    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully"}

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
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

    return category

@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_user),
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

    update_data = category_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    if "name" in update_data:
        if not update_data["name"].strip():
            raise HTTPException(
                status_code=400,
                detail="Category name cannot be empty"
            )

        existing_category = db.query(Category).filter(
            Category.name == update_data["name"],
            Category.id != category_id
        ).first()

        if existing_category:
            raise HTTPException(
                status_code=400,
                detail="Category name already exists"
            )

    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    return category
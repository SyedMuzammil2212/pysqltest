from decimal import Decimal

from main.database import SessionLocal
from main.models import Category, Product


def seed_data():
    db = SessionLocal()

    try:
        categories_data = [
            {
                "name": "Electronics",
                "description": "Electronic devices and accessories"
            },
            {
                "name": "Clothing",
                "description": "Clothes and fashion products"
            },
            {
                "name": "Books",
                "description": "Books and educational materials"
            }
        ]

        for category_data in categories_data:
            category = db.query(Category).filter(
                Category.name == category_data["name"]
            ).first()

            if category is None:
                category = Category(**category_data)
                db.add(category)

        db.flush()

        categories = {
            category.name: category.id
            for category in db.query(Category).all()
        }

        products_data = [
            {
                "sku": "ELEC001",
                "name": "Wireless Mouse",
                "description": "Wireless optical mouse",
                "price": Decimal("599.00"),
                "stock": 50,
                "category_id": categories["Electronics"]
            },
            {
                "sku": "ELEC002",
                "name": "USB Keyboard",
                "description": "USB wired keyboard",
                "price": Decimal("899.00"),
                "stock": 30,
                "category_id": categories["Electronics"]
            },
            {
                "sku": "ELEC003",
                "name": "Bluetooth Headphones",
                "description": "Wireless Bluetooth headphones",
                "price": Decimal("1499.00"),
                "stock": 25,
                "category_id": categories["Electronics"]
            },
            {
                "sku": "CLOTH001",
                "name": "Cotton T-Shirt",
                "description": "Regular fit cotton t-shirt",
                "price": Decimal("499.00"),
                "stock": 100,
                "category_id": categories["Clothing"]
            },
            {
                "sku": "CLOTH002",
                "name": "Denim Jeans",
                "description": "Classic blue denim jeans",
                "price": Decimal("1299.00"),
                "stock": 40,
                "category_id": categories["Clothing"]
            },
            {
                "sku": "BOOK001",
                "name": "Python Programming",
                "description": "Beginner-friendly Python programming book",
                "price": Decimal("650.00"),
                "stock": 20,
                "category_id": categories["Books"]
            }
        ]

        for product_data in products_data:
            product = db.query(Product).filter(
                Product.sku == product_data["sku"]
            ).first()

            if product is None:
                db.add(Product(**product_data))

        db.commit()
        print("Sample categories and products inserted successfully!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
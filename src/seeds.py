from sqlmodel import Session, select
from src.db import engine, create_db_and_tables
from src.models import Product

def seed_db():
    create_db_and_tables()
    with Session(engine) as session:
        existing = session.exec(select(Product)).first()
        if existing:
            print("Database already seeded.")
            return
        
        products = [
            Product(name="Smartphone", description="High-end smartphone with AMOLED display", price=999.99, stock_quantity=50),
            Product(name="Laptop", description="Powerful laptop for development", price=1499.99, stock_quantity=30),
            Product(name="Headphones", description="Noise-cancelling wireless headphones", price=299.99, stock_quantity=100),
            Product(name="Smartwatch", description="Fitness tracker with heart rate monitor", price=249.99, stock_quantity=75),
            Product(name="Tablet", description="10-inch tablet for media consumption", price=449.99, stock_quantity=40),
        ]
        
        session.add_all(products)
        session.commit()
        print("Database seeded with initial products.")

if __name__ == "__main__":
    seed_db()


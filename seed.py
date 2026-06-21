import time
import random
import uuid
from datetime import datetime, timedelta, timezone
from db import init_db, SessionLocal, Product

CATEGORIES = [
    "Electronics", "Clothing", "Home & Kitchen", 
    "Books", "Sports & Outdoors", "Beauty", 
    "Toys", "Automotive", "Garden", "Grocery"
]

ADJECTIVES = [
    "Premium", "Wireless", "Eco-Friendly", "Ergonomic", "Portable", 
    "Smart", "Ultra", "Classic", "Mini", "Professional", 
    "Sleek", "Durable", "Compact", "Luxury", "Modern"
]

NOUNS = [
    "Gadget", "Headphones", "Chair", "Speaker", "Backpack", 
    "Flask", "Keyboard", "Watch", "Light", "Camera", 
    "Tracker", "Charger", "Desk", "Lamp", "Bottle"
]

def seed_database():
    print("Initializing database schema...")
    init_db()
    
    db = SessionLocal()
    
    # Check if we already have data
    existing_count = db.query(Product).count()
    if existing_count >= 200000:
        print(f"Database already contains {existing_count} products. Skipping seeding.")
        db.close()
        return

    print("Generating 200,000 products...")
    start_time = time.time()
    
    total_products = 200000
    batch_size = 20000
    current_datetime = datetime.now(timezone.utc)
    
    # We will bulk insert in batches to optimize memory usage and database transaction speed
    for batch_num in range(0, total_products, batch_size):
        batch_start_time = time.time()
        mappings = []
        
        for i in range(batch_size):
            product_idx = batch_num + i + 1
            category = random.choice(CATEGORIES)
            name = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)} #{product_idx:06d}"
            price = round(random.uniform(4.99, 1499.99), 2)
            
            # Stagger timestamps backward by 5-15 seconds per product
            current_datetime -= timedelta(seconds=random.randint(5, 15))
            
            mappings.append({
                "id": str(uuid.uuid4()),
                "name": name,
                "category": category,
                "price": price,
                "created_at": current_datetime,
                "updated_at": current_datetime
            })
            
        # Bulk insert mappings
        db.bulk_insert_mappings(Product, mappings)
        db.commit()
        
        batch_end_time = time.time()
        print(f"Inserted batch {batch_num // batch_size + 1}/{total_products // batch_size} "
              f"({batch_size} products) in {batch_end_time - batch_start_time:.2f} seconds.")

    total_duration = time.time() - start_time
    print(f"Seeding completed successfully! Total products: {total_products}. Total time: {total_duration:.2f} seconds.")
    db.close()

if __name__ == "__main__":
    seed_database()

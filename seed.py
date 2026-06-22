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

CATEGORY_NOUNS = {
    "Electronics": ["Smartphone", "Headphones", "Speaker", "Keyboard", "Laptop", "Charger", "Smartwatch", "Camera", "Tracker"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Sneakers", "Socks", "Sweater", "Dress", "Hoodie", "Belt"],
    "Home & Kitchen": ["Chair", "Desk", "Lamp", "Blender", "Coffee Maker", "Toaster", "Spatula", "Knife Set", "Dinnerware"],
    "Books": ["Novel", "Textbook", "Biography", "Cookbook", "Thriller", "Comic Book", "Encyclopedia", "Dictionary"],
    "Sports & Outdoors": ["Flask", "Water Bottle", "Backpack", "Tent", "Yoga Mat", "Dumbbell", "Sleeping Bag", "Compass"],
    "Beauty": ["Lipstick", "Mascara", "Moisturizer", "Perfume", "Shampoo", "Face Wash", "Hair Dryer", "Sunscreen"],
    "Toys": ["Action Figure", "Board Game", "Puzzle", "Lego Set", "Teddy Bear", "Toy Car", "Doll", "Water Gun"],
    "Automotive": ["Tire", "Car Wax", "Wiper Blade", "Engine Oil", "GPS Tracker", "Seat Cover", "Jumper Cables", "Car Charger"],
    "Garden": ["Lawn Mower", "Hose", "Flower Pot", "Seeds", "Pruning Shears", "Fertilizer", "Watering Can", "Shovel"],
    "Grocery": ["Olive Oil", "Coffee Beans", "Cereal", "Pasta", "Chocolate Bar", "Green Tea", "Honey", "Maple Syrup"]
}

CATEGORY_PRICES = {
    "Electronics": (49.99, 1299.99),
    "Clothing": (14.99, 199.99),
    "Home & Kitchen": (19.99, 499.99),
    "Books": (5.99, 59.99),
    "Sports & Outdoors": (9.99, 299.99),
    "Beauty": (7.99, 149.99),
    "Toys": (9.99, 199.99),
    "Automotive": (12.99, 599.99),
    "Garden": (9.99, 399.99),
    "Grocery": (2.99, 39.99)
}

ADJECTIVES = [
    "Premium", "Wireless", "Eco-Friendly", "Ergonomic", "Portable", 
    "Smart", "Ultra", "Classic", "Mini", "Professional", 
    "Sleek", "Durable", "Compact", "Luxury", "Modern"
]

def seed_database():
    print("Initializing database schema...")
    init_db()
    
    db = SessionLocal()
    
    # We will clear the existing database to apply the new correlated values
    print("Clearing existing products for new correlated database...")
    db.query(Product).delete()
    db.commit()

    print("Generating 200,000 products with semantic correlations...")
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
            noun = random.choice(CATEGORY_NOUNS[category])
            name = f"{random.choice(ADJECTIVES)} {noun} #{product_idx:06d}"
            
            min_p, max_p = CATEGORY_PRICES[category]
            price = round(random.uniform(min_p, max_p), 2)
            
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

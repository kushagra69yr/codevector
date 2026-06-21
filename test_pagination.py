import time
import uuid
import random
from datetime import datetime, timezone, timedelta
from db import SessionLocal, Product, init_db
from sqlalchemy import or_, and_

def test_performance():
    print("\n=== PERFORMANCE TEST ===")
    db = SessionLocal()
    
    # 1. Warm up database
    total_count = db.query(Product).count()
    print(f"Total products in database: {total_count}")
    if total_count < 200000:
        print("Warning: Database has less than 200k products. Run seed.py first.")
        db.close()
        return

    # Let's pick a cursor deep in the database to test cursor pagination speed
    # First, let's fetch the first 100,000 products' sorting keys to construct a middle cursor
    print("Fetching a product from the middle of the catalog...")
    middle_product = db.query(Product.created_at, Product.id)\
                       .order_by(Product.created_at.desc(), Product.id.desc())\
                       .offset(100000)\
                       .limit(1)\
                       .first()
    
    middle_created_at, middle_id = middle_product
    print(f"Middle Product Cursor: created_at={middle_created_at}, id={middle_id}")

    # Test 1: Cursor-based Pagination (Deep page)
    print("\nMeasuring Cursor Pagination speed (Deep Page at ~100k)...")
    start_time = time.perf_counter()
    
    cursor_results = db.query(Product)\
        .filter(
            or_(
                Product.created_at < middle_created_at,
                and_(
                    Product.created_at == middle_created_at,
                    Product.id < middle_id
                )
            )
        )\
        .order_by(Product.created_at.desc(), Product.id.desc())\
        .limit(50)\
        .all()
        
    cursor_duration = (time.perf_counter() - start_time) * 1000
    print(f"Cursor Pagination: Fetched {len(cursor_results)} rows in {cursor_duration:.2f} ms")

    # Test 2: Offset-based Pagination (Deep page)
    print("\nMeasuring Offset Pagination speed (OFFSET 100,000)...")
    start_time = time.perf_counter()
    
    offset_results = db.query(Product)\
        .order_by(Product.created_at.desc(), Product.id.desc())\
        .offset(100000)\
        .limit(50)\
        .all()
        
    offset_duration = (time.perf_counter() - start_time) * 1000
    print(f"Offset Pagination: Fetched {len(offset_results)} rows in {offset_duration:.2f} ms")

    # Compare
    print("\n--- Speed Comparison Results ---")
    print(f"Cursor time: {cursor_duration:.2f} ms")
    print(f"Offset time: {offset_duration:.2f} ms")
    if cursor_duration > 0:
        print(f"Cursor pagination is {offset_duration / cursor_duration:.1f}x faster at page depth 100,000!")

    db.close()

def test_drift_and_concurrency():
    print("\n=== CONCURRENCY DRIFT-FREE PAGINATION TEST ===")
    db = SessionLocal()
    
    # 1. Fetch Page 1 (newest 50 products)
    print("Fetching Page 1 (first 50 products)...")
    page1 = db.query(Product)\
              .order_by(Product.created_at.desc(), Product.id.desc())\
              .limit(50)\
              .all()
              
    page1_ids = {p.id for p in page1}
    last_product_page1 = page1[-1]
    cursor_created_at = last_product_page1.created_at
    cursor_id = last_product_page1.id
    
    print(f"Page 1 last item: Name='{last_product_page1.name}', created_at={cursor_created_at}")

    # 2. Simulate concurrent insert of 50 new items at the top
    print("\nSimulating: 50 new products are added in the background...")
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    injected_mappings = []
    for i in range(50):
        # Fresh timestamps (newer than Page 1 items)
        created_at = now + timedelta(seconds=i + 60)
        injected_mappings.append({
            "id": str(uuid.uuid4()),
            "name": f"Concurrently-Added Injected Product #{i+1:02d}",
            "category": "Electronics",
            "price": 99.99,
            "created_at": created_at,
            "updated_at": created_at
        })
    db.bulk_insert_mappings(Product, injected_mappings)
    db.commit()
    print("Successfully injected 50 products in the database.")

    # 3. Fetch Page 2 using the Cursor (Drift-Free)
    print("\nFetching Page 2 using the cursor (Cursor-Based pagination)...")
    page2_cursor = db.query(Product)\
        .filter(
            or_(
                Product.created_at < cursor_created_at,
                and_(
                    Product.created_at == cursor_created_at,
                    Product.id < cursor_id
                )
            )
        )\
        .order_by(Product.created_at.desc(), Product.id.desc())\
        .limit(50)\
        .all()
        
    page2_cursor_ids = {p.id for p in page2_cursor}
    
    # 4. Fetch Page 2 using Offset (Offset-Based pagination: LIMIT 50 OFFSET 50)
    print("Fetching Page 2 using offset (OFFSET 50 pagination)...")
    page2_offset = db.query(Product)\
                     .order_by(Product.created_at.desc(), Product.id.desc())\
                     .offset(50)\
                     .limit(50)\
                     .all()
                     
    page2_offset_ids = {p.id for p in page2_offset}

    # Verify standard behavior vs offset behavior
    # With Offset, the 50 newly inserted products pushed all products down by 50 rows.
    # Therefore, Page 2 using OFFSET 50 will contain the exact same products that were in Page 1!
    offset_duplicates = page1_ids.intersection(page2_offset_ids)
    
    # With Cursor, the page bounds are pinned to the last product of page 1.
    # Therefore, Page 2 using Cursor will have 0 duplicates from Page 1, and will not miss any.
    cursor_duplicates = page1_ids.intersection(page2_cursor_ids)

    print("\n--- Concurrency Verification Results ---")
    print(f"Number of duplicate products seen on Page 2 with Offset pagination: {len(offset_duplicates)}")
    print(f"Number of duplicate products seen on Page 2 with Cursor pagination: {len(cursor_duplicates)}")
    
    assert len(cursor_duplicates) == 0, "Error: Cursor pagination contains duplicate products!"
    assert len(offset_duplicates) == 50, "Warning: Offset pagination did not exhibit duplicates (check injection times)"
    
    print("\nSUCCESS: Cursor pagination successfully prevented all duplicates and data drift under concurrent writes!")
    
    # Clean up the injected test products to avoid database pollution
    injected_ids = {p["id"] for p in injected_mappings}
    db.query(Product).filter(Product.id.in_(injected_ids)).delete(synchronize_session=False)
    db.commit()
    print("Cleaned up injected test products.")
    db.close()

if __name__ == "__main__":
    init_db()
    test_performance()
    test_drift_and_concurrency()

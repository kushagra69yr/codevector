import os
import base64
import json
import random
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from pydantic import BaseModel
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from db import get_db, Product, init_db

app = FastAPI(title="Product Catalog API", version="1.0.0")

# Enable CORS for easy local integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProductCreate(BaseModel):
    name: str
    category: str
    price: float

class ProductResponse(BaseModel):
    id: str
    name: str
    category: str
    price: float
    created_at: str
    updated_at: str

class PaginatedProductsResponse(BaseModel):
    products: List[ProductResponse]
    next_cursor: Optional[str]
    limit: int
    count: int

def decode_cursor(cursor_str: str):
    """
    Decodes a base64 encoded cursor containing created_at and id.
    Returns (created_at_datetime, product_id) or (None, None).
    """
    try:
        decoded = base64.b64decode(cursor_str.encode("utf-8")).decode("utf-8")
        data = json.loads(decoded)
        created_at = datetime.fromisoformat(data["created_at"])
        if created_at.tzinfo is not None:
            created_at = created_at.replace(tzinfo=None)
        return created_at, data["id"]
    except Exception:
        return None, None

def encode_cursor(created_at: datetime, product_id: str) -> Optional[str]:
    """
    Encodes created_at and id into a base64 string.
    """
    if not created_at:
        return None
    naive_created_at = created_at.replace(tzinfo=None) if created_at.tzinfo is not None else created_at
    data = {
        "created_at": naive_created_at.isoformat(),
        "id": product_id
    }
    encoded = base64.b64encode(json.dumps(data).encode("utf-8")).decode("utf-8")
    return encoded

@app.on_event("startup")
def startup_event():
    # Make sure database tables exist
    init_db()

@app.get("/api/products", response_model=PaginatedProductsResponse)
def get_products(
    category: Optional[str] = Query(None, description="Filter products by category"),
    limit: int = Query(50, ge=1, le=100, description="Number of products to retrieve"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination (base64 encoded)")
):
    # Use a new DB session context manager to ensure clean isolation
    from db import SessionLocal
    db = SessionLocal()
    try:
        query = db.query(Product)
        
        # Apply category filter
        if category:
            query = query.filter(Product.category == category)
        
        # Apply cursor pagination conditions
        if cursor:
            cursor_created_at, cursor_id = decode_cursor(cursor)
            if cursor_created_at and cursor_id:
                query = query.filter(
                    or_(
                        Product.created_at < cursor_created_at,
                        and_(
                            Product.created_at == cursor_created_at,
                            Product.id < cursor_id
                        )
                    )
                )
            else:
                raise HTTPException(status_code=400, detail="Invalid cursor format")
        
        # Order by newest first, breaking ties with ID (both DESC)
        query = query.order_by(Product.created_at.desc(), Product.id.desc())
        
        # Retrieve limit + 1 items to determine if a next page exists
        products = query.limit(limit + 1).all()
        
        has_next = len(products) > limit
        result_products = products[:limit]
        
        # Generate the next cursor using the last product in the current page
        next_cursor = None
        if has_next and result_products:
            last_item = result_products[-1]
            next_cursor = encode_cursor(last_item.created_at, last_item.id)
            
        # Serialize the product list
        serialized_products = [
            ProductResponse(
                id=p.id,
                name=p.name,
                category=p.category,
                price=float(p.price),
                created_at=p.created_at.isoformat(),
                updated_at=p.updated_at.isoformat()
            )
            for p in result_products
        ]
        
        return PaginatedProductsResponse(
            products=serialized_products,
            next_cursor=next_cursor,
            limit=limit,
            count=len(serialized_products)
        )
    finally:
        db.close()

@app.post("/api/products", response_model=ProductResponse)
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    """
    Creates a new product (used to simulate single updates/additions).
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    product = Product(
        id=str(uuid.uuid4()),
        name=product_data.name,
        category=product_data.category,
        price=product_data.price,
        created_at=now,
        updated_at=now
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductResponse(
        id=product.id,
        name=product.name,
        category=product.category,
        price=float(product.price),
        created_at=product.created_at.isoformat(),
        updated_at=product.updated_at.isoformat()
    )

CATEGORIES_POOL = ["Electronics", "Clothing", "Home & Kitchen", "Books", "Sports & Outdoors"]
INJECTED_ADJECTIVES = ["New-Release", "Hot-Item", "Concurrently-Added", "Real-Time", "Fresh-Stock"]
INJECTED_NOUNS = ["Product", "Offer", "Edition", "Deals", "Arrival"]

@app.post("/api/products/inject")
def inject_products():
    """
    Endpoint that simulates 50 new products being added concurrently.
    Sets their created_at times slightly in the future relative to the last seeded items,
    ensuring they appear at the very top of the list.
    """
    from db import SessionLocal
    db = SessionLocal()
    try:
        mappings = []
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        
        for i in range(50):
            # Stagger timestamps slightly to create a clear order
            created_at = now + timedelta(seconds=i)
            mappings.append({
                "id": str(uuid.uuid4()),
                "name": f"{random.choice(INJECTED_ADJECTIVES)} {random.choice(INJECTED_NOUNS)} #{random.randint(1000, 9999)}",
                "category": random.choice(CATEGORIES_POOL),
                "price": round(random.uniform(9.99, 199.99), 2),
                "created_at": created_at,
                "updated_at": created_at
            })
            
        db.bulk_insert_mappings(Product, mappings)
        db.commit()
        return {"status": "success", "message": "Injected 50 products at the top of the catalog"}
    finally:
        db.close()

# Serves static files for our UI
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

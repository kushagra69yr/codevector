import os
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Numeric, DateTime, Index
from sqlalchemy.orm import declarative_base, sessionmaker

# Default to local SQLite database in the project directory
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "products.db")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# For SQLite, we need to allow multithreading access if using pool
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Define composite indexes for high-performance cursor pagination
    __table_args__ = (
        Index("idx_products_category_created_at_id", "category", created_at.desc(), id.desc()),
        Index("idx_products_created_at_id", created_at.desc(), id.desc()),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": float(self.price),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

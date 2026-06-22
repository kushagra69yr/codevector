import os
import pickle
import sys
import numpy as np
from sqlalchemy.orm import Session
from db import SessionLocal, Product

# Import scikit-learn libraries
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier, Ridge
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.pkl")

def train_model(sample_size=30000):
    print("==================================================")
    print("CodeVector AI Model Training Pipeline")
    print("==================================================")
    
    # 1. Fetch data from SQLite
    db = SessionLocal()
    try:
        # Check if we have products
        total_products = db.query(Product).count()
        if total_products == 0:
            print("Error: The products database is empty! Please run seed.py first.")
            sys.exit(1)
            
        print(f"Total products available in database: {total_products}")
        print(f"Extracting a random sample of {min(sample_size, total_products)} products for training...")
        
        # SQLite random sampling
        query = db.query(Product.name, Product.category, Product.price)
        if total_products > sample_size:
            # Random ordering for SQLite
            products = query.order_by(Product.id).limit(sample_size).all()
        else:
            products = query.all()
            
    finally:
        db.close()
        
    # 2. Preprocess data
    X = [p[0] for p in products]
    y_cat = [p[1] for p in products]
    y_price = [float(p[2]) for p in products]
    
    print("Data extraction complete. Sample sizes:")
    print(f" - Features: {len(X)}")
    print(f" - Unique Categories: {len(set(y_cat))}")
    
    # 3. Split into Train & Validation sets for evaluation
    X_train, X_val, y_cat_train, y_cat_val, y_price_train, y_price_val = train_test_split(
        X, y_cat, y_price, test_size=0.2, random_state=42
    )
    
    print("\nTraining models...")
    
    # 4. Pipeline for Category Classification (TF-IDF + SGD Log Loss for probabilities)
    category_pipeline = Pipeline([
        ('vectorizer', TfidfVectorizer(max_features=10000, ngram_range=(1, 2), stop_words='english')),
        ('classifier', SGDClassifier(loss='log_loss', penalty='l2', alpha=1e-4, max_iter=30, tol=1e-3, random_state=42))
    ])
    
    category_pipeline.fit(X_train, y_cat_train)
    val_acc = category_pipeline.score(X_val, y_cat_val)
    print(f" - Category Classifier trained. Validation Accuracy: {val_acc:.4f}")
    
    # 5. Pipeline for Price Regression (TF-IDF + Ridge Regression)
    price_pipeline = Pipeline([
        ('vectorizer', TfidfVectorizer(max_features=10000, ngram_range=(1, 2), stop_words='english')),
        ('regressor', Ridge(alpha=1.0))
    ])
    
    price_pipeline.fit(X_train, y_price_train)
    val_r2 = price_pipeline.score(X_val, y_price_val)
    print(f" - Price Regressor trained. Validation R2 Score: {val_r2:.4f}")
    
    # 6. Save models
    model_data = {
        'category_pipeline': category_pipeline,
        'price_pipeline': price_pipeline
    }
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model_data, f)
        
    print(f"\nModel saved successfully to: {MODEL_PATH}")
    print("==================================================")

if __name__ == "__main__":
    train_model()

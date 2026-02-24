"""
Unified Knowledge Database for STM
Stores all extracted data, validation results, and scores
Uses SQLite (completely FREE, no server needed)
"""

import sqlite3
import json
import os
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH, DATABASE_DIR

class UnifiedDatabase:
    """
    Manages all STM data in a single SQLite database.
    Think of this as your system's memory - everything gets saved here!
    """
    
    def __init__(self):
        """Initialize database connection"""
        # Create database directory if it doesn't exist
        os.makedirs(DATABASE_DIR, exist_ok=True)
        
        self.db_path = DB_PATH
        self.conn = None
        self.cursor = None
        
        print(f"📦 Initializing database at: {self.db_path}")
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print("✅ Database connected successfully!")
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            raise
    
    def _create_tables(self):
        """Create all necessary tables if they don't exist"""
        
        # Table 1: Products (basic info about each product)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                category TEXT,
                brand TEXT,
                image_path TEXT,
                webpage_path TEXT,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(product_name, brand)
            )
        ''')
        
        # Table 2: Extracted Text (from OCR)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_text (
                text_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                text_content TEXT,
                source_type TEXT,
                position_x INTEGER,
                position_y INTEGER,
                confidence REAL,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')
        
        # Table 3: Visual Cues (health symbols detected)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS visual_cues (
                cue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                cue_type TEXT,
                confidence REAL,
                description TEXT,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')
        
        # Table 4: Nutrition Facts
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS nutrition_facts (
                nutrition_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                energy_kj REAL,
                energy_kcal REAL,
                fat REAL,
                saturated_fat REAL,
                carbohydrates REAL,
                sugar REAL,
                protein REAL,
                salt REAL,
                fiber REAL,
                per_100g BOOLEAN,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')
        
        # Table 5: Health Claims (extracted and validated)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_claims (
                claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                claim_text TEXT,
                claim_type TEXT,
                is_explicit BOOLEAN,
                validation_status TEXT,
                scientific_evidence TEXT,
                legal_status TEXT,
                confidence_score REAL,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')
        
        # Table 6: Anomaly Scores (nutritional analysis)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomaly_scores (
                anomaly_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                anomaly_score REAL,
                is_anomaly BOOLEAN,
                contributing_nutrients TEXT,
                category_comparison TEXT,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')
        
        # Table 7: Final Integrity Scores
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS integrity_scores (
                score_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                semantic_score REAL,
                legal_score REAL,
                nutrition_score REAL,
                final_score REAL,
                risk_level TEXT,
                recommendation TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')
        
        self.conn.commit()
        print("✅ All database tables created successfully!")
    
    def add_product(self, product_name, category=None, brand=None, 
                   image_path=None, webpage_path=None):
        """Add a new product to database"""
        try:
            self.cursor.execute('''
                INSERT INTO products (product_name, category, brand, image_path, webpage_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (product_name, category, brand, image_path, webpage_path))
            
            self.conn.commit()
            product_id = self.cursor.lastrowid
            print(f"✅ Product added: {product_name} (ID: {product_id})")
            return product_id
            
        except sqlite3.IntegrityError:
            # Product already exists, get its ID
            self.cursor.execute('''
                SELECT product_id FROM products 
                WHERE product_name = ? AND brand = ?
            ''', (product_name, brand))
            product_id = self.cursor.fetchone()[0]
            print(f"ℹ️  Product already exists: {product_name} (ID: {product_id})")
            return product_id
    
    def save_nutrition(self, product_id, nutrition_data):
        """Save nutrition facts for a product"""
        self.cursor.execute('''
            INSERT INTO nutrition_facts 
            (product_id, energy_kj, energy_kcal, fat, saturated_fat, 
             carbohydrates, sugar, protein, salt, fiber, per_100g)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product_id,
            nutrition_data.get('energy_kj'),
            nutrition_data.get('energy_kcal'),
            nutrition_data.get('fat'),
            nutrition_data.get('saturated_fat'),
            nutrition_data.get('carbohydrates'),
            nutrition_data.get('sugar'),
            nutrition_data.get('protein'),
            nutrition_data.get('salt'),
            nutrition_data.get('fiber'),
            nutrition_data.get('per_100g', True)
        ))
        self.conn.commit()
        print(f"✅ Nutrition data saved for product ID: {product_id}")
    
    def save_integrity_score(self, product_id, semantic_score, legal_score, 
                            nutrition_score, final_score, risk_level, recommendation):
        """Save final integrity score"""
        self.cursor.execute('''
            INSERT INTO integrity_scores 
            (product_id, semantic_score, legal_score, nutrition_score, 
             final_score, risk_level, recommendation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (product_id, semantic_score, legal_score, nutrition_score, 
              final_score, risk_level, recommendation))
        self.conn.commit()
        print(f"✅ Integrity score saved: {final_score:.2f} ({risk_level})")
    
    def get_all_products(self):
        """Get all products from database"""
        self.cursor.execute('SELECT * FROM products')
        return self.cursor.fetchall()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("📪 Database connection closed")


# Test the database
if __name__ == "__main__":
    print("🧪 Testing Unified Database...")
    db = UnifiedDatabase()
    
    # Test adding a product
    test_id = db.add_product(
        product_name="Test Product",
        category="Supplements",
        brand="TestBrand"
    )
    
    print(f"\n✅ Database test successful! Test product ID: {test_id}")
    db.close()
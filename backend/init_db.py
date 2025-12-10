"""
Script d'initialisation de la base de données avec des données de démonstration
"""

from database import SessionLocal, engine, Base
from models import Category, Product, User
from auth import get_password_hash
from datetime import datetime

# Créer les tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Créer les catégories
    categories_data = [
        {"name": "Smartphones", "slug": "smartphones", "description": "Téléphones intelligents"},
        {"name": "Ordinateurs", "slug": "ordinateurs", "description": "Ordinateurs portables et de bureau"},
        {"name": "Audio", "slug": "audio", "description": "Écouteurs, enceintes et accessoires audio"},
        {"name": "Accessoires", "slug": "accessoires", "description": "Accessoires technologiques"},
        {"name": "Vêtements", "slug": "vetements", "description": "Vêtements et mode"}
    ]
    
    for cat_data in categories_data:
        existing = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
        if not existing:
            category = Category(**cat_data)
            db.add(category)
    
    # Créer un utilisateur admin
    admin_email = "admin@jerrytech.ht"
    existing_admin = db.query(User).filter(User.email == admin_email).first()
    if not existing_admin:
        password_hash = get_password_hash("admin123")
        admin = User(
            email=admin_email,
            name="Admin JerryTech",
            password_hash=password_hash,
            is_admin=True
        )
        db.add(admin)
    
    # Créer des produits de démonstration
    products_data = [
        {
            "name": "iPhone 15 Pro",
            "description": "Le dernier iPhone avec puce A17 Pro",
            "price": 85000,
            "original_price": 95000,
            "category": "smartphones",
            "brand": "Apple",
            "image": "https://via.placeholder.com/300x300/1a73e8/ffffff?text=iPhone+15+Pro",
            "stock": 10,
            "rating": 4.8,
            "featured": True
        },
        {
            "name": "MacBook Air M2",
            "description": "Laptop ultra-fin avec puce M2",
            "price": 120000,
            "original_price": 135000,
            "category": "ordinateurs",
            "brand": "Apple",
            "image": "https://via.placeholder.com/300x300/1a73e8/ffffff?text=MacBook+Air+M2",
            "stock": 5,
            "rating": 4.9,
            "featured": True
        },
        {
            "name": "AirPods Pro",
            "description": "Écouteurs avec réduction de bruit active",
            "price": 25000,
            "original_price": 28000,
            "category": "audio",
            "brand": "Apple",
            "image": "https://via.placeholder.com/300x300/1a73e8/ffffff?text=AirPods+Pro",
            "stock": 20,
            "rating": 4.7,
            "featured": True
        },
        {
            "name": "T-Shirt JerryTech Premium",
            "description": "T-shirt 100% coton avec logo JerryTech",
            "price": 1500,
            "original_price": 2000,
            "category": "vetements",
            "brand": "JerryTech",
            "image": "https://via.placeholder.com/300x300/1a73e8/ffffff?text=T-Shirt+Premium",
            "stock": 50,
            "rating": 4.5,
            "featured": False
        },
        {
            "name": "Casquette JerryTech",
            "description": "Casquette ajustable avec logo brodé",
            "price": 1200,
            "category": "vetements",
            "brand": "JerryTech",
            "image": "https://via.placeholder.com/300x300/1a73e8/ffffff?text=Casquette",
            "stock": 30,
            "rating": 4.3,
            "featured": False
        },
        {
            "name": "Sweat-shirt JerryTech",
            "description": "Sweat-shirt confortable avec capuche",
            "price": 3500,
            "original_price": 4000,
            "category": "vetements",
            "brand": "JerryTech",
            "image": "https://via.placeholder.com/300x300/1a73e8/ffffff?text=Sweat-shirt",
            "stock": 25,
            "rating": 4.6,
            "featured": True
        }
    ]
    
    for prod_data in products_data:
        existing = db.query(Product).filter(Product.name == prod_data["name"]).first()
        if not existing:
            product = Product(**prod_data)
            db.add(product)
    
    db.commit()
    print("✅ Base de données initialisée avec succès!")
    print("📦 Catégories créées")
    print("👤 Utilisateur admin créé (email: admin@jerrytech.ht, password: admin123)")
    print("🛍️ Produits de démonstration créés")
    
except Exception as e:
    db.rollback()
    print(f"❌ Erreur lors de l'initialisation: {e}")
finally:
    db.close()


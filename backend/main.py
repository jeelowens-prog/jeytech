"""
JerryTech E-commerce Backend API
FastAPI backend pour le site e-commerce JerryTech
"""

from fastapi import FastAPI, HTTPException, Depends, status, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uvicorn
import json

from database import SessionLocal, engine, Base
from models import Product, Category, Order, OrderItem, User, ContactMessage
from schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    CategoryResponse, OrderCreate, OrderResponse,
    UserCreate, UserLogin, ContactCreate, ContactResponse
)
from auth import verify_token, create_access_token, get_password_hash, verify_password
from cloudinary_config import upload_image, delete_image, extract_public_id_from_url

# Créer les tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="JerryTech API",
    description="API REST pour le site e-commerce JerryTech",
    version="1.0.0"
)

# CORS middleware pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines exactes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Dependency pour obtenir la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency pour vérifier l'authentification
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token invalide")
    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    return user

# ===== ROUTES PRODUITS =====

@app.get("/api/products", response_model=List[ProductResponse])
def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    featured: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Récupérer la liste des produits avec filtres optionnels"""
    query = db.query(Product)
    
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) |
            (Product.description.ilike(f"%{search}%"))
        )
    
    if featured:
        query = query.filter(Product.featured == True)
    
    query = query.filter(Product.in_stock == True)
    
    if limit:
        query = query.limit(limit)
    
    products = query.all()
    return products

@app.get("/api/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Récupérer un produit par son ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return product

@app.get("/api/debug/product/{product_id}")
def debug_product(product_id: int, db: Session = Depends(get_db)):
    """Endpoint de debug pour voir les données brutes"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}
    
    return {
        "id": product.id,
        "name": product.name,
        "image": product.image,
        "images_raw": product.images,
        "images_type": str(type(product.images))
    }

@app.post("/api/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    name: str = Form(...),
    category: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    original_price: Optional[float] = Form(None),
    stock: int = Form(0),
    brand: Optional[str] = Form(None),
    rating: float = Form(0.0),
    featured: bool = Form(False),
    in_stock: bool = Form(True),
    image_files: List[UploadFile] = File([]),
    image_url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouveau produit (admin seulement)"""
    import json
    
    # Vérifier si l'utilisateur est admin
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé - Admin requis")
    
    # Gérer l'upload d'images multiples
    uploaded_images = []
    primary_image = image_url
    
    print(f"Received {len(image_files)} image files")
    
    # Upload les fichiers images
    for idx, image_file in enumerate(image_files):
        print(f"Processing file {idx}: {image_file.filename}")
        if image_file and image_file.filename:
            try:
                upload_result = upload_image(image_file)
                print(f"Uploaded to: {upload_result['url']}")
                uploaded_images.append(upload_result["url"])
                # La première image devient l'image principale
                if idx == 0:
                    primary_image = upload_result["url"]
            except Exception as e:
                print(f"Error uploading: {e}")
                raise HTTPException(status_code=400, detail=f"Erreur upload image: {str(e)}")
    
    print(f"Uploaded images list: {uploaded_images}")
    
    # Si aucune image, utiliser placeholder
    if not primary_image:
        primary_image = f"https://via.placeholder.com/300x300/1a73e8/ffffff?text={name.replace(' ', '+')}"
    
    # Créer le produit
    db_product = Product(
        name=name,
        category=category,
        description=description,
        price=price,
        original_price=original_price,
        stock=stock,
        brand=brand,
        rating=rating,
        featured=featured,
        in_stock=in_stock,
        image=primary_image,
        images=json.dumps(uploaded_images) if uploaded_images else None
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.put("/api/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    name: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    original_price: Optional[float] = Form(None),
    stock: Optional[int] = Form(None),
    brand: Optional[str] = Form(None),
    rating: Optional[float] = Form(None),
    featured: Optional[bool] = Form(None),
    in_stock: Optional[bool] = Form(None),
    image_files: List[UploadFile] = File([]),
    image_url: Optional[str] = Form(None),
    replace_images: bool = Form(False),  # Si True, remplace toutes les images existantes
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un produit (admin seulement)"""
    import json
    
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé - Admin requis")
    
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Mettre à jour les champs fournis
    if name is not None:
        db_product.name = name
    if category is not None:
        db_product.category = category
    if description is not None:
        db_product.description = description
    if price is not None:
        db_product.price = price
    if original_price is not None:
        db_product.original_price = original_price
    if stock is not None:
        db_product.stock = stock
    if brand is not None:
        db_product.brand = brand
    if rating is not None:
        db_product.rating = rating
    if featured is not None:
        db_product.featured = featured
    if in_stock is not None:
        db_product.in_stock = in_stock
    
    # Gérer l'upload d'images multiples
    uploaded_images = []
    has_new_images = False
    
    print(f"Update product {product_id}: received {len(image_files)} files")
    
    for idx, image_file in enumerate(image_files):
        print(f"Processing file {idx}: {image_file.filename}")
        if image_file and image_file.filename:
            has_new_images = True
            try:
                upload_result = upload_image(image_file)
                print(f"Uploaded to: {upload_result['url']}")
                uploaded_images.append(upload_result["url"])
                # La première image devient l'image principale
                if idx == 0:
                    # Supprimer l'ancienne image principale de Cloudinary
                    if db_product.image:
                        old_public_id = extract_public_id_from_url(db_product.image)
                        if old_public_id:
                            try:
                                delete_image(old_public_id)
                            except:
                                pass
                    db_product.image = upload_result["url"]
            except Exception as e:
                print(f"Error uploading: {e}")
                raise HTTPException(status_code=400, detail=f"Erreur upload image: {str(e)}")
    
    # Mettre à jour les images
    if has_new_images:
        if replace_images:
            # Supprimer les anciennes images de Cloudinary
            if db_product.images:
                try:
                    old_images = json.loads(db_product.images)
                    for old_url in old_images:
                        old_public_id = extract_public_id_from_url(old_url)
                        if old_public_id:
                            try:
                                delete_image(old_public_id)
                            except:
                                pass
                except:
                    pass
            db_product.images = json.dumps(uploaded_images)
        else:
            # Ajouter aux images existantes
            existing_images = []
            if db_product.images:
                try:
                    existing_images = json.loads(db_product.images)
                except:
                    pass
            existing_images.extend(uploaded_images)
            db_product.images = json.dumps(existing_images)
    elif image_url is not None:
        # Si une nouvelle URL est fournie
        if db_product.image and image_url != db_product.image:
            old_public_id = extract_public_id_from_url(db_product.image)
            if old_public_id:
                try:
                    delete_image(old_public_id)
                except:
                    pass
        db_product.image = image_url
    
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Supprimer un produit (admin seulement)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé - Admin requis")
    
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Supprimer l'image de Cloudinary si elle existe
    if db_product.image:
        public_id = extract_public_id_from_url(db_product.image)
        if public_id:
            try:
                delete_image(public_id)
            except:
                pass  # Ignorer les erreurs de suppression
    
    db.delete(db_product)
    db.commit()
    return None

# ===== ROUTES CATÉGORIES =====

@app.get("/api/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Récupérer toutes les catégories"""
    categories = db.query(Category).order_by(Category.name).all()
    return categories

@app.post("/api/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    name: str,
    slug: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer une nouvelle catégorie (admin seulement)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé - Admin requis")
    
    # Générer le slug si non fourni
    if not slug:
        slug = name.lower().replace(" ", "-").replace("é", "e").replace("è", "e").replace("ê", "e")
    
    # Vérifier si la catégorie existe déjà
    existing = db.query(Category).filter(
        (Category.slug == slug) | (Category.name == name)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Cette catégorie existe déjà")
    
    db_category = Category(name=name, slug=slug, description=description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# ===== ROUTES AUTHENTIFICATION =====

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Créer un nouveau compte utilisateur"""
    # Vérifier si l'email existe déjà
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=hashed_password,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    token = create_access_token({"user_id": db_user.id, "email": db_user.email})
    return {
        "token": token,
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "name": db_user.name,
            "is_admin": db_user.is_admin
        }
    }

@app.post("/api/auth/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Connexion utilisateur"""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    token = create_access_token({"user_id": user.id, "email": user.email})
    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_admin": user.is_admin
        }
    }

# ===== ROUTES COMMANDES =====

@app.post("/api/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Créer une nouvelle commande"""
    # Calculer le total
    total = 0
    order_items = []
    
    for item_data in order_data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Produit {item_data.product_id} non trouvé")
        
        if product.stock < item_data.quantity:
            raise HTTPException(status_code=400, detail=f"Stock insuffisant pour {product.name}")
        
        item_total = product.price * item_data.quantity
        total += item_total
        
        order_items.append({
            "product": product,
            "quantity": item_data.quantity,
            "price": product.price
        })
    
    # Créer la commande
    db_order = Order(
        user_id=current_user.id,
        total=total,
        status="pending",
        shipping_address=order_data.shipping_address,
        phone=order_data.phone
    )
    db.add(db_order)
    db.flush()
    
    # Créer les items de commande
    for item in order_items:
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item["product"].id,
            quantity=item["quantity"],
            price=item["price"]
        )
        db.add(db_item)
        # Mettre à jour le stock
        item["product"].stock -= item["quantity"]
    
    db.commit()
    db.refresh(db_order)
    return db_order

@app.get("/api/orders", response_model=List[OrderResponse])
def get_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Récupérer les commandes de l'utilisateur (ou toutes si admin)"""
    if current_user.is_admin:
        orders = db.query(Order).all()
    else:
        orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return orders

@app.put("/api/orders/{order_id}")
def update_order_status(
    order_id: int,
    status: str = Query(..., description="Nouveau statut: pending, processing, completed, cancelled"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour le statut d'une commande (admin seulement)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé - Admin requis")
    
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    if status not in ["pending", "processing", "completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Statut invalide")
    
    db_order.status = status
    db.commit()
    db.refresh(db_order)
    
    return db_order

# ===== ROUTES CONTACT =====

@app.post("/api/contact", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact_message(contact_data: ContactCreate, db: Session = Depends(get_db)):
    """Créer un message de contact"""
    db_message = ContactMessage(**contact_data.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


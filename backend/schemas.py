"""
Schémas Pydantic pour la validation des données
"""

import json
from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional
from datetime import datetime

# ===== PRODUITS =====

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    category: str
    brand: Optional[str] = None
    image: Optional[str] = None  # Primary image
    images: Optional[List[str]] = None  # Additional images as list of URLs
    stock: int = 0
    in_stock: bool = True
    rating: float = 0.0
    featured: bool = False

    @field_validator('images', mode='before')
    @classmethod
    def parse_images(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return []
        return v

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    image: Optional[str] = None
    images: Optional[List[str]] = None
    stock: Optional[int] = None
    in_stock: Optional[bool] = None
    rating: Optional[float] = None
    featured: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ===== CATÉGORIES =====

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# ===== UTILISATEURS =====

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    is_admin: bool
    
    class Config:
        from_attributes = True

# ===== COMMANDES =====

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    shipping_address: str
    phone: str

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total: float
    status: str
    shipping_address: str
    phone: str
    created_at: datetime
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True

# ===== CONTACT =====

class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    subject: Optional[str] = None
    message: str

class ContactResponse(BaseModel):
    id: int
    name: str
    email: str
    subject: Optional[str] = None
    message: str
    created_at: datetime
    
    class Config:
        from_attributes = True


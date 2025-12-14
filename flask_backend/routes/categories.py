"""
Routes API Catégories
"""

from flask import Blueprint, request, jsonify, g
from models import db, Category
from auth import admin_required

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/api/categories', methods=['GET'])
def get_categories():
    """Récupérer toutes les catégories"""
    categories = Category.query.order_by(Category.name).all()
    return jsonify([c.to_dict() for c in categories])


@categories_bp.route('/api/categories', methods=['POST'])
@admin_required
def create_category():
    """Créer une nouvelle catégorie (admin seulement)"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Le nom est requis'}), 400
    
    name = data.get('name')
    slug = data.get('slug')
    description = data.get('description')
    
    # Générer le slug si non fourni
    if not slug:
        slug = name.lower().replace(' ', '-').replace('é', 'e').replace('è', 'e').replace('ê', 'e')
    
    # Vérifier si la catégorie existe déjà
    existing = Category.query.filter(
        db.or_(Category.slug == slug, Category.name == name)
    ).first()
    
    if existing:
        return jsonify({'error': 'Cette catégorie existe déjà'}), 400
    
    category = Category(name=name, slug=slug, description=description)
    db.session.add(category)
    db.session.commit()
    
    return jsonify(category.to_dict()), 201

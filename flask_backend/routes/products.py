"""
Routes API Produits
"""

from flask import Blueprint, request, jsonify, g
import json
from models import db, Product
from auth import token_required, admin_required
from cloudinary_config import upload_image, delete_image, extract_public_id_from_url

products_bp = Blueprint('products', __name__)


@products_bp.route('/api/products', methods=['GET'])
def get_products():
    """Récupérer la liste des produits avec filtres optionnels"""
    category = request.args.get('category')
    search = request.args.get('search')
    limit = request.args.get('limit', type=int)
    featured = request.args.get('featured', type=lambda x: x.lower() == 'true')
    
    query = Product.query
    
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%')
            )
        )
    
    if featured:
        query = query.filter(Product.featured == True)
    
    query = query.filter(Product.in_stock == True)
    
    if limit:
        query = query.limit(limit)
    
    products = query.all()
    return jsonify([p.to_dict() for p in products])


@products_bp.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Récupérer un produit par son ID"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Produit non trouvé'}), 404
    return jsonify(product.to_dict())


@products_bp.route('/api/debug/product/<int:product_id>', methods=['GET'])
def debug_product(product_id):
    """Endpoint de debug pour voir les données brutes"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'image': product.image,
        'images_raw': product.images,
        'images_type': str(type(product.images))
    })


@products_bp.route('/api/products', methods=['POST'])
@admin_required
def create_product():
    """Créer un nouveau produit (admin seulement)"""
    # Récupérer les données du formulaire
    name = request.form.get('name')
    category = request.form.get('category')
    description = request.form.get('description')
    price = request.form.get('price', type=float)
    original_price = request.form.get('original_price', type=float)
    stock = request.form.get('stock', 0, type=int)
    brand = request.form.get('brand')
    rating = request.form.get('rating', 0.0, type=float)
    featured = request.form.get('featured', 'false').lower() == 'true'
    in_stock = request.form.get('in_stock', 'true').lower() == 'true'
    image_url = request.form.get('image_url')
    
    if not name or not category or not price:
        return jsonify({'error': 'name, category et price sont requis'}), 400
    
    # Gérer l'upload d'images multiples
    uploaded_images = []
    primary_image = image_url
    
    image_files = request.files.getlist('image_files')
    
    for idx, image_file in enumerate(image_files):
        if image_file and image_file.filename:
            try:
                upload_result = upload_image(image_file)
                uploaded_images.append(upload_result['url'])
                if idx == 0:
                    primary_image = upload_result['url']
            except Exception as e:
                return jsonify({'error': f'Erreur upload image: {str(e)}'}), 400
    
    # Placeholder si aucune image
    if not primary_image:
        primary_image = f"https://via.placeholder.com/300x300/1a73e8/ffffff?text={name.replace(' ', '+')}"
    
    # Créer le produit
    product = Product(
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
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify(product.to_dict()), 201


@products_bp.route('/api/products/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """Mettre à jour un produit (admin seulement)"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Produit non trouvé'}), 404
    
    # Mettre à jour les champs fournis
    if 'name' in request.form:
        product.name = request.form.get('name')
    if 'category' in request.form:
        product.category = request.form.get('category')
    if 'description' in request.form:
        product.description = request.form.get('description')
    if 'price' in request.form:
        product.price = request.form.get('price', type=float)
    if 'original_price' in request.form:
        product.original_price = request.form.get('original_price', type=float)
    if 'stock' in request.form:
        product.stock = request.form.get('stock', type=int)
    if 'brand' in request.form:
        product.brand = request.form.get('brand')
    if 'rating' in request.form:
        product.rating = request.form.get('rating', type=float)
    if 'featured' in request.form:
        product.featured = request.form.get('featured', 'false').lower() == 'true'
    if 'in_stock' in request.form:
        product.in_stock = request.form.get('in_stock', 'true').lower() == 'true'
    
    # Gérer l'upload d'images
    uploaded_images = []
    has_new_images = False
    replace_images = request.form.get('replace_images', 'false').lower() == 'true'
    
    image_files = request.files.getlist('image_files')
    
    for idx, image_file in enumerate(image_files):
        if image_file and image_file.filename:
            has_new_images = True
            try:
                upload_result = upload_image(image_file)
                uploaded_images.append(upload_result['url'])
                if idx == 0:
                    # Supprimer l'ancienne image
                    if product.image:
                        old_public_id = extract_public_id_from_url(product.image)
                        if old_public_id:
                            try:
                                delete_image(old_public_id)
                            except:
                                pass
                    product.image = upload_result['url']
            except Exception as e:
                return jsonify({'error': f'Erreur upload image: {str(e)}'}), 400
    
    # Mettre à jour les images
    if has_new_images:
        if replace_images:
            # Supprimer les anciennes images
            if product.images:
                try:
                    old_images = json.loads(product.images)
                    for old_url in old_images:
                        old_public_id = extract_public_id_from_url(old_url)
                        if old_public_id:
                            try:
                                delete_image(old_public_id)
                            except:
                                pass
                except:
                    pass
            product.images = json.dumps(uploaded_images)
        else:
            # Ajouter aux images existantes
            existing_images = []
            if product.images:
                try:
                    existing_images = json.loads(product.images)
                except:
                    pass
            existing_images.extend(uploaded_images)
            product.images = json.dumps(existing_images)
    elif 'image_url' in request.form:
        image_url = request.form.get('image_url')
        if product.image and image_url != product.image:
            old_public_id = extract_public_id_from_url(product.image)
            if old_public_id:
                try:
                    delete_image(old_public_id)
                except:
                    pass
        product.image = image_url
    
    db.session.commit()
    
    return jsonify(product.to_dict())


@products_bp.route('/api/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """Supprimer un produit (admin seulement)"""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Produit non trouvé'}), 404
    
    # Supprimer l'image de Cloudinary
    if product.image:
        public_id = extract_public_id_from_url(product.image)
        if public_id:
            try:
                delete_image(public_id)
            except:
                pass
    
    db.session.delete(product)
    db.session.commit()
    
    return '', 204

"""
Routes API Commandes
"""

from flask import Blueprint, request, jsonify, g
from models import db, Order, OrderItem, Product
from auth import token_required, admin_required

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/api/orders', methods=['POST'])
@token_required
def create_order():
    """Créer une nouvelle commande"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Données JSON requises'}), 400
    
    items_data = data.get('items', [])
    shipping_address = data.get('shipping_address')
    phone = data.get('phone')
    
    if not items_data or not shipping_address or not phone:
        return jsonify({'error': 'items, shipping_address et phone sont requis'}), 400
    
    # Calculer le total
    total = 0
    order_items = []
    
    for item_data in items_data:
        product_id = item_data.get('product_id')
        quantity = item_data.get('quantity', 1)
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': f'Produit {product_id} non trouvé'}), 404
        
        if product.stock < quantity:
            return jsonify({'error': f'Stock insuffisant pour {product.name}'}), 400
        
        item_total = product.price * quantity
        total += item_total
        
        order_items.append({
            'product': product,
            'quantity': quantity,
            'price': product.price
        })
    
    # Créer la commande
    order = Order(
        user_id=g.current_user.id,
        total=total,
        status='pending',
        shipping_address=shipping_address,
        phone=phone
    )
    
    db.session.add(order)
    db.session.flush()  # Pour obtenir l'ID
    
    # Créer les items de commande
    for item in order_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product'].id,
            quantity=item['quantity'],
            price=item['price']
        )
        db.session.add(order_item)
        # Mettre à jour le stock
        item['product'].stock -= item['quantity']
    
    db.session.commit()
    
    return jsonify(order.to_dict()), 201


@orders_bp.route('/api/orders', methods=['GET'])
@token_required
def get_orders():
    """Récupérer les commandes (user: ses commandes, admin: toutes)"""
    if g.current_user.is_admin:
        orders = Order.query.all()
    else:
        orders = Order.query.filter_by(user_id=g.current_user.id).all()
    
    return jsonify([o.to_dict() for o in orders])


@orders_bp.route('/api/orders/<int:order_id>', methods=['PUT'])
@admin_required
def update_order_status(order_id):
    """Mettre à jour le statut d'une commande (admin seulement)"""
    status = request.args.get('status')
    
    if not status:
        return jsonify({'error': 'Le paramètre status est requis'}), 400
    
    valid_statuses = ['pending', 'processing', 'completed', 'cancelled']
    if status not in valid_statuses:
        return jsonify({'error': f'Statut invalide. Valeurs acceptées: {", ".join(valid_statuses)}'}), 400
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Commande non trouvée'}), 404
    
    order.status = status
    db.session.commit()
    
    return jsonify(order.to_dict())

"""
Routes API Contact
"""

from flask import Blueprint, request, jsonify
from models import db, ContactMessage
import re

contact_bp = Blueprint('contact', __name__)


def validate_email(email):
    """Valider le format de l'email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@contact_bp.route('/api/contact', methods=['POST'])
def create_contact_message():
    """Créer un message de contact"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Données JSON requises'}), 400
    
    name = data.get('name')
    email = data.get('email')
    subject = data.get('subject')
    message = data.get('message')
    
    # Validation
    if not name or not email or not message:
        return jsonify({'error': 'name, email et message sont requis'}), 400
    
    if not validate_email(email):
        return jsonify({'error': 'Format email invalide'}), 400
    
    # Créer le message
    contact_message = ContactMessage(
        name=name,
        email=email,
        subject=subject,
        message=message
    )
    
    db.session.add(contact_message)
    db.session.commit()
    
    return jsonify(contact_message.to_dict()), 201

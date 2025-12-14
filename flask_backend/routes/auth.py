"""
Routes API Authentification
"""

from flask import Blueprint, request, jsonify
from models import db, User
from auth import create_access_token, get_password_hash, verify_password
from extensions import limiter
import re

auth_bp = Blueprint('auth', __name__)


def validate_email(email):
    """Valider le format de l'email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@auth_bp.route('/api/auth/register', methods=['POST'])
@limiter.limit("5 per minute")  # Max 5 inscriptions par minute par IP
def register():
    """Créer un nouveau compte utilisateur"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Données JSON requises'}), 400
    
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    
    # Validation
    if not email or not name or not password:
        return jsonify({'error': 'Email, nom et mot de passe sont requis'}), 400
    
    if not validate_email(email):
        return jsonify({'error': 'Format email invalide'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Le mot de passe doit contenir au moins 6 caractères'}), 400
    
    # Vérifier si l'email existe déjà
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Cet email est déjà utilisé'}), 400
    
    # Créer l'utilisateur
    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        name=name,
        password_hash=hashed_password,
        is_admin=False
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Générer le token
    token = create_access_token({'user_id': user.id, 'email': user.email})
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    }), 201


@auth_bp.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")  # Max 10 tentatives de login par minute par IP
def login():
    """Connexion utilisateur"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Données JSON requises'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email et mot de passe sont requis'}), 400
    
    # Trouver l'utilisateur
    user = User.query.filter_by(email=email).first()
    
    if not user or not verify_password(password, user.password_hash):
        return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
    
    # Générer le token
    token = create_access_token({'user_id': user.id, 'email': user.email})
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    })

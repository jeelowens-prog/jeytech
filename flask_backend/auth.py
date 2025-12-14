"""
Gestion de l'authentification JWT pour Flask
"""

from datetime import datetime, timedelta
from functools import wraps
import jwt
import bcrypt
from flask import request, jsonify, current_app, g


def get_password_hash(password: str) -> str:
    """Hasher un mot de passe avec bcrypt"""
    password_bytes = password.encode('utf-8')
    # Limiter à 72 bytes (limite bcrypt)
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier un mot de passe"""
    try:
        if hashed_password.startswith('$2'):
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        else:
            # Fallback pour anciens hashs
            import hashlib
            return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Créer un token JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=30)
    
    to_encode['exp'] = expire
    
    secret_key = current_app.config['SECRET_KEY']
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm='HS256')
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Vérifier et décoder un token JWT"""
    try:
        secret_key = current_app.config['SECRET_KEY']
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Décorateur pour protéger les routes avec JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Récupérer le token du header Authorization
        auth_header = request.headers.get('Authorization')
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        
        if not token:
            return jsonify({'error': 'Token manquant'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token invalide'}), 401
        
        # Récupérer l'utilisateur
        from models import User
        user = User.query.get(payload.get('user_id'))
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 401
        
        # Stocker l'utilisateur dans g
        g.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """Décorateur pour les routes admin"""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if not g.current_user.is_admin:
            return jsonify({'error': 'Accès refusé - Admin requis'}), 403
        return f(*args, **kwargs)
    
    return decorated

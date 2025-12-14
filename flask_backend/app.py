"""
JerryTech E-commerce Backend API - Flask
"""

import os
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_migrate import Migrate
from functools import wraps

from config import get_config
from models import db
from extensions import limiter
from cloudinary_config import init_cloudinary
from routes import register_blueprints


def create_app(config_object=None):
    """Application Factory Pattern"""
    app = Flask(__name__)
    
    # Configuration
    if config_object is None:
        config_object = get_config()
    app.config.from_object(config_object)
    
    # Initialiser les extensions
    db.init_app(app)
    Migrate(app, db)
    limiter.init_app(app)
    
    # Configuration CORS sécurisée
    # En production, définir ALLOWED_ORIGINS dans les variables d'environnement
    # Exemple: ALLOWED_ORIGINS=https://jerrytech.com,https://www.jerrytech.com
    allowed_origins = os.getenv('ALLOWED_ORIGINS', '*')
    if allowed_origins != '*':
        allowed_origins = [origin.strip() for origin in allowed_origins.split(',')]
    
    # Si allowed_origins est '*', on ne peut pas utiliser supports_credentials=True
    supports_credentials = True
    if allowed_origins == '*':
        supports_credentials = False
    
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-API-Key"],
            "supports_credentials": supports_credentials
        }
    })
    
    # Middleware de vérification d'API Key (optionnel)
    @app.before_request
    def check_api_key():
        """Vérifier l'API Key si elle est configurée"""
        api_key = os.getenv('API_KEY')
        
        if request.method == 'OPTIONS':
            return None
            
        # Si pas d'API Key configurée, skip la vérification
        if not api_key:
            return None
        
        # Endpoints publics qui ne nécessitent pas d'API Key
        public_endpoints = [
            '/',
            '/health',
            '/api/auth/login',
            '/api/auth/register',
            '/api/products',
            '/api/categories',
            '/api/contact'
        ]
        
        # Vérifier si c'est un endpoint public (GET seulement pour products/categories)
        path = request.path
        is_public_get = (
            path in public_endpoints or
            (path.startswith('/api/products') and request.method == 'GET') or
            (path.startswith('/api/categories') and request.method == 'GET')
        )
        
        if is_public_get:
            return None
        
        # Pour les autres endpoints, vérifier l'API Key ou le token JWT
        request_api_key = request.headers.get('X-API-Key')
        auth_header = request.headers.get('Authorization')
        
        # Si l'utilisateur a un token JWT, pas besoin d'API Key
        if auth_header and auth_header.startswith('Bearer '):
            return None
        
        # Sinon, vérifier l'API Key
        if request_api_key != api_key:
            return jsonify({'error': 'API Key invalide ou manquante'}), 401
        
        return None
    
    # Initialiser Cloudinary
    init_cloudinary(app)
    
    # Enregistrer les blueprints
    register_blueprints(app)
    
    # Route de base pour vérifier que l'API fonctionne
    @app.route('/')
    def index():
        return jsonify({
            'name': 'JerryTech API',
            'version': '1.0.0',
            'status': 'running',
            'documentation': 'Utilisez les endpoints /api/* pour accéder à l\'API'
        })
    
    # Route de health check pour Render
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy'}), 200
    
    # Gestionnaire d'erreurs global
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Non autorisé'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Accès interdit'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Ressource non trouvée'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Erreur interne du serveur'}), 500
    
    return app


# Pour gunicorn en production
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


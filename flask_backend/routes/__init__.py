"""
Routes Blueprints pour l'API Flask
"""

from flask import Blueprint

# Import des blueprints
from .products import products_bp
from .categories import categories_bp
from .auth import auth_bp
from .orders import orders_bp
from .contact import contact_bp


def register_blueprints(app):
    """Enregistrer tous les blueprints avec l'application Flask"""
    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(contact_bp)

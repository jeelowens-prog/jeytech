"""
Script de démarrage pour le développement local
"""

from app import create_app

if __name__ == '__main__':
    app = create_app()
    
    # Créer les tables si elles n'existent pas (dev only)
    with app.app_context():
        from models import db
        db.create_all()
        print("✅ Base de données initialisée")
    
    print("🚀 Démarrage du serveur Flask...")
    print("📍 API disponible sur: http://localhost:5000")
    print("📖 Documentation: http://localhost:5000/")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

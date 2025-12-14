"""
Script pour créer un utilisateur admin
Usage: python create_admin.py
"""

from app import create_app
from models import db, User
from auth import get_password_hash

def create_admin():
    app = create_app()
    
    with app.app_context():
        print("=== Création d'un compte Admin ===")
        print()
        
        email = input("Email admin: ").strip()
        name = input("Nom complet: ").strip()
        password = input("Mot de passe: ").strip()
        
        if not email or not name or not password:
            print("❌ Tous les champs sont requis!")
            return
        
        # Vérifier si l'email existe déjà
        existing = User.query.filter_by(email=email).first()
        if existing:
            # Mettre à jour en admin
            existing.is_admin = True
            db.session.commit()
            print(f"✅ L'utilisateur {email} est maintenant admin!")
        else:
            # Créer un nouvel admin
            admin = User(
                email=email,
                name=name,
                password_hash=get_password_hash(password),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Admin créé avec succès!")
            print(f"   Email: {email}")
            print(f"   Nom: {name}")

if __name__ == "__main__":
    create_admin()

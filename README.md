# JerryTech E-commerce

Site e-commerce moderne avec backend Python (FastAPI) et frontend statique.

## 🚀 Fonctionnalités

- **Gestion des produits** : Smartphones, Ordinateurs, Audio, Accessoires, **Vêtements**
- **API REST** complète avec FastAPI
- **Base de données SQLite** (facilement migrable vers PostgreSQL)
- **Authentification JWT** pour les utilisateurs et admin
- **Gestion des commandes** avec suivi de stock
- **Interface d'administration** complète
- **Frontend responsive** avec TailwindCSS

## 📋 Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

## 🛠️ Installation

### 1. Installer les dépendances Python

`ash
cd backend
pip install -r requirements.txt
`

### 2. Initialiser la base de données

`ash
python init_db.py
`

Cela créera :
- Les tables de la base de données
- Un utilisateur admin (email: dmin@jerrytech.ht, password: dmin123)
- Des produits de démonstration incluant des vêtements

### 3. Démarrer le serveur backend

`ash
python main.py
`

Le serveur API sera accessible sur http://localhost:8000

### 4. Ouvrir le frontend

Ouvrez simplement index.html dans votre navigateur, ou utilisez un serveur local :

`ash
# Avec Python
python -m http.server 8080

# Ou avec Node.js
npx http-server
`

Puis ouvrez http://localhost:8080 dans votre navigateur.

## 📚 Documentation API

Une fois le serveur démarré, la documentation interactive est disponible sur :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## 🔐 Comptes par défaut

- **Admin** : 
  - Email: dmin@jerrytech.ht
  - Password: dmin123

## 📁 Structure du projet

`
.
├── backend/
│   ├── main.py           # Application FastAPI principale
│   ├── database.py       # Configuration de la base de données
│   ├── models.py         # Modèles SQLAlchemy
│   ├── schemas.py        # Schémas Pydantic
│   ├── auth.py           # Gestion de l'authentification JWT
│   ├── init_db.py        # Script d'initialisation
│   ├── requirements.txt # Dépendances Python
│   └── jerrytech.db      # Base de données SQLite (créée après init)
├── resources/            # Images et ressources
├── *.html               # Pages du frontend
├── main.js              # JavaScript principal
└── README.md            # Ce fichier
`

## 🎨 Catégories de produits

- **Smartphones** : iPhone, Samsung, Xiaomi, etc.
- **Ordinateurs** : MacBook, PC portables, etc.
- **Audio** : Écouteurs, enceintes, etc.
- **Accessoires** : Chargeurs, coques, câbles, etc.
- **Vêtements** : T-shirts, casquettes, sweat-shirts JerryTech

## 🔧 Configuration

### Changer l'URL de l'API

Dans main.js, l'URL de l'API est automatiquement détectée :
- En local (localhost ou 127.0.0.1) : http://localhost:8000
- En production : https://api.jerrytech.ht

### Changer la clé secrète JWT

Modifiez SECRET_KEY dans ackend/auth.py pour la production.

## 📝 Notes

- La base de données SQLite est créée dans le dossier ackend/
- Pour la production, considérez l'utilisation de PostgreSQL ou MySQL
- Configurez CORS dans main.py pour limiter les origines autorisées
- Changez la clé secrète JWT en production

## 🐛 Dépannage

### Le serveur ne démarre pas
- Vérifiez que Python 3.8+ est installé
- Vérifiez que toutes les dépendances sont installées : pip install -r requirements.txt

### Erreur CORS
- Le backend autorise toutes les origines en développement
- En production, modifiez llow_origins dans main.py

### Produits non chargés
- Vérifiez que le serveur backend est démarré
- Vérifiez la console du navigateur pour les erreurs
- Vérifiez que la base de données est initialisée

## 📄 Licence

Ce projet est un exemple éducatif.


<!-- TODO: Ajouter une section sur le déploiement -->
alembic revision --autogenerate -m "add age to user"
alembic upgrade head

# Configuration Cloudinary

## Étapes pour configurer Cloudinary

### 1. Créer un compte Cloudinary

1. Allez sur [https://cloudinary.com](https://cloudinary.com)
2. Créez un compte gratuit (généralement suffisant pour commencer)
3. Une fois connecté, allez dans le **Dashboard**

### 2. Récupérer vos clés API

Dans le Dashboard Cloudinary, vous trouverez :
- **Cloud Name** : Votre nom de cloud (ex: `dxyz123`)
- **API Key** : Votre clé API
- **API Secret** : Votre secret API

### 3. Configurer le fichier .env

1. Copiez le fichier `.env.example` vers `.env` :
   ```bash
   cp .env.example .env
   ```

2. Éditez le fichier `.env` et remplacez les valeurs :
   ```env
   CLOUDINARY_CLOUD_NAME=votre_cloud_name
   CLOUDINARY_API_KEY=votre_api_key
   CLOUDINARY_API_SECRET=votre_api_secret
   ```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 5. Tester l'upload

Une fois configuré, vous pouvez tester l'upload d'images depuis la page admin.

## Notes importantes

- **Sécurité** : Ne commitez JAMAIS le fichier `.env` dans Git
- **Limites** : Le plan gratuit de Cloudinary a des limites (25GB de stockage, 25GB de bande passante/mois)
- **Formats supportés** : JPG, PNG, WebP, GIF
- **Taille max** : 10MB par défaut (configurable)

## Structure des dossiers Cloudinary

Les images seront organisées dans Cloudinary comme suit :
- `jerrytech/products/` : Images des produits


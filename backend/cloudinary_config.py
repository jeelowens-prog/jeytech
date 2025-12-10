"""
Configuration Cloudinary pour l'upload d'images
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

# Configuration Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def upload_image(file, folder="jerrytech/products"):
    """
    Upload une image vers Cloudinary
    
    Args:
        file: Fichier image (FastAPI UploadFile)
        folder: Dossier dans Cloudinary (défaut: jerrytech/products)
    
    Returns:
        dict: Informations de l'image uploadée (url, public_id, etc.)
    """
    try:
        # Lire le contenu du fichier
        file_content = file.file.read()
        
        # Upload vers Cloudinary
        result = cloudinary.uploader.upload(
            file_content,
            folder=folder,
            resource_type="image",
            transformation=[
                {"width": 800, "height": 800, "crop": "limit", "quality": "auto"},
                {"fetch_format": "auto"}
            ]
        )
        
        return {
            "url": result["secure_url"],
            "public_id": result["public_id"],
            "width": result.get("width"),
            "height": result.get("height"),
            "format": result.get("format")
        }
    except Exception as e:
        raise Exception(f"Erreur lors de l'upload: {str(e)}")

def delete_image(public_id):
    """
    Supprimer une image de Cloudinary
    
    Args:
        public_id: ID public de l'image dans Cloudinary
    
    Returns:
        dict: Résultat de la suppression
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result
    except Exception as e:
        raise Exception(f"Erreur lors de la suppression: {str(e)}")

def extract_public_id_from_url(url):
    """
    Extraire le public_id d'une URL Cloudinary
    
    Args:
        url: URL de l'image Cloudinary
    
    Returns:
        str: public_id ou None
    """
    try:
        # Format: https://res.cloudinary.com/{cloud_name}/image/upload/{version}/{public_id}.{format}
        if "cloudinary.com" in url:
            parts = url.split("/")
            # Trouver l'index de "upload"
            upload_index = None
            for i, part in enumerate(parts):
                if part == "upload":
                    upload_index = i
                    break
            
            if upload_index and upload_index + 2 < len(parts):
                # Le public_id est après "upload" et la version
                public_id_with_format = "/".join(parts[upload_index + 2:])
                # Enlever l'extension
                public_id = public_id_with_format.rsplit(".", 1)[0]
                return public_id
    except:
        pass
    return None


#!/bin/bash

echo "========================================"
echo "  JerryTech Backend - Démarrage"
echo "========================================"
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "ERREUR: Python 3 n'est pas installé"
    exit 1
fi

# Vérifier si les dépendances sont installées
echo "Vérification des dépendances..."
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "Installation des dépendances..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERREUR: Échec de l'installation des dépendances"
        exit 1
    fi
fi

# Vérifier si la base de données existe
if [ ! -f "jerrytech.db" ]; then
    echo "Initialisation de la base de données..."
    python3 init_db.py
    if [ $? -ne 0 ]; then
        echo "ERREUR: Échec de l'initialisation de la base de données"
        exit 1
    fi
fi

echo ""
echo "Démarrage du serveur API..."
echo "API disponible sur: http://localhost:8000"
echo "Documentation: http://localhost:8000/docs"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

python3 main.py


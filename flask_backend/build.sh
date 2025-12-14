#!/usr/bin/env bash
# Script de build pour Render

set -o errexit

echo "📦 Installation des dépendances..."
pip install -r requirements.txt

echo "🔄 Application des migrations..."
flask db upgrade

echo "✅ Build terminé!"

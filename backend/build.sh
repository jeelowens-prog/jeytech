#!/usr/bin/env bash
# exit on error
set -o errexit

# Met à jour pip
pip install --upgrade pip

# Installe les dépendances
pip install -r requirements.txt

# Lance les migrations Alembic
python -m alembic upgrade head

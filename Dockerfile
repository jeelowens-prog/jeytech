# Utiliser Python 3.11 slim
FROM python:3.11-slim

# Définir le dossier de travail
WORKDIR /app
ENV PYTHONPATH=/app/backend

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer Poetry
RUN pip install --no-cache-dir "poetry==2.2.1"
RUN poetry config virtualenvs.create false

# Copier les fichiers nécessaires
COPY pyproject.toml poetry.lock* ./
COPY backend/ ./backend
COPY backend/alembic.ini ./backend/alembic.ini
COPY resources/ ./resources
COPY *.html ./
COPY main.js ./

# Installer les dépendances via Poetry
RUN poetry install --no-root --no-interaction

# Exécuter Alembic pour les migrations via Poetry
RUN alembic -c backend/alembic.ini upgrade head

# Exposer le port pour Render
EXPOSE 8000

# Commande de démarrage
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

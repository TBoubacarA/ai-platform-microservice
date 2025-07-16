#!/bin/bash

# Vérifier si l'environnement est déjà activé
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Charger les variables d'environnement
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo "Environment variables loaded from .env"
else
    echo "Warning: No .env file found"
fi

# Démarrer le service
uvicorn app.main:app --port ${PORT:-8003}
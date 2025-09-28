FROM python:3.9-slim

# Métadonnées
LABEL maintainer="RODIO Network"
LABEL version="1.0.0"
LABEL description="RODIO Oracle Node - Sécurisé et Production Ready"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV RODIO_ENV=production

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Création des répertoires nécessaires
RUN mkdir -p logs

# Création d'un utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 rodio && \
    chown -R rodio:rodio /app && \
    chmod +x /app/src/api/main.py

# Changement vers l'utilisateur non-root
USER rodio

# Exposition du port API
EXPOSE 8080

# Healthcheck pour Docker
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health || exit 1

# Point d'entrée
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
# Image de base : Python 3.12 en version slim (aligné avec le projet local)
FROM python:3.12-slim

# Copie du binaire uv depuis l'image officielle
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Répertoire de travail dans le conteneur
WORKDIR /app

# Copie des fichiers de dépendances d'abord
COPY pyproject.toml uv.lock ./

# Installation des dépendances (sans les dépendances de dev)
RUN uv sync --frozen --no-dev --no-install-project

# Copie du reste du code source
COPY . .

# Installation du projet lui-même
RUN uv sync --frozen --no-dev

# Dossier partagé pour la base SQLite sur Kubernetes
ENV DB_DIR="/app/data"
ENV PYTHONUNBUFFERED=1

# Port exposé par Streamlit
EXPOSE 8501

# Commande par défaut (utilisée par le conteneur Streamlit)
CMD ["uv", "run", "streamlit", "run", "src/air_quality_app/streamlit_front/front-alerte/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
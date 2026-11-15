# Image de base : Python 3.12 en version slim (aligné avec le projet local)
FROM python:3.12-slim

# Copie du binaire uv depuis l'image officielle
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Répertoire de travail dans le conteneur
WORKDIR /app

# ... (le reste du fichier reste strictement identique)

# Copie des fichiers de dépendances d'abord
COPY pyproject.toml uv.lock ./

# Installation des dépendances (sans les dépendances de dev)
RUN uv sync --frozen --no-dev --no-install-project

# Copie du reste du code source
COPY . .

# Installation du projet lui-même
RUN uv sync --frozen --no-dev

# Création d'un utilisateur non-root et attribution des droits sur /app
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app

# On bascule sur cet utilisateur
USER appuser

# Port exposé par Streamlit
EXPOSE 8501

# Commande de démarrage : on réutilise notre entrypoint uv
CMD ["uv", "run", "app"]
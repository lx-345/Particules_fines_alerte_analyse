import os
import sqlite3
from pathlib import Path

# Définition du chemin
DB_DIR = os.getenv("DB_DIR", os.path.join(os.getcwd(), "data"))
DB_PATH = Path(DB_DIR) / "alertes.sqlite"


def init_db():
    """Crée la base, nettoie les doublons et empêche leur création."""
    # Création du dossier parent de manière sécurisée
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(str(DB_PATH)) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()

        # 1. Création de la table de base
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_capteur TEXT NOT NULL,
                prenom TEXT NOT NULL,
                nom TEXT NOT NULL,
                email TEXT NOT NULL,
                emplacement TEXT NOT NULL,
                date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # 2. Nettoyage des doublons existants (on garde la plus ancienne inscription)
        cursor.execute(
            """
            DELETE FROM users
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM users
                GROUP BY email, numero_capteur
            )
            """
        )

        # 3. Verrouillage pour l'avenir avec un Index Unique
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_email_capteur 
            ON users(email, numero_capteur)
            """
        )

        conn.commit()


def ajouter_utilisateur(
    capteur: str, prenom: str, nom: str, email: str, emplacement: str
):
    """Insère un abonné ou lève une erreur s'il est déjà existant."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO users (numero_capteur, prenom, nom, email, emplacement)
                VALUES (?, ?, ?, ?, ?)
                """,
                (capteur, prenom, nom, email, emplacement),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            # Cette erreur sera attrapée par ton bloc try/except dans Streamlit
            raise ValueError(
                f"L'adresse {email} est déjà inscrite pour le capteur {capteur}."
            )


def purger_base_de_donnees() -> None:
    """Supprime tous les inscrits et réinitialise le compteur d'ID."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        cursor = conn.cursor()
        # Supprime toutes les lignes de la table
        cursor.execute("DELETE FROM users")
        # Remet le compteur de l'auto-incrément (ID) à zéro
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='users'")
        conn.commit()

import os
import sqlite3
from pathlib import Path

# Définition du chemin
DB_DIR = os.getenv("DB_DIR", os.path.join(os.getcwd(), "data"))
DB_PATH = Path(DB_DIR) / "alertes.sqlite"


def init_db():
    """Crée la base et active le mode WAL pour la lecture"""
    """/écriture concurrente."""
    # Création du dossier parent de manière sécurisée
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # str(DB_PATH) garantit que sqlite3 reçoit bien du te
    with sqlite3.connect(str(DB_PATH)) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()
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
        conn.commit()


def ajouter_utilisateur(
    capteur: str, prenom: str, nom: str, email: str, emplacement: str
):
    """Insère un nouvel abonné dans la base de données."""
    with sqlite3.connect(str(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (numero_capteur, prenom, nom, email, emplacement)
            VALUES (?, ?, ?, ?, ?)
            """,
            (capteur, prenom, nom, email, emplacement),
        )
        conn.commit()

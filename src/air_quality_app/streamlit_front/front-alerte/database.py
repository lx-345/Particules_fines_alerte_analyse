import sqlite3
from pathlib import Path

# Résolution dynamique du chemin racine (5 niveaux plus haut)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
DB_PATH = BASE_DIR / "data" / "air_quality_local.db"

def init_db():
    """Crée la base et active le mode WAL pour la lecture/écriture concurrente."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_capteur TEXT NOT NULL,
                prenom TEXT NOT NULL,
                nom TEXT NOT NULL,
                email TEXT NOT NULL,
                emplacement TEXT NOT NULL,
                date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def ajouter_utilisateur(capteur: str, prenom: str, nom: str, email: str, emplacement: str):
    """Insère un nouvel abonné dans la base de données."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (numero_capteur, prenom, nom, email, emplacement)
            VALUES (?, ?, ?, ?, ?)
        """, (capteur, prenom, nom, email, emplacement))
        conn.commit()
import sqlite3
from typing import Dict, List
from .config import DB_PATH, logger

def obtenir_abonnements_par_capteur() -> Dict[str, List[Dict[str, str]]]:
    """Récupère les utilisateurs groupés par capteur depuis SQLite."""
    if not DB_PATH.exists():
        logger.warning(f"La base de données {DB_PATH} n'existe pas encore.")
        return {}

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT numero_capteur, prenom, nom, email, emplacement FROM users;")
            lignes = cursor.fetchall()
            
            abonnements = {}
            for capteur_id, prenom, nom, email, emplacement in lignes:
                capteur_id = str(capteur_id).strip()
                if capteur_id not in abonnements:
                    abonnements[capteur_id] = []
                abonnements[capteur_id].append({
                    "prenom": prenom,
                    "nom": nom,
                    "email": email,
                    "emplacement": emplacement
                })
            return abonnements
    except sqlite3.Error as e:
        logger.error(f"Erreur de lecture de la base de données : {e}")
        return {}
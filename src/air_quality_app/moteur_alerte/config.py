import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Chemins absolus
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(BASE_DIR / ".env")
DB_PATH = BASE_DIR / "data" / "air_quality_local.db"

# Configuration Email
MAIL_SENDER = os.getenv("MAIL_SENDER")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))

# Paramètres de l'application
INTERVALLE_SCRAPING = 60  # Secondes
SEUIL_ALERTE_NIVEAU = 2   # Déclenchement à partir de "Moyen" (2)

CATEGORIES_ATMO = ["Bon", "Moyen", "Dégradé", "Mauvais", "Très mauvais", "Extrêmement mauvais"]
SEUILS_PM25 = [10, 20, 25, 50, 75]
SEUILS_PM10 = [20, 40, 50, 100, 150]

# Configuration globale du Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("air_quality")
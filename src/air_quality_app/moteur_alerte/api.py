import pandas as pd
from datetime import datetime
from typing import Tuple, Optional
from .config import logger, CATEGORIES_ATMO, SEUILS_PM25, SEUILS_PM10

def obtenir_dernieres_mesures(chip_id: str) -> Tuple[Optional[float], Optional[float], Optional[float], str]:
    """Interroge l'archive CSV Madavi et calcule les moyennes récentes."""
    date_du_jour = datetime.now().strftime("%Y-%m-%d")
    url = f"https://api-rrd.madavi.de/data_csv/csv-files/{date_du_jour}/data-esp8266-{chip_id}-{date_du_jour}.csv"

    try:
        # Téléchargement du CSV
        df = pd.read_csv(url, sep=";")
        
        # Conversion fuseau horaire
        df["Time"] = pd.to_datetime(df["Time"]).dt.tz_localize("UTC").dt.tz_convert("Europe/Paris")
        derniere_date = df["Time"].max()
        
        # Filtrage sur les 10 dernières minutes
        seuil = derniere_date - pd.Timedelta(minutes=10)
        df_recent = df[df["Time"] >= seuil]

        # Calcul des moyennes (remplacement du pm25 = 80 en dur par la vraie donnée)
        
        pm25 = float(df_recent["SDS_P2"].mean())
        pm10 = float(df_recent["SDS_P1"].mean())
        
        # Gestion optionnelle de l'humidité si le capteur (ex: BME280) est présent
        hr = float(df_recent["BME280_humidity"].mean()) if "BME280_humidity" in df_recent.columns else None

        return round(pm25, 2), round(pm10, 2), hr, str(derniere_date)

    except Exception as e:
        logger.error(f"Erreur Madavi pour le capteur {chip_id} : {e}")
        return None, None, None, ""

def calculer_niveau_atmo(pm25: float, pm10: float) -> Tuple[int, str]:
    """Calcule l'indice global (1 à 6) selon les seuils ATMO."""
    pos_pm25 = next((i for i, seuil in enumerate(SEUILS_PM25) if pm25 <= seuil), len(SEUILS_PM25))
    pos_pm10 = next((i for i, seuil in enumerate(SEUILS_PM10) if pm10 <= seuil), len(SEUILS_PM10))
    niveau_global = max(pos_pm25 + 1, pos_pm10 + 1)
    return niveau_global, CATEGORIES_ATMO[niveau_global - 1]
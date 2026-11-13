import requests
from typing import Tuple, Optional
from .config import logger, CATEGORIES_ATMO, SEUILS_PM25, SEUILS_PM10

def obtenir_dernieres_mesures(chip_id: str) -> Tuple[Optional[float], Optional[float], Optional[float], str]:
    """Interroge l'API Sensor.Community pour un capteur donné."""
    url = f"https://data.sensor.community/airrohr/v1/sensor/{chip_id}/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return None, None, None, ""
            
        dernier_releve = data[0]
        horodatage = dernier_releve.get("timestamp", "")
        
        pm25 = pm10 = hr = None
        for valeur in dernier_releve.get("sensordatavalues", []):
            if valeur["value_type"] == "P2":
                pm25 = float(valeur["value"])
            elif valeur["value_type"] == "P1":
                pm10 = float(valeur["value"])
            elif valeur["value_type"] == "humidity":
                hr = float(valeur["value"])
                
        return pm25, pm10, hr, horodatage
    except requests.RequestException as e:
        logger.error(f"Erreur API pour le capteur {chip_id} : {e}")
        return None, None, None, ""

def calculer_niveau_atmo(pm25: float, pm10: float) -> Tuple[int, str]:
    """Calcule l'indice global (1 à 6) selon les seuils ATMO."""
    pos_pm25 = next((i for i, seuil in enumerate(SEUILS_PM25) if pm25 <= seuil), len(SEUILS_PM25))
    pos_pm10 = next((i for i, seuil in enumerate(SEUILS_PM10) if pm10 <= seuil), len(SEUILS_PM10))
    niveau_global = max(pos_pm25 + 1, pos_pm10 + 1)
    return niveau_global, CATEGORIES_ATMO[niveau_global - 1]
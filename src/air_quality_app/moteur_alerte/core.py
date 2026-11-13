import time
from typing import Dict
from .config import logger, INTERVALLE_SCRAPING, SEUIL_ALERTE_NIVEAU, DB_PATH
from .database import obtenir_abonnements_par_capteur
from .api import obtenir_dernieres_mesures, calculer_niveau_atmo
from .notifications import envoyer_salve_alertes

def main():
    logger.info("Démarrage du moteur d'alertes Air Quality...")
    logger.info(f"Base de données ciblée : {DB_PATH}")
    
    etats_alertes: Dict[str, bool] = {}

    while True:
        abonnements = obtenir_abonnements_par_capteur()

        if not abonnements:
            logger.info("Aucun capteur ou abonné trouvé en base. En attente...")
        else:
            for chip_id, liste_utilisateurs in abonnements.items():
                if chip_id not in etats_alertes:
                    etats_alertes[chip_id] = False

                pm25, pm10, hr, horodatage = obtenir_dernieres_mesures(chip_id)

                if pm25 is None or pm10 is None:
                    continue

                niveau_global, statut_global = calculer_niveau_atmo(pm25, pm10)
                logger.info(f"Capteur {chip_id} | ATMO : {niveau_global} ({statut_global}) | Abonnés : {len(liste_utilisateurs)}")

                if niveau_global >= SEUIL_ALERTE_NIVEAU:
                    if not etats_alertes[chip_id]:
                        logger.warning(f"DÉCLENCHEMENT ALERTE pour {chip_id} ({statut_global})")
                        envoyer_salve_alertes(liste_utilisateurs, chip_id, statut_global, niveau_global, pm25, pm10)
                        etats_alertes[chip_id] = True
                else:
                    if etats_alertes[chip_id]:
                        logger.info(f"RETOUR À LA NORMALE pour le capteur {chip_id}. Alerte réarmée.")
                        etats_alertes[chip_id] = False

        time.sleep(INTERVALLE_SCRAPING)

if __name__ == "__main__":
    main()
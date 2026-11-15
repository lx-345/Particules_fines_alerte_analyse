import time
from typing import Dict

from .api import calculer_niveau_atmo, obtenir_dernieres_mesures
from .config import DB_PATH, INTERVALLE_SCRAPING, SEUIL_ALERTE_NIVEAU, logger
from .database import obtenir_abonnements_par_capteur
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

                # La ligne ci-dessous a été coupée proprement pour respecter PEP 8
                logger.info(
                    f"Capteur {chip_id} | ATMO : {niveau_global} ({statut_global}) "
                    f"| Abonnés : {len(liste_utilisateurs)}"
                )

                if niveau_global >= SEUIL_ALERTE_NIVEAU:
                    if not etats_alertes[chip_id]:
                        logger.warning(
                            f"DÉCLENCHEMENT ALERTE pour {chip_id} ({statut_global})"
                        )
                        envoyer_salve_alertes(
                            liste_utilisateurs,
                            chip_id,
                            statut_global,
                            niveau_global,
                            pm25,
                            pm10,
                        )
                        etats_alertes[chip_id] = True
                else:
                    if etats_alertes[chip_id]:
                        logger.info(
                            f"RETOUR À LA NORMALE pour {chip_id}. Alerte réarmée."
                        )
                        etats_alertes[chip_id] = False

        time.sleep(INTERVALLE_SCRAPING)


if __name__ == "__main__":
    main()

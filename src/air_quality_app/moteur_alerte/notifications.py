import smtplib
from email.message import EmailMessage
from typing import Dict, List

from .config import MAIL_PASSWORD, MAIL_SENDER, SMTP_PORT, SMTP_SERVER, logger


def envoyer_salve_alertes(
    destinataires: List[Dict[str, str]],
    chip_id: str,
    statut: str,
    niveau: int,
    pm25: float,
    pm10: float,
):
    """Ouvre une session SMTP unique et envoie les emails aux abonnés."""
    if not destinataires:
        return

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(MAIL_SENDER, MAIL_PASSWORD)

            for user in destinataires:
                msg = EmailMessage()
                msg[
                    "Subject"
                ] = f"⚠️ Alerte Qualité de l'Air - Capteur {chip_id} ({statut})"
                msg["From"] = MAIL_SENDER
                msg["To"] = user["email"]

                msg.set_content(
                    f"Bonjour {user['prenom']} {user['nom']},\n\n"
                    "Une dégradation de la qualité de l'air a été détectée sur "
                    f"votre capteur {user['emplacement']} ({chip_id}) :\n\n"
                    f"• Statut global : {statut} (Niveau {niveau}/6)\n"
                    f"• PM 2.5 : {pm25:.1f} µg/m³\n"
                    f"• PM 10  : {pm10:.1f} µg/m³\n\n"
                    "Pensez à limiter l'aération et à consulter votre tableau de bord."
                )
                server.send_message(msg)
                logger.info(f"Email envoyé à {user['email']} (Capteur: {chip_id})")

    except Exception as e:
        logger.error(f"Échec critique SMTP pour le capteur {chip_id} : {e}")


# Validation CI finale
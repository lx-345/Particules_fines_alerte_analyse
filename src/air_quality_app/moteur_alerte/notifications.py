import os
import smtplib
from email.message import EmailMessage

from .config import MAIL_PASSWORD, MAIL_SENDER, SMTP_PORT, SMTP_SERVER, logger


def envoyer_salve_alertes(
    destinataires: list[dict[str, str]],
    chip_id: str,
    statut: str,
    niveau: int,
    pm25: float,
    pm10: float,
) -> None:
    """Ouvre une session SMTP unique et envoie les emails aux abonnés."""
    if not destinataires:
        return

    # Compatibilité avec MAIL_* (config.py) et SMTP_* (deployment.yaml)
    expediteur = MAIL_SENDER or os.getenv("SMTP_USER")
    mot_de_passe = (MAIL_PASSWORD or os.getenv("SMTP_PASSWORD") or "").replace(" ", "")

    if not expediteur or not mot_de_passe:
        msg_err = "Identifiants SMTP manquants (MAIL_SENDER / SMTP_USER)."
        logger.error(msg_err)
        raise ValueError(msg_err)

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.login(expediteur, mot_de_passe)

            for user in destinataires:
                email_dest = user.get("email", "").strip()
                if not email_dest:
                    continue

                prenom = user.get("prenom", "")
                nom = user.get("nom", "")
                lieu = user.get("emplacement", "Inconnu")

                msg = EmailMessage()
                msg[
                    "Subject"
                ] = f"⚠️ Alerte Qualité de l'Air - Capteur {chip_id} ({statut})"
                msg["From"] = expediteur
                msg["To"] = email_dest

                msg.set_content(
                    f"Bonjour {prenom} {nom},\n\n"
                    "Une dégradation de la qualité de l'air a été "
                    f"détectée sur votre capteur {lieu} ({chip_id}) :\n\n"
                    f"• Statut global : {statut} (Niveau {niveau}/6)\n"
                    f"• PM 2.5 : {pm25:.1f} µg/m³\n"
                    f"• PM 10  : {pm10:.1f} µg/m³\n\n"
                    "Pensez à limiter l'aération et à consulter "
                    "votre tableau de bord."
                )
                server.send_message(msg)
                logger.info(f"Email envoyé à {email_dest} (Capteur: {chip_id})")

    except Exception as e:
        logger.error(f"Échec critique SMTP pour le capteur {chip_id} : {e}")
        raise


# git commit

import os
import smtplib
import sqlite3
from email.mime.text import MIMEText
from pathlib import Path

import pandas as pd
import streamlit as st
from database import (
    DB_PATH,
    ajouter_utilisateur,
    init_db,
    purger_base_de_donnees,
)

from air_quality_app.moteur_alerte.api import (
    calculer_niveau_atmo,
    obtenir_dernieres_mesures,
)


def envoyer_email_smtp(destinataire: str, sujet: str, corps: str) -> tuple[bool, str]:
    """Envoie un e-mail via SMTP_SSL sur le port 465."""
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 465))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_user or not smtp_password:
        return False, "Variables SMTP_USER ou SMTP_PASSWORD manquantes."

    msg = MIMEText(corps)
    msg["Subject"] = sujet
    msg["From"] = smtp_user
    msg["To"] = destinataire

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10) as server:
            server.login(smtp_user, smtp_password.replace(" ", ""))
            server.sendmail(smtp_user, [destinataire], msg.as_string())
        return True, "E-mail envoye !"
    except Exception as e:
        return False, str(e)


def envoyer_email_test(destinataire: str, chip_id: str) -> tuple[bool, str]:
    """Teste la recuperation Madavi et envoie le bilan par e-mail."""
    pm25, pm10, hr, info_date = obtenir_dernieres_mesures(chip_id.strip())

    if pm25 is not None and pm10 is not None:
        niveau, qualite = calculer_niveau_atmo(pm25, pm10)
        hr_txt = f"{hr:.1f} %" if hr is not None else "Non mesuree"
        resume = f"{qualite} ({niveau}/6) | PM2.5: {pm25} | PM10: {pm10}"
        corps_message = (
            f"Bilan qualite de l'air - Capteur {chip_id}\n"
            f"Derniere mesure : {info_date}\n\n"
            f"- Indice ATMO : {niveau}/6 ({qualite})\n"
            f"- PM2.5 (moy. 10 min) : {pm25} ug/m3\n"
            f"- PM10 (moy. 10 min) : {pm10} ug/m3\n"
            f"- Humidite : {hr_txt}\n"
        )
    else:
        resume = f"Aucune donnee Madavi aujourd'hui pour {chip_id}"
        corps_message = (
            f"Test d'alerte pour le capteur {chip_id}\n"
            f"Impossible de recuperer les mesures sur Madavi.\n"
        )

    sujet = f"Test Alerte Air - Capteur {chip_id}"
    ok, msg = envoyer_email_smtp(destinataire, sujet, corps_message)
    return ok, f"{msg} ({resume})" if ok else msg


def simuler_verification_globale(forcer_envoi: bool = True) -> list[str]:
    """Parcourt tous les inscrits de SQLite et déclenche les alertes."""
    journaux = []
    seuil_test = 1 if forcer_envoi else 3

    conn = sqlite3.connect(str(DB_PATH))
    try:
        df_users = pd.read_sql("SELECT * FROM users", conn)
    except Exception as e:
        conn.close()
        return [f"Erreur lecture table users : {e}"]
    conn.close()

    if df_users.empty:
        return ["Aucun utilisateur inscrit dans la base SQLite."]

    for _, user in df_users.iterrows():
        chip_id = str(user.get("numero_capteur", "")).strip()
        email = str(user.get("email", "")).strip()
        prenom = str(user.get("prenom", "Utilisateur"))

        if not chip_id or not email:
            continue

        pm25, pm10, hr, info_date = obtenir_dernieres_mesures(chip_id)
        if pm25 is None or pm10 is None:
            journaux.append(f"Capteur {chip_id} ({email}) : Aucune donnee.")
            continue

        niveau, qualite = calculer_niveau_atmo(pm25, pm10)

        if niveau >= seuil_test:
            hr_txt = f"{hr:.1f} %" if hr is not None else "Non mesuree"
            sujet = f"ALERTE Air {qualite} ({niveau}/6) - Capteur {chip_id}"
            corps = (
                f"Bonjour {prenom},\n\n"
                f"Alerte automatique pour votre capteur {chip_id} "
                f"({info_date}) :\n"
                f"- Indice ATMO : {niveau}/6 ({qualite})\n"
                f"- PM2.5 (moy. 10 min) : {pm25} ug/m3\n"
                f"- PM10 (moy. 10 min) : {pm10} ug/m3\n"
                f"- Humidite : {hr_txt}\n"
            )
            ok, msg = envoyer_email_smtp(email, sujet, corps)
            etat = "E-mail envoye" if ok else f"Erreur SMTP ({msg})"
            journaux.append(
                f"Capteur {chip_id} -> {qualite} ({niveau}/6) : {etat} a {email}"
            )
        else:
            journaux.append(
                f"Capteur {chip_id} -> {qualite} ({niveau}/6) : "
                f"Sous le seuil ({seuil_test}), aucun envoi."
            )

    return journaux


def main():
    st.set_page_config(page_title="Alertes Qualite Air")

    st.title("Alertes Qualite de l'Air")
    st.markdown(
        "Inscrivez-vous pour recevoir un e-mail des que la qualite "
        "de l'air se degrade sur votre capteur."
    )

    init_db()

    with st.form("inscription_form"):
        st.subheader("Vos coordonnees")
        col1, col2 = st.columns(2)
        with col1:
            prenom = st.text_input("Prenom")
        with col2:
            nom = st.text_input("Nom")

        email = st.text_input("Adresse e-mail")

        st.subheader("Votre capteur")
        numero_capteur = st.text_input("Numero du capteur (Chip ID)")
        emplacement = st.selectbox("Emplacement", ["Exterieur", "Interieur"])

        submit = st.form_submit_button("M'inscrire aux alertes")

        if submit:
            if all([prenom, nom, email, numero_capteur]):
                try:
                    ajouter_utilisateur(numero_capteur, prenom, nom, email, emplacement)
                    st.success(
                        "Inscription reussie. Alertes activees pour le "
                        f"capteur {numero_capteur}."
                    )
                except Exception as e:
                    st.error(f"Erreur lors de l'inscription : {e}")
            else:
                st.warning("Veuillez remplir tous les champs obligatoires.")

    st.divider()

    st.subheader("Tester un capteur unitaire (Madavi)")
    col_mail, col_cap = st.columns(2)
    with col_mail:
        email_test = st.text_input(
            "Adresse e-mail :", placeholder="ton.email@gmail.com"
        )
    with col_cap:
        capteur_test = st.text_input(
            "Numero du capteur (Chip ID) :", placeholder="Ex: 14990683"
        )

    if st.button("Tester mon alerte"):
        if not email_test or not capteur_test:
            st.warning("Veuillez saisir un e-mail et un Chip ID.")
        else:
            with st.spinner("Appel de moteur_alerte.api en cours..."):
                succes, message = envoyer_email_test(email_test, capteur_test)
                if succes:
                    st.success(message)
                else:
                    st.error(f"Echec de l'envoi : {message}")

    st.divider()

    if st.checkbox("Afficher le contenu de la base (debug)"):
        conn = sqlite3.connect(str(DB_PATH))

        query_tables = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = pd.read_sql(query_tables, conn)
        st.write("Tables disponibles :", tables)

        try:
            df = pd.read_sql("SELECT id, numero_capteur, prenom FROM users", conn)
            st.dataframe(df)
        except Exception as e:
            st.error(f"Erreur de lecture : {e}")
        finally:
            conn.close()

        st.subheader("Zone de danger (Nettoyage)")
        if st.button("🚨 Vider toute la base de données"):
            try:
                purger_base_de_donnees()
                st.success("La base de données a été entièrement vidée !")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur lors de la purge : {e}")

        st.subheader("Contrôle du moteur d'alerte")
        if st.button("🔓 Réinitialiser le verrou anti-spam (Worker)"):
            try:
                # On crée un fichier "signal" dans le dossier partagé
                dossier_data = Path(os.getenv("DB_DIR", "data"))
                dossier_data.mkdir(exist_ok=True)
                (dossier_data / "reset_spam.flag").touch()
                st.success(
                    "Signal envoyé ! Le worker réinitialisera ses alertes "
                    "à son prochain cycle (dans max 60s)."
                )
            except Exception as e:
                st.error(f"Erreur lors de l'envoi du signal : {e}")

        st.subheader("Simulation du moteur sur la base SQLite")
        forcer = st.checkbox(
            "Forcer l'alerte meme si l'air est Bon (seuil >= 1)", value=True
        )
        if st.button("Lancer la verification sur tous les inscrits"):
            with st.spinner("Verification de tous les inscrits SQLite..."):
                resultats = simuler_verification_globale(forcer_envoi=forcer)
                for ligne in resultats:
                    st.info(ligne)


if __name__ == "__main__":
    main()

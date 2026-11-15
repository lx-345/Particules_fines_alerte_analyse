import os
import smtplib
import sqlite3
from email.mime.text import MIMEText

import pandas as pd
import requests
import streamlit as st
from database import DB_PATH, ajouter_utilisateur, init_db


def recuperer_donnees_capteur(chip_id: str) -> tuple[bool, str]:
    """Recupere les donnees PM2.5 et PM10 via l'API Sensor.Community."""
    url = f"https://data.sensor.community/airrohr/v1/sensor/{chip_id}/"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return False, f"Aucune donnee recente pour le capteur {chip_id}."

        valeurs = data[0].get("sensordatavalues", [])
        mesures = {v["value_type"]: v["value"] for v in valeurs}
        pm25 = mesures.get("P2", "N/A")
        pm10 = mesures.get("P1", "N/A")
        return True, f"PM2.5 : {pm25} µg/m³ | PM10 : {pm10} µg/m³"
    except Exception as e:
        return False, f"Erreur API capteur ({chip_id}) : {e}"


def envoyer_email_test(destinataire: str, chip_id: str) -> tuple[bool, str]:
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 465))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_user or not smtp_password:
        return (
            False,
            "Variables SMTP_USER ou SMTP_PASSWORD manquantes.",
        )

    ok_capteur, infos_air = recuperer_donnees_capteur(chip_id)
    statut = "Connecte" if ok_capteur else "Erreur de connexion"

    corps_message = (
        f"Test d'alerte pour le capteur {chip_id}\n"
        f"Statut API : {statut}\n"
        f"Releve actuel : {infos_air}\n"
    )

    msg = MIMEText(corps_message)
    msg["Subject"] = f"Test Alerte Air - Capteur {chip_id}"
    msg["From"] = smtp_user
    msg["To"] = destinataire

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10) as server:
            server.login(smtp_user, smtp_password.replace(" ", ""))
            server.sendmail(smtp_user, [destinataire], msg.as_string())
        return True, f"E-mail envoye ! ({infos_air})"
    except Exception as e:
        return False, str(e)


def main():
    st.set_page_config(page_title="Alertes Qualite Air")

    st.title("Alertes Qualite de l'Air")
    st.markdown(
        "Inscrivez-vous pour recevoir un e-mail des que la qualite "
        "de l'air se degrade sur votre capteur."
    )

    # Initialisation de la base au chargement de la page
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

    # Section de test d'envoi d'e-mail avec donnees du capteur
    st.subheader("Tester la reception et la connexion au capteur")
    col_mail, col_cap = st.columns(2)
    with col_mail:
        email_test = st.text_input(
            "Adresse e-mail :", placeholder="ton.email@gmail.com"
        )
    with col_cap:
        capteur_test = st.text_input(
            "ID du capteur a tester :", placeholder="Ex: 778803"
        )

    if st.button("Tester mon alerte"):
        if not email_test or not capteur_test:
            st.warning("Veuillez saisir un e-mail et un ID de capteur.")
        else:
            with st.spinner("Recuperation des donnees et envoi en cours..."):
                succes, message = envoyer_email_test(email_test, capteur_test)
                if succes:
                    st.success(message)
                else:
                    st.error(f"Echec de l'envoi : {message}")

    st.divider()

    # Section de debug de la base de donnees
    if st.checkbox("Afficher le contenu de la base (debug)"):
        conn = sqlite3.connect(str(DB_PATH))

        query_tables = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = pd.read_sql(query_tables, conn)
        st.write("Tables disponibles :", tables)

        try:
            df = pd.read_sql("SELECT * FROM users", conn)
            st.dataframe(df)
        except Exception as e:
            st.error(f"Erreur de lecture : {e}")
        finally:
            conn.close()


if __name__ == "__main__":
    main()

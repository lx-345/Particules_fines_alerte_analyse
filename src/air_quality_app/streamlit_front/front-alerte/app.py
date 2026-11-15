import os
import smtplib
import sqlite3
from email.mime.text import MIMEText

import pandas as pd
import streamlit as st
from database import DB_PATH, ajouter_utilisateur, init_db


def envoyer_email_test(destinataire: str) -> tuple[bool, str]:
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_user or not smtp_password:
        return (
            False,
            "Variables SMTP_USER ou SMTP_PASSWORD manquantes sur le serveur.",
        )

    msg = MIMEText("Ceci est un test d'alerte de qualite de l'air depuis Streamlit.")
    msg["Subject"] = "Test Alerte Qualite de l'Air"
    msg["From"] = smtp_user
    msg["To"] = destinataire

    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password.replace(" ", ""))
            server.sendmail(smtp_user, [destinataire], msg.as_string())
        return True, "E-mail envoye avec succes !"
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

    # Section de test d'envoi d'e-mail
    st.subheader("Tester la reception des alertes")
    email_test = st.text_input(
        "Adresse e-mail pour le test :", placeholder="ton.email@gmail.com"
    )

    if st.button("Tester mon alerte"):
        if not email_test:
            st.warning("Veuillez saisir une adresse e-mail.")
        else:
            with st.spinner("Envoi de l'e-mail de test en cours..."):
                succes, message = envoyer_email_test(email_test)
                if succes:
                    st.success(message)
                else:
                    st.error(f"Echec de l'envoi : {message}")

    st.divider()

    # Section de debug de la base de donnees
    if st.checkbox("Afficher le contenu de la base (debug)"):
        # str() evite l'erreur de type avec pathlib
        conn = sqlite3.connect(str(DB_PATH))

        # Requete extraite pour respecter la limite de 88 caracteres
        query_tables = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = pd.read_sql(query_tables, conn)
        st.write("Tables disponibles :", tables)

        try:
            # La table creee dans init_db() s'appelle 'users'
            df = pd.read_sql("SELECT * FROM users", conn)
            st.dataframe(df)
        except Exception as e:
            st.error(f"Erreur de lecture : {e}")
        finally:
            # Garantit la fermeture de la connexion meme en cas d'erreur
            conn.close()


if __name__ == "__main__":
    main()

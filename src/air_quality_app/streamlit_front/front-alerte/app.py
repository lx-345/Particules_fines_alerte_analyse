import sqlite3

import pandas as pd
import streamlit as st
from database import DB_PATH, ajouter_utilisateur, init_db


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
                        "Inscription reussie. Alertes activees pour le capteur "
                        f"{numero_capteur}."
                    )
                except Exception as e:
                    st.error(f"Erreur lors de l'inscription : {e}")
            else:
                st.warning("Veuillez remplir tous les champs obligatoires.")


if __name__ == "__main__":
    main()
if st.checkbox("Afficher le contenu de la base (debug)"):
    # Utilisation de str() pour éviter l'erreur de type avec pathlib
    conn = sqlite3.connect(str(DB_PATH))

    # Extraction de la requête pour aérer le code et respecter les 88 caractères
    query_tables = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql(query_tables, conn)
    st.write("Tables disponibles :", tables)

    try:
        # La table créée dans init_db() s'appelle 'users'
        df = pd.read_sql("SELECT * FROM users", conn)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Erreur de lecture : {e}")
    finally:
        # Le bloc finally garantit que la connexion sera fermée même en cas d'erreur
        conn.close()

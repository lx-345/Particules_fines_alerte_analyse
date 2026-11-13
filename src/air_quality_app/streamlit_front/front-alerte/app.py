import streamlit as st
from database import init_db, ajouter_utilisateur

def main():
    st.set_page_config(page_title="Alertes Qualite Air")
    
    st.title("Alertes Qualite de l'Air")
    st.markdown("Inscrivez-vous pour recevoir un e-mail des que la qualite de l'air se degrade sur votre capteur.")

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
                    st.success(f"Inscription reussie. Alertes activees pour le capteur {numero_capteur}.")
                except Exception as e:
                    st.error(f"Erreur lors de l'inscription : {e}")
            else:
                st.warning("Veuillez remplir tous les champs obligatoires.")

if __name__ == "__main__":
    main()
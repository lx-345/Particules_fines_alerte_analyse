# test_moteur_alerte.py
from air_quality_app.moteur_alerte.api import calculer_niveau_atmo


def test_calculer_niveau_atmo_air_bon():
    # Cas nominal : valeurs très basses
    niveau, statut = calculer_niveau_atmo(5.0, 10.0)
    assert niveau == 1
    assert statut == "Bon"


def test_calculer_niveau_atmo_air_mauvais_pm25_dominant():
    # Cas où le PM2.5 est critique mais le PM10 est bon
    niveau, statut = calculer_niveau_atmo(45.0, 10.0)
    assert niveau >= 4  # Le moteur doit prendre le pire des deux

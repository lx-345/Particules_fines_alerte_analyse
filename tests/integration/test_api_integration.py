import pytest

from src.air_quality_app.moteur_alerte.api import obtenir_dernieres_mesures


@pytest.mark.integration
def test_obtenir_dernieres_mesures_retourne_types_valides():
    """
    Vérifie que la fonction communique bien avec Madavi
    et renvoie la bonne structure.
    """
    pm25, pm10, hr, horodatage = obtenir_dernieres_mesures("14990683")

    # On vérifie la structure (tuple de 4 éléments) et les types
    assert isinstance(pm25, (float, type(None)))
    assert isinstance(pm10, (float, type(None)))
    assert isinstance(hr, (float, type(None)))
    assert isinstance(horodatage, str)

    # Si des données ont été trouvées, on vérifie leur domaine métier (valeurs logiques)
    if pm25 is not None:
        assert pm25 >= 0  # Une concentration ne peut pas être négative
    if pm10 is not None:
        assert pm10 >= 0
    if hr is not None:
        assert 0 <= hr <= 100  # L'humidité est un pourcentage

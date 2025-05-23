from utils import get_distance_from_google
from datetime import datetime

PRIX_CHAUFFEUR_PAR_JOUR = 180

def get_dynamic_questions(responses):
    base_questions = [
        {"key": "departure", "question": "D’où partez-vous ?"},
        {"key": "destination", "question": "Quelle est la destination ?"},
        {"key": "trip_type", "question": "Souhaitez-vous un aller simple ou aller-retour ?"},
        {"key": "departure_date", "question": "Quelle est la date du départ ?"},
    ]

    trip = responses.get("trip_type", "").lower()
    if "aller" in trip and "retour" in trip:
        base_questions.append({"key": "return_date", "question": "Quelle est la date du retour ?"})

    suite = [
        {"key": "passengers", "question": "Combien de personnes voyageront ?"},
        {"key": "group_type", "question": "Quel est le type de groupe ? (scolaire, association, entreprise, autre)"},
        {"key": "special_needs", "question": "Des besoins particuliers ? (PMR, bagages...)"},
        {"key": "email", "question": "À quelle adresse e-mail pouvons-nous envoyer un récapitulatif ?"}
    ]

    return base_questions + suite

def generate_predevis(data):
    try:
        passengers = int(data.get("passengers", 0))
    except (ValueError, TypeError):
        passengers = 0

    departure = data.get("departure", "")
    destination = data.get("destination", "")
    distance_km = get_distance_from_google(departure, destination)

    trip = data.get("trip_type", "").lower()
    if "aller" in trip and "retour" in trip:
        distance_km *= 2

    date_depart_str = data.get("departure_date", "")
    try:
        date_depart = datetime.strptime(date_depart_str, "%Y-%m-%d")
    except ValueError:
        date_depart = datetime.today()

    haute_saison = date_depart.month in [7, 8]
    week_end = date_depart.weekday() in [5, 6]

    saison_multiplier = 1.0
    if haute_saison:
        saison_multiplier += 0.15
    if week_end:
        saison_multiplier += 0.10

    vitesse_moyenne = 80
    duree_base = distance_km / vitesse_moyenne
    pauses = (duree_base // 2) * 0.33
    duree_totale = round(duree_base + pauses, 1)
    nb_chauffeurs = 1 if duree_totale <= 8 else 2

    tarifs = {
        "Classe A": {"Minibus 9": 2.10, "Minibus 20": 2.60, "Autocar 45": 3.20, "Autocar étage 90": 3.90},
        "Classe B": {"Minibus 9": 1.80, "Minibus 20": 2.30, "Autocar 45": 2.80, "Autocar étage 90": 3.40},
        "Classe C": {"Minibus 9": 1.60, "Minibus 20": 2.00, "Autocar 45": 2.40, "Autocar étage 90": 2.90},
    }

    capacites = {
        "Minibus 9": 9,
        "Minibus 20": 20,
        "Autocar 45": 45,
        "Autocar étage 90": 90
    }

    resultats = []

    for classe, tarif_vehicules in tarifs.items():
        devis = {
            "classe": classe,
            "vehicules": [],
            "distance": distance_km,
            "duree": duree_totale,
            "nb_chauffeurs": nb_chauffeurs,
            "frais_chauffeur": PRIX_CHAUFFEUR_PAR_JOUR * nb_chauffeurs,
            "total_ht": 0,
            "description": ""
        }

        if classe == "Classe A":
            devis["description"] = "Premium : sièges inclinables, Wi-Fi, climatisation renforcée, toilettes."
        elif classe == "Classe B":
            devis["description"] = "Standard : climatisation, bons sièges, confort classique."
        else:
            devis["description"] = "Économique : équipement basique, sans options."

        passagers_restants = passengers

        for vehicule, capacite in sorted(capacites.items(), key=lambda x: -x[1]):
            if passagers_restants <= 0:
                break
            nb_vehicules = passagers_restants // capacite
            if passagers_restants % capacite != 0:
                nb_vehicules += 1

            prix_km = tarif_vehicules[vehicule] * saison_multiplier
            cout = round(nb_vehicules * prix_km * distance_km)

            devis["vehicules"].append({
                "type": vehicule,
                "nombre": nb_vehicules,
                "prix_km": round(prix_km, 2),
                "cout": cout
            })

            devis["total_ht"] += cout
            break

        if distance_km < 100:
            devis["forfait_minimum"] = 250
            devis["total_ht"] = max(devis["total_ht"], 250)
        else:
            devis["forfait_minimum"] = 0

        devis["total_ht"] += devis["frais_chauffeur"]
        resultats.append(devis)

    return resultats

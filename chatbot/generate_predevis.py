def generate_predevis(data):
    distance_km = 150  # Distance simulée pour le test
    passengers = int(data.get("passengers", 0))
    jours = 1  # Pour l’instant, on considère 1 jour standard

    tarifs = {
        "Classe A": {
            "Minibus 9": 2.10,
            "Minibus 20": 2.60,
            "Autocar 45": 3.20,
            "Autocar étage 90": 3.90
        },
        "Classe B": {
            "Minibus 9": 1.80,
            "Minibus 20": 2.30,
            "Autocar 45": 2.80,
            "Autocar étage 90": 3.40
        },
        "Classe C": {
            "Minibus 9": 1.60,
            "Minibus 20": 2.00,
            "Autocar 45": 2.40,
            "Autocar étage 90": 2.90
        },
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
            "frais_chauffeur": 180 * jours,
            "total_ht": 0
        }

        passagers_restants = passengers

        for vehicule, capacite in sorted(capacites.items(), key=lambda x: -x[1]):
            if passagers_restants <= 0:
                break
            nb_vehicules = passagers_restants // capacite
            if passagers_restants % capacite != 0:
                nb_vehicules += 1

            prix_km = tarif_vehicules[vehicule]
            cout = nb_vehicules * prix_km * distance_km

            devis["vehicules"].append({
                "type": vehicule,
                "nombre": nb_vehicules,
                "prix_km": prix_km,
                "cout": cout
            })

            devis["total_ht"] += cout
            break  # Choix optimal : on ne prend qu'un type de véhicule ici

        if distance_km < 100:
            devis["forfait_minimum"] = 250
            devis["total_ht"] = max(devis["total_ht"], 250)
        else:
            devis["forfait_minimum"] = 0

        devis["total_ht"] += devis["frais_chauffeur"]
        resultats.append(devis)

    return resultats
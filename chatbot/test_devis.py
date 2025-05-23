from pprint import pprint
from chatbot_logic import generate_predevis

# Exemple de données simulées issues du chatbot
donnees_chatbot = {
    "passengers": "32",
    "departure": "Paris",
    "destination": "Lyon",
    "trip_type": "Aller-retour",
    "departure_date": "2025-06-12",
    "return_date": "2025-06-14"
}

# Appel de la fonction
resultats = generate_predevis(donnees_chatbot)

# Affichage lisible dans la console
print("=== PRÉ-DEVIS (Simulation 150 km) ===\n")
for devis in resultats:
    print(f"Classe : {devis['classe']}")
    print(f"Distance estimée : {devis['distance']} km")
    print("Véhicule(s) proposé(s) :")
    for v in devis["vehicules"]:
        print(f"  - {v['nombre']} x {v['type']} à {v['prix_km']} €/km = {v['cout']:.2f} €")
    print(f"Frais chauffeur : {devis['frais_chauffeur']} €")
    if devis["forfait_minimum"] > 0:
        print(f"Forfait minimum appliqué : {devis['forfait_minimum']} €")
    print(f"➡️ Total HT : {devis['total_ht']:.2f} €")
    print("-" * 40)

def generate_summary(responses):
    return f"""
    📄 Récapitulatif :
    - Départ : {responses['departure']}
    - Destination : {responses['destination']}
    - Trajet : {responses['trip_type']}
    - Date départ : {responses['departure_date']}
    - Date retour : {responses['return_date']}
    - Passagers : {responses['passengers']}
    - Type de groupe : {responses['group_type']}
    - Besoins : {responses['special_needs']}
    - Email : {responses['email']}
    """
import json
from datetime import datetime
import os

def save_request_to_json(responses, filename="data/requests.json"):
    # Crée le dossier data/ s'il n'existe pas
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    responses["timestamp"] = datetime.now().isoformat()
    data.append(responses)

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

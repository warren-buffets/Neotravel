import os
import json
import requests
from datetime import datetime

def generate_summary(responses):
    return_date = responses.get("return_date", "Non applicable")
    return f"""
📄 Récapitulatif :
- Départ : {responses.get('departure')}
- Destination : {responses.get('destination')}
- Trajet : {responses.get('trip_type')}
- Date départ : {responses.get('departure_date')}
- Date retour : {return_date}
- Passagers : {responses.get('passengers')}
- Type de groupe : {responses.get('group_type')}
- Besoins : {responses.get('special_needs')}
- Email : {responses.get('email')}
"""

def save_request_to_json(responses, filename="data/requests.json"):
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

def get_distance_from_google(departure, destination):
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    params = {
        "origins": departure,
        "destinations": destination,
        "key": api_key,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data["status"] == "OK":
            element = data["rows"][0]["elements"][0]
            if element["status"] == "OK":
                distance_meters = element["distance"]["value"]
                return round(distance_meters / 1000, 1)
    except Exception as e:
        print("Erreur Google Maps:", e)

    return 150  # fallback

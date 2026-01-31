import requests
import json

url = "http://localhost:5000/predict"

data = {
    "city": "Casablanca",
    "quartier": "Sidi Maarouf",
    "property_type": "Appartement",
    "surface_m2": 70,
    "num_rooms": 3,
    "num_bathrooms": 1
}

print("📤 Envoi de la requête...")
print(json.dumps(data, indent=2))

try:
    response = requests.post(url, json=data)
    print(f"\n📥 Status Code: {response.status_code}")
    print(f"📥 Réponse:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"❌ Erreur: {e}")
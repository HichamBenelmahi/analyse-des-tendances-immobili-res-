# -*- coding: utf-8 -*-
"""
API Flask pour la prédiction de prix immobiliers au Maroc
Supporte deux modèles : Vente et Location
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
import os

app = Flask(__name__, static_folder='../frontend/out', static_url_path='')
CORS(app)

# ============================================
# CONFIGURATION DES CHEMINS
# ============================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
MODEL_DIR = os.path.join(PROJECT_ROOT, 'models')

print(f"📂 Chemin des modèles : {MODEL_DIR}")



# Variables globales pour les modèles
model_vente = None
model_location = None
target_encoder = None
scaler = None
numeric_features = []
categorical_features = []
all_features_order = []
model_performance_vente = {}
model_performance_location = {}

try:
    # --- MODÈLE VENTE ---
    print("\n📦 Chargement du modèle VENTE...")
    with open(os.path.join(MODEL_DIR, 'gradient_boosting_model.pkl'), 'rb') as f:
        model_vente = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'target_encoder.pkl'), 'rb') as f:
        target_encoder_vente = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'scaler.pkl'), 'rb') as f:
        scaler_vente = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'feature_names.pkl'), 'rb') as f:
        feature_names_vente = pickle.load(f)
    print("✅ Modèle Vente chargé (modèle + encoder + scaler)")
    
    # --- MODÈLE LOCATION ---
    print("\n📦 Chargement du modèle LOCATION...")
    with open(os.path.join(MODEL_DIR, 'model_Location_final_stacking.pkl'), 'rb') as f:
        model_location = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'location_target_encoder.pkl'), 'rb') as f:
        target_encoder_location = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'location_scaler.pkl'), 'rb') as f:
        scaler_location = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'location_feature_names.pkl'), 'rb') as f:
        feature_names_location = pickle.load(f)
    print("✅ Modèle Location chargé (modèle + encoder + scaler)")
    
    # Variables globales (pour compatibilité)
    numeric_features = feature_names_vente.get('numeric_features', [])
    categorical_features = feature_names_vente.get('categorical_features', [])
    all_features_order = numeric_features + categorical_features
    
    # --- PERFORMANCES ---
    print("\n📦 Chargement des performances...")
    perf_vente = pd.read_csv(os.path.join(MODEL_DIR, 'model_performance_summary.csv'))
    model_performance_vente = perf_vente.iloc[0].to_dict()
    print(f"✅ Vente - RMSE: {model_performance_vente.get('rmse_test', 0):,.0f} DH")
    
    perf_location = pd.read_csv(os.path.join(MODEL_DIR, 'location_model_performance_summary.csv'))
    model_performance_location = perf_location.iloc[0].to_dict()
    print(f"✅ Location - RMSE: {model_performance_location.get('rmse_test_dh', 0):,.0f} DH")
    
    print("\n" + "="*60)
    print("✅ TOUS LES MODÈLES SONT PRÊTS !")
    print("="*60)
    
    MODELS_LOADED = True
    
except Exception as e:
    print(f"\n❌ Erreur lors du chargement des modèles : {e}")
    import traceback
    traceback.print_exc()
    MODELS_LOADED = False

# ============================================
# DONNÉES DISPONIBLES
# ============================================
AVG_PRICE_PER_M2 = 28500

AVAILABLE_DATA = {
    'cities': ['Casablanca', 'Marrakech', 'Rabat', 'Tanger'],
    'quartiers': {
        'Casablanca': [
            'Bourgogne Ouest', 'Casablanca Finance City', 'Gauthier', 'Californie',
            'Ain Diab', 'Maârif', 'Anfa', 'Racine', 'Benjdia', 'Centre Ville',
            'Mers Sultan', 'Oasis', 'Sidi Maarouf', 'Hay Hassani', 'Ain Chock',
            'Hay Mohammadi', 'Sidi Moumen', 'Bernoussi', 'Bouskoura', 'Dar Bouazza'
        ],
        'Marrakech': [
            'Agdal', 'Guéliz', 'Hivernage', "Route de l'Ourika", 'Amelkis',
            'Route de Ouarzazate', 'Hay Targa', 'Médina', 'Palmeraie', 'Semlalia'
        ],
        'Rabat': [
            'Agdal', 'Hassan - Centre Ville', 'Souissi', 'Aviation - Mabella',
            'Les Orangers', 'Hay El Menzah', 'Riyad', "L'Ocean", 'Hay Ryad'
        ],
        'Tanger': [
            'Malabata', 'Centre', 'Achakar', 'Marjane', 'Médina', 'Tanja Balia',
            'Californie', 'Boukhalef', 'Mghogha', 'Charf', 'Iberia'
        ]
    },
    'property_types': ['Appartement', 'Villa', 'Maison', 'Riad'],
    'transaction_types': ['vente', 'location']
}

# ============================================
# ENDPOINTS
# ============================================

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/info')
def api_info():
    return jsonify({
        'name': 'API Prédiction Immobilière Maroc',
        'version': '2.0',
        'description': 'Supporte Vente et Location',
        'models': {
            'vente': 'Gradient Boosting',
            'location': 'Stacking Ensemble'
        },
        'status': 'running' if MODELS_LOADED else 'error'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy' if MODELS_LOADED else 'degraded',
        'models_loaded': MODELS_LOADED,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/data')
def get_data():
    return jsonify(AVAILABLE_DATA)

@app.route('/model-info')
def model_info():
    return jsonify({
        'vente': {
            'model_type': 'Gradient Boosting Regressor',
            'r2_test': float(model_performance_vente.get('r2_test', 0)),
            'rmse_test': float(model_performance_vente.get('rmse_test', 0))
        },
        'location': {
            'model_type': 'Stacking Ensemble',
            'r2_test': float(model_performance_location.get('r2_test_log', 0)),
            'rmse_test': float(model_performance_location.get('rmse_test_dh', 0))
        }
    })

@app.route('/predict', methods=['POST'])
def predict():
    if not MODELS_LOADED:
        return jsonify({'error': 'Modèles non chargés'}), 503
    
    try:
        data = request.get_json()
        print(f"\n📥 Données reçues : {data}")
        
        # Extraction des données
        transaction_type = data.get('transaction_type', 'vente').lower()
        city = data['city']
        quartier = data['quartier']
        property_type = data['property_type']
        surface_m2 = float(data['surface_m2'])
        num_rooms = int(data['num_rooms'])
        num_bathrooms = int(data['num_bathrooms'])
        
        print(f"📊 Transaction: {transaction_type.upper()}")
        print(f"✅ {city}, {quartier}, {surface_m2}m², {num_rooms}ch, {num_bathrooms}sdb")
        
        # Sélection du modèle et des encodeurs selon le type de transaction
        if transaction_type == 'location':
            model = model_location
            target_encoder = target_encoder_location
            scaler = scaler_location
            features_dict = feature_names_location
            performance = model_performance_location
            rmse_key = 'rmse_test_dh'
            print("🔄 Utilisation du modèle LOCATION")
        else:
            model = model_vente
            target_encoder = target_encoder_vente
            scaler = scaler_vente
            features_dict = feature_names_vente
            performance = model_performance_vente
            rmse_key = 'rmse_test'
            print("🔄 Utilisation du modèle VENTE")
        
        # Features pour ce modèle
        num_features = features_dict.get('numeric_features', numeric_features)
        cat_features = features_dict.get('categorical_features', categorical_features)
        all_features = num_features + cat_features
        
        # Créer le DataFrame
        new_data = pd.DataFrame({
            'city': [city],
            'quartier': [quartier],
            'property_type': [property_type],
            'surface_m2': [surface_m2],
            'num_rooms': [num_rooms],
            'num_bathrooms': [num_bathrooms]
        })
        
        # Feature Engineering
        new_data['surface_rooms'] = new_data['surface_m2'] * new_data['num_rooms']
        new_data['bathrooms_rooms_ratio'] = new_data['num_bathrooms'] / (new_data['num_rooms'] + 1)
        new_data['total_rooms'] = new_data['num_rooms'] + new_data['num_bathrooms']
        new_data['surface_per_room'] = new_data['surface_m2'] / (new_data['total_rooms'] + 1)
        new_data['price_per_m2'] = AVG_PRICE_PER_M2 if transaction_type == 'vente' else 80
        
        # Préparer les features
        new_features = new_data[all_features].copy()
        
        # Target Encoding
        new_features[cat_features] = target_encoder.transform(
            new_features[cat_features]
        )
        
        # Standardisation
        new_features[num_features] = scaler.transform(
            new_features[num_features]
        )
        
        # Prédiction
        prediction = float(model.predict(new_features)[0])
        
        # Pour location, le modèle peut prédire en log, convertir si nécessaire
        if transaction_type == 'location' and prediction < 100:
            # Si la prédiction semble être en log (petit nombre)
            prediction = np.exp(prediction)
        
        print(f"💰 Prédiction: {prediction:,.2f} DH")
        
        if prediction < 0:
            return jsonify({'error': 'Prédiction négative invalide'}), 400
        
        # Calcul de l'intervalle de confiance
        rmse = float(performance.get(rmse_key, 0))
        
        # Construction de la réponse
        response = {
            'success': True,
            'transaction_type': transaction_type,
            'prediction': {
                'price_dh': round(prediction, 2),
                'price_millions': round(prediction / 1_000_000, 2),
                'price_per_m2': round(prediction / surface_m2, 2),
                'confidence_interval': {
                    'min': round(max(0, prediction - rmse), 2),
                    'max': round(prediction + rmse, 2),
                    'margin': round(rmse, 2)
                }
            },
            'input': data
        }
        
        if transaction_type == 'location':
            # Pour location, ajouter le prix mensuel
            response['prediction']['price_monthly'] = round(prediction, 2)
            response['prediction']['price_dh'] = round(prediction, 2)
            response['prediction']['price_millions'] = None  # Pas pertinent pour location
        
        print(f"✅ Réponse envoyée\n")
        return jsonify(response), 200
        
    except KeyError as e:
        print(f"❌ Champ manquant : {e}")
        return jsonify({'error': f'Champ manquant: {str(e)}'}), 400
    except Exception as e:
        print(f"❌ ERREUR : {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ============================================
# ENDPOINTS STATISTIQUES
# ============================================

# Charger les données pour les stats
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'clean_data')
df_vente = None
df_location = None

# Fonction de chargement et nettoyage robuste
def load_and_clean_data(filepath, source_type='vente'):
    try:
        if not os.path.exists(filepath):
            print(f"⚠️ Fichier introuvable: {filepath}")
            return None
            
        df = pd.read_csv(filepath)
        
        # Standardisation des colonnes
        col_mapping = {
            'ville': 'city', 
            'prix': 'price', 
            'surface': 'surface_m2',
            'quartier': 'quartier'
        }
        df = df.rename(columns=col_mapping)
        
        # Vérification des colonnes requises
        required_cols = ['city', 'price', 'surface_m2']
        if not all(col in df.columns for col in required_cols):
            print(f"⚠️ Colonnes manquantes dans {filepath}. Colonnes: {df.columns.tolist()}")
            return None

        # Nettoyage numérique
        for col in ['price', 'surface_m2']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Suppression des NaNs
        df_clean = df.dropna(subset=['price', 'surface_m2', 'city'])
        total_count = len(df_clean)
        
        # Filtrage des outliers POUR LES MOYENNES (Copie du DF)
        df_stats = df_clean.copy()
        
        if source_type == 'vente':
            # Prix entre 100k et 50M DH
            df_stats = df_stats[(df_stats['price'] > 100000) & (df_stats['price'] < 50000000)]
        else:
            # Loyer entre 500 et 50k DH
            df_stats = df_stats[(df_stats['price'] > 500) & (df_stats['price'] < 50000)]
            
        # Surface entre 10 et 1000 m²
        df_stats = df_stats[(df_stats['surface_m2'] > 10) & (df_stats['surface_m2'] < 1000)]
        
        print(f"✅ {source_type.upper()} chargé: {total_count} annonces (dont {len(df_stats)} retenues pour stats)")
        
        # On retourne le DF nettoyé (sans NaNs) mais avec outliers pour le compte, 
        # et on attachera les stats calculées sur df_stats
        return df_clean, df_stats
        
    except Exception as e:
        print(f"❌ Erreur chargement {filepath}: {e}")
        return None, None

try:
    vente_path = os.path.join(DATA_DIR, 'annonces_nettoyees_mubawab.csv')
    df_vente, df_vente_stats = load_and_clean_data(vente_path, 'vente')
    
    location_path = os.path.join(DATA_DIR, 'location_all_sources.csv')
    df_location, df_location_stats = load_and_clean_data(location_path, 'location')
    
except Exception as e:
    print(f"⚠️ Erreur chargement données stats: {e}")

# Fonction pour filtrer les textes en arabe
def is_latin_text(text):
    """Vérifie si le texte contient principalement des caractères latins"""
    if not text or not isinstance(text, str):
        return False
    latin_chars = sum(1 for c in text if c.isascii() or c in 'éèêëàâäùûüôöîïç')
    return latin_chars / max(len(text), 1) > 0.5

def filter_cities(cities_list):
    """Filtre les villes pour ne garder que celles en caractères latins"""
    return [city for city in cities_list if is_latin_text(city)]

@app.route('/stats/summary')
def stats_summary():
    """Résumé global des statistiques"""
    result = {
        'vente': {},
        'location': {},
        'cities': []
    }
    
    if df_vente is not None and df_vente_stats is not None:
        result['vente'] = {
            'count': int(len(df_vente)), # Total sans NaNs
            'prix_moyen': float(df_vente_stats['price'].mean()), # Moyenne sur données filtrées
            'prix_m2_moyen': float(df_vente_stats['price'].mean() / df_vente_stats['surface_m2'].mean()) if 'surface_m2' in df_vente_stats.columns else 0,
            'surface_moyenne': float(df_vente_stats['surface_m2'].mean()) if 'surface_m2' in df_vente_stats.columns else 0
        }
        result['cities'] = filter_cities(df_vente['city'].dropna().unique().tolist())
    
    if df_location is not None and df_location_stats is not None:
        result['location'] = {
            'count': int(len(df_location)), # Total sans NaNs
            'prix_moyen': float(df_location_stats['price'].mean()), # Moyenne sur données filtrées
            'prix_m2_moyen': float(df_location_stats['price'].mean() / df_location_stats['surface_m2'].mean()) if 'surface_m2' in df_location_stats.columns else 0,
            'surface_moyenne': float(df_location_stats['surface_m2'].mean()) if 'surface_m2' in df_location_stats.columns else 0
        }
        # Combiner les villes (filtrées)
        if df_vente is not None:
            all_cities = set(result['cities']) | set(filter_cities(df_location['city'].dropna().unique().tolist()))
            result['cities'] = sorted(list(all_cities))
    
    return jsonify(result)

@app.route('/stats/city/<city>')
def stats_city(city):
    """Statistiques pour une ville"""
    result = {
        'city': city,
        'vente': None,
        'location': None,
        'quartiers': []
    }
    
    if df_vente is not None:
        city_data = df_vente[df_vente['city'].str.lower() == city.lower()]
        if len(city_data) > 0:
            result['vente'] = {
                'count': int(len(city_data)),
                'prix_moyen': float(city_data['price'].mean()),
                'prix_min': float(city_data['price'].min()),
                'prix_max': float(city_data['price'].max()),
                'prix_m2_moyen': float(city_data['price'].mean() / city_data['surface_m2'].mean()) if 'surface_m2' in city_data.columns else 0,
                'surface_moyenne': float(city_data['surface_m2'].mean()) if 'surface_m2' in city_data.columns else 0
            }
            if 'quartier' in city_data.columns:
                quartiers = city_data['quartier'].dropna().unique().tolist()
                result['quartiers'] = sorted(quartiers)
    
    if df_location is not None:
        city_data = df_location[df_location['city'].str.lower() == city.lower()]
        if len(city_data) > 0:
            result['location'] = {
                'count': int(len(city_data)),
                'prix_moyen': float(city_data['price'].mean()),
                'prix_min': float(city_data['price'].min()),
                'prix_max': float(city_data['price'].max()),
                'prix_m2_moyen': float(city_data['price'].mean() / city_data['surface_m2'].mean()) if 'surface_m2' in city_data.columns else 0,
                'surface_moyenne': float(city_data['surface_m2'].mean()) if 'surface_m2' in city_data.columns else 0
            }
            if 'quartier' in city_data.columns:
                quartiers_loc = city_data['quartier'].dropna().unique().tolist()
                result['quartiers'] = sorted(list(set(result['quartiers']) | set(quartiers_loc)))
    
    return jsonify(result)

@app.route('/stats/quartiers/<city>')
def stats_quartiers(city):
    """Statistiques par quartier pour une ville (pour graphiques)"""
    result = {
        'city': city,
        'vente': [],
        'location': []
    }
    
    if df_vente is not None and 'quartier' in df_vente.columns:
        city_data = df_vente[df_vente['city'].str.lower() == city.lower()]
        quartier_stats = city_data.groupby('quartier').agg({
            'price': ['count', 'mean']
        }).reset_index()
        quartier_stats.columns = ['quartier', 'count', 'prix_moyen']
        quartier_stats = quartier_stats.sort_values('prix_moyen', ascending=False).head(10)
        result['vente'] = quartier_stats.to_dict(orient='records')
    
    if df_location is not None and 'quartier' in df_location.columns:
        city_data = df_location[df_location['city'].str.lower() == city.lower()]
        quartier_stats = city_data.groupby('quartier').agg({
            'price': ['count', 'mean']
        }).reset_index()
        quartier_stats.columns = ['quartier', 'count', 'prix_moyen']
        quartier_stats = quartier_stats.sort_values('prix_moyen', ascending=False).head(10)
        result['location'] = quartier_stats.to_dict(orient='records')
    
    return jsonify(result)

# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏠 API Prédiction Immobilière Maroc v2.0")
    print("="*60)
    print("📍 URL : http://localhost:5000")
    print("📦 Modèles : Vente + Location")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
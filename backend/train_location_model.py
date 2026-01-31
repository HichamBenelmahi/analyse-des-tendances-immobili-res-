"""
Script pour réentraîner le modèle de location
Compatible avec la version actuelle de numpy/scikit-learn
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from category_encoders import TargetEncoder
from datetime import datetime

# Chemins
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'clean_data')
MODEL_DIR = os.path.join(PROJECT_ROOT, 'models')

print("="*60)
print("🏠 ENTRAINEMENT DU MODÈLE LOCATION")
print("="*60)

# Charger les données
data_path = os.path.join(DATA_DIR, 'location_ready_for_ml.csv')
print(f"\n📂 Chargement : {data_path}")
df = pd.read_csv(data_path)
print(f"✅ {len(df)} lignes chargées")
print(f"📊 Colonnes : {list(df.columns)}")

# Renommer les colonnes (exact match from dataset)
df = df.rename(columns={
    'ville': 'city',
    'prix': 'price',
    'surface': 'surface_m2',
    'nb_chambres': 'num_rooms',
    'nb_salle_de_bain': 'num_bathrooms',
    'type_bien': 'property_type'
})
print(f"✅ Colonnes renommées : {list(df.columns)}")

# Feature Engineering
print("\n🔧 Feature Engineering...")
df['surface_rooms'] = df['surface_m2'] * df['num_rooms']
df['total_rooms'] = df['num_rooms'] + df['num_bathrooms']
df['surface_per_room'] = df['surface_m2'] / (df['total_rooms'] + 1)
df['bathrooms_rooms_ratio'] = df['num_bathrooms'] / (df['num_rooms'] + 1)
df['price_per_m2'] = 80  # Prix moyen location

# Définir les features
numeric_features = ['surface_m2', 'num_rooms', 'num_bathrooms', 'surface_rooms', 
                    'bathrooms_rooms_ratio', 'total_rooms', 'surface_per_room', 'price_per_m2']
categorical_features = ['city', 'quartier', 'property_type']

# Nettoyer les données
print("\n🧹 Nettoyage...")
df = df.dropna(subset=['price', 'surface_m2', 'city'])
df = df[df['price'] > 0]
df = df[df['surface_m2'] > 0]
df = df[(df['price'] >= 500) & (df['price'] <= 100000)]

print(f"✅ {len(df)} lignes après nettoyage")
print(f"📊 Prix : min={df['price'].min():.0f}, max={df['price'].max():.0f}, mean={df['price'].mean():.0f}")

# Préparer X et y
X = df[numeric_features + categorical_features].copy()
y = df['price'].copy()

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"\n🔀 Train: {len(X_train)}, Test: {len(X_test)}")

# Target Encoding
print("\n🔄 Target Encoding...")
encoder = TargetEncoder(cols=categorical_features)
X_train[categorical_features] = encoder.fit_transform(X_train[categorical_features], y_train)
X_test[categorical_features] = encoder.transform(X_test[categorical_features])

# Standardisation
print("🔄 Standardisation...")
scaler = StandardScaler()
X_train[numeric_features] = scaler.fit_transform(X_train[numeric_features])
X_test[numeric_features] = scaler.transform(X_test[numeric_features])

# Entraînement
print("\n🏋️ Entraînement Gradient Boosting...")
model = GradientBoostingRegressor(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42,
    verbose=1
)

model.fit(X_train, y_train)
print("✅ Modèle entraîné !")

# Évaluation
y_pred_test = model.predict(X_test)
r2_test = r2_score(y_test, y_pred_test)
rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
mae_test = mean_absolute_error(y_test, y_pred_test)

print(f"\n📈 Résultats : R²={r2_test:.4f}, RMSE={rmse_test:,.0f} DH, MAE={mae_test:,.0f} DH")

# Sauvegarder
print("\n💾 Sauvegarde...")

with open(os.path.join(MODEL_DIR, 'location_model.pkl'), 'wb') as f:
    pickle.dump(model, f)
print("✅ location_model.pkl")

with open(os.path.join(MODEL_DIR, 'location_target_encoder.pkl'), 'wb') as f:
    pickle.dump(encoder, f)
print("✅ location_target_encoder.pkl")

with open(os.path.join(MODEL_DIR, 'location_scaler.pkl'), 'wb') as f:
    pickle.dump(scaler, f)
print("✅ location_scaler.pkl")

with open(os.path.join(MODEL_DIR, 'location_feature_names.pkl'), 'wb') as f:
    pickle.dump({'numeric_features': numeric_features, 'categorical_features': categorical_features}, f)
print("✅ location_feature_names.pkl")

perf_df = pd.DataFrame([{
    'model_name': 'GradientBoosting_Location',
    'r2_test': r2_test, 'rmse_test_dh': rmse_test, 'mae_test_dh': mae_test,
    'date_training': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}])
perf_df.to_csv(os.path.join(MODEL_DIR, 'location_model_performance_summary.csv'), index=False)
print("✅ location_model_performance_summary.csv")

print("\n" + "="*60)
print("✅ MODÈLE LOCATION PRÊT !")
print("="*60)

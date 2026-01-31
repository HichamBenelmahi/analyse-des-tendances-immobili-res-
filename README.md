# 🏠 ImmoPredict Maroc

**Application d'Estimation Immobilière Basée sur l'IA au Maroc**

![ImmoPredict Banner](https://via.placeholder.com/1200x600/F97316/FFFFFF?text=ImmoPredict+Maroc)

## 📋 À Propos
ImmoPredict Maroc est une application full-stack moderne permettant d'estimer le prix de vente ou le loyer mensuel d'un bien immobilier au Maroc (Appartement, Villa, Maison, Riad).

L'application utilise des modèles de **Machine Learning** entraînés sur des milliers d'annonces réelles (Source: Avito, Mubawab) pour fournir des estimations précises basées sur la ville, le quartier, la surface et les caractéristiques du bien.

## ✨ Fonctionnalités Clés

### 🧠 Intelligence Artificielle
- **Modèle Vente** : Gradient Boosting Regressor (Précision ~92%)
- **Modèle Location** : Stacking Ensemble (Précision ~94%)
- **Estimation Instantanée** : Prix de vente ou loyer mensuel

### 🎨 Interface Utilisateur Premium
- **Conversational UI** : Interface type "Chatbot" pour une saisie fluide
- **Theme Adaptatif** : Mode Sombre (Dark) & Clair (Light)
- **Design Moderne** : Glassmorphism, Animations Fluides, Composants Custom
- **Visualisation** : Graphiques interactifs des prix par quartier

### 📊 Statistiques & Données
- **Analyse de Marché** : Prix moyen, surface moyenne, prix/m² par ville
- **Filtrage Intelligent** : Exclusion automatique des données aberrantes (Outliers)
- **Sources Fiables** : Données nettoyées provenant des plateformes leaders

## 🛠️ Stack Technique

### Frontend
- **Framework** : Next.js 14 (App Router)
- **Langage** : TypeScript
- **Styling** : Tailwind CSS + Framer Motion
- **Charts** : Recharts

### Backend
- **Framework** : Flask (Python)
- **ML** : Scikit-learn, Pandas, NumPy
- **API** : RESTful endpoints

## 🚀 Installation & Démarrage

### Pré-requis
- Python 3.8+
- Node.js 18+

### 1. Backend (API & Modèles)
```bash
cd backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur Flask
python app.py
```
*Le serveur démarrera sur http://localhost:5000*

### 2. Frontend (Interface)
```bash
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev
```
*L'application sera accessible sur http://localhost:3000*

## 📁 Structure du Projet

```
analyse-des-tendances-immobili-res-/
├── backend/
│   ├── models/            # Modèles ML (.pkl)
│   ├── app.py             # API Flask
│   └── train_model.py     # Scripts d'entraînement
├── frontend/
│   ├── src/
│   │   ├── app/           # Pages Next.js
│   │   ├── components/    # Composants React (ChatInterface, StatsSection...)
│   │   └── lib/           # Utilitaires API
│   └── public/            # Assets
└── data/                  # Datasets (nettoyés et bruts)
```

## 🤝 Contribution
Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une PR.

## 📄 Licence
Ce projet est sous licence MIT.
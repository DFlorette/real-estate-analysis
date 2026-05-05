## 🔍 Rôle de chaque partie
📂 data/
- raw/ : données originales (ex : Demandes de valeurs foncières)
- processed/ : nettoyées
- external/ : enrichissements (ex : Base Adresse Nationale)

👉 ⚠️ ne jamais modifier raw/

📂 notebooks/
👉 pour explorer et tester

Mais :  
- pas de logique métier critique dedans
- juste exploration / visualisation



# Analyse immobilière France

## Objectif
Identifier les zones sous-évaluées

## Données
- DVF
- BAN

## Méthodologie
- Chargement de données
- Nettoyage
- Feature engineering
- Analyse

## Résultats
- top villes sous-évaluées
- facteurs clés

## Run project
pip install -r requirements.txt
python main.py

## API
uvicorn api.app:app --reload

## Results
- Price per m² analysis
- Outlier detection
- Investment insights
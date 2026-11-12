# Qui va gagner la Coupe du monde 2030 ?

Projet IA/Data réalisé en binôme par Godonou Joseph et SELMAN Marjane.

## Objectif
Prédire si une équipe nationale gagne son match, puis pronostiquer la Coupe du monde 2030.

## Données
Source : https://github.com/martj42/international_results
(résultats de matchs internationaux depuis 1872, Coupe du monde 2026 incluse).

Détails des choix (fichiers retenus, période depuis 1990, nuls = non-victoire) : [docs/donnees.md](docs/donnees.md).

## Installation
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Préparer les données
À lancer depuis la racine du projet, avec l'environnement virtuel activé :
```powershell
python -m src.data
```
Cette commande :
1. télécharge les fichiers bruts dans `data/raw/` (`src/datadownload.py`) ;
2. nettoie les matchs (dates, doublons, anciens noms de pays, période >= 1990) ;
3. crée une ligne par équipe et par match, avec la cible `win` (1 = victoire, 0 = nul ou défaite) ;
4. vérifie la cohérence des données ;
5. enregistre `data/processed/matches_clean.csv` et `data/processed/team_matches.csv`.

Pour ne faire que le téléchargement : `python -m src.datadownload`.

## Explorer les données
Notebook : `notebooks/data.ipynb`.

## Lancer le dashboard
```powershell
streamlit run app/app.py
```
(à venir)

## Structure du projet
```
data/raw/        données brutes téléchargées (non versionnées)
data/processed/  données nettoyées (générées, non versionnées)
notebooks/       exploration
src/             collecte, nettoyage, variables, modèles
app/             dashboard Streamlit
docs/            documentation et démarche
```

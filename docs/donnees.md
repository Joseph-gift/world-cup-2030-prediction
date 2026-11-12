# Données et préparation (Étape 1)

## 1. Sources

Toutes les données viennent du dépôt public
[martj42/international_results](https://github.com/martj42/international_results)
(résultats de matchs internationaux de football depuis 1872, Coupe du monde 2026 incluse).
Elles sont téléchargées automatiquement par `src/datadownload.py` (aucune saisie manuelle)
dans `data/raw/`, qui n'est jamais modifié ni versionné.

| Fichier | Statut | Raison |
|---|---|---|
| `results.csv` | **Utilisé** | 49 940 matchs : date, équipes, scores, tournoi, lieu, terrain neutre. Base de la cible et des variables. |
| `former_names.csv` | **Utilisé** | Anciens noms de pays (Zaïre, Upper Volta…) ramenés au nom actuel pendant la bonne période, pour ne pas couper l'historique d'une équipe en deux. |
| `shootouts.csv` | **Téléchargé, gardé pour plus tard** | Il donne le vainqueur des matchs nuls décidés aux tirs au but. Inutile pour prédire « victoire ou non » dans le temps réglementaire, mais indispensable pour la simulation de la Coupe du monde 2030 (phases à élimination directe : il faut un vainqueur). |
| `goalscorers.csv` | **Écarté** | Les buteurs ne sont connus qu'après le match : les utiliser pour prédire ce match serait une **fuite de données**. Fichier volumineux et sans lien avec la cible « victoire / pas victoire ». |

## 2. Période retenue : depuis 1990

Nous gardons uniquement les matchs à partir du 1er janvier 1990 (32 821 matchs sur 49 940, soit
65 642 lignes équipe-match). Raisons :

- Le football de 1872-1989 n'est pas comparable à celui d'aujourd'hui (règles, nombre d'équipes,
  niveau, professionnalisation, calendrier).
- La forme récente d'une équipe n'a pas de sens si l'on mélange des époques différentes.
- Les noms de pays changent beaucoup avant 1990, ce qui fragilise le nettoyage : 26 des 36 lignes
  de `former_names.csv` se terminent avant 1990. Les 10 autres (Russie, Serbie, Tchécoslovaquie,
  RD Congo, Eswatini, Macédoine du Nord, Curaçao, Samoa) concernent encore des matchs après 1990
  et sont bien corrigées par `clean_matches`.
- 1990 laisse plus de 30 ans de données : largement assez pour entraîner et tester un modèle.

Le paramètre `START_YEAR` de `src/data.py` permet de changer ce choix facilement.

## 3. Nettoyage (`src/data.py`)

1. Conversion de `date` en vrai format date.
2. Suppression des matchs sans score et des doublons (aucun trouvé dans les données brutes).
3. Remplacement des anciens noms de pays par le nom actuel, uniquement pendant la période concernée.
4. Filtre sur la période (>= 1990).
5. Tri chronologique : indispensable pour que les variables de forme (Étape 3) n'utilisent que le passé.

## 4. Table équipe-match et cible

Chaque match devient **deux lignes** (une par équipe), avec `goals_for`, `goals_against`,
`is_home`, `neutral`, `tournament` et `match_id` (qui relie les deux lignes d'un même match).

- `is_home = 1` seulement pour l'équipe à domicile sur un terrain **non neutre**. Sur terrain neutre,
  aucune des deux équipes n'a l'avantage du terrain (`is_home = 0` pour les deux).
- **Cible `win`** : 1 si `goals_for > goals_against`, **0 sinon**. Un match nul vaut donc
  **non-victoire**, comme le demande le sujet (« gagne ou non »).
  Le score est celui du temps de jeu (prolongation comprise), sans les tirs au but.

## 5. Contrôles de cohérence (`check_data`)

- exactement 2 lignes par match (65 642 = 2 × 32 821) ;
- `win` ne vaut que 0 ou 1 ;
- aucun score négatif, aucune valeur manquante ;
- dates triées ;
- nombre de victoires = nombre de matchs non nuls (une victoire d'un côté = une défaite de l'autre).

## 6. Premiers constats (voir `notebooks/data.ipynb`)

| Lieu | Taux de victoire | Lignes |
|---|---|---|
| Domicile | 50,7 % | 23 494 |
| Extérieur | 25,9 % | 23 494 |
| Terrain neutre | 38,2 % | 18 654 |

- Taux de victoire global : **38,3 %**. Part de nuls : **23,5 %** (= 1 − 2 × 38,3 %).
- Le groupement par `neutral` seul ne montre rien d'utile : comme chaque match donne une victoire et
  une défaite, la moyenne vaut toujours (1 − part de nuls) / 2. D'où la colonne `venue`
  (domicile / extérieur / neutre).
- **Modèle de référence** : prédire toujours « ne gagne pas » donne déjà **61,7 %** d'accuracy.
  Un modèle de machine learning doit faire mieux, et l'accuracy seule ne suffit pas
  (on regardera aussi la matrice de confusion, la précision et le rappel).

## 7. Limites déjà identifiées

- Les nuls sont regroupés avec les défaites : la cible mélange deux situations différentes.
- Le niveau des adversaires varie beaucoup (matchs amicaux, qualifications) : à corriger plus tard
  avec un classement Elo.
- Les données ne contiennent ni blessures, ni compositions, ni enjeu réel du match.

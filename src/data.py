import pandas as pd

from src.datadownload import RAW_DIR, download_data

PROCESSED_DIR = RAW_DIR.parent / "processed"
START_YEAR = 1990  # football moderne : on ignore les matchs plus anciens


def load_raw():
    results = pd.read_csv(RAW_DIR / "results.csv")
    former_names = pd.read_csv(RAW_DIR / "former_names.csv")
    return results, former_names


def clean_matches(results, former_names, start_year=START_YEAR):
    df = results.copy()

    # 1. Dates en vrai format date
    df["date"] = pd.to_datetime(df["date"])

    # 2. Matchs sans score (non joués) et doublons
    df = df.dropna(subset=["home_score", "away_score"])
    df = df.drop_duplicates()
    df[["home_score", "away_score"]] = df[["home_score", "away_score"]].astype(int)

    # 3. Anciens noms de pays -> nom actuel, uniquement pendant la période concernée
    fn = former_names.copy()
    fn["start_date"] = pd.to_datetime(fn["start_date"])
    fn["end_date"] = pd.to_datetime(fn["end_date"])
    for _, row in fn.iterrows():
        in_period = (df["date"] >= row["start_date"]) & (df["date"] <= row["end_date"])
        for col in ["home_team", "away_team"]:
            df.loc[in_period & (df[col] == row["former"]), col] = row["current"]

    # 4. Filtre de période
    df = df[df["date"].dt.year >= start_year]

    # 5. Tri chronologique (indispensable pour les variables de forme de l'étape 3)
    df = df.sort_values("date", kind="stable").reset_index(drop=True)
    return df


def to_team_matches(matches):
    """Une ligne par équipe et par match."""
    m = matches.copy()
    m["match_id"] = m.index
    neutral = m["neutral"].astype(int)

    home = pd.DataFrame({
        "match_id": m["match_id"],
        "date": m["date"],
        "team": m["home_team"],
        "opponent": m["away_team"],
        "goals_for": m["home_score"],
        "goals_against": m["away_score"],
        "is_home": 1 - neutral,   # avantage du terrain seulement si le match n'est pas neutre
        "neutral": neutral,
        "tournament": m["tournament"],
    })
    away = pd.DataFrame({
        "match_id": m["match_id"],
        "date": m["date"],
        "team": m["away_team"],
        "opponent": m["home_team"],
        "goals_for": m["away_score"],
        "goals_against": m["home_score"],
        "is_home": 0,
        "neutral": neutral,
        "tournament": m["tournament"],
    })

    team_df = pd.concat([home, away], ignore_index=True)
    team_df = team_df.sort_values(["date", "match_id"], kind="stable").reset_index(drop=True)

    # Cible : 1 = victoire, 0 = nul ou défaite
    team_df["win"] = (team_df["goals_for"] > team_df["goals_against"]).astype(int)
    return team_df


def check_data(matches, team_df):
    """Contrôles de cohérence."""
    assert len(team_df) == 2 * len(matches), "2 lignes attendues par match"
    assert team_df.groupby("match_id").size().eq(2).all(), "chaque match doit apparaître 2 fois"
    assert team_df["win"].isin([0, 1]).all(), "win doit valoir 0 ou 1"
    assert (team_df[["goals_for", "goals_against"]] >= 0).all().all(), "scores négatifs"
    assert team_df.isna().sum().sum() == 0, "valeurs manquantes"
    assert team_df["date"].is_monotonic_increasing, "dates non triées"
    # une victoire d'un côté = une défaite de l'autre ; les nuls n'ont aucun gagnant
    assert team_df["win"].sum() == (matches["home_score"] != matches["away_score"]).sum()
    print("Contrôles OK")


def build_dataset():
    download_data()
    results, former_names = load_raw()
    matches = clean_matches(results, former_names)
    team_df = to_team_matches(matches)
    check_data(matches, team_df)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    matches.to_csv(PROCESSED_DIR / "matches_clean.csv", index=False)
    team_df.to_csv(PROCESSED_DIR / "team_matches.csv", index=False)
    print(f"{len(matches)} matchs -> {len(team_df)} lignes équipe-match")
    return matches, team_df


if __name__ == "__main__":
    build_dataset()
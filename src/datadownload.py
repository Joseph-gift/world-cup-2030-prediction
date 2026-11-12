import requests 
import pandas as pd
from pathlib import Path

base = "https://raw.githubusercontent.com/martj42/international_results/master/"
fichiers_csv = ["former_names.csv", "goalscorers.csv", "results.csv", "shootouts.csv"]

Path("dataraw").mkdir(exist_ok=True)

for f in fichiers_csv:
    df = pd.read_csv(base + f)
    df.to_csv(f"dataraw/{f}", index=False)
    print(f, df.shape)
from os import path
from pathlib import Path
import requests

BASE_URL = "https://raw.githubusercontent.com/martj42/international_results/master/"
FILES = ["results.csv", "former_names.csv", "shootouts.csv"]
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def download_data():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        response = requests.get(BASE_URL + name, timeout=30)
        response.raise_for_status()
        (RAW_DIR/name).write_bytes(response.content)
        print(f"{name} téléchargé ({len(response.content) / 1e6:.1f} Mo)")


if __name__ == "__main__":
    download_data()
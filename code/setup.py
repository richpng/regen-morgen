import requests
from urllib3 import disable_warnings
from pathlib import Path
import os

disable_warnings()

def get_PLZ_coordinates_file():
    parent_dir = Path(__file__).parent
    if (parent_dir /"data"/"PLZ.csv").exists():
        return
    result = requests.get("https://symerio.github.io/postal-codes-data/data/geonames/DE.txt", verify=False)
    if not os.path.exists(parent_dir/"data"):
        os.mkdir(parent_dir/"data")
    with open(parent_dir /"data"/"PLZ.csv", "bw") as file:
        file.write(result.content)

def fix_encoding(content:str):
    corrected = content
    ENCODING_FIXES = {
    # Basis-Umlaute
    "Ã¼": "ü",        # für, über
    "Ã¤": "ä",        # später, wählen
    "Ã¶": "ö",        # können, löschen
    "ÃŸ": "ß",        # Grüße, Fußbereich
    "ÃƒÂ¼": "ü",      # über, für, zurück
    "ÃƒÂ¤": "ä",      # wählen, später, erfüllt
    }
    for x in ENCODING_FIXES:
        corrected = corrected.replace(x, ENCODING_FIXES[x])
    return corrected

if __name__ == "__main__":
    get_PLZ_coordinates_file()
    parent_dir = Path(__file__).parent
    with open(parent_dir /"data"/"PLZ.csv", "r") as file:
        content = fix_encoding(file.read())
    print(content)
import requests
import json 
import csv
from pathlib import Path
from urllib3 import disable_warnings
from datetime import date, timedelta
# latitude + longitude
disable_warnings()

def get_place_coordinates() -> dict:
    """Read csv File with fields Postleitzahl, City, longitude, latitude"""
    field_names = [
        "country_code",
        "postal_code",
        "place_name",
        "state_name",
        "state_code",
        "county_name",
        "county_code",
        "community_name",
        "community_code",
        "latitude",
        "longitude",
        "accuracy"]
    place_coordinates = {}
    filepath = Path(__file__).parent / "data" / "PLZ.csv"
    with open(filepath, "r", encoding="utf-8") as file:
        rows = list(csv.DictReader(file,delimiter="\t", fieldnames=field_names))
        for row in rows:
            place_coordinates[int(row["postal_code"])] = (float(row["longitude"]), float(row["latitude"]))
            place_coordinates[row["place_name"].lower()] = (float(row["longitude"]), float(row["latitude"]))
    return place_coordinates
 
def get_rain_forecast(coordinates):
    url = "https://api.open-meteo.com/v1/forecast"
    latitude, longitude = coordinates
    print(coordinates)
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    params = {
	    "latitude": latitude,
	    "longitude": longitude,
	    "daily": "rain_sum",
	    "hourly": "rain",
	    "models": "icon_seamless",
        "timezone": "Europe/Berlin",
        "start_date": tomorrow,
        "end_date" : tomorrow
    }

    try:
        result = requests.get(url, params=params, verify=False)
        result.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
        return None
    return result.json()

def search_place(query:str)-> dict:
    url = "https://photon.komoot.io/api/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0",
       }
    params = {"q": query}
    result = requests.get(url, params=params, headers=headers,verify=False)
    result.raise_for_status()
    return result

def extrapolate_rain_data(rain_per_hour:list) -> string:
    max_rain = max(rain_per_hour)
    if max_rain == 0:
        return "Nein"
    if max_rain < 2.5:
        return "Bisschen"
    if max_rain < 10:
        return "Ziemlich"
    if max_rain < 50:
        return "Stark"
    return "Schau, dass du zuhause bleibst!"

if __name__ == "__main__":
    from setup import get_PLZ_coordinates_file
    get_PLZ_coordinates_file()
    place_coords = get_place_coordinates()
    place = input("Wo? : ").lower()
    if place in place_coords:
        found_place = place_coords[place]
    else:
        found_place = search_place(place).json()["features"][0]["geometry"]["coordinates"]
    print(json.dumps(found_place, indent=2))
    forecast = get_rain_forecast(found_place)
    #print(json.dumps(forecast, indent=2))
    rain = forecast["hourly"]["rain"]
    print(extrapolate_rain_data(rain))
    print(rain)
import requests
import json 
import csv
from pathlib import Path
from urllib3 import disable_warnings
from datetime import date, timedelta
import logging
import os

class RainFinder:

    #Stores places with mapped coordinates for fast access
    places_coordinates = None

    def __init__(self, logger=None):
        #TODO Install certificates
        disable_warnings()

        #Make initially sure postcode file is available
        self.__get_PLZ_coordinates_file()
       
        if logger != None:
            self.log = logger
        else:
            self.log = logging.getLogger(__name__)
            self.log.info("Initiated own logger in class")
            logging.basicConfig(filename="rainfinder.log", encoding="utf-8", level=logging.DEBUG)

        self.places_coordinates = self.__get_place_coordinates()
        if __name__ == "__main__":
            self.__run_manual()
            exit()

    #Loads the csv file into memory for fast access
    def __get_place_coordinates(self) -> dict:
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
    
    #Gets the metro data from external api based on coordinates
    @staticmethod
    def __get_rain_forecast(coordinates):
        url = "https://api.open-meteo.com/v1/forecast"
        latitude, longitude = coordinates
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

    #Get coordinates for places not in csv
    @staticmethod
    def __search_place(query:str)-> dict:
        url = "https://photon.komoot.io/api/"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0",
           }
        params = {"q": query}
        result = requests.get(url, params=params, headers=headers,verify=False)
        result.raise_for_status()
        return result

    #Make prediction for rain based on provided metro data
    @staticmethod
    def __extrapolate_rain_data(rain_per_hour:list) -> str:
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


    #Fixes encoding for csv due to it not being utf8 encoded
    def __fix_encoding(content:str):
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

    #Retrieves place coordination mapping file from external source
    @staticmethod
    def __get_PLZ_coordinates_file()->None:
        parent_dir = Path(__file__).parent
        if (parent_dir /"data"/"PLZ.csv").exists():
            return
        result = requests.get("https://symerio.github.io/postal-codes-data/data/geonames/DE.txt", verify=False)
        if not os.path.exists(parent_dir/"data"):
            os.mkdir(parent_dir/"data")
        with open(parent_dir /"data"/"PLZ.csv", "bw") as file:
            file.write(result.content)

    #Resolves coordinates for place by loaded csv or api as fallback
    def __get_coordinates_for_place(self, place:str):
        found_coordinates = None
        if place in self.places_coordinates:
            found_coordinates = self.places_coordinates[place]
        else:
            found_coordinates = self.__search_place(place).json()["features"][0]["geometry"]["coordinates"]

        return found_coordinates


    #Return result based on place
    def retrieveRainResult(self, place:str)->dict:
        self.log.debug(json.dumps(place, indent=2))
        coordinates = self.__get_coordinates_for_place(place)
        forecast = self.__get_rain_forecast(coordinates)
        rain_data = forecast["hourly"]["rain"]
        max_rain = max(rain_data)
        is_raining = False
        if max_rain > 0:
            is_raining = True

        #TODO Include exact place
        rain_result = {"isRaining": is_raining, "rain_data": rain_data, "extrapolate": self.__extrapolate_rain_data(rain_data)}

        return rain_result

    #For testing the class manually when not called by app
    def __run_manual(self):
        place = input("Wo? : ").lower()

        print(self.retrieveRainResult(place))

#Used for debugging
RainFinder()

import requests
import json 
import csv
from pathlib import Path
from urllib3 import disable_warnings
from datetime import date, timedelta, datetime
import logging
import os
import xmltodict

class RainFinder:

    #Stores places with mapped coordinates for fast access
    places_coordinates = None

    def __init__(self, logger=None):
        #TODO Install certificates
        disable_warnings()

        #Make initially sure postcode file is available
        if logger != None:
            self.log = logger
        else:
            self.log = logging.getLogger(__name__)
            self.log.info("Initiated own logger in class")
            logging.basicConfig(encoding="utf-8", level=logging.INFO)

        if __name__ == "__main__":
            self.__run_manual()
            exit()
    

    #Gets the metro data from external api based on coordinates
    def __get_rain_forecast(self, coordinates):
        longitude, latitude = coordinates
        url = f"https://api.met.no/weatherapi/locationforecast/2.0/classic?lat={latitude:.2f}&lon={longitude:.2f}"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0",
            }
        try:
            result = requests.get(url, verify=False, headers=headers)
            result.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.log.error(f"No data for coordinates: {coordinates}, {e}")
            return None
        content = xmltodict.parse(result.text)
        return content

    @staticmethod
    def __parse_forecast_for_tomorrow(forecast:dict) -> list:
        hourly = []
        current_timestamp = datetime.combine(date.today() + timedelta(days=1), datetime.min.time())
        end_timestamp = current_timestamp+timedelta(days=1)
        next_timestamp = current_timestamp + timedelta(hours=1)
        for entry in forecast["weatherdata"]["product"]["time"]:
            if "precipitation" not in entry["location"]:
                continue
            if entry["@from"] == current_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ") and entry["@to"] == next_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"):
                hourly.append(float(entry["location"]["precipitation"]["@value"]))
                current_timestamp = next_timestamp
                next_timestamp += timedelta(hours=1)
        return hourly


    #Get coordinates for places not in csv
    def __search_place(self, query:str)-> dict:
        url = "https://photon.komoot.io/api/"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0",
           }
        params = {"q": query}
        try:
            result = requests.get(url, params=params, headers=headers,verify=False)
            result.raise_for_status()
        except requests.exceptions.HTTPError:
            self.log.error(f"No location for string: {query}")
            return None
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



    #Resolves coordinates for place by loaded csv or api as fallback
    def __get_coordinates_for_place(self, place:str):
        found_coordinates = self.__search_place(place).json()["features"]
        if len(found_coordinates) == 0:
            return None
        return found_coordinates[0]["geometry"]["coordinates"]


    #Return result based on place
    def retrieve_rain_result(self, place:str)->dict:
        self.log.debug(json.dumps(place, indent=2))
        coordinates = self.__get_coordinates_for_place(place)
        if coordinates is None:
            return None
        forecast = self.__get_rain_forecast(coordinates)
        if forecast is None:
            return None
        self.log.debug(json.dumps(forecast, indent=2))
        rain_data = self.__parse_forecast_for_tomorrow(forecast)
        max_rain = max(rain_data)
        is_raining = False
        if max_rain > 0:
            is_raining = True

        #TODO Include exact place
        rain_result = {"is_raining": is_raining, "rain_data": rain_data, "extrapolate": self.__extrapolate_rain_data(rain_data)}

        return rain_result

    #For testing the class manually when not called by app
    def __run_manual(self):
        place = input("Wo? : ").lower()

        print(self.retrieve_rain_result(place))

#Used for debugging
RainFinder()
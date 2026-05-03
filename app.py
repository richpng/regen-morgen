from flask import Flask, request
from flask import render_template
import random
from src.rainfinder.core import get_place_coordinates, get_rain_forecast, search_place
from src.rainfinder import setup

app = Flask(__name__)

setup.get_PLZ_coordinates_file()
app.plz_coordinats_map = get_place_coordinates()



@app.route("/")
def serve_index():
    return render_template('regen.html')

@app.route("/regen")
def query_for_rain():
    location = request.args.get("location")
    #latitude = request.args.get("lat")
    #longitude = request.args.get("lon")
    found_place = None
    if location in app.plz_coordinats_map:
        found_place = app.plz_coordinats_map[location]
    else:
        found_place = search_place(location).json()["features"][0]["geometry"]["coordinates"]
    if found_place is None:
        raise Exception("found_place is None")
    day_forecast = get_rain_forecast(found_place)
    hourly_forecast = day_forecast["hourly"]["rain"]
    is_raining=True

    return render_template("regen.html", location=location, is_raining=is_raining)
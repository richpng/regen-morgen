from flask import Flask, request
from flask import render_template
import random
from src.rainfinder import rainfinder

app = Flask(__name__)

rainy = rainfinder.RainFinder()


@app.route("/")
def serve_index():
    return render_template('regen.html')

@app.route("/regen")
def query_for_rain():
    location = request.args.get("location")
    #latitude = request.args.get("lat")
    #longitude = request.args.get("lon")
    rainresult_dict = rainy.retrieve_rain_result(location)
    """
    found_place = None
    if location in app.plz_coordinats_map:
        found_place = app.plz_coordinats_map[location]
    else:
        found_place = search_place(location).json()["features"][0]["geometry"]["coordinates"]
    if found_place is None:
        raise Exception("found_place is None")
    day_forecast = get_rain_forecast(found_place)
    hourly_forecast = day_forecast["hourly"]["rain"]
    """
    is_raining=rainresult_dict["is_raining"]

    return render_template("regen.html", location=location, is_raining=is_raining)
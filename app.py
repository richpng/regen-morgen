from flask import Flask
from flask import render_template
import random

app = Flask(__name__)

@app.route("/")
def serve_index():
    return render_template('index.html')

@app.route("/regen")
def query_for_rain():
    if random.randint(0, 1) == 0:
        return "<h1>no</h1>"
    return "<h1>yes</h1>"
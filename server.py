from flask import Flask, render_template

from api import api
from data import start_loading_loop

import requests
import random

app = Flask("KEGWeatherHist")
app.register_blueprint(api, url_prefix="/api")

@app.route("/")
def index():
    return render_template("index.html")
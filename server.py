from flask import Flask, render_template
from api import api

import datetime


app = Flask("KEGWeatherHist")
app.register_blueprint(api, url_prefix="/api")


@app.route("/")
def index():
    # Return index page with current year for copyright
    return render_template("index.html", year=datetime.date.today().year)

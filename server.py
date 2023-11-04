from flask import Flask, render_template, redirect, abort
from api import api, init_limiter

import datetime

app = Flask("KEGWeatherHist")
app.register_blueprint(api, url_prefix="/api")
init_limiter(app)

DOWNLOAD_LIST_POSSIBILITIES = []

for data_type in [
    {"name": "Temperatur", "type": "temperature"},
    {"name": "Luftfeuchtigkeit", "type": "humidity"},
    {"name": "Luftdruck", "type": "pressure"},
    {"name": "Regenfall", "type": "rain"},
    {"name": "Windgeschwindigkeit", "type": "wind_speed"},
    {"name": "Windrichtung", "type": "wind_direction"},
]:
    for mode in [
        {"name": "Tag", "mode": "day"},
        {"name": "Woche", "mode": "week"},
        {"name": "Monat", "mode": "month"},
    ]:
        for data_format in [
            {"name": "Graph", "format": "image"},
            {"name": "Json", "format": "json"},
        ]:
            DOWNLOAD_LIST_POSSIBILITIES.append(
                {
                    "name": f"{data_format['name']} ({data_type['name']}, {mode['name']})",
                    "link": f"/download/{data_format['format']}/{data_type['type']}/{mode['mode']}",
                }
            )


@app.route("/")
def index():
    # Return index page with current year for copyright
    return render_template("index.html", year=datetime.date.today().year)


@app.route("/download/")
def download_select():
    return render_template("download_list.html", downloads=DOWNLOAD_LIST_POSSIBILITIES)


@app.route("/download/<string:file_type>/<string:data_type>/<string:mode>")
def download(file_type, data_type, mode):
    match file_type:
        case "image":
            return redirect(f"/api/img/{data_type}/{mode}?mode=download")
        case "json":
            return redirect(f"/api/{data_type}/{mode}?mode=download")
        case _:
            abort(404)

from .vars import *
from .env import env
from .data import history, IntervalType
from .graph_generation import generate_graph

from jinja2 import Environment, FileSystemLoader

import os
import json
import time
import shutil
import socket

import pytz

from datetime import datetime


def get_data(data_type: str, mode: str, allow_current: bool):
    ts = int(time.time())
    match mode:
        case "current":
            if not allow_current:
                return None

            if data_type[0:4] == "wind":
                # If data has something to do with wind, load from seperate sub-dictionary
                res = str(history.current_data.wind.__getattribute__(data_type[5:]))
            else:
                # Else read from main dictionary
                res = str(history.current_data.__getattribute__(data_type))
        case "day":
            res = history.get_history(ts - 60 * 60 * 24, IntervalType.HOURLY, data_type)
        case "week":
            res = history.get_history(
                ts - 60 * 60 * 24 * 7, IntervalType.DAILY, data_type
            )
        case "month":
            res = history.get_history(
                ts - 60 * 60 * 24 * 30, IntervalType.DAILY, data_type
            )

    return res


def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    i = s.getsockname()[0]
    s.close()
    return i


def build_files(path: str):
    # Render templates
    template_dir = os.path.join(APP_ROOT_PATH, "templates")
    jinja_env = Environment(loader=FileSystemLoader(template_dir))
    for f in os.listdir(template_dir):
        template_vars = {}
        if f == "base.html":
            continue
        elif f == "index.html":
            template_vars["timestamp"] = int(time.time())
        elif f == "download.html":
            template_vars["downloads"] = DOWNLOAD_LIST_POSSIBILITIES
        elif f == "meteoware.html":
            template_vars["ip"] = getIP()
            template_vars["interval"] = env.get("UPLOAD_INTERVAL", 5)

        jinja_env.get_template(f, globals=template_vars).stream().dump(
            os.path.join(path, f)
        )

        if f == "index.html":
            template_vars["embed"] = True
            jinja_env.get_template(f, globals=template_vars).stream().dump(
                os.path.join(path, "embed.html")
            )

    # Copy static files
    static_dir = os.path.join(APP_ROOT_PATH, "static")
    shutil.copytree(static_dir, os.path.join(path, "static"))

    # Generate data json and graphs
    # Located in /api/<kind>/<span>
    for combination in ALL_DATA_COMBINATIONS:
        file_path = os.path.join(
            path, "api", combination["kind"], combination["span"] + ".json"
        )
        data = get_data(combination["kind"], combination["span"], True)

        if data == None:
            continue

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="UTF-8") as f:
            if combination["span"] == "current":
                f.write(data)
            else:
                json.dump(data, f, indent=4)

        if combination["span"] != "current":
            file_path = os.path.join(
                path, "api", "img", combination["kind"], combination["span"] + ".jpg"
            )
            data = get_data(combination["kind"], combination["span"], False)

            if data == None:
                continue

            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            graph = generate_graph(
                data["labels"],
                data["entries"],
                1920,
                1080,
                combination["title"],
                "Daten (c) Karl-Ernst-Gymnasium Amorbach. Alle Rechte vorbehalten. Stand: "
                + datetime.now().strftime("%d.%m.%Y. %H:%M"),
            )

            with open(file_path, "wb") as f:
                f.write(graph.getbuffer())

    file_path = os.path.join(path, "api", "all.json")
    with open(file_path, "w", encoding="UTF-8") as f:
        json.dump(history.current_data.model_dump(), f, indent=4)

    file_path = os.path.join(path, "api", "meteoware-live.json")
    with open(file_path, "w", encoding="UTF-8") as f:
        tz = pytz.timezone(os.environ.get("TIMEZONE", "Europe/Berlin"))
        _date = datetime.fromtimestamp(history.current_data_time)
        _date = tz.normalize(tz.localize(_date, is_dst=True))

        # UTC timestamp
        date = _date.strftime("%Y%m%d%H%M%S")

        json.dump(
            {
                "header": {"generator": "meteohub", "version": "1.0"},
                "current": {
                    "dt": {"local": date, "utc": date},
                    "temperature": {"v": history.current_data.temperature},
                    # "dewpoint": {"v": history.current_data.dewpoint},
                    "dewpoint": {"v": 0},
                    "pressure": {"v": history.current_data.pressure},
                    "humidity": {"v": history.current_data.humidity},
                    "precipitation": [
                        {"v": history.current_data.rain, "p": "rate"},
                    ],
                    "wind": {
                        "speed": {"v": history.current_data.wind.speed},
                        # "gust": {"v": wind["@gust"]},
                        "gust": {"v": 0},
                        "direction": {"v": history.current_data.wind.direction},
                    },
                },
            },
            f,
            indent=4,
        )

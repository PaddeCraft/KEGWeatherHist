from .vars import *
from .env import env
from .data import history, IntervalType
from .graph_generation import generate_graph

from jinja2 import Environment, FileSystemLoader

import os
import json
import time
import shutil

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

        jinja_env.get_template(f, globals=template_vars).stream().dump(
            os.path.join(path, f)
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

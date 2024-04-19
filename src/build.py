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
import platform

from getmac import get_mac_address

from datetime import datetime, timezone


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


# ---------------------------------------------------------------------------- #
#                                  Main files                                  #
# ---------------------------------------------------------------------------- #


def build_templates(path: str):
    # Render templates
    template_dir = os.path.join(APP_ROOT_PATH, "templates")
    jinja_env = Environment(loader=FileSystemLoader(template_dir))
    for f in os.listdir(template_dir):
        template_vars = {}
        localpath = path
        if f == "base.html":
            continue
        elif f == "tabulator.html":
            continue
        elif f == "meteoware.html":
            template_vars["interval"] = env.get("UPLOAD_INTERVAL", 5)
        rtfile = f
        if f == "day.html":
            template_vars["timestamp"] = int(time.time())
            localpath = os.path.join(path, "day")
            rtfile = "index.html"
            os.mkdir(localpath)
        elif f == "week.html":
            template_vars["timestamp"] = int(time.time())
            localpath = os.path.join(path, "week")
            rtfile = "index.html"
            os.mkdir(localpath)
        elif f == "month.html":
            template_vars["timestamp"] = int(time.time())
            localpath = os.path.join(path, "month")
            rtfile = "index.html"
            os.mkdir(localpath)
        elif f == "info.html":
            template_vars["timestamp"] = int(time.time())
            localpath = os.path.join(path, "info")
            rtfile = "index.html"
            os.mkdir(localpath)
        elif f == "live.html":
            template_vars["timestamp"] = int(time.time())
            localpath = os.path.join(path, "live")
            rtfile = "index.html"
            os.mkdir(localpath)
        elif f == "legacy.html":
            localpath = os.path.join(path, "legacy")
            rtfile = "index.html"
            os.mkdir(localpath)
        elif f == "api_index.html":
            template_vars["downloads"] = DOWNLOAD_LIST_POSSIBILITIES
            localpath = os.path.join(path, "api")
            rtfile = "index.html"
            if not os.path.exists(localpath):
                os.mkdir(localpath)
        elif f == "api_docs.html":
            localpath = os.path.join(path, "api")
            rtfile = "docs.html"
            if not os.path.exists(localpath):
                os.mkdir(localpath)
        jinja_env.get_template(f, globals=template_vars).stream().dump(
            os.path.join(localpath, rtfile)
        )

        if f == "index.html":
            template_vars["embed"] = True
            jinja_env.get_template(f, globals=template_vars).stream().dump(
                os.path.join(path, "embed.html")
            )

    # Copy static files
    static_dir = os.path.join(APP_ROOT_PATH, "static")
    shutil.copytree(static_dir, os.path.join(path, "static"))


def build_data_files(path: str):
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
        json.dump(
            {**history.current_data.model_dump(), "timestamp": int(time.time())},
            f,
            indent=4,
        )

    file_path = os.path.join(path, "api", "meteoware-live.json")
    with open(file_path, "w", encoding="UTF-8") as f:
        # UTC timestamp
        date = datetime.fromtimestamp(
            history.current_data_time, tz=timezone.utc
        ).strftime("%Y%m%d%H%M%S")

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


# ---------------------------------------------------------------------------- #
#                                  Status file                                 #
# ---------------------------------------------------------------------------- #


def build_status_file(directory: str, status: dict):
    # --------------------------- Check for git updates -------------------------- #

    git_status = {}

    try:
        # Based on this answer: https://stackoverflow.com/a/3278427

        git_output_local = os.popen("git rev-parse @").read().strip()
        git_output_remote = os.popen("git rev-parse @{u}").read().strip()
        git_output_base = os.popen("git merge-base @ @{u}").read().strip()

        git_status["up_to_date"] = git_output_local == git_output_remote
        git_status["update_available"] = git_output_local == git_output_base
        git_status["local_changes"] = git_output_remote == git_output_base

        # If all are false, the branch is diverged
        if all(not git_status[key] for key in git_status):
            raise Exception("Diverged branch.")

        git_current_commit = os.popen("git rev-parse HEAD").read().strip()
        git_current_commit_message = os.popen("git log -1 --pretty=%B").read().strip()

        git_status["commit"] = {
            "hash": git_current_commit,
            "message": git_current_commit_message,
        }

        git_status["error"] = False

    except Exception as e:
        git_status["error"] = True
        git_status["error_message"] = str(e)

    # ---------------------------------- Uptime ---------------------------------- #

    last_reboot = None
    uptime = None

    try:
        with open(os.path.join(APP_ROOT_PATH, "lastReboot.txt"), encoding="UTF-8") as f:
            last_reboot = f.read().strip()
    except Exception as e:
        pass

    try:
        with open("/proc/uptime") as f:
            uptime = float(f.read().strip().split(" ")[0])
    except Exception as e:
        pass

    # ------------------------------- Machine info ------------------------------- #

    machine_info = {}
    try:
        machine_info["arch"] = platform.machine()
        machine_info["hostname"] = platform.node()
        machine_info["identifier"] = platform.platform()
        machine_info["platform"] = platform.system() + " " + platform.release()

        machine_info["specs"] = {
            "cores": os.cpu_count(),
            "memory": os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"),
        }
        machine_info["python"] = {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
        }
    except Exception as e:
        pass

    hardware_info = {}
    try:
        with open("/proc/device-tree/model") as f:
            board_name = f.read().strip()

        hardware_info["board"] = board_name
    except Exception as e:
        pass

    machine_info["hardware"] = hardware_info

    # ------------------------------ Write the file ------------------------------ #

    with open(os.path.join(directory, "status.json"), "w", encoding="UTF-8") as f:
        json.dump(
            {
                "status": status,
                "system": {
                    "ip_addr": getIP(),
                    "mac_addr": get_mac_address(),
                    "last_reboot": last_reboot,
                    "uptime": uptime,
                    "platform": machine_info,
                },
                "git": git_status,
                "timestamp": int(time.time()),
            },
            f,
            indent=4,
        )

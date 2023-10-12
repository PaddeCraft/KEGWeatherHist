import requests
import xmltodict
import pyautogui as ag
import flask
import socket
from flask import render_template

from typing import Any

app = flask.Flask(__name__)
webserverIP = ""

# ---------------------------------------------------------------------------- #
#                                   Constants                                  #
# ---------------------------------------------------------------------------- #

# * The MeteoHub IP
#! Change to the correct ip
METEOHUB_IP = "172.16.210.220"
# * The interval to update the data, in minutes
DATA_INTERVAL = 5


class DefaultValuedDict:
    def __init__(self, data: dict, default_value: any) -> None:
        if type(data) == dict:
            self.data = data
        else:
            self.data = {}

        self.default_value = default_value

    def __getattribute__(self, __name: str) -> Any:
        if __name in self.data:
            return self.__getattribute__(__name)
        return self.default_value

    def __setattr__(self, __name: str, __value: Any) -> None:
        self.data[__name] = __value

    def get(self, __name):
        return self.__getattribute__(__name)


def update():
    d = None

    try:
        r = requests.get(
            f"http://{METEOHUB_IP}/meteolog.cgi?type=xml&quotes=1&mode=data&info=station&info=utcdate&info=sensorids"
        ).text
        d = xmltodict.parse(r)["logger"]
    except Exception:
        d = DefaultValuedDict({}, {})

    inside = DefaultValuedDict(d.get("THB"), 0)
    outside = DefaultValuedDict(d.get("TH"), 0)
    wind = DefaultValuedDict(d.get("WIND"), 0)
    # TODO: Fix rain
    rain = DefaultValuedDict(d.get("RAIN"), 0)

    return inside, outside, wind, rain


@app.route("/data")
def data():
    inside, outside, wind, rain = update()
    return {
        "header": {"generator": "meteohub", "version": "1.0"},
        "current": {
            "dt": {"local": outside["@date"], "utc": outside["@date"]},
            "temperature": {"v": outside["@temp"]},
            "dewpoint": {"v": outside["@dew"]},
            "pressure": {"v": inside["@press"]},
            "humidity": {"v": outside["@hum"]},
            # TODO: Fix rain
            "precipitation": [
                {"v": rain["@rate"], "p": "rate"},
                {"v": 0.00, "p": "last60m"},
            ],
            "wind": {
                "speed": {"v": wind["@wind"]},
                "gust": {"v": wind["@gust"]},
                "direction": {"v": wind["@dir"]},
            },
        },
    }


@app.route("/")
def index():
    return render_template("index.html", ip=webserverIP, interval=DATA_INTERVAL)


def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    i = s.getsockname()[0]
    s.close()
    return i


if __name__ == "__main__":
    ag.moveTo(0, 0)
    webserverIP = getIP()
    app.run(port=8080, host="0.0.0.0")

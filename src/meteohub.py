from .env import env
from .default_valued_dict import DefaultValuedDict

import requests
import xmltodict

import time

def get_data():
    r = requests.get(
        f"{env.get('METEOHUB_URL')}/meteolog.cgi?type=xml&quotes=1&mode=data&info=station&info=utcdate&info=sensorids"
    ).text
    d = xmltodict.parse(r)["logger"]

    inside = DefaultValuedDict(d.get("THB"), None)
    outside = DefaultValuedDict(d.get("TH"), None)
    wind = DefaultValuedDict(d.get("WIND"), None)
    # TODO: Fix rain
    rain = DefaultValuedDict(d.get("RAIN"), None)

    return inside, outside, wind, rain


def fmt_data():
    global data_queue

    try:
        inside, outside, wind, rain = get_data()
    except Exception as e:
        print("Exp", e)
        return

    timestamp = int(time.time())
    request_data = {}

    request_data = {
        "temperature": None,
        "humidity": None,
        "pressure": None,
        "rain": None,
        "wind": None,
    }

    if outside["@temp"] != None:
        request_data["temperature"] = float(outside["@temp"])
    if outside["@hum"] != None:
        request_data["humidity"] = float(outside["@hum"])
    if inside["@press"] != None:
        request_data["pressure"] = int(float(inside["@press"]))
    if rain["@rate"] != None:
        request_data["rain"] = float(rain["@rate"])

    if wind["@wind"] != None and wind["@dir"] != None:
        request_data["wind"] = {
            "speed": float(wind["@wind"]),
            "direction": int(float(wind["@dir"])),
        }

    return request_data, timestamp
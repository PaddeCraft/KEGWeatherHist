import time
import requests
import xmltodict
import sys


from os import environ
from dotenv import load_dotenv
import hashlib
import json as jsON
from cryptography.fernet import Fernet

from default_valued_dict import DefaultValuedDict

# ---------------------------------------------------------------------------- #
#                                   Constants                                  #
# ---------------------------------------------------------------------------- #

# * The MeteoHub IP
# ! Change to the correct ip
METEOHUB_IP = "172.16.210.220"
# * The interval to collect data, in minutes
DATA_INTERVAL = 5
# * The url to post the data to
POST_HOST = "http://localhost:8080/"

# ---------------------------------------------------------------------------- #
#                                     Code                                     #
# ---------------------------------------------------------------------------- #
isDebug = False
load_dotenv()

# ---------------------------- Construct post url ---------------------------- #
tmp = POST_HOST
if POST_HOST[-1] != "/":
    tmp += "/"
tmp += "api/post"

POST_ENDPOINT = tmp
print("Send to ", POST_ENDPOINT)
del tmp


# ---------------- Post queue in case of network/server outage --------------- #
data_queue = []


# --------------------------------- Functions -------------------------------- #
def get_data():
    if isDebug:
        print("Got Data in Debug Mode!")
        return (
            DefaultValuedDict({}, 39),
            DefaultValuedDict({}, 42),
            DefaultValuedDict({}, 5),
            DefaultValuedDict({}, 10),
        )
    r = requests.get(
        f"http://{METEOHUB_IP}/meteolog.cgi?type=xml&quotes=1&mode=data&info=station&info=utcdate&info=sensorids"
    ).text
    d = xmltodict.parse(r)["logger"]

    inside = DefaultValuedDict(d.get("THB"), None)
    outside = DefaultValuedDict(d.get("TH"), None)
    wind = DefaultValuedDict(d.get("WIND"), None)
    # TODO: Fix rain
    rain = DefaultValuedDict(d.get("RAIN"), None)

    return inside, outside, wind, rain


def queue_data():
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

    m = hashlib.sha256()
    m.update(jsON.dumps(request_data, separators=(",", ":")).encode("UTF-8"))

    data = {
        "meta": {"timestamp": timestamp},
        "data": request_data,
        "verify": {
            "hash": Fernet(environ["VERIFICATION_KEY"].encode("UTF-8"))
            .encrypt(m.digest())
            .decode("UTF-8"),
            "enc": Fernet(environ["VERIFICATION_KEY"].encode("UTF-8"))
            .encrypt(str(timestamp).encode("UTF-8"))
            .decode("UTF-8"),
        },  #
    }

    data_queue.append(data)


# -------------------------------- Event loop -------------------------------- #
next_post = time.time()
if len(sys.argv) == 2 and sys.argv[1] == "debug":
    print("Debug Mode is Active!")
    isDebug = True
while True:
    if time.time() > next_post:
        next_post += 60 * DATA_INTERVAL
        queue_data()
        time.sleep(1)
    for _ in range(len(data_queue)):
        item = data_queue.pop(0)
        try:
            requests.post(POST_ENDPOINT, json=item)
        except Exception as e:
            data_queue.insert(0, item)

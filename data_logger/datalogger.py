import time
import requests
import xmltodict

from os import environ
from dotenv import load_dotenv

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
POST_HOST = "http://localhost/"

# ---------------------------------------------------------------------------- #
#                                     Code                                     #
# ---------------------------------------------------------------------------- #

load_dotenv()

# ---------------------------- Construct post url ---------------------------- #
tmp = POST_HOST
if POST_HOST[-1] != "/":
    tmp += "/"
tmp += "api/post"

POST_ENDPOINT = tmp
del tmp


# ---------------- Post queue in case of network/server outage --------------- #
data_queue = []


# --------------------------------- Functions -------------------------------- #
def get_data():
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
    except Exception:
        return

    timestamp = int(time.time())
    verification_phrase = str(time.time())

    data = {
        "meta": {"timestamp": timestamp},
        "data": {
            "temperature": outside["@temp"],
            "humidity": outside["@hum"],
            "pressure": inside["@press"],
            # TODO: Fix rain
            "rain": rain["@rate"],
            "wind": {"speed": wind["@wind"], "direction": wind["@dir"]},
        },
        "verify": {
            "res": verification_phrase,
            "enc": Fernet(environ["VERIFICATION_KEY"].encode("UTF-8")).encrypt(verification_phrase.encode("UTF-8")).decode("UTF-8")
        }#
    }

    data_queue.append(data)


# -------------------------------- Event loop -------------------------------- #
next_post = time.time()
while True:
    if time.time() > next_post:
        next_post += 60 * DATA_INTERVAL
        queue_data()

    for _ in range(len(data_queue)):
        item = data_queue.pop(0)
        try:
            requests.post(POST_ENDPOINT, json=item)
        except Exception:
            data_queue.insert(0, item)

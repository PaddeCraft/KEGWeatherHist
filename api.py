from flask import Blueprint, abort, request
from data import current_data, validate_and_save, history, IntervalType

import time

api = Blueprint("api", __name__)

# ---------------------------------------------------------------------------- #
#                             Specific data routes                             #
# ---------------------------------------------------------------------------- #

@api.get("/<string:data_type>/<string:mode>")
def get(data_type:str, mode:str):
    if not data_type in ["temperature", "humidity", "pressure", "rain", "wind_speed", "wind_direction"]:
        abort(404)
        
    ts = int(time.time())
    match mode:
        case "current":
            if data_type[0:4] == "wind":
                return str(current_data.wind.__getattribute__(data_type[5:]))
            else:
                return str( current_data.__getattribute__(data_type))
        case "day":
            return history.get_history(ts - 60*60*24, IntervalType.HOURLY, data_type)
        case "week":
            return history.get_history(ts - 60*60*24*7, IntervalType.DAILY, data_type)
        case "month":
            return history.get_history(ts - 60*60*24*30, IntervalType.DAILY, data_type)
        case _:
            abort(404)


# ---------------------------------------------------------------------------- #
#                              General data routes                             #
# ---------------------------------------------------------------------------- #


@api.post("/post")
def post():
    data = request.json()
    if not request.is_json:
        abort(400)

    if not validate_and_save(data):
        abort(422)


@api.get("/all")
def get_all():
    return current_data.model_dump(mode="json")

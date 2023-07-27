from flask import Blueprint, abort

api = Blueprint("api", __name__)

@api.route("/temperature/<string:mode>")
def temperature(mode:str):
    return [10 for _ in range(30)]
    match mode:
        case "current":
            pass
        case "day":
            pass
        case "week":
            pass
        case "month":
            pass
        case _:
            abort(404)
            
@api.route("/humidity/<string:mode>")
def humidity(mode:str):
    return [10 for _ in range(30)]
    match mode:
        case "current":
            pass
        case "day":
            pass
        case "week":
            pass
        case "month":
            pass
        case _:
            abort(404)
            
@api.route("/pressure/<string:mode>")
def pressure(mode:str):
    return [10 for _ in range(30)]
    match mode:
        case "current":
            pass
        case "day":
            pass
        case "week":
            pass
        case "month":
            pass
        case _:
            abort(404)
            
@api.route("/rain/<string:mode>")
def rain(mode:str):
    return [10 for _ in range(30)]
    match mode:
        case "current":
            pass
        case "day":
            pass
        case "week":
            pass
        case "month":
            pass
        case _:
            abort(404)
            
@api.route("/wind/<string:mode>")
def wind(mode:str):
    return [{"speed": 21, "direction": 210}]
    match mode:
        case "current":
            pass
        case "day":
            pass
        case "week":
            pass
        case "month":
            pass
        case _:
            abort(404)
from flask import Blueprint, abort, request, send_file, Response, render_template
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from datetime import datetime

import json
import time

from data import history, IntervalType

from graph_generation import (
    generate_graph,
    MIN_GRAPH_WIDTH,
    MIN_GRAPH_HEIGHT,
    MAX_GRAPH_WIDTH,
    MAX_GRAPH_HEIGHT,
)

api = Blueprint("api", __name__)

limiter = limiter = Limiter(
    get_remote_address,
    storage_uri="memory://",
)


def init_limiter(app):
    limiter.init_app(app)


# ---------------------------------------------------------------------------- #
#                             Specific data routes                             #
# ---------------------------------------------------------------------------- #


def get_data(data_type: str, mode: str, allow_current: bool):
    if not data_type in [
        "temperature",
        "humidity",
        "pressure",
        "rain",
        "wind_speed",
        "wind_direction",
    ]:
        abort(404)

    ts = int(time.time())
    match mode:
        case "current":
            if not allow_current:
                abort(404)

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
        case _:
            abort(404)

    return res


@api.get("/<string:data_type>/<string:mode>")
@limiter.limit("400 per minute")
def get(data_type: str, mode: str):
    is_download = request.args.get("mode") == "download"
    data = get_data(data_type, mode, not is_download)

    if is_download:
        return Response(
            json.dumps(data),
            headers={
                "Content-Disposition": f'attachment; filename="keg-weather_data-json-{int(time.time())}-{data_type}-{mode}.json"'
            },
        )

    return data


# ---------------------------------------------------------------------------- #
#                                NoScript graphs                               #
# ---------------------------------------------------------------------------- #


@api.get("/img/<string:data_type>/<string:mode>")
@limiter.limit("100 per hour")
def get_image(data_type: str, mode: str):
    if mode == "current":
        abort(404)

    is_download = request.args.get("mode") == "download"

    data = get_data(data_type, mode, False)

    width = 1280
    height = 720
    header = f"{data_type} ({mode})"

    if (_width := request.args.get("width")) != None:
        if not _width.isdigit():
            return "Width parameter invalid", 400
        _width = int(_width)

        if _width < MIN_GRAPH_WIDTH or _width > MAX_GRAPH_WIDTH:
            return (
                f"Outside width constrains: {MIN_GRAPH_WIDTH}<=width<={MAX_GRAPH_WIDTH}",
                400,
            )

        width = _width

    if (_height := request.args.get("height")) != None:
        if not _height.isdigit():
            return "Height parameter invalid", 400
        _height = int(_height)

        if _height < MIN_GRAPH_HEIGHT or _height > MAX_GRAPH_HEIGHT:
            return (
                f"Outside height constrains: {MIN_GRAPH_HEIGHT}<=width<={MAX_GRAPH_HEIGHT}",
                400,
            )

        height = _height

    if (_header := request.args.get("header")) != None:
        header = _header

    download_cfg = (
        {
            "as_attachment": True,
            "download_name": f"keg-weather_data-graph-{int(time.time())}-{data_type}-{mode}.jpeg",
        }
        if is_download
        else {}
    )

    return send_file(
        generate_graph(
            data["labels"],
            data["entries"],
            width,
            height,
            header,
            "Daten (c) Karl-Ernst-Gymnasium Amorbach. Alle Rechte vorbehalten. Stand: "
            + datetime.now().strftime("%d.%m.%Y. %H:%M"),
        ),
        mimetype="image/jpeg",
        **download_cfg,
    )


# ---------------------------------------------------------------------------- #
#                              General data routes                             #
# ---------------------------------------------------------------------------- #


@api.post("/post")
def post():
    data = request.json

    if not request.is_json:
        abort(400)

    if not history.validate_and_save(data):
        abort(422)

    return {"status": "ok"}


@api.get("/all")
@limiter.limit("15 per hour")
def get_all():
    return history.current_data.model_dump(mode="json")


# ---------------------------------------------------------------------------- #
#                                     Docs                                     #
# ---------------------------------------------------------------------------- #


@api.get("/docs")
def get_api_docs():
    return render_template("api_docs.html")

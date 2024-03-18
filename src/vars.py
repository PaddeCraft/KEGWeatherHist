import os

APP_SRC_PATH = os.path.dirname(os.path.abspath(__file__))
APP_ROOT_PATH = os.path.join(APP_SRC_PATH, "../")

ALL_DATA_COMBINATIONS = []
for kind in [
    {"id": "temperature", "name": "Temperatur"},
    {"id": "humidity", "name": "Luftfeuchtigkeit"},
    {"id": "pressure", "name": "Luftdruck"},
    {"id": "rain", "name": "Regen"},
    {"id": "wind_speed", "name": "Windgeschwindigkeit"},
    {"id": "wind_direction", "name": "Windrichtung"},
]:
    for span in [
        {"id": "current", "name": "Aktuell"},
        {"id": "day", "name": "Tag"},
        {"id": "week", "name": "Woche"},
        {"id": "month", "name": "Monat"},
    ]:
        ALL_DATA_COMBINATIONS.append(
            {
                "kind": kind["id"],
                "span": span["id"],
                "title": f"{kind['name']} ({span['name']})",
            }
        )

DOWNLOAD_LIST_POSSIBILITIES = []
for data_type in [
    {"name": "Temperatur", "type": "temperature"},
    {"name": "Luftfeuchtigkeit", "type": "humidity"},
    {"name": "Luftdruck", "type": "pressure"},
    {"name": "Regenfall", "type": "rain"},
    {"name": "Windgeschwindigkeit", "type": "wind_speed"},
    {"name": "Windrichtung", "type": "wind_direction"},
]:
    for mode in [
        {"name": "Tag", "mode": "day"},
        {"name": "Woche", "mode": "week"},
        {"name": "Monat", "mode": "month"},
    ]:
        for data_format in [
            {"name": "Graph", "format": "image"},
            {"name": "Json", "format": "json"},
        ]:
            DOWNLOAD_LIST_POSSIBILITIES.append(
                {
                    "name": f"{data_format['name']} ({data_type['name']}, {mode['name']})",
                    "link": f"../api/{'img/' if data_format['format'] == 'image' else ''}{data_type['type']}/{mode['mode']}."
                    + ("json" if data_format["format"] == "json" else "jpg"),
                }
            )

import os
import pickle
import datetime

from enum import Enum
from pydantic import BaseModel, ValidationError

from config import *


# ---------------------------------------------------------------------------- #
#                          Data structure definitions                          #
# ---------------------------------------------------------------------------- #
class WeatherWindData(BaseModel):
    speed: float | int = 0
    direction: int = 0


class WeatherData(BaseModel):
    temperature: float | int = 0
    humidity: float | int = 0
    pressure: int = 0
    rain: float | int = 0
    wind: WeatherWindData = WeatherWindData()


class PostMetaData(BaseModel):
    timestamp: int


class PostData(BaseModel):
    meta: PostMetaData
    data: WeatherData


# ---------------------------------------------------------------------------- #
#                           Helper classes/functions                           #
# ---------------------------------------------------------------------------- #

class IntervalType(Enum):
    HOURLY = 60
    DAILY = 60*24

class WeatherHistory:
    def __init__(self) -> None:
        self.history = []

        # If data is present, load it
        if os.path.isfile(HISTORY_FILE):
            with open(HISTORY_FILE, "rb") as hist:
                self.history = pickle.load(hist)

    def load(self, data: WeatherData, timestamp: int):
        dump = data.model_dump()
        dump["wind_speed"] = dump["wind"]["speed"]
        dump["wind_direction"] = dump["wind"]["direction"]
        del dump["wind"]
        
        self.history.append({"ts": timestamp, "data": dump})

        # Save to disk
        with open(HISTORY_FILE, "wb") as hist:
            pickle.dump(self.history, hist)

    def get_history(self, start_ts:int, interval:IntervalType, key:str):
        res = {
            "labels": [],
            "entries": []
        }
        
        next_ts = start_ts
        avg_tmp = []
        
        for i, entry in enumerate(self.history):
            if not entry["ts"] >= start_ts:
                continue
            
            if entry["ts"] < next_ts or i+1 == len(self.history):
                avg_tmp.append(entry["data"][key])
                
            if entry["ts"] >= next_ts or i+1 == len(self.history):
                date = datetime.datetime.fromtimestamp(next_ts)
                res["entries"].insert(0, sum(avg_tmp) / len(avg_tmp))
                res["labels"].insert(0, date.strftime("%H") if interval == IntervalType.HOURLY else date.strftime("%a, %d.%m.%y"))
                
                next_ts += interval.value * 60
        
        return res


# ---------------------------------------------------------------------------- #
#                             Current data tracking                            #
# ---------------------------------------------------------------------------- #
current_data_time = 0
current_data = WeatherData(
    **{
        "temperature": 0,
        "humidity": 0,
        "pressure": 0,
        "rain": 0,
        "wind": {"speed": 0, "direction": 0},
    }
)

history = WeatherHistory()

def validate_and_save(data: dict):
    global current_data, current_data_time

    try:
        loaded = PostData(**data)
    except ValidationError:
        return False

    if loaded.meta.timestamp > current_data_time:
        # TODO: Save to disk
        current_data_time = loaded.meta.timestamp
        current_data = loaded.data

    return True

import os
import time
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
    # The value is the time in minutes
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
        """Load data into history

        Args:
            data (WeatherData): The weather data
            timestamp (int): The timestamp
        """
        
        # Convert data to dict
        dump = data.model_dump()
        dump["wind_speed"] = dump["wind"]["speed"]
        dump["wind_direction"] = dump["wind"]["direction"]
        del dump["wind"]
        
        # Delete data older than 30 days
        tmp = []
        min_timestamp = time.time() - 60*60*24*30
        for entry in self.history:
            if entry["ts"] >= min_timestamp:
                tmp.append(entry)
        self.history = tmp
        del tmp
        
        # Add new entry to history
        self.history.append({"ts": timestamp, "data": dump})

        # Save to disk
        with open(HISTORY_FILE, "wb") as hist:
            pickle.dump(self.history, hist)

    def get_history(self, start_ts:int, interval:IntervalType, key:str):
        """Gets data from history

        Args:
            start_ts (int): The start timestamp
            interval (IntervalType): The interval (hourly or daily)
            key (str): The key in the data, e.g. temperature

        Returns:
            _type_: _description_
        """
        res = {
            "labels": [],
            "entries": []
        }
        
        next_ts = start_ts
        avg_tmp = []
        
        # Iterate through every entry in the history
        for i, entry in enumerate(self.history):
            # If the entry isn't even in the selected range, ignore it
            if not entry["ts"] >= start_ts:
                continue

            # Add the entry if it's in the current interval or if it's the last
            if entry["ts"] < next_ts or i+1 == len(self.history):
                avg_tmp.append(entry["data"][key])
                
            # Calculate the average and the labels if the interval has passed or we are at the last entry
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

def validate_and_save(data: dict) -> bool:
    """Validates the data and saves it if valid

    Args:
        data (dict): The data

    Returns:
        bool: Returns True if data is valid, False if invalid
    """
    global current_data, current_data_time

    # Check if data is valud
    try:
        loaded = PostData(**data)
    except ValidationError:
        return False

    # Save data to history
    history.load(current_data, current_data_time)
    
    # If it's the newest data, use as current data
    if loaded.meta.timestamp > current_data_time:
        current_data_time = loaded.meta.timestamp
        current_data = loaded.data

    return True

import os
import time
import pickle
import datetime

from enum import Enum

import pytz
from pydantic import BaseModel, ValidationError

try:
    from statistics import fmean as average
except ImportError:
    print(
        "[WARN] Cannot import statistics.fmean (Python 3.8+), the slower version statistics.mean will be used instead."
    )
    from statistics import mean as average

from .env import env

HISTORY_FILE = env.get("HISTORY_FILE", "weather_history.pickle")


# ---------------------------------------------------------------------------- #
#                          Data structure definitions                          #
# ---------------------------------------------------------------------------- #


class WeatherWindData(BaseModel):
    speed: float | int = 0
    direction: int = 0


class WeatherData(BaseModel):
    temperature: float | int | None = None
    humidity: float | int | None = None
    pressure: int | None = None
    rain: float | int | None = None
    wind: WeatherWindData | None = None


class PostMetaData(BaseModel):
    timestamp: int


class DataVerification(BaseModel):
    hash: str
    enc: str


class PostData(BaseModel):
    meta: PostMetaData
    data: WeatherData
    verify: DataVerification


# ---------------------------------------------------------------------------- #
#                           Helper classes/functions                           #
# ---------------------------------------------------------------------------- #


class IntervalType(Enum):
    # The value is the time in minutes
    HOURLY = 60
    DAILY = 60 * 24


class WeatherHistory:
    def __init__(self) -> None:
        self.history = []

        # Initialize current data
        self.current_data_time = 0
        self.current_data = WeatherData(
            **{
                "temperature": 0,
                "humidity": 0,
                "pressure": 0,
                "rain": 0,
                "wind": {"speed": 0, "direction": 0},
            }
        )

        # If data is present, load it
        if os.path.isfile(HISTORY_FILE):
            with open(HISTORY_FILE, "rb") as hist:
                self.history = pickle.load(hist)

            # Load newest data
            for item in self.history:
                if item["ts"] > self.current_data_time:
                    self.set_current_data(WeatherData(**item["data"]), item["ts"])

    def set_current_data(self, data: WeatherData, timestamp: int):
        curr = self.current_data.model_dump()
        for key, value in data.model_dump().items():
            if value != None:
                curr[key] = value

        self.current_data = WeatherData(**curr)
        self.current_data_time = timestamp

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
        min_timestamp = time.time() - 60 * 60 * 24 * 30
        for entry in self.history:
            if entry["ts"] >= min_timestamp:
                tmp.append(entry)
        self.history = tmp
        del tmp

        # Add new entry to history
        self.history.append({"ts": timestamp, "data": dump})

        # If newest data, set as current data
        if timestamp > self.current_data_time:
            self.set_current_data(data, timestamp)

        # Save to disk
        with open(HISTORY_FILE, "wb") as hist:
            pickle.dump(self.history, hist)

    def get_history(self, start_ts: int, interval: IntervalType, key: str):
        """Gets data from history

        Args:
            start_ts (int): The start timestamp
            interval (IntervalType): The interval (hourly or daily)
            key (str): The key in the data, e.g. temperature

        Returns:
            dict[list]: A dict with entries and a label for each entry
        """
        res = {"labels": [], "entries": [], "timestamps": []}

        next_ts = start_ts
        avg_tmp = []
        date_tmp = []

        # Iterate through every entry in the history
        for i, entry in enumerate(sorted(self.history, key=lambda x: x["ts"])):
            # If the entry isn't even in the selected range, ignore it
            if entry["ts"] < start_ts:
                continue

            if i == 0:
                while entry["ts"] > next_ts:
                    next_ts += interval.value * 60
                next_ts -= interval.value * 60

            if entry["data"][key] != None:
                avg_tmp.append(entry["data"][key])
                date_tmp.append(entry["ts"])

            # Add the entry if it's in the current interval or if it's the last
            if entry["ts"] > next_ts or i + 1 == len(self.history):
                tz = pytz.timezone(os.environ.get("TIMEZONE", "Europe/Berlin"))

                # Calculate the average and the labels if the interval has passed or we are at the last entry
                try:
                    timestamp = int(average(date_tmp))
                    date = datetime.datetime.fromtimestamp(timestamp, tz=tz)
                except Exception:
                    timestamp = 0
                    date = datetime.datetime.fromtimestamp(0, tz=tz)

                try:
                    res["entries"].append(average(avg_tmp))
                except Exception:
                    res["entries"].append(0)

                res["labels"].append(
                    date.strftime("%H:00")
                    if interval == IntervalType.HOURLY
                    else date.strftime("%a, %d.%m.%y"),
                )

                res["timestamps"].append(timestamp)

                while entry["ts"] > next_ts:
                    next_ts += interval.value * 60
                date_tmp = []
                avg_tmp = []

        return res


history = WeatherHistory()

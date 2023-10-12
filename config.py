import os

# The file path for the weather history pickle file
HISTORY_FILE = "weather_history.pickle"
if (path := os.environ.get("HISTORY_FILE")) != None:
    HISTORY_FILE = path
from src.data import history, WeatherData
from src.meteohub import fmt_data
from src.build import build_files
from src.env import env
from src.ftp import *

import time

from tempfile import TemporaryDirectory


def loop():
    data, timestamp = fmt_data()

    history.load(WeatherData(**data), timestamp)

    ftp = ftp_connect(env.get("FTP_ADDR"), env.get("FTP_USER"), env.get("FTP_PASS"))
    ensure_directory(ftp, env.get("FTP_DIR"))

    with TemporaryDirectory() as tmp_dir:
        build_files(tmp_dir)
        upload_directory(ftp, tmp_dir, env.get("FTP_DIR"))

    ftp.close()

    print("Uploaded data.")


next_post = time.time()

while True:
    if time.time() > next_post:
        next_post += 60 * env.get("UPLOAD_INTERVAL", 5)
        loop()
        time.sleep(1)

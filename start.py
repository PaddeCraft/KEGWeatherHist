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

    use_sftp = env.get("USE_SFTP")
    ftp = FTPLib.get_connector(
        env.get("FTP_ADDR"),
        env.get("FTP_USER"),
        env.get("FTP_PASS"),
        use_sftp,
        env.get("SFTP_KEY", None),
    )

    ftp.ensure_directory(env.get("FTP_DIR"))

    with TemporaryDirectory() as tmp_dir:
        build_files(tmp_dir)
        ftp.upload_directory(tmp_dir, env.get("FTP_DIR"))

    ftp.close()

    print("Uploaded data.")


next_post = time.time()

while True:
    if time.time() > next_post:
        next_post += 60 * env.get("UPLOAD_INTERVAL", 5)
        loop()
        time.sleep(1)

from src.build import build_files, build_status_file
from src.data import history, WeatherData
from src.meteohub import fmt_data
from src.env import env
from src.ftp import *

import time

from tempfile import TemporaryDirectory


status = {"code": "operational", "message": "Everything is fine."}


def loop():
    global status

    data_fetch_success = False

    try:
        data, timestamp = fmt_data()
        data_fetch_success = True
    except Exception as e:
        status["code"] = "meteohub_unavailable"
        status["message"] = str(e)
        print("Exp", e)

    try:
        history.load(WeatherData(**data), timestamp)
    except Exception as e:
        if data_fetch_success:
            status["code"] = "history_exception"
            status["message"] = str(e)
            print("Exp", e)

    use_sftp = env.get("USE_SFTP")

    try:
        ftp = FTPLib.get_connector(
            env.get("FTP_ADDR"),
            env.get("FTP_USER"),
            env.get("FTP_PASS"),
            use_sftp,
            env.get("SFTP_KEY", None),
        )

        ftp.ensure_directory(env.get("FTP_DIR"))

        with TemporaryDirectory() as tmp_dir:
            try:
                if data_fetch_success:
                    build_files(tmp_dir)
            except Exception as e:
                status["code"] = "build_exception"
                status["message"] = str(e)
                print("Exp", e)

            build_status_file(tmp_dir, status)
            ftp.upload_directory(tmp_dir, env.get("FTP_DIR"))

        ftp.close()

        status["code"] = "operational"
        status["message"] = "Everything is fine."

        print("Uploaded data.")

    except Exception as e:
        status["code"] = "ftp_exception"
        status["message"] = str(e)
        print("Exp", e)
        print("Failed to upload data due to ftp exception.")


next_post = time.time()

while True:
    if time.time() > next_post:
        next_post += 60 * env.get("UPLOAD_INTERVAL", 5)
        loop()

        time.sleep(1)

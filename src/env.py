from typed_env import *

typed_vars = [
    v("FTP_USER", str),
    v("FTP_PASS", str),
    v("FTP_ADDR", str),
    v("USE_SFTP", bool),
    v("SFTP_KEY", str, OPTIONAL),
    v("FTP_DIR", str),
    v("METEOHUB_URL", str),
    v("TIMEZONE", str, OPTIONAL),
    v("UPLOAD_INTERVAL", int, OPTIONAL),
    v("HISTORY_FILE", str, OPTIONAL),
]

env = load_env(typed_vars)

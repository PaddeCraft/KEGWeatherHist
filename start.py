from src.build import build_files
from src.env import env
from src.ftp import *

from tempfile import TemporaryDirectory

ftp = ftp_connect(env.get("FTP_ADDR"), env.get("FTP_USER"), env.get("FTP_PASS"))
ensure_directory(ftp, env.get("FTP_DIR"))

with TemporaryDirectory() as tmp_dir:
    build_files(tmp_dir)
    upload_directory(ftp, tmp_dir, env.get("FTP_DIR"))
    print("Done")

ftp.close()

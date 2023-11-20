import ftplib
import os


def ftp_connect(host, user, passwd):
    ftp = ftplib.FTP()

    port = 21
    if ":" in host:
        port = int(host.split(":")[1])
        host = host.split(":")[0]

    ftp.connect(host, port)

    try:
        ftp.login(user, passwd)
    except ftplib.error_perm:
        return None

    return ftp


def upload_file(ftp, local_path, remote_path):
    with open(local_path, "rb") as file_descriptor:
        try:
            ftp.storbinary("STOR " + remote_path, file_descriptor)
        except ftplib.error_perm:
            return False

    return True


def ensure_directory(ftp, path):
    pth = ""
    for part in path.split("/"):
        pth += part + "/"
        try:
            ftp.mkd(pth)
        except ftplib.error_perm as e:
            pass


def upload_directory(ftp, local_path, remote_path):
    ensure_directory(ftp, remote_path)

    for file in os.listdir(local_path):
        path = os.path.join(local_path, file)
        if os.path.isdir(path):
            upload_directory(ftp, path, os.path.join(remote_path, file))

        else:
            if not upload_file(ftp, path, os.path.join(remote_path, file)):
                return False

    return True

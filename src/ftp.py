import ftplib
import pysftp
import paramiko

from base64 import decodebytes

import os


class FTPLib:
    @staticmethod
    def get_connector(
        host, user, passwd, is_sftp, known_hosts=None
    ) -> "FTPLib.Connector":
        if is_sftp:
            return FTPLib.SFTPConnector(host, user, passwd, known_hosts)
        return FTPLib.FTPConnector(host, user, passwd)

    class Connector:
        def __init__(self, host, user, passwd, known_hosts=None) -> None:
            pass

        def upload_file(self, path, remote_path):
            pass

        def upload_directory(self, path, remote_path):
            pass

        def ensure_directory(self, remote_path):
            pass

        def close(self):
            pass

    class FTPConnector(Connector):
        def __init__(self, host, user, passwd, known_hosts) -> None:
            ftp = ftplib.FTP()

            port = 21
            if ":" in host:
                port = int(host.split(":")[1])
                host = host.split(":")[0]

            ftp.connect(host, port)

            try:
                ftp.login(user, passwd)
            except ftplib.error_perm:
                raise Exception("Invalid credentials")

            self.ftp = ftp

        def upload_directory(self, path, remote_path):
            self.ensure_directory(remote_path)

            for file in os.listdir(path):
                path = os.path.join(path, file)
                if os.path.isdir(path):
                    self.upload_directory(remote_path, os.path.join(remote_path, file))

                else:
                    if not self.upload_file(path, os.path.join(remote_path, file)):
                        return False

            return True

        def upload_file(self, path, remote_path):
            with open(path, "rb") as file_descriptor:
                try:
                    self.ftp.storbinary("STOR " + remote_path, file_descriptor)
                except ftplib.error_perm:
                    return False

            return True

        def ensure_directory(self, remote_path):
            pth = ""

            for part in remote_path.split("/"):
                pth += part + "/"

                try:
                    self.ftp.mkd(pth)
                except ftplib.error_perm as e:
                    pass

        def close(self):
            return self.ftp.close()

    class SFTPConnector(Connector):
        @staticmethod
        def get_ssh_key(known_hosts):
            key = None
            data = decodebytes(known_hosts.split(" ")[2].encode())
            match known_hosts.split(" ")[1]:
                case "ssh-rsa":
                    key = paramiko.RSAKey(data=data)
                case "ssh-ed25519":
                    key = paramiko.Ed25519Key(data=data)
                case "ecdsa-sha2-nistp256":
                    key = paramiko.ECDSAKey(data=data)
                case "ssh-dss":
                    key = paramiko.DSSKey(data=data)
                case _:
                    raise "Invalid key type!"

            return *known_hosts.split(" ")[:2], key

        def __init__(self, host, user, passwd, known_hosts):
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys.add(*FTPLib.SFTPConnector.get_ssh_key(known_hosts))

            self.sftp = pysftp.Connection(
                host,
                username=user,
                password=passwd,
                cnopts=cnopts,
            )

        def upload_file(self, path, remote_path):
            self.sftp.put(path, remote_path)

        def upload_directory(self, path, remote_path):
            self.sftp.put_r(path, remote_path)

        def ensure_directory(self, remote_path):
            if not self.sftp.exists(remote_path):
                self.sftp.makedirs(remote_path)

        def close(self):
            self.sftp.close()

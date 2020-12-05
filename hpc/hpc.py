import os
import stat

import paramiko


class Hpc:
    def __init__(self, name):
        self.name = name
        if self.name == "probe":
            self.pkey = paramiko.RSAKey.from_private_key_file(
                r"C:\Users\shen\Desktop\杂物\探索100\KEY\caobynew",
                password="molecularsimulation",
            )
            self.ip = "166.111.143.18"
            self.username = "caoby"
            self.trans = paramiko.Transport((self.ip, 22))

        elif self.name == "kamui":
            self.ip = "41.0.0.188"
            self.username = "caoby"
            self.passwd = "axyr5Lr6"
            self.trans = paramiko.Transport((self.ip, 22))

    def __enter__(self):
        if self.name == "probe":
            self.trans.connect(username=self.username, pkey=self.pkey)
        elif self.name == "kamui":
            self.trans.connect(username=self.username, password=self.passwd)
        self.sftp = paramiko.SFTPClient.from_transport(self.trans)
        self.ssh = paramiko.SSHClient()
        self.ssh._transport = self.trans
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.trans.close()

    def __get_all_files(self, directory, remote=True):  # revise from CSDN:littleRpl
        all_files = []
        if remote == True:
            files = self.sftp.listdir_attr(directory)
            for file in files:
                filename = directory + "/" + file.filename

                if stat.S_ISDIR(file.st_mode):  # 如果是文件夹的话递归处理
                    all_files.extend(self.__get_all_files(filename))
                else:
                    all_files.append(filename)

            return all_files
        else:
            for direc, folder, files in os.walk(directory):
                for file in files:
                    all_files.append(os.path.join(direc, file))
            return all_files

    def upload(self, localpath, remotepath):
        if os.path.isfile(localpath):
            self.sftp.put(localpath, remotepath)
        else:
            all_files = self.__get_all_files(localpath, remote=False)
            for file in all_files:

                remote_filename = file.replace(localpath, remotepath).replace("\\", "/")
                print(remote_filename)
                remote_path = os.path.dirname(remote_filename)

                try:
                    sftp.stat(remote_path)
                except:
                    self.run_shell("mkdir -p {}".format(remote_path))  # 使用这个远程执行命令

                self.sftp.put(file, remote_filename)

    def download(self, localpath, remotepath):
        if stat.S_ISREG(self.sftp.lstat(remotepath).st_mode):
            self.sftp.get(remotepath, localpath)
        else:
            all_files = self.__get_all_files(remotepath, remote=True)
            for file in all_files:

                local_filename = file.replace(remotepath, localpath)
                local_path = os.path.dirname(local_filename)
                if not os.path.exists(local_path):
                    os.makedirs(local_path)
                self.sftp.get(file, local_filename)

    def run_shell(self, command):
        command = "bash -lc '{}'".format(command)
        stdin, stdout, stderr = self.ssh.exec_command(command, get_pty=True)
        out = stdout.read().decode()
        error = stderr.read().decode()
        return out
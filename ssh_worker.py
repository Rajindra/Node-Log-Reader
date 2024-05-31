from PyQt6.QtCore import QThread, pyqtSignal
from paramiko import SSHClient, AutoAddPolicy

class SSHCheckWorker(QThread):
    signal = pyqtSignal(str, str)

    def __init__(self, host, username):
        super().__init__()
        self.host = host
        self.username = username

    def run(self):
        if self.check_ssh_connection(self.host, self.username):
            self.signal.emit('SSH target is live', 'green')
        else:
            self.signal.emit('SSH target is not live', 'red')

    def check_ssh_connection(self, host, username):
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        try:
            client.connect(host, username=username)
            client.close()
            return True
        except Exception as e:
            return False

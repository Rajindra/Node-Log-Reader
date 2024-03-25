import os
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QComboBox, QLabel, QMessageBox, QPlainTextEdit, QCheckBox
from PyQt6.QtCore import Qt
import paramiko
from scp import SCPClient
import threading
import re

local_output_file_path = r'logCollector.log'

class NodeLogReader(QWidget):
    def __init__(self):
        super().__init__()
        self.initializeUI()

    def initializeUI(self):
        self.setWindowTitle('Node Logs Collector')
        self.setGeometry(100, 100, 600, 500)

        self.layout = QVBoxLayout()


        self.command = QLineEdit()
        self.command.setPlaceholderText('Enter your command')
        self.layout.addWidget(self.command)

        self.host_name = QComboBox()
        self.host_name.setEditable(True)
        self.host_name.addItems(["gotsva1739.got.volvocars.net"])
        self.layout.addWidget(self.host_name)

        self.user_name = QComboBox()
        self.user_name.setEditable(True)
        self.user_name.addItems(["hiluser", "sprite", "hulk"])
        self.layout.addWidget(self.user_name)

        self.node_name = QComboBox()
        self.node_name.setEditable(True)
        self.node_name.addItems(["HPA", "HPB", "USB1", "USB2", "RIG"])
        self.layout.addWidget(self.node_name)

        self.label = QLabel("Ready")
        self.layout.addWidget(self.label)

        button = QPushButton('Download logs')
        button.clicked.connect(self.onButtonClick)
        self.layout.addWidget(button)

        helpButton = QPushButton('Help')
        helpButton.clicked.connect(self.showHelpDialog)
        self.layout.addWidget(helpButton)

        self.myCheckBox = QCheckBox("Enable payload")
        self.myCheckBox.stateChanged.connect(self.checkboxChanged)
        self.layout.addWidget(self.myCheckBox)

        #commandInput = QPlainTextEdit()
        #commandInput.setPlaceholderText("Enter your payload")
        #self.layout.addWidget(commandInput)
        self.payload = QPlainTextEdit()

        self.setLayout(self.layout)


    def onButtonClick(self):
        threading.Thread(target=self.downloadLogs, daemon=True).start()

    def showHelpDialog(self):
        helpText = """Thank you for using Node log collector.

        For feedback or suggestions, please contact me at:
        tharindu.piyasekara@volvocars.com

        Your feedback is highly appreciated!
        """
        QMessageBox.information(self, 'Help & Feedback', helpText)

    def downloadLogs(self):
        username = self.user_name.currentText()
        linux_server_ip = self.host_name.currentText()
        node_name = self.node_name.currentText()
        cmd = self.command.text()

        self.updateStatusLabel("Connecting...")

        remote_script_path = '/home/hiluser/MyCommander.py'

        try:
            # Initialize SSH connection
            with paramiko.SSHClient() as ssh:
                ssh.load_system_host_keys()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(linux_server_ip, username=username)
                self.updateStatusLabel("Connected to the server.")

                if node_name == "RIG":
                    if self.myCheckBox.isChecked():
                        payload = self.payload.toPlainText().splitlines()
                        ssh_command = f'export PATH=$PATH:/opt/python3.8/bin/swut && cd /home/hiluser'
                        self.executeRemote(ssh, ssh_command)
                        for line in payload:
                            print(line)
                            parts = line.split(',')
                            #ssh_command = f'cd /home/hiluser && /opt/python3.8/bin/{cmd} >> /home/hiluser/logCollector.log'
                            ssh_command = f'/opt/python3.8/bin/{parts[0].strip()} | tee -a /home/hiluser/logCollector.log'
                            self.updateStatusLabel("Running RIG cmd: {parts[0]}")
                            self.executeRemote(ssh, ssh_command, validation=parts[1])
                    else:
                        ssh_command = f'cd /home/hiluser && {cmd} >> /home/hiluser/logCollector.log'
                        self.updateStatusLabel("Running RIG cmds")
                        self.executeRemote(ssh, ssh_command)
                else :
                    ssh_command = f'python3.8 {remote_script_path} \'{cmd}\' -o {local_output_file_path} -p {node_name}'
                    self.updateStatusLabel("Executing node command")
                    self.executeRemote(ssh, ssh_command, "MyCommander.py", remote_script_path)

                self.downloadFile(ssh)

        except Exception as e:
            self.updateStatusLabel(f"Error: {str(e)}")

    def updateStatusLabel(self, message):
        self.label.setText(message)
        QApplication.processEvents()

    def executeRemote(self, ssh, ssh_command, script_file_name=None, script_path=None, validation=None):
        self.updateStatusLabel(f"executeRemote: {ssh_command}")

        if script_file_name is not None and script_path is not None:
            script_file = self.get_resource_path(script_file_name)
            with SCPClient(ssh.get_transport()) as scp:
                scp.put(script_file, script_path)
                self.updateStatusLabel("File uploaded to server.")

        match = False
        stdin, stdout, stderr = ssh.exec_command(ssh_command, get_pty=True)

        if validation is not None:
            for line in iter(stdout.readline, ""):
                #validator_pattern = {validation}
                pattern = r"Raw response: " + validation.strip()
                match = re.match(pattern, line.strip())
                if match:
                    match = True
                    break

            if match:
                print("Verified")
            else:
                print("Failed")


    def downloadFile(self, ssh):
        remote_output_file_path = '/home/hiluser/logCollector.log'
        with SCPClient(ssh.get_transport()) as scp:
            scp.get(remote_output_file_path, local_output_file_path)
            self.updateStatusLabel(f"Output file copied to {local_output_file_path}")

    def get_resource_path(self, relative_path):
        """Get the absolute path to the resource, works for dev and for PyInstaller."""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def checkboxChanged(self):
        if self.myCheckBox.isChecked():
            print("Checkbox is checked.")
            self.payload.setVisible(True)
            self.layout.addWidget(self.payload)
            self.updateStatusLabel("Payload mode enabled")
        else:
            print("Checkbox is unchecked.")
            self.payload.setVisible(False)
            self.layout.addWidget(self.payload)
            self.updateStatusLabel("Payload mode disabled")


def main():
    app = QApplication(sys.argv)
    window = NodeLogReader()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

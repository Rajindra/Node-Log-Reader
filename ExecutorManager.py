import os
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QComboBox, QLabel, QMessageBox, QPlainTextEdit, QCheckBox, QProgressBar, QFileDialog
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import paramiko
from scp import SCPClient
import logging
import time
from utils import load_rig_list 

local_output_file_path = r'logCollector.log'
hi_comander_path = '/home/hiluser/recovery'
remote_script_path = '/home/hiluser/MyCommander.py'

# Configure logging
logging.basicConfig(filename='application.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class SSHWorker(QThread):
    progressChanged = pyqtSignal(int)
    statusChanged = pyqtSignal(str)
    completed = pyqtSignal()

    def __init__(self, username, linux_server_ip, node_name, cmd, payload, checkbox_checked):
        super().__init__()
        self.username = username
        self.linux_server_ip = linux_server_ip
        self.node_name = node_name
        self.cmd = cmd
        self.payload = payload
        self.checkbox_checked = checkbox_checked

    def run(self):
        try:
            self.statusChanged.emit("Connecting...")
            with paramiko.SSHClient() as ssh:
                ssh.load_system_host_keys()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(self.linux_server_ip, username=self.username)
                self.statusChanged.emit("Connected to the server.")
                self.setupRig(ssh)

                if self.node_name == "RIG":
                    if self.checkbox_checked:
                        payload_lines = self.payload.splitlines()
                        self.executeRemote(ssh, "cd /home/hiluser")
                        number_of_lines = len(payload_lines)

                        for index, line in enumerate(payload_lines, start=1):
                            logging.info(line)
                            command = f'{line} >> /home/hiluser/logCollector.log'
                            self.executeRemote(ssh, command)
                            self.statusChanged.emit("Executing node commands")
                            self.progressChanged.emit(int((index / number_of_lines) * 100))
                    else:
                        ssh_command = f'cd /home/hiluser && {self.cmd} >> /home/hiluser/logCollector.log'
                        self.statusChanged.emit("Running RIG cmds")
                        self.executeRemote(ssh, ssh_command)
                        self.progressChanged.emit(100)
                else:
                    if self.checkbox_checked:
                        payload_lines = self.payload.splitlines()
                        commands = ['cd /home/hiluser']
                        for line in payload_lines:
                            logging.info(line)
                            command = f'python3.8 ./MyCommander.py \'{line}\' -o /home/hiluser/logCollector.log -p {self.node_name}'
                            commands.append(command)

                        combined_command = ' && '.join(commands)

                        self.statusChanged.emit("Executing node commands")
                        self.executeRemote(ssh, combined_command)
                    else:
                        command = f'python3.8 ./MyCommander.py \'{self.cmd}\' -o /home/hiluser/logCollector.log -p {self.node_name}'
                        self.statusChanged.emit("Executing node command")
                        self.executeRemote(ssh, command)

                self.downloadFile(ssh)
                ssh.close()
                self.statusChanged.emit("All commands executed.")
                self.completed.emit()

        except Exception as e:
            logging.error(f"Exception: {str(e)}")
            self.statusChanged.emit(f"Error: {str(e)}")
            self.completed.emit()

    def setupRig(self, ssh):
        logging.info("setupRig")
        script_file = ExecutorManager.get_resource_path("resources/MyCommander.py")
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(script_file, remote_script_path)
            self.statusChanged.emit("Commander File uploaded to server.")

        hi_commander = ExecutorManager.get_resource_path("resources/recovery")
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(hi_commander, hi_comander_path)
            self.statusChanged.emit("HI commander uploaded to server.")

    def executeRemote(self, ssh, ssh_command):
        self.statusChanged.emit(f"Executing: {ssh_command[:30]}")
        stdin, stdout, stderr = ssh.exec_command(ssh_command, get_pty=True)

        if ssh_command.startswith("swut"):
            ssh_command = ssh_command.replace("swut", "/opt/python3.8/bin/swut", 1)

        while not stdout.channel.exit_status_ready():
            time.sleep(1)

        output = stdout.read().decode()
        error = stderr.read().decode()

        logging.info("Command: %s", ssh_command)
        if output:
            logging.info("Output: %s", output)
        if error:
            logging.error("Error: %s", error)
        
        logging.info("ExecuteRemote Done")

    def downloadFile(self, ssh):
        remote_output_file_path = '/home/hiluser/logCollector.log'
        with SCPClient(ssh.get_transport()) as scp:
            scp.get(remote_output_file_path, local_output_file_path)
            self.statusChanged.emit(f"Output file copied to {local_output_file_path}")
            self.statusChanged.emit("Log file collection complete.")
            time.sleep(1)
        
        self.open_file()

    def open_file(self):
        relative_path = "logCollector.log"  # Update this path to your relative file location
        file_name = os.path.join(os.path.dirname(__file__), relative_path)
        
        try:
            # Read the contents of the file
            with open(file_name, 'r') as file:
                file_contents = file.read()
            
            # Display the file contents in the text edit widget
            self.text_edit.setPlainText(file_contents)
        except FileNotFoundError:
            self.text_edit.setPlainText(f"File not found: {file_name}")
        except Exception as e:
            self.text_edit.setPlainText(f"An error occurred: {str(e)}")

class ExecutorManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 500)
        self.initializeUI()

    def initializeUI(self):
        self.setWindowTitle('Ikman | Snabb')
        self.setGeometry(100, 100, 600, 500)

        self.layout = QVBoxLayout()

        self.command = QLineEdit()
        self.command.setPlaceholderText('Enter your command')
        self.layout.addWidget(self.command)

        self.host_name = QComboBox()
        self.host_name.setEditable(True)
        rig_list = load_rig_list()
        self.host_name.addItems(rig_list)
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

        self.loadButton = QPushButton('Load PayLoad from File', self)
        self.loadButton.clicked.connect(self.loadFile)
        self.layout.addWidget(self.loadButton)

        button = QPushButton('Run!')
        button.clicked.connect(self.onButtonClick)
        self.layout.addWidget(button)

        button_swut = QPushButton('SWUT Generator')
        button_swut.clicked.connect(self.onSwutButtonClick)
        self.layout.addWidget(button_swut)

        helpButton = QPushButton('Help')
        helpButton.clicked.connect(self.showHelpDialog)
        self.layout.addWidget(helpButton)

        self.myCheckBox = QCheckBox("Enable payload")
        self.myCheckBox.stateChanged.connect(self.checkboxChanged)
        self.layout.addWidget(self.myCheckBox)

        self.payload = QPlainTextEdit()

        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)
        self.layout.addWidget(self.progressBar)

        self.setLayout(self.layout)

    def onButtonClick(self):
        username = self.user_name.currentText()
        linux_server_ip = self.host_name.currentText()
        node_name = self.node_name.currentText()
        cmd = self.command.text()
        payload = self.payload.toPlainText()
        checkbox_checked = self.myCheckBox.isChecked()

        self.progressBar.setValue(0)

        self.worker = SSHWorker(username, linux_server_ip, node_name, cmd, payload, checkbox_checked)
        self.worker.progressChanged.connect(self.progressBar.setValue)
        self.worker.statusChanged.connect(self.updateStatusLabel)
        self.worker.completed.connect(self.onWorkerCompleted)
        self.worker.start()

    def loadFile(self):
        # Open a file dialog to select a file
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)")
        
        if fileName:
            try:
                # Read the file content and load it into the QTextEdit widget
                with open(fileName, 'r') as file:
                    fileContent = file.read()
                    self.payload.setPlainText(fileContent)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not read file: {str(e)}")

    def onWorkerCompleted(self):
        self.updateStatusLabel("Task completed.")

    def onSwutButtonClick(self):
        logging.info("WIP : Swut Generator")

    def showHelpDialog(self):
        helpText = """Thank you for using Node log collector.

        For feedback or suggestions, please contact me at:
        tharindu.piyasekara@volvocars.com

        Your feedback is highly appreciated!
        """
        QMessageBox.information(self, 'Help & Feedback', helpText)

    def updateStatusLabel(self, message):
        logging.info(message)
        self.label.setText(message)
        QApplication.processEvents()

    def checkboxChanged(self):
        if self.myCheckBox.isChecked():
            self.payload.setVisible(True)
            self.layout.addWidget(self.payload)
            self.updateStatusLabel("Payload mode enabled")
        else:
            self.payload.setVisible(False)
            self.layout.addWidget(self.payload)
            self.updateStatusLabel("Payload mode disabled")

    @staticmethod
    def get_resource_path(relative_path):
        """Get the absolute path to the resource, works for dev and for PyInstaller."""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

def main():
    app = QApplication(sys.argv)
    window = ExecutorManager()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

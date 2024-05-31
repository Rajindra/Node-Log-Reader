from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QLineEdit, QComboBox, QMenuBar, QMenu, QVBoxLayout, QGridLayout
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon, QFileSystemModel, QAction
from PyQt6.QtCore import QDir
from custom_list_view import CustomListView
from ssh_worker import SSHCheckWorker
from utils import get_remote_files
from utils import load_rig_list
import os

class HILRigManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('HIL rig manager')
        self.initUI()

    def initUI(self):
        main_layout = QGridLayout()

        rig_information_layout = self.create_rig_information_layout()
        local_layout = self.create_local_layout()
        remote_layout = self.create_remote_layout()
        vertical_layout = self.create_vertical_layout()

        main_layout.addLayout(rig_information_layout, 1,1,1,3)
        main_layout.addLayout(local_layout, 2, 1)
        main_layout.addLayout(remote_layout,2, 2)
        main_layout.addLayout(vertical_layout,2,3)

        self.setLayout(main_layout)
        self.setWindowTitle('HILRigManager')
        self.setGeometry(300, 300, 1200, 800)
        self.show()

    def create_rig_information_layout(self):
        layout = QHBoxLayout()
        self.rig_info_combobox = QComboBox()
        rig_list = load_rig_list()
        self.rig_info_combobox.addItems(rig_list)
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_rig)
        self.ssh_status_label = QLabel()

        layout.addWidget(QLabel("Rig Information:"))
        layout.addWidget(self.rig_info_combobox)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.ssh_status_label)

        return layout

    def create_local_layout(self):
        layout = QVBoxLayout()

        local_but_text_layout = QHBoxLayout()
        self.local_model = QFileSystemModel()
        self.local_model.setRootPath(QDir.homePath())
        self.local_view = CustomListView()
        self.local_view.setModel(self.local_model)
        self.local_view.setRootIndex(self.local_model.index(QDir.homePath()))
        self.local_view.setFixedSize(600, 800)
        self.local_view.doubleClicked.connect(self.on_local_view_double_clicked)

        local_up_button = QPushButton()
        local_up_button.setIcon(QIcon.fromTheme('go-up'))
        local_up_button.clicked.connect(self.on_local_view_up_button_clicked)

        self.local_path_edit = QLineEdit()
        self.local_path_edit.setText(QDir.homePath())
        self.local_path_edit.returnPressed.connect(lambda: self.local_view.setRootIndex(self.local_model.index(self.local_path_edit.text())))

        local_but_text_layout.addWidget(local_up_button)
        local_but_text_layout.addWidget(self.local_path_edit)
        layout.addLayout(local_but_text_layout)
        layout.addWidget(self.local_view)
        return layout

    def create_remote_layout(self):
        layout = QVBoxLayout()
        remote_but_text_layout = QHBoxLayout()

        self.remote_model = QStandardItemModel()

        placeholder_item = QStandardItem(QIcon.fromTheme('dialog-information'), "No active remote connection")
        self.remote_model.appendRow(placeholder_item)

        self.remote_view = CustomListView()
        self.remote_view.setModel(self.remote_model)
        self.remote_view.setFixedSize(600, 800)
        self.remote_view.doubleClicked.connect(self.on_remote_view_double_clicked)

        remote_up_button = QPushButton()
        remote_up_button.setIcon(QIcon.fromTheme('go-up'))
        remote_up_button.clicked.connect(self.on_remote_view_up_button_clicked)

        self.remote_path_edit = QLineEdit()
        self.remote_path_edit.setText('.')
        self.remote_path_edit.returnPressed.connect(self.on_remote_path_edit_return_pressed)

        remote_but_text_layout.addWidget(remote_up_button)
        remote_but_text_layout.addWidget(self.remote_path_edit)
        layout.addLayout(remote_but_text_layout)
        layout.addWidget(self.remote_view)
        return layout

    def create_vertical_layout(self):
        layout = QVBoxLayout()

        upload_button = QPushButton('Upload')
        jump_login_button = QPushButton('Jump Login')
        get_logs_button = QPushButton('Get Logs')

        layout.addWidget(upload_button)
        layout.addWidget(jump_login_button)
        layout.addWidget(get_logs_button)

        menu_bar = QMenuBar()
        file_menu = QMenu('Log', menu_bar)
        file_menu.addAction('Get DLT logs')
        file_menu.addAction('Get SLOGs')
        file_menu.addSeparator()
        log_level_menu = QMenu('Log Level', file_menu)
        log_levels = ['Info', 'Debug', 'Warning', 'Error']
        for log_level in log_levels:
            action = QAction(log_level, log_level_menu)
            action.setCheckable(True)
            log_level_menu.addAction(action)

        file_menu.addMenu(log_level_menu)

        button = QPushButton('Log')
        button.setMenu(file_menu)

        layout.addWidget(button)
        return layout
    
    def connect_to_rig(self):
        self.host_name =  self.rig_info_combobox.currentText()
        self.worker = SSHCheckWorker(self.host_name, 'hiluser')
        self.worker.signal.connect(self.update_ssh_status_label)
        self.worker.start()

        self.remote_model.clear()
        for file_type, file_name in get_remote_files():
            if file_type == 'folder':
                item = QStandardItem(QIcon.fromTheme('folder'), file_name)
            else:
                item = QStandardItem(QIcon.fromTheme('text-x-generic'), file_name)
            self.remote_model.appendRow(item)

    def update_ssh_status_label(self, text, color):
        self.ssh_status_label.setText(text)
        self.ssh_status_label.setStyleSheet(f'color: {color}')

    def on_remote_view_double_clicked(self, index):
        clicked_item_name = self.remote_model.itemFromIndex(index).text()
        current_path = self.remote_path_edit.text()
        clicked_path = os.path.join(current_path, clicked_item_name)

        self.remote_model.clear()
        for file_type, file_name in get_remote_files(clicked_path):
            if file_type == 'folder':
                item = QStandardItem(QIcon.fromTheme('folder'), file_name)
            else:
                item = QStandardItem(QIcon.fromTheme('text-x-generic'), file_name)
            self.remote_model.appendRow(item)

        self.remote_path_edit.setText(clicked_path)

    def on_local_view_double_clicked(self, index):
        clicked_path = self.local_model.filePath(index)
        self.local_view.setRootIndex(self.local_model.index(clicked_path))
        self.local_path_edit.setText(clicked_path)

    def on_remote_path_edit_return_pressed(self):
        entered_path = self.remote_path_edit.text()
        files = get_remote_files(entered_path)

        if files is not None:
            self.remote_model.clear()
            for file_type, file_name in files:
                if file_type == 'folder':
                    item = QStandardItem(QIcon.fromTheme('folder'), file_name)
                else:
                    item = QStandardItem(QIcon.fromTheme('text-x-generic'), file_name)
                self.remote_model.appendRow(item)
            self.remote_view.setRootIndex(self.remote_model.indexFromItem(item))
        else:
            print("Invalid directory.")

    def on_local_view_up_button_clicked(self):
        current_index = self.local_view.rootIndex()

        if current_index.parent().isValid():
            self.local_view.setRootIndex(current_index.parent())
            self.local_path_edit.setText(self.local_model.filePath(current_index.parent()))
        else:
            print("Already at the top level.")

    def on_remote_view_up_button_clicked(self):
        current_path = self.remote_path_edit.text()

        if current_path != '/':
            parent_path = os.path.dirname(current_path)
            self.remote_model.clear()
            for file_type, file_name in get_remote_files(parent_path):
                if file_type == 'folder':
                    item = QStandardItem(QIcon.fromTheme('folder'), file_name)
                else:
                    item = QStandardItem(QIcon.fromTheme('text-x-generic'), file_name)
                self.remote_model.appendRow(item)

            self.remote_path_edit.setText(parent_path)
        else:
            print("Already at the top level.")


import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QMdiArea, QMdiSubWindow, QLabel, QFrame
from PyQt6.QtGui import QIcon, QDragEnterEvent, QDropEvent, QDrag
from PyQt6.QtCore import Qt, QMimeData, QSize
from hil_rig_manager import HILRigManager
from executor_manager import ExecutorManager

class DraggableLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()

            drag.setMimeData(mime_data)
            drag.setHotSpot(event.position().toPoint() - self.rect().topLeft())

            drop_action = drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        position = event.position().toPoint()
        self.move(position)
        event.setDropAction(Qt.DropAction.MoveAction)
        event.accept()

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Ikman | Snabb')
        self.setGeometry(100, 100, 1200, 800)
        self.setAcceptDrops(True)

        self.init_ui()

    def init_ui(self):
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        
        toolbar = self.addToolBar("Main Toolbar")
        
        open_hil_rig_manager_action = QPushButton('Open HIL Rig Manager')
        #open_hil_rig_manager_action.setIcon(QIcon('path/to/your/icon.png'))
        open_hil_rig_manager_action.clicked.connect(self.open_hil_rig_manager)
        toolbar.addWidget(open_hil_rig_manager_action)

        open_executor_manager_action = QPushButton('Open Executor Manager')
        #open_executor_manager_action.setIcon(QIcon('path/to/your/icon.png'))
        open_executor_manager_action.clicked.connect(self.open_executor_manager)
        toolbar.addWidget(open_executor_manager_action)


        self.showMaximized()

    def open_hil_rig_manager(self):
        hil_rig_manager = HILRigManager()
        sub_window = QMdiSubWindow()
        sub_window.setWidget(hil_rig_manager)
        sub_window.setWindowTitle('HIL Rig Manager')
        sub_window.setMinimumSize(600, 500)
        self.mdi_area.addSubWindow(sub_window)
        sub_window.show()

    def open_executor_manager(self):
        executor_manager = ExecutorManager()
        sub_window = QMdiSubWindow()
        sub_window.setWidget(executor_manager)
        sub_window.setWindowTitle('Executor Manager')
        sub_window.setMinimumSize(600, 500)
        self.mdi_area.addSubWindow(sub_window)
        sub_window.show()

def main():
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.showMaximized()  # Start the application in full screen
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

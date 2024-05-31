from PyQt6.QtWidgets import QListView, QMenu
from PyQt6.QtGui import QAction

class CustomListView(QListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def contextMenuEvent(self, event):
        menu = QMenu()
        menu.addAction('Upload')
        menu.addAction('Permissions')
        menu.addSeparator()

        log_level_menu = QMenu('Run test', menu)
        log_levels = ['Robot test', 'Debug', 'Run executable', 'Memory profiler']
        for log_level in log_levels:
            action = QAction(log_level, log_level_menu)
            log_level_menu.addAction(action)

        menu.addMenu(log_level_menu)
        menu.exec(event.globalPos())

import uuid
from datetime import datetime
from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QWidget,
)

from ..auth import AuthManager
from ..config import APP_NAME
from ..models import ContentPlan, ContentStatus, Platform
from ..scheduler_engine import SchedulerEngine
from ..storage import SecureStorage
from .about_dialog import AboutDialog
from .dashboard_widget import DashboardWidget
from .log_widget import LogWidget
from .planner_widget import PlannerWidget
from .session_widget import SessionWidget


class MainWindow(QMainWindow):
    def __init__(self, storage: SecureStorage, auth_manager: AuthManager, scheduler: SchedulerEngine) -> None:
        super().__init__()
        self.storage = storage
        self.auth_manager = auth_manager
        self.scheduler = scheduler
        self.setWindowTitle(APP_NAME)
        self.resize(1200, 720)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.addItem(QListWidgetItem("Dashboard"))
        self.sidebar.addItem(QListWidgetItem("Oturumlar"))
        self.sidebar.addItem(QListWidgetItem("Planlama"))
        self.sidebar.addItem(QListWidgetItem("Loglar"))
        self.sidebar.addItem(QListWidgetItem("Hakkında"))
        self.sidebar.currentRowChanged.connect(self._on_change)

        self.stack = QStackedWidget()
        self.dashboard = DashboardWidget(storage, auth_manager)
        self.sessions = SessionWidget(auth_manager)
        self.planner = PlannerWidget(storage, auth_manager, scheduler)
        self.logs = LogWidget(storage)
        self.about = AboutDialog()

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.sessions)
        self.stack.addWidget(self.planner)
        self.stack.addWidget(self.logs)
        self.stack.addWidget(self.about)

        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack)

        self.setCentralWidget(container)
        self.sidebar.setCurrentRow(0)

    def _on_change(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.dashboard.refresh()
        elif index == 1:
            self.sessions.refresh()
        elif index == 2:
            self.planner.refresh()
        elif index == 3:
            self.logs.refresh()


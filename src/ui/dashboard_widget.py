from datetime import datetime
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QGridLayout, QWidget

from ..auth import AuthManager
from ..models import ContentStatus, Platform
from ..storage import SecureStorage


class DashboardWidget(QWidget):
    def __init__(self, storage: SecureStorage, auth_manager: AuthManager) -> None:
        super().__init__()
        self.storage = storage
        self.auth_manager = auth_manager

        self.today_label = QLabel()
        self.week_label = QLabel()
        self.sent_label = QLabel()
        self.active_label = QLabel()

        grid = QGridLayout(self)
        grid.addWidget(QLabel("Bugün planlı içerik"), 0, 0)
        grid.addWidget(self.today_label, 0, 1)
        grid.addWidget(QLabel("Bu hafta planlı"), 1, 0)
        grid.addWidget(self.week_label, 1, 1)
        grid.addWidget(QLabel("Son 7 gün gönderilen"), 2, 0)
        grid.addWidget(self.sent_label, 2, 1)
        grid.addWidget(QLabel("Aktif hesaplar"), 3, 0)
        grid.addWidget(self.active_label, 3, 1)

        self.refresh()
        timer = QTimer(self)
        timer.timeout.connect(self.refresh)
        timer.start(5000)

    def refresh(self) -> None:
        plans = self.storage.load_plans()
        today = datetime.utcnow().date()
        week = datetime.utcnow().isocalendar().week
        today_count = sum(1 for p in plans if p.scheduled_for.date() == today)
        week_count = sum(1 for p in plans if p.scheduled_for.isocalendar().week == week)
        sent_count = sum(1 for p in plans if p.status == ContentStatus.SENT)
        accounts = [acc.platform.value for acc in self.auth_manager.accounts]

        self.today_label.setText(str(today_count))
        self.week_label.setText(str(week_count))
        self.sent_label.setText(str(sent_count))
        self.active_label.setText(", ".join(accounts) if accounts else "Aktif oturum yok")


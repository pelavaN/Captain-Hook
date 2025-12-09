from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from ..storage import SecureStorage


class LogWidget(QWidget):
    def __init__(self, storage: SecureStorage) -> None:
        super().__init__()
        self.storage = storage
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Zaman", "Platform", "İçerik", "Mesaj"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self) -> None:
        logs = self.storage.load_logs()
        self.table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            self.table.setItem(row, 0, QTableWidgetItem(log.timestamp.strftime("%Y-%m-%d %H:%M:%S")))
            self.table.setItem(row, 1, QTableWidgetItem(log.platform.value))
            self.table.setItem(row, 2, QTableWidgetItem(log.content_id))
            self.table.setItem(row, 3, QTableWidgetItem(f"{log.status.value}: {log.message}"))


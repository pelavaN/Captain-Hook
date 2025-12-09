import uuid
from datetime import datetime
from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDateTimeEdit,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..auth import AuthManager
from ..models import ContentPlan, ContentStatus, Platform
from ..scheduler_engine import SchedulerEngine
from ..storage import SecureStorage


class PlannerWidget(QWidget):
    def __init__(self, storage: SecureStorage, auth_manager: AuthManager, scheduler: SchedulerEngine) -> None:
        super().__init__()
        self.storage = storage
        self.auth_manager = auth_manager
        self.scheduler = scheduler

        layout = QHBoxLayout(self)

        form_container = QWidget()
        form = QFormLayout(form_container)

        self.title_field = QLineEdit()
        self.description_field = QTextEdit()
        self.hashtags_field = QLineEdit()
        self.youtube_tags_field = QLineEdit()
        self.media_path_field = QLineEdit()
        self.thumbnail_path_field = QLineEdit()
        self.datetime_field = QDateTimeEdit(datetime.now())
        self.datetime_field.setCalendarPopup(True)

        media_btn = QPushButton("Dosya Seç")
        media_btn.clicked.connect(self._select_media)
        thumb_btn = QPushButton("Thumbnail Seç")
        thumb_btn.clicked.connect(self._select_thumb)

        self.instagram_chk = QCheckBox("Instagram")
        self.youtube_chk = QCheckBox("YouTube")

        form.addRow("Başlık / Açıklama", self.title_field)
        form.addRow("Detaylı Açıklama", self.description_field)
        form.addRow("Instagram Hashtagleri", self.hashtags_field)
        form.addRow("YouTube Etiketleri (virgülle)", self.youtube_tags_field)
        form.addRow("Medya Dosyası", self.media_path_field)
        form.addRow("", media_btn)
        form.addRow("Thumbnail", self.thumbnail_path_field)
        form.addRow("", thumb_btn)
        form.addRow("Planlanan Tarih/Saat", self.datetime_field)
        form.addRow("Platformlar", self._platform_row())

        save_btn = QPushButton("Planı Kaydet")
        save_btn.clicked.connect(self._save_plan)
        form.addRow(save_btn)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Platform", "Tarih", "Durum", "Medya", "Hata"])
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(form_container, 1)
        layout.addWidget(self.table, 2)
        self.refresh()

    def _platform_row(self) -> QWidget:
        w = QWidget()
        row = QHBoxLayout(w)
        row.addWidget(self.instagram_chk)
        row.addWidget(self.youtube_chk)
        row.addStretch()
        return w

    def _select_media(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Medya Seç")
        if path:
            self.media_path_field.setText(path)

    def _select_thumb(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Thumbnail Seç")
        if path:
            self.thumbnail_path_field.setText(path)

    def _save_plan(self) -> None:
        platforms: List[Platform] = []
        if self.instagram_chk.isChecked():
            platforms.append(Platform.INSTAGRAM)
        if self.youtube_chk.isChecked():
            platforms.append(Platform.YOUTUBE)

        plan = ContentPlan(
            id=str(uuid.uuid4()),
            title=self.title_field.text(),
            description=self.description_field.toPlainText(),
            hashtags=self.hashtags_field.text(),
            youtube_tags=[t.strip() for t in self.youtube_tags_field.text().split(",") if t.strip()],
            media_path=self.media_path_field.text(),
            thumbnail_path=self.thumbnail_path_field.text() or None,
            scheduled_for=self.datetime_field.dateTime().toPython(),
            platforms=platforms,
        )
        plans = self.storage.load_plans()
        plans.append(plan)
        self.storage.save_plans(plans)
        self.scheduler.schedule_plan(plan)
        self.refresh()

    def refresh(self) -> None:
        plans = self.storage.load_plans()
        self.table.setRowCount(len(plans))
        for row, plan in enumerate(plans):
            self.table.setItem(row, 0, QTableWidgetItem(plan.id))
            self.table.setItem(row, 1, QTableWidgetItem(", ".join(p.value for p in plan.platforms)))
            self.table.setItem(row, 2, QTableWidgetItem(plan.scheduled_for.strftime("%Y-%m-%d %H:%M")))
            self.table.setItem(row, 3, QTableWidgetItem(plan.status.value))
            self.table.setItem(row, 4, QTableWidgetItem(plan.media_path))
            self.table.setItem(row, 5, QTableWidgetItem(plan.last_error or ""))


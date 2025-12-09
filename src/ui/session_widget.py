from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..auth import AuthManager
from ..models import Platform


class SessionWidget(QWidget):
    def __init__(self, auth_manager: AuthManager) -> None:
        super().__init__()
        self.auth_manager = auth_manager
        layout = QVBoxLayout(self)

        self.instagram_box = self._build_box(Platform.INSTAGRAM)
        self.youtube_box = self._build_box(Platform.YOUTUBE)

        layout.addWidget(self.instagram_box)
        layout.addWidget(self.youtube_box)
        layout.addStretch()

        self.refresh()
        timer = QTimer(self)
        timer.timeout.connect(self.refresh)
        timer.start(3000)

    def _build_box(self, platform: Platform) -> QGroupBox:
        box = QGroupBox(f"{platform.value.title()} Oturumu")
        grid = QGridLayout(box)
        grid.addWidget(QLabel("Kullanıcı Adı"), 0, 0)
        username = QLineEdit()
        username.setObjectName(f"username-{platform.value}")
        grid.addWidget(username, 0, 1)

        connect_btn = QPushButton("OAuth ile bağlan")
        connect_btn.clicked.connect(lambda: self.auth_manager.open_oauth(platform))
        fake_btn = QPushButton("Test Modu: Fake Token")
        fake_btn.clicked.connect(lambda: self._fake_login(platform, username))
        disconnect_btn = QPushButton("Çıkış Yap")
        disconnect_btn.clicked.connect(lambda: self._disconnect(platform))

        grid.addWidget(connect_btn, 1, 0)
        grid.addWidget(fake_btn, 1, 1)
        grid.addWidget(disconnect_btn, 2, 0, 1, 2)

        self._status_label = QLabel()
        self._status_label.setObjectName(f"status-{platform.value}")
        grid.addWidget(self._status_label, 3, 0, 1, 2)
        return box

    def refresh(self) -> None:
        for platform in Platform:
            status_label = self.findChild(QLabel, f"status-{platform.value}")
            account = self.auth_manager.get_account(platform)
            if account:
                delta = datetime.utcnow() - account.connected_at
                status_label.setText(
                    f"Bağlı: {account.username} (Oturum {delta.seconds // 3600} saat {delta.seconds // 60 % 60} dakikadır aktif)"
                )
            else:
                status_label.setText("Bağlı değil")

    def _fake_login(self, platform: Platform, username_field: QLineEdit) -> None:
        username = username_field.text().strip() or "demo"
        self.auth_manager.connect_with_fake_token(platform, username)
        self.refresh()

    def _disconnect(self, platform: Platform) -> None:
        self.auth_manager.disconnect(platform)
        self.refresh()


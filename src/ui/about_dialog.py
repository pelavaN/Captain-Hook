from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ..config import APP_NAME, DEVELOPER_NAME


class AboutDialog(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Hakkında")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<h2>{APP_NAME}</h2>"))
        layout.addWidget(QLabel("Sosyal medya içerik planlama ve otomatik paylaşım aracı."))
        layout.addWidget(QLabel(f"Uygulama Geliştiricisi: {DEVELOPER_NAME}"))
        layout.addWidget(QLabel("Instagram & YouTube için planlama, loglama ve zamanlama özellikleri içerir."))
        layout.addWidget(QLabel("OAuth bilgilerinizi Ayarlar kısmındaki .env dosyasında tanımlayın."))


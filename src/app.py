import logging
import sys
import uuid
from datetime import datetime

from PySide6.QtWidgets import QApplication

from .auth import AuthManager
from .config import APP_NAME, ensure_data_dir
from .models import ContentPlan, Platform
from .platform_clients import dispatch_plan
from .scheduler_engine import SchedulerEngine
from .storage import SecureStorage
from .ui.main_window import MainWindow

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def build_app() -> QApplication:
    ensure_data_dir()
    storage = SecureStorage()
    auth_manager = AuthManager(storage)

    def dispatcher(plan: ContentPlan, platform: Platform) -> bool:
        return dispatch_plan(plan, platform, auth_manager.get_account)

    scheduler = SchedulerEngine(storage, dispatcher)
    scheduler.hydrate_existing(storage.load_plans())
    scheduler.start()

    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName(APP_NAME)

    window = MainWindow(storage, auth_manager, scheduler)
    window.show()
    return qt_app


def main():
    app = build_app()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

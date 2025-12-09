import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Social Scheduler Desktop"
DEVELOPER_NAME = "Burak BEKER"
DATA_DIR = Path.home() / ".social_scheduler"
STATE_FILE = DATA_DIR / "app_state.json"
LOG_FILE = DATA_DIR / "activity.log"
SECRET_KEY = os.getenv("APP_SECRET_KEY") or "development-secret-key-change-me"
TIMEZONE = os.getenv("APP_TIMEZONE", "local")

INSTAGRAM_CLIENT_ID = os.getenv("INSTAGRAM_CLIENT_ID", "")
INSTAGRAM_CLIENT_SECRET = os.getenv("INSTAGRAM_CLIENT_SECRET", "")
INSTAGRAM_REDIRECT_URI = os.getenv("INSTAGRAM_REDIRECT_URI", "http://localhost:5000/instagram/callback")

YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REDIRECT_URI = os.getenv("YOUTUBE_REDIRECT_URI", "http://localhost:5000/youtube/callback")


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from cryptography.fernet import Fernet, InvalidToken

from .config import SECRET_KEY, STATE_FILE, ensure_data_dir
from .models import ContentPlan, LogEntry, PlatformAccount, Platform, ContentStatus


class SecureStorage:
    def __init__(self) -> None:
        ensure_data_dir()
        self.state_file = STATE_FILE
        self._fernet = Fernet(self._derive_key(SECRET_KEY))
        if not self.state_file.exists():
            self._write_state({"accounts": [], "plans": [], "logs": []})

    def _derive_key(self, secret: str) -> bytes:
        padded = secret.encode().ljust(32, b"0")[:32]
        import base64

        return base64.urlsafe_b64encode(padded)

    def _write_state(self, payload: Dict) -> None:
        with self.state_file.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)

    def _read_state(self) -> Dict:
        if not self.state_file.exists():
            return {"accounts": [], "plans": [], "logs": []}
        with self.state_file.open(encoding="utf-8") as fh:
            return json.load(fh)

    def load_accounts(self) -> List[PlatformAccount]:
        state = self._read_state()
        accounts = []
        for item in state.get("accounts", []):
            try:
                decrypted = self._fernet.decrypt(item["access_token"].encode()).decode()
            except (InvalidToken, KeyError):
                decrypted = ""
            accounts.append(
                PlatformAccount(
                    platform=Platform(item["platform"]),
                    username=item["username"],
                    access_token=decrypted,
                    refresh_token=item.get("refresh_token"),
                    expires_at=datetime.fromisoformat(item["expires_at"]) if item.get("expires_at") else None,
                    connected_at=datetime.fromisoformat(item["connected_at"]),
                )
            )
        return accounts

    def save_accounts(self, accounts: List[PlatformAccount]) -> None:
        state = self._read_state()
        state["accounts"] = [
            {
                "platform": acc.platform.value,
                "username": acc.username,
                "access_token": self._fernet.encrypt(acc.access_token.encode()).decode(),
                "refresh_token": acc.refresh_token,
                "expires_at": acc.expires_at.isoformat() if acc.expires_at else None,
                "connected_at": acc.connected_at.isoformat(),
            }
            for acc in accounts
        ]
        self._write_state(state)

    def load_plans(self) -> List[ContentPlan]:
        state = self._read_state()
        plans = []
        for item in state.get("plans", []):
            plans.append(
                ContentPlan(
                    id=item["id"],
                    title=item["title"],
                    description=item["description"],
                    hashtags=item.get("hashtags", ""),
                    youtube_tags=item.get("youtube_tags", []),
                    media_path=item["media_path"],
                    thumbnail_path=item.get("thumbnail_path"),
                    scheduled_for=datetime.fromisoformat(item["scheduled_for"]),
                    platforms=[Platform(p) for p in item.get("platforms", [])],
                    status=ContentStatus(item.get("status", ContentStatus.PENDING.value)),
                    last_error=item.get("last_error"),
                )
            )
        return plans

    def save_plans(self, plans: List[ContentPlan]) -> None:
        state = self._read_state()
        state["plans"] = [
            {
                "id": plan.id,
                "title": plan.title,
                "description": plan.description,
                "hashtags": plan.hashtags,
                "youtube_tags": plan.youtube_tags,
                "media_path": plan.media_path,
                "thumbnail_path": plan.thumbnail_path,
                "scheduled_for": plan.scheduled_for.isoformat(),
                "platforms": [p.value for p in plan.platforms],
                "status": plan.status.value,
                "last_error": plan.last_error,
            }
            for plan in plans
        ]
        self._write_state(state)

    def load_logs(self) -> List[LogEntry]:
        state = self._read_state()
        logs = []
        for item in state.get("logs", []):
            logs.append(
                LogEntry(
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    platform=Platform(item["platform"]),
                    content_id=item["content_id"],
                    status=ContentStatus(item["status"]),
                    message=item["message"],
                )
            )
        return logs

    def append_log(self, entry: LogEntry) -> None:
        state = self._read_state()
        state.setdefault("logs", []).append(
            {
                "timestamp": entry.timestamp.isoformat(),
                "platform": entry.platform.value,
                "content_id": entry.content_id,
                "status": entry.status.value,
                "message": entry.message,
            }
        )
        self._write_state(state)


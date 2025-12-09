import webbrowser
from datetime import datetime, timedelta
from typing import Optional

from .config import (
    INSTAGRAM_CLIENT_ID,
    INSTAGRAM_CLIENT_SECRET,
    INSTAGRAM_REDIRECT_URI,
    YOUTUBE_CLIENT_ID,
    YOUTUBE_CLIENT_SECRET,
    YOUTUBE_REDIRECT_URI,
)
from .models import Platform, PlatformAccount
from .storage import SecureStorage


class AuthManager:
    def __init__(self, storage: SecureStorage) -> None:
        self.storage = storage
        self.accounts = storage.load_accounts()

    def get_account(self, platform: Platform) -> Optional[PlatformAccount]:
        for acc in self.accounts:
            if acc.platform == platform:
                return acc
        return None

    def connect_with_fake_token(self, platform: Platform, username: str) -> PlatformAccount:
        # Placeholder: replace with OAuth flow
        access_token = f"token-{platform.value}-{username}"
        account = PlatformAccount(
            platform=platform,
            username=username,
            access_token=access_token,
            refresh_token=None,
            expires_at=datetime.utcnow() + timedelta(hours=2),
            connected_at=datetime.utcnow(),
        )
        self._upsert_account(account)
        return account

    def _upsert_account(self, account: PlatformAccount) -> None:
        filtered = [a for a in self.accounts if a.platform != account.platform]
        filtered.append(account)
        self.accounts = filtered
        self.storage.save_accounts(self.accounts)

    def disconnect(self, platform: Platform) -> None:
        self.accounts = [a for a in self.accounts if a.platform != platform]
        self.storage.save_accounts(self.accounts)

    def oauth_url(self, platform: Platform) -> str:
        if platform == Platform.INSTAGRAM:
            return (
                "https://api.instagram.com/oauth/authorize"
                f"?client_id={INSTAGRAM_CLIENT_ID}&redirect_uri={INSTAGRAM_REDIRECT_URI}&response_type=code&scope=user_profile,user_media"
            )
        return (
            "https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={YOUTUBE_CLIENT_ID}&redirect_uri={YOUTUBE_REDIRECT_URI}&response_type=code&scope=https://www.googleapis.com/auth/youtube.upload"
        )

    def open_oauth(self, platform: Platform) -> None:
        url = self.oauth_url(platform)
        webbrowser.open(url)


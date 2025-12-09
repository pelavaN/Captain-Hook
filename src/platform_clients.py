import logging
import time
from pathlib import Path
from typing import Optional

import requests

from .models import ContentPlan, Platform

logger = logging.getLogger(__name__)


class InstagramClient:
    def __init__(self, access_token: str, client_id: str, client_secret: str) -> None:
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret

    def upload(self, plan: ContentPlan) -> bool:
        logger.info("Instagram post gönderimi simule ediliyor: %s", plan.id)
        time.sleep(1)
        return True


class YouTubeClient:
    def __init__(self, access_token: str, client_id: str, client_secret: str) -> None:
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret

    def upload(self, plan: ContentPlan) -> bool:
        logger.info("YouTube video yükleme simule ediliyor: %s", plan.id)
        time.sleep(1)
        return True


def dispatch_plan(plan: ContentPlan, platform: Platform, account_lookup) -> bool:
    account = account_lookup(platform)
    if not account:
        logger.error("Platform için aktif oturum yok: %s", platform.value)
        plan.last_error = "Aktif oturum bulunamadı"
        return False
    if platform == Platform.INSTAGRAM:
        client = InstagramClient(account.access_token, "", "")
        return client.upload(plan)
    if platform == Platform.YOUTUBE:
        client = YouTubeClient(account.access_token, "", "")
        return client.upload(plan)
    return False


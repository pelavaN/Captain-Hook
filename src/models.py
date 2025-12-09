from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class Platform(str, Enum):
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"


class ContentStatus(str, Enum):
    PENDING = "Beklemede"
    SENT = "Gönderildi"
    FAILED = "Hata"


@dataclass
class PlatformAccount:
    platform: Platform
    username: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    connected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ContentPlan:
    id: str
    title: str
    description: str
    hashtags: str
    youtube_tags: List[str]
    media_path: str
    thumbnail_path: Optional[str]
    scheduled_for: datetime
    platforms: List[Platform]
    status: ContentStatus = ContentStatus.PENDING
    last_error: Optional[str] = None


@dataclass
class LogEntry:
    timestamp: datetime
    platform: Platform
    content_id: str
    status: ContentStatus
    message: str


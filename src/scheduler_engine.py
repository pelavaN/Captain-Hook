from datetime import datetime
from typing import Callable, Dict, List

from apscheduler.schedulers.background import BackgroundScheduler

from .models import ContentPlan, ContentStatus, LogEntry, Platform
from .storage import SecureStorage


class SchedulerEngine:
    def __init__(self, storage: SecureStorage, dispatcher: Callable[[ContentPlan, Platform], bool]):
        self.storage = storage
        self.dispatcher = dispatcher
        self.scheduler = BackgroundScheduler()

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown()

    def schedule_plan(self, plan: ContentPlan) -> None:
        for platform in plan.platforms:
            self.scheduler.add_job(
                self._run_job,
                "date",
                run_date=plan.scheduled_for,
                args=[plan, platform],
                id=f"{plan.id}-{platform.value}",
                replace_existing=True,
            )

    def hydrate_existing(self, plans: List[ContentPlan]) -> None:
        now = datetime.utcnow()
        for plan in plans:
            if plan.status != ContentStatus.PENDING:
                continue
            if plan.scheduled_for < now:
                continue
            self.schedule_plan(plan)

    def _run_job(self, plan: ContentPlan, platform: Platform) -> None:
        succeeded = self.dispatcher(plan, platform)
        updated_plans = self.storage.load_plans()
        for idx, existing in enumerate(updated_plans):
            if existing.id == plan.id:
                if succeeded:
                    existing.status = ContentStatus.SENT
                    existing.last_error = None
                else:
                    existing.status = ContentStatus.FAILED
                updated_plans[idx] = existing
                break
        self.storage.save_plans(updated_plans)

        log_entry = LogEntry(
            timestamp=datetime.utcnow(),
            platform=platform,
            content_id=plan.id,
            status=ContentStatus.SENT if succeeded else ContentStatus.FAILED,
            message="Gönderildi" if succeeded else (plan.last_error or "Gönderim hatası"),
        )
        self.storage.append_log(log_entry)


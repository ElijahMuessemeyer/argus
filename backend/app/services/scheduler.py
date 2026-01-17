"""APScheduler setup for background tasks."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger("services.scheduler")

scheduler = AsyncIOScheduler()


def setup_scheduler() -> AsyncIOScheduler:
    """Configure and return the scheduler."""
    settings = get_settings()

    if not settings.scheduler_enabled:
        logger.info("Scheduler disabled")
        return scheduler

    # Import tasks here to avoid circular imports
    from app.tasks.refresh_data import refresh_market_data
    from app.tasks.detect_signals import detect_all_signals

    # Data refresh job - every 5 minutes during market hours (Mon-Fri, 9:30 AM - 4:00 PM ET)
    scheduler.add_job(
        refresh_market_data,
        CronTrigger(
            day_of_week="mon-fri",
            hour="9-15",
            minute="*/5",
            timezone="America/New_York",
        ),
        id="refresh_market_data",
        name="Refresh Market Data",
        replace_existing=True,
        max_instances=1,
    )

    # Also run at market open (9:30 AM)
    scheduler.add_job(
        refresh_market_data,
        CronTrigger(
            day_of_week="mon-fri",
            hour="9",
            minute="30",
            timezone="America/New_York",
        ),
        id="refresh_market_data_open",
        name="Refresh Market Data at Open",
        replace_existing=True,
        max_instances=1,
    )

    # Signal detection job - every 5 minutes during market hours
    scheduler.add_job(
        detect_all_signals,
        CronTrigger(
            day_of_week="mon-fri",
            hour="9-15",
            minute="*/5",
            timezone="America/New_York",
        ),
        id="detect_signals",
        name="Detect Trading Signals",
        replace_existing=True,
        max_instances=1,
    )

    # At market close (4:00 PM), run final detection
    scheduler.add_job(
        detect_all_signals,
        CronTrigger(
            day_of_week="mon-fri",
            hour="16",
            minute="5",
            timezone="America/New_York",
        ),
        id="detect_signals_close",
        name="Detect Trading Signals at Close",
        replace_existing=True,
        max_instances=1,
    )

    logger.info("Scheduler configured with market hours jobs")

    return scheduler


def start_scheduler() -> None:
    """Start the scheduler."""
    settings = get_settings()

    if not settings.scheduler_enabled:
        return

    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


def shutdown_scheduler() -> None:
    """Shutdown the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("Scheduler shut down")

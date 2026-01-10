"""
Background job scheduler for Pillio Health Hub.

Uses APScheduler for async background tasks like daily notification checks.
"""

import logging
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: Optional[AsyncIOScheduler] = None


async def run_daily_notifications():
    """Run all daily notification checks."""
    try:
        from app.services.notification_triggers import NotificationTriggers
        from app.database import async_session
        
        async with async_session() as db:
            triggers = NotificationTriggers(db)
            await triggers.run_all_daily_checks()
            logger.info("Daily notification checks completed successfully")
    except Exception as e:
        logger.error(f"Error running daily notification checks: {e}", exc_info=True)


async def run_weekly_adherence_report():
    """Run weekly adherence analysis and send reports."""
    try:
        from app.services.notification_triggers import NotificationTriggers
        from app.database import async_session
        
        async with async_session() as db:
            triggers = NotificationTriggers(db)
            await triggers.check_adherence_patterns_all_users()
            logger.info("Weekly adherence check completed successfully")
    except Exception as e:
        logger.error(f"Error running weekly adherence check: {e}", exc_info=True)


def get_scheduler() -> AsyncIOScheduler:
    """Get or create the global scheduler instance."""
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
    return scheduler


def setup_scheduler(scheduler_instance: Optional[AsyncIOScheduler] = None) -> AsyncIOScheduler:
    """Configure scheduled jobs.
    
    Args:
        scheduler_instance: Optional scheduler instance to configure.
                           If not provided, gets/creates the global instance.
    
    Returns:
        Configured scheduler instance.
    """
    if scheduler_instance is None:
        scheduler_instance = get_scheduler()
    
    # Clear any existing jobs to avoid duplicates on restart
    scheduler_instance.remove_all_jobs()
    
    # Daily notification check at 8 AM
    scheduler_instance.add_job(
        run_daily_notifications,
        CronTrigger(hour=8, minute=0),
        id='daily_notifications',
        name='Daily notification checks',
        replace_existing=True,
        max_instances=1
    )
    
    # Weekly adherence check on Sunday at 9 AM
    scheduler_instance.add_job(
        run_weekly_adherence_report,
        CronTrigger(day_of_week='sun', hour=9, minute=0),
        id='weekly_adherence',
        name='Weekly adherence analysis',
        replace_existing=True,
        max_instances=1
    )
    
    logger.info("Scheduler configured with daily notifications and weekly adherence checks")
    return scheduler_instance


async def start_scheduler():
    """Start the background scheduler."""
    scheduler_instance = get_scheduler()
    setup_scheduler(scheduler_instance)
    
    if not scheduler_instance.running:
        scheduler_instance.start()
        logger.info("Background scheduler started")
    else:
        logger.info("Scheduler was already running")


async def stop_scheduler():
    """Stop the background scheduler gracefully."""
    global scheduler
    if scheduler is not None and scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("Background scheduler stopped")
        scheduler = None


def is_scheduler_running() -> bool:
    """Check if the scheduler is currently running."""
    global scheduler
    return scheduler is not None and scheduler.running

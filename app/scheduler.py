"""
Background job scheduler using APScheduler
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = BackgroundScheduler()


def start_scheduler(scan_function):
    """
    Start the background scheduler
    scan_function: Function to call for scheduled scans
    """
    if not settings.ENABLE_AUTO_SCAN:
        logger.info("Auto-scan disabled in configuration")
        return

    try:
        # Add scheduled scan job
        scheduler.add_job(
            func=scan_function,
            trigger=IntervalTrigger(hours=settings.SCAN_INTERVAL_HOURS),
            id='scheduled_scan',
            name='Scheduled metals scan',
            replace_existing=True,
            max_instances=1  # Prevent concurrent scans
        )

        # Start the scheduler
        scheduler.start()

        logger.info(
            f"Scheduler started: scanning every {settings.SCAN_INTERVAL_HOURS} hours"
        )

    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        raise


def stop_scheduler():
    """Stop the background scheduler gracefully"""
    try:
        if scheduler.running:
            scheduler.shutdown(wait=True)
            logger.info("Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")


def get_scheduler_status() -> dict:
    """Get current scheduler status"""
    if not scheduler.running:
        return {
            "running": False,
            "next_run": None,
            "jobs": []
        }

    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None
        })

    return {
        "running": True,
        "jobs": jobs,
        "interval_hours": settings.SCAN_INTERVAL_HOURS
    }


def trigger_immediate_scan():
    """Trigger an immediate scan (bypasses schedule)"""
    # This will be called directly by the API endpoint
    # The actual scan function is passed to start_scheduler
    pass

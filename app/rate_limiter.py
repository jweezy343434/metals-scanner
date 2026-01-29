"""
Rate limiting system for API calls
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging
import time

from app.database import RateLimitTracker, get_db_context
from app.exceptions import APIRateLimitError
from app.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Multi-layer rate limiting protection"""

    def __init__(self):
        self.last_call_time = {}  # Track last call time for burst protection

    def check_and_increment(self, api_name: str, db: Session = None) -> bool:
        """
        Check if API call is allowed and increment counter
        Raises APIRateLimitError if limit exceeded
        """
        should_close_db = False
        if db is None:
            db = next(get_db_context())
            should_close_db = True

        try:
            # Get tracker
            tracker = db.query(RateLimitTracker).filter(
                RateLimitTracker.api_name == api_name
            ).first()

            if not tracker:
                logger.warning(f"No rate limit tracker found for {api_name}")
                return True

            # Check if reset is needed
            now = datetime.utcnow()
            if now >= tracker.reset_at:
                self._reset_tracker(tracker, now)

            # Determine which limit to check
            if tracker.daily_limit:
                if tracker.daily_calls_used >= tracker.daily_limit:
                    raise APIRateLimitError(
                        api_name=api_name,
                        limit=tracker.daily_limit,
                        reset_at=tracker.reset_at.isoformat()
                    )
                tracker.daily_calls_used += 1
            elif tracker.monthly_limit:
                if tracker.monthly_calls_used >= tracker.monthly_limit:
                    raise APIRateLimitError(
                        api_name=api_name,
                        limit=tracker.monthly_limit,
                        reset_at=tracker.reset_at.isoformat()
                    )
                tracker.monthly_calls_used += 1

            # Burst protection: Ensure minimum 200ms between calls
            last_call = self.last_call_time.get(api_name)
            if last_call:
                elapsed = time.time() - last_call
                if elapsed < 0.2:  # 200ms
                    sleep_time = 0.2 - elapsed
                    logger.debug(f"Burst protection: sleeping {sleep_time:.3f}s for {api_name}")
                    time.sleep(sleep_time)

            # Update last call time
            tracker.last_call_at = now
            self.last_call_time[api_name] = time.time()

            db.commit()
            logger.debug(
                f"{api_name} rate limit: {tracker.daily_calls_used or tracker.monthly_calls_used} "
                f"/ {tracker.daily_limit or tracker.monthly_limit}"
            )
            return True

        except APIRateLimitError:
            raise
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            db.rollback()
            raise
        finally:
            if should_close_db:
                db.close()

    def _reset_tracker(self, tracker: RateLimitTracker, now: datetime):
        """Reset tracker counters when period expires"""
        if tracker.daily_limit:
            # Reset daily counter
            tracker.daily_calls_used = 0
            tracker.reset_at = now.replace(hour=0, minute=0, second=0) + timedelta(days=1)
            logger.info(f"Reset daily counter for {tracker.api_name}")
        elif tracker.monthly_limit:
            # Reset monthly counter
            tracker.monthly_calls_used = 0
            # Next month, first day
            if now.month == 12:
                tracker.reset_at = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0)
            else:
                tracker.reset_at = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0)
            logger.info(f"Reset monthly counter for {tracker.api_name}")

    def get_status(self, api_name: str, db: Session = None) -> dict:
        """Get current rate limit status for an API"""
        should_close_db = False
        if db is None:
            db = next(get_db_context())
            should_close_db = True

        try:
            tracker = db.query(RateLimitTracker).filter(
                RateLimitTracker.api_name == api_name
            ).first()

            if not tracker:
                return None

            # Check if reset is needed
            now = datetime.utcnow()
            if now >= tracker.reset_at:
                self._reset_tracker(tracker, now)
                db.commit()

            limit = tracker.daily_limit or tracker.monthly_limit
            calls_used = tracker.daily_calls_used or tracker.monthly_calls_used
            calls_remaining = limit - calls_used

            return {
                "api_name": api_name,
                "limit": limit,
                "calls_used": calls_used,
                "calls_remaining": calls_remaining,
                "percentage_used": round((calls_used / limit) * 100, 2),
                "reset_at": tracker.reset_at,
                "last_call_at": tracker.last_call_at
            }
        finally:
            if should_close_db:
                db.close()

    def get_all_statuses(self, db: Session = None) -> list:
        """Get rate limit status for all APIs"""
        should_close_db = False
        if db is None:
            db = next(get_db_context())
            should_close_db = True

        try:
            trackers = db.query(RateLimitTracker).all()
            return [self.get_status(t.api_name, db) for t in trackers]
        finally:
            if should_close_db:
                db.close()


# Global rate limiter instance
rate_limiter = RateLimiter()

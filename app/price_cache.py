"""
Smart caching for spot prices to conserve API calls
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
import logging
import pytz

from app.database import SpotPrice, get_db_context
from app.config import settings

logger = logging.getLogger(__name__)


class PriceCache:
    """Intelligent caching based on market hours"""

    def __init__(self):
        self.eastern = pytz.timezone('US/Eastern')

    def is_market_hours(self) -> bool:
        """
        Check if current time is during market hours
        Monday-Friday, 9:30 AM - 4:00 PM ET
        """
        now_et = datetime.now(self.eastern)

        # Check if weekend
        if now_et.weekday() >= 5:  # Saturday=5, Sunday=6
            return False

        # Check time range (9:30 AM - 4:00 PM)
        market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)

        return market_open <= now_et <= market_close

    def get_cache_duration_minutes(self) -> int:
        """
        Determine cache duration based on current time
        - Market hours (Mon-Fri 9:30AM-4PM ET): 15 minutes
        - Off-hours weekdays: 1 hour
        - Weekends: 4 hours
        """
        now_et = datetime.now(self.eastern)

        # Weekend
        if now_et.weekday() >= 5:
            return settings.CACHE_WEEKEND

        # Market hours
        if self.is_market_hours():
            return settings.CACHE_MARKET_HOURS

        # Off-hours weekday
        return settings.CACHE_OFF_HOURS

    def get_cached_price(self, metal_type: str, db: Session = None) -> dict:
        """
        Get cached price if still valid, otherwise return None
        Returns dict with price_per_oz, fetched_at, age_minutes, is_stale
        """
        should_close_db = False
        if db is None:
            db = next(get_db_context())
            should_close_db = True

        try:
            # Get latest price for metal type
            latest_price = db.query(SpotPrice).filter(
                SpotPrice.metal_type == metal_type
            ).order_by(desc(SpotPrice.fetched_at)).first()

            if not latest_price:
                logger.debug(f"No cached price found for {metal_type}")
                return None

            # Calculate age
            now = datetime.utcnow()
            age = now - latest_price.fetched_at
            age_minutes = int(age.total_seconds() / 60)

            # Determine if cache is still valid
            cache_duration = self.get_cache_duration_minutes()
            is_stale = age_minutes >= cache_duration

            logger.debug(
                f"{metal_type} cache: age={age_minutes}min, "
                f"duration={cache_duration}min, stale={is_stale}"
            )

            return {
                "price_per_oz": latest_price.price_per_oz,
                "fetched_at": latest_price.fetched_at,
                "age_minutes": age_minutes,
                "is_stale": is_stale
            }
        finally:
            if should_close_db:
                db.close()

    def should_fetch_fresh(self, metal_type: str, db: Session = None) -> bool:
        """
        Determine if a fresh API call is needed
        Returns True if cache is stale or doesn't exist
        """
        cached = self.get_cached_price(metal_type, db)
        if not cached:
            return True
        return cached["is_stale"]

    def store_price(self, metal_type: str, price_per_oz: float, db: Session = None):
        """Store a new spot price in cache"""
        should_close_db = False
        if db is None:
            db = next(get_db_context())
            should_close_db = True

        try:
            new_price = SpotPrice(
                metal_type=metal_type,
                price_per_oz=price_per_oz,
                fetched_at=datetime.utcnow()
            )
            db.add(new_price)
            db.commit()
            logger.info(f"Stored {metal_type} price: ${price_per_oz:.2f}/oz")
        except Exception as e:
            logger.error(f"Failed to store price: {e}")
            db.rollback()
            raise
        finally:
            if should_close_db:
                db.close()

    def get_or_fetch_price(self, metal_type: str, fetch_func, db: Session = None) -> dict:
        """
        Get cached price or fetch fresh if needed
        fetch_func should be a callable that returns price_per_oz
        Returns dict with price_per_oz, fetched_at, age_minutes, from_cache
        """
        cached = self.get_cached_price(metal_type, db)

        # Use cache if valid
        if cached and not cached["is_stale"]:
            logger.info(f"Using cached {metal_type} price (age: {cached['age_minutes']}min)")
            return {
                **cached,
                "from_cache": True
            }

        # Fetch fresh price
        try:
            logger.info(f"Fetching fresh {metal_type} price from API")
            fresh_price = fetch_func(metal_type)
            self.store_price(metal_type, fresh_price, db)

            return {
                "price_per_oz": fresh_price,
                "fetched_at": datetime.utcnow(),
                "age_minutes": 0,
                "is_stale": False,
                "from_cache": False
            }
        except Exception as e:
            # Fallback to stale cache if API fails
            if cached:
                logger.warning(
                    f"API fetch failed, using stale cache for {metal_type} "
                    f"(age: {cached['age_minutes']}min): {e}"
                )
                return {
                    **cached,
                    "from_cache": True,
                    "fallback": True
                }
            else:
                logger.error(f"API fetch failed and no cache available for {metal_type}: {e}")
                raise

    def cleanup_old_prices(self, days_to_keep: int = 7, db: Session = None):
        """Remove spot prices older than specified days"""
        should_close_db = False
        if db is None:
            db = next(get_db_context())
            should_close_db = True

        try:
            cutoff = datetime.utcnow() - timedelta(days=days_to_keep)
            deleted = db.query(SpotPrice).filter(
                SpotPrice.fetched_at < cutoff
            ).delete()
            db.commit()
            logger.info(f"Cleaned up {deleted} old spot prices")
            return deleted
        finally:
            if should_close_db:
                db.close()


# Global cache instance
price_cache = PriceCache()

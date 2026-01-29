"""
Metals API client for spot prices
"""
import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.rate_limiter import rate_limiter
from app.price_cache import price_cache
from app.exceptions import APIConnectionError
import requests

logger = logging.getLogger(__name__)


class MetalsAPIClient:
    """Client for metals-api.com with caching"""

    def __init__(self):
        self.api_key = settings.METALS_API_KEY
        self.base_url = "https://metals-api.com/api"
        self.timeout = settings.API_TIMEOUT

    def get_spot_prices(self, db: Session = None) -> Dict[str, float]:
        """
        Get current spot prices for gold and silver
        Returns dict: {'gold': price_per_oz, 'silver': price_per_oz}
        Uses intelligent caching to conserve API calls
        """
        prices = {}

        # Get gold price with caching
        try:
            gold_result = price_cache.get_or_fetch_price(
                'gold',
                lambda _: self._fetch_price('XAU', db),
                db
            )
            prices['gold'] = gold_result['price_per_oz']

            if gold_result.get('from_cache'):
                cache_status = "stale fallback" if gold_result.get('fallback') else "cache"
                logger.info(
                    f"Gold price from {cache_status}: ${prices['gold']:.2f}/oz "
                    f"(age: {gold_result['age_minutes']}min)"
                )
        except Exception as e:
            logger.error(f"Failed to get gold price: {e}")
            prices['gold'] = None

        # Get silver price with caching
        try:
            silver_result = price_cache.get_or_fetch_price(
                'silver',
                lambda _: self._fetch_price('XAG', db),
                db
            )
            prices['silver'] = silver_result['price_per_oz']

            if silver_result.get('from_cache'):
                cache_status = "stale fallback" if silver_result.get('fallback') else "cache"
                logger.info(
                    f"Silver price from {cache_status}: ${prices['silver']:.2f}/oz "
                    f"(age: {silver_result['age_minutes']}min)"
                )
        except Exception as e:
            logger.error(f"Failed to get silver price: {e}")
            prices['silver'] = None

        return prices

    def _fetch_price(self, symbol: str, db: Session = None) -> float:
        """
        Fetch fresh price from metals-api.com
        symbol: 'XAU' for gold, 'XAG' for silver
        Returns price per troy ounce in USD
        """
        # Check rate limit
        rate_limiter.check_and_increment("metals-api", db)

        # Make API request
        endpoint = "/latest"
        params = {
            'access_key': self.api_key,
            'base': 'USD',
            'symbols': symbol
        }

        try:
            logger.debug(f"Fetching {symbol} price from metals-api.com")
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            # Check API response
            if not data.get('success', False):
                error_msg = data.get('error', {}).get('info', 'Unknown error')
                raise APIConnectionError('metals-api', error_msg)

            # Extract rate and convert to price per ounce
            # API returns: 1 USD = X oz of metal (inverse)
            # We need: 1 oz of metal = Y USD
            rate = data.get('rates', {}).get(symbol)
            if not rate or rate <= 0:
                raise APIConnectionError('metals-api', f'Invalid rate for {symbol}: {rate}')

            # Invert the rate to get price per ounce
            price_per_oz = 1.0 / rate

            logger.info(f"{symbol} price fetched: ${price_per_oz:.2f}/oz")
            return price_per_oz

        except requests.exceptions.RequestException as e:
            raise APIConnectionError('metals-api', str(e))

    def get_price_by_metal_type(self, metal_type: str, db: Session = None) -> Optional[float]:
        """
        Get price for a specific metal type
        metal_type: 'gold' or 'silver'
        Returns price per troy ounce or None
        """
        if metal_type not in ['gold', 'silver']:
            logger.error(f"Invalid metal type: {metal_type}")
            return None

        prices = self.get_spot_prices(db)
        return prices.get(metal_type)

    def get_cached_prices_only(self, db: Session = None) -> Dict[str, Optional[float]]:
        """
        Get only cached prices without making API calls
        Useful for rate limit conservation
        """
        prices = {}

        for metal_type in ['gold', 'silver']:
            cached = price_cache.get_cached_price(metal_type, db)
            if cached:
                prices[metal_type] = cached['price_per_oz']
            else:
                prices[metal_type] = None

        return prices


# Global client instance
metals_api_client = MetalsAPIClient()

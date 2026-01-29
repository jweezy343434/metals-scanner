"""
eBay scraper using Finding API
"""
import re
from typing import List, Dict, Optional
import logging
from sqlalchemy.orm import Session

from app.scrapers.base import BaseScraper
from app.config import settings
from app.rate_limiter import rate_limiter
from app.exceptions import WeightExtractionError

logger = logging.getLogger(__name__)

# Weight extraction patterns (priority order)
WEIGHT_PATTERNS = [
    # Troy ounces: "1 oz", "1.5 troy ounce", "1/10 oz"
    (r'(\d+(?:\.\d+)?)\s*(?:troy\s*)?(?:oz|ounce)(?:s)?', 1.0),
    # Fractions: "1/10 oz", "1/4 ounce"
    (r'(\d+)/(\d+)\s*(?:troy\s*)?(?:oz|ounce)(?:s)?', 1.0),
    # Grams: "10 grams", "5g", "31.1g"
    (r'(\d+(?:\.\d+)?)\s*g(?:ram)?(?:s)?', 0.0321507),  # 1g = 0.0321507 troy oz
]


class EbayScraper(BaseScraper):
    """eBay Finding API scraper with weight extraction"""

    def __init__(self):
        super().__init__(
            api_name="ebay",
            base_url="https://svcs.ebay.com/services/search/FindingService/v1"
        )
        self.app_id = settings.EBAY_API_KEY

    def scrape(
        self,
        search_terms: List[str] = None,
        max_results: int = 100,
        db: Session = None
    ) -> List[Dict]:
        """
        Scrape eBay for metal listings
        Returns list of standardized listing dictionaries
        """
        if search_terms is None:
            search_terms = [
                "gold bullion",
                "silver bullion",
                "gold eagle",
                "silver eagle"
            ]

        all_listings = []

        for term in search_terms:
            try:
                # Check rate limit before making request
                rate_limiter.check_and_increment("ebay", db)

                # Make API request
                listings = self._search_ebay(term, max_results)
                all_listings.extend(listings)

                logger.info(f"Found {len(listings)} listings for '{term}'")

            except Exception as e:
                logger.error(f"Failed to scrape eBay for '{term}': {e}")
                # Continue with other search terms

        # Deduplicate by external_id
        unique_listings = {listing['external_id']: listing for listing in all_listings}
        logger.info(
            f"Total listings: {len(all_listings)}, "
            f"Unique: {len(unique_listings)}"
        )

        return list(unique_listings.values())

    def _search_ebay(self, keyword: str, max_results: int) -> List[Dict]:
        """Search eBay Finding API for keyword"""
        params = {
            'OPERATION-NAME': 'findItemsByKeywords',
            'SERVICE-VERSION': '1.0.0',
            'SECURITY-APPNAME': self.app_id,
            'RESPONSE-DATA-FORMAT': 'JSON',
            'REST-PAYLOAD': '',
            'keywords': keyword,
            'paginationInput.entriesPerPage': min(max_results, 100),
            'itemFilter(0).name': 'ListingType',
            'itemFilter(0).value': 'FixedPrice',
            'itemFilter(1).name': 'Currency',
            'itemFilter(1).value': 'USD',
            'itemFilter(2).name': 'MaxPrice',
            'itemFilter(2).value': '10000',
            'itemFilter(3).name': 'MinPrice',
            'itemFilter(3).value': '50',
            'sortOrder': 'PricePlusShippingLowest'
        }

        response = self.make_request("", params=params)
        data = response.json()

        # Parse response
        return self._parse_ebay_response(data, keyword)

    def _parse_ebay_response(self, data: dict, keyword: str) -> List[Dict]:
        """Parse eBay API response and extract listings"""
        listings = []

        try:
            search_result = data.get('findItemsByKeywordsResponse', [{}])[0]
            search_result = search_result.get('searchResult', [{}])[0]
            items = search_result.get('item', [])

            if not items:
                logger.debug(f"No items found in response for '{keyword}'")
                return []

            for item in items:
                try:
                    listing = self._parse_item(item, keyword)
                    if listing:
                        listings.append(listing)
                except Exception as e:
                    logger.warning(f"Failed to parse item: {e}")
                    continue

        except Exception as e:
            logger.error(f"Failed to parse eBay response: {e}")

        return listings

    def _parse_item(self, item: dict, keyword: str) -> Optional[Dict]:
        """Parse a single eBay item"""
        try:
            # Extract basic fields
            item_id = item.get('itemId', [None])[0]
            title = item.get('title', [None])[0]
            price_info = item.get('sellingStatus', [{}])[0].get('currentPrice', [{}])[0]
            price = float(price_info.get('__value__', 0))
            url = item.get('viewItemURL', [None])[0]

            if not all([item_id, title, price, url]):
                logger.debug(f"Skipping item with missing fields")
                return None

            # Determine metal type from keyword
            metal_type = self._determine_metal_type(keyword, title)

            # Extract weight
            weight_oz, extraction_failed = self._extract_weight(title)

            # Build standardized listing
            return {
                'source': 'ebay',
                'external_id': item_id,
                'title': title,
                'price': price,
                'metal_type': metal_type,
                'weight_oz': weight_oz,
                'weight_extraction_failed': extraction_failed,
                'url': url
            }

        except Exception as e:
            logger.error(f"Error parsing item: {e}")
            return None

    def _determine_metal_type(self, keyword: str, title: str) -> str:
        """Determine if listing is gold or silver"""
        keyword_lower = keyword.lower()
        title_lower = title.lower()

        if 'gold' in keyword_lower or 'gold' in title_lower:
            return 'gold'
        elif 'silver' in keyword_lower or 'silver' in title_lower:
            return 'silver'
        else:
            # Default based on keyword
            return 'gold' if 'gold' in keyword_lower else 'silver'

    def _extract_weight(self, title: str) -> tuple[Optional[float], bool]:
        """
        Extract weight from title using regex patterns
        Returns (weight_oz, extraction_failed)
        """
        title_lower = title.lower()

        for pattern, conversion_factor in WEIGHT_PATTERNS:
            match = re.search(pattern, title_lower)
            if match:
                try:
                    # Handle fractions (e.g., "1/10 oz")
                    if len(match.groups()) == 2 and '/' in pattern:
                        numerator = float(match.group(1))
                        denominator = float(match.group(2))
                        weight = (numerator / denominator) * conversion_factor
                    else:
                        weight = float(match.group(1)) * conversion_factor

                    # Validate weight is reasonable
                    if weight <= 0 or weight > 1000:  # Max 1000 oz
                        logger.debug(f"Invalid weight extracted: {weight}")
                        continue

                    logger.debug(f"Extracted weight: {weight:.4f} oz from '{title}'")
                    return round(weight, 4), False

                except (ValueError, ZeroDivisionError) as e:
                    logger.debug(f"Failed to parse weight match: {e}")
                    continue

        # No valid weight found
        logger.debug(f"No weight pattern matched in '{title}'")
        return None, True

    def extract_weight_from_title(self, title: str) -> Optional[float]:
        """
        Public method to extract weight (for testing/debugging)
        Returns weight in troy ounces or None
        """
        weight_oz, _ = self._extract_weight(title)
        return weight_oz

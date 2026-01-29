# Contributing to Metals Arbitrage Scanner

Thank you for your interest in improving this project! This guide will help you understand the codebase and make common modifications.

## Table of Contents

1. [Code Structure](#code-structure)
2. [Adding New Metal Types](#adding-new-metal-types)
3. [Adding New Data Sources](#adding-new-data-sources)
4. [Modifying the Dashboard](#modifying-the-dashboard)
5. [Development Setup](#development-setup)
6. [Testing Your Changes](#testing-your-changes)
7. [Common Modifications](#common-modifications)

## Code Structure

The project follows a modular architecture:

```
metals-scanner/
├── app/
│   ├── main.py              # FastAPI application & endpoints
│   ├── config.py            # Settings & environment variables
│   ├── database.py          # Database models (SQLAlchemy)
│   ├── schemas.py           # API request/response models (Pydantic)
│   ├── exceptions.py        # Custom error classes
│   ├── rate_limiter.py      # API quota management
│   ├── price_cache.py       # Intelligent price caching
│   ├── price_api.py         # metals-api.com client
│   ├── scheduler.py         # Background job scheduler
│   ├── scrapers/
│   │   ├── base.py          # Abstract scraper class
│   │   ├── ebay.py          # eBay scraper implementation
│   │   └── __init__.py      # Scraper exports
│   └── static/
│       └── index.html       # Web dashboard (HTML/CSS/JS)
├── data/                    # SQLite database (created at runtime)
├── logs/                    # Application logs
├── docker-compose.yml       # Container orchestration
├── Dockerfile               # Container build instructions
└── requirements.txt         # Python dependencies
```

### Key Components

**Backend (Python/FastAPI):**
- `main.py` - HTTP endpoints, scan orchestration, business logic
- `database.py` - Data persistence, schema definitions
- `scrapers/` - Marketplace integrations (eBay, etc.)
- `price_api.py` - Spot price fetching with caching

**Frontend (Vanilla JavaScript):**
- `static/index.html` - Single-page dashboard with inline JS
- No build step required - pure HTML/CSS/JS

**Infrastructure:**
- Rate limiting prevents API quota exhaustion
- Smart caching reduces API calls (market-hours aware)
- SQLite with WAL mode for concurrency
- APScheduler for background jobs

## Adding New Metal Types

Currently supports: Gold, Silver, Platinum (partially)

### To add Palladium:

#### 1. Update Schemas

Edit `app/schemas.py`:

```python
class MetalType(str, Enum):
    """Supported metal types"""
    GOLD = "gold"
    SILVER = "silver"
    PLATINUM = "platinum"
    PALLADIUM = "palladium"  # Add this
    ALL = "all"
```

#### 2. Add Price Fetching

Edit `app/price_api.py`:

```python
def get_spot_prices(self, db: Session = None) -> Dict[str, float]:
    """Get current spot prices for all metals"""
    prices = {}

    # Existing gold/silver code...

    # Add palladium
    try:
        palladium_result = price_cache.get_or_fetch_price(
            'palladium',
            lambda _: self._fetch_price('XPD', db),  # XPD = palladium symbol
            db
        )
        prices['palladium'] = palladium_result['price_per_oz']
    except Exception as e:
        logger.error(f"Failed to get palladium price: {e}")
        prices['palladium'] = None

    return prices
```

#### 3. Update eBay Searches

Edit `app/scrapers/ebay.py`, add search term:

```python
def scrape(self, search_terms=None, max_results=100, db=None):
    if search_terms is None:
        search_terms = [
            "gold bullion",
            "silver bullion",
            "gold eagle",
            "silver eagle",
            "palladium bullion"  # Add this
        ]
    # ... rest of method
```

Also update metal type detection:

```python
def _determine_metal_type(self, keyword: str, title: str) -> str:
    keyword_lower = keyword.lower()
    title_lower = title.lower()

    if 'gold' in keyword_lower or 'gold' in title_lower:
        return 'gold'
    elif 'silver' in keyword_lower or 'silver' in title_lower:
        return 'silver'
    elif 'platinum' in keyword_lower or 'platinum' in title_lower:
        return 'platinum'
    elif 'palladium' in keyword_lower or 'palladium' in title_lower:  # Add
        return 'palladium'
    else:
        return 'gold'
```

#### 4. Update Dashboard

Edit `app/static/index.html`:

**Add spot price display:**
```html
<!-- After silver price -->
<div class="text-center">
    <p class="text-blue-200 text-sm mb-1">Palladium Spot</p>
    <p class="text-3xl font-bold" id="palladiumSpotPrice">$--</p>
    <p class="text-blue-200 text-xs" id="palladiumSpotAge">Loading...</p>
</div>
```

**Add to filter dropdown:**
```html
<select id="metalTypeFilter" onchange="applyFilters()">
    <option value="all">All Metals</option>
    <option value="gold">Gold</option>
    <option value="silver">Silver</option>
    <option value="platinum">Platinum</option>
    <option value="palladium">Palladium</option>  <!-- Add -->
</select>
```

**Update JavaScript loading:**
```javascript
// In loadSpotPrices() function
prices.forEach(price => {
    spotPrices[price.metal_type] = price.price_per_oz;

    if (price.metal_type === 'gold') {
        // ... existing code
    } else if (price.metal_type === 'silver') {
        // ... existing code
    } else if (price.metal_type === 'palladium') {  // Add this
        document.getElementById('palladiumSpotPrice').textContent =
            `$${price.price_per_oz.toFixed(2)}`;
        document.getElementById('palladiumSpotAge').textContent =
            `Updated ${price.age_minutes} min ago`;
    }
});
```

**Update color coding:**
```javascript
const metalColors = {
    gold: 'bg-yellow-100 text-yellow-800',
    silver: 'bg-gray-200 text-gray-800',
    platinum: 'bg-blue-100 text-blue-800',
    palladium: 'bg-purple-100 text-purple-800'  // Add this
};
```

#### 5. Test

```bash
# Restart application
docker-compose restart

# Trigger scan
curl -X POST http://localhost:8000/api/scan

# Verify palladium listings appear
curl "http://localhost:8000/api/deals?metal_type=palladium"
```

## Adding New Data Sources

Currently supports: eBay

### Example: Adding Amazon

#### 1. Create Scraper

Create `app/scrapers/amazon.py`:

```python
"""
Amazon scraper using Product Advertising API
"""
from typing import List, Dict
import logging
from sqlalchemy.orm import Session

from app.scrapers.base import BaseScraper
from app.rate_limiter import rate_limiter
from app.config import settings

logger = logging.getLogger(__name__)


class AmazonScraper(BaseScraper):
    """Amazon Product Advertising API scraper"""

    def __init__(self):
        super().__init__(
            api_name="amazon",
            base_url="https://webservices.amazon.com/paapi5"
        )
        self.access_key = settings.AMAZON_ACCESS_KEY
        self.secret_key = settings.AMAZON_SECRET_KEY
        self.partner_tag = settings.AMAZON_PARTNER_TAG

    def scrape(self, search_terms=None, max_results=100, db=None):
        """
        Scrape Amazon for metal listings
        Returns list of standardized dictionaries
        """
        if search_terms is None:
            search_terms = ["gold bullion", "silver bullion"]

        all_listings = []

        for term in search_terms:
            try:
                # Check rate limit
                rate_limiter.check_and_increment("amazon", db)

                # Make API request (implementation depends on Amazon API)
                listings = self._search_amazon(term, max_results)
                all_listings.extend(listings)

                logger.info(f"Found {len(listings)} Amazon listings for '{term}'")

            except Exception as e:
                logger.error(f"Failed to scrape Amazon for '{term}': {e}")
                continue

        return all_listings

    def _search_amazon(self, keyword: str, max_results: int) -> List[Dict]:
        """Search Amazon API for keyword"""
        # Implementation depends on Amazon Product Advertising API
        # See: https://docs.aws.amazon.com/AWSECommerceService/latest/DG/

        params = {
            'Keywords': keyword,
            'SearchIndex': 'All',
            'ItemCount': min(max_results, 10),  # Amazon limit
            'ResponseGroup': 'ItemAttributes,Offers'
        }

        response = self.make_request("/SearchItems", params=params)
        return self._parse_amazon_response(response.json(), keyword)

    def _parse_amazon_response(self, data: dict, keyword: str) -> List[Dict]:
        """Parse Amazon API response"""
        listings = []

        for item in data.get('SearchResult', {}).get('Items', []):
            try:
                # Extract price
                price_str = item['Offers']['Listings'][0]['Price']['Amount']
                price = float(price_str)

                # Build standardized listing
                listings.append({
                    'source': 'amazon',
                    'external_id': item['ASIN'],
                    'title': item['ItemInfo']['Title']['DisplayValue'],
                    'price': price,
                    'metal_type': self._determine_metal_type(keyword, item['ItemInfo']['Title']['DisplayValue']),
                    'weight_oz': self._extract_weight(item['ItemInfo']['Title']['DisplayValue']),
                    'weight_extraction_failed': False,
                    'url': item['DetailPageURL']
                })
            except Exception as e:
                logger.warning(f"Failed to parse Amazon item: {e}")
                continue

        return listings

    def _determine_metal_type(self, keyword: str, title: str) -> str:
        """Determine metal type from keyword/title"""
        # Copy from eBay scraper or create shared utility
        pass

    def _extract_weight(self, title: str):
        """Extract weight from title"""
        # Copy from eBay scraper or create shared utility
        pass
```

#### 2. Add Configuration

Edit `app/config.py`:

```python
class Settings(BaseSettings):
    # Existing keys...
    EBAY_API_KEY: str
    METALS_API_KEY: str

    # Add Amazon keys
    AMAZON_ACCESS_KEY: Optional[str] = None
    AMAZON_SECRET_KEY: Optional[str] = None
    AMAZON_PARTNER_TAG: Optional[str] = None
```

Edit `.env.example`:

```bash
# Amazon Product Advertising API
AMAZON_ACCESS_KEY=your_amazon_access_key
AMAZON_SECRET_KEY=your_amazon_secret_key
AMAZON_PARTNER_TAG=your_amazon_partner_tag
```

#### 3. Register Scraper

Edit `app/scrapers/__init__.py`:

```python
from app.scrapers.base import BaseScraper
from app.scrapers.ebay import EbayScraper
from app.scrapers.amazon import AmazonScraper

__all__ = ['BaseScraper', 'EbayScraper', 'AmazonScraper']
```

#### 4. Add Rate Limiting

Edit `app/database.py` in `init_db()`:

```python
# Amazon tracker
amazon_tracker = db.query(RateLimitTracker).filter(
    RateLimitTracker.api_name == "amazon"
).first()
if not amazon_tracker:
    amazon_tracker = RateLimitTracker(
        api_name="amazon",
        daily_limit=8640,  # Amazon Product Advertising API limit
        daily_calls_used=0,
        reset_at=datetime.utcnow().replace(hour=0, minute=0, second=0)
    )
    db.add(amazon_tracker)
db.commit()
```

#### 5. Integrate into Main App

Edit `app/main.py` in `perform_scan()`:

```python
def perform_scan(db: Session, search_terms=None, max_results=100):
    start_time = datetime.utcnow()
    errors = []
    listings_found = 0

    # Get spot prices
    spot_prices = metals_api_client.get_spot_prices(db)

    # Scrape eBay
    try:
        ebay_scraper = EbayScraper()
        ebay_listings = ebay_scraper.scrape(
            search_terms=search_terms,
            max_results=max_results,
            db=db
        )
        listings_found += len(ebay_listings)

        # Process eBay listings...
    except Exception as e:
        errors.append(f"eBay scraping failed: {str(e)}")

    # Scrape Amazon (add this)
    try:
        amazon_scraper = AmazonScraper()
        amazon_listings = amazon_scraper.scrape(
            search_terms=search_terms,
            max_results=max_results,
            db=db
        )
        listings_found += len(amazon_listings)

        # Process Amazon listings (same as eBay)
        for listing_data in amazon_listings:
            # ... process listing same as eBay
    except Exception as e:
        errors.append(f"Amazon scraping failed: {str(e)}")
        logger.error(f"Amazon scan failed: {e}")

    # ... rest of function
```

#### 6. Update Dashboard

Edit `app/static/index.html`:

```html
<div class="flex flex-wrap gap-4" id="sourceFilters">
    <label class="flex items-center space-x-2 cursor-pointer">
        <input type="checkbox" value="ebay" checked onchange="applyFilters()">
        <span class="text-sm text-gray-700">eBay</span>
    </label>
    <label class="flex items-center space-x-2 cursor-pointer">
        <input type="checkbox" value="amazon" checked onchange="applyFilters()">
        <span class="text-sm text-gray-700">Amazon</span>
    </label>
</div>
```

## Modifying the Dashboard

The dashboard is a single HTML file with inline JavaScript.

### Change Color Scheme

Edit `app/static/index.html`:

```html
<!-- Current: Blue gradient -->
<div class="bg-gradient-to-r from-blue-600 to-blue-700 ...">

<!-- Change to: Purple gradient -->
<div class="bg-gradient-to-r from-purple-600 to-purple-700 ...">
```

### Add New Filter

Example: Add minimum price filter

**HTML:**
```html
<div>
    <label class="block text-sm font-semibold text-gray-700 mb-2">
        Min Price: $<span id="minPriceValue">0</span>
    </label>
    <input
        type="range"
        id="minPriceSlider"
        min="0"
        max="5000"
        value="0"
        step="50"
        class="w-full"
        oninput="updateMinPrice(this.value)"
    >
</div>
```

**JavaScript:**
```javascript
function updateMinPrice(value) {
    document.getElementById('minPriceValue').textContent = value;
    applyFilters();
}

function applyFilters() {
    const metalType = document.getElementById('metalTypeFilter').value;
    const minMargin = parseFloat(document.getElementById('minMarginSlider').value);
    const minPrice = parseFloat(document.getElementById('minPriceSlider').value);  // Add

    let filtered = allListings.filter(listing => {
        // Existing filters...

        // Add price filter
        if (listing.price < minPrice) {
            return false;
        }

        return true;
    });

    // ... rest of function
}
```

### Change Auto-Refresh Interval

Edit the `toggleAutoRefresh()` function:

```javascript
function toggleAutoRefresh() {
    const enabled = document.getElementById('autoRefreshToggle').checked;

    if (enabled) {
        autoRefreshInterval = setInterval(() => {
            loadSpotPrices();
            loadListings();
        }, 180000); // Change: 3 minutes (was 5 minutes)
        showStatus('Auto-refresh enabled (every 3 minutes)', 'info');
    }
    // ... rest
}
```

## Development Setup

### Local Development (without Docker)

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment:**
   ```bash
   cp .env.example .env
   nano .env  # Add API keys
   ```

4. **Run application:**
   ```bash
   # From project root
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Enable hot reload for HTML:**
   - Edit `app/static/index.html`
   - Refresh browser (no restart needed)

### Docker Development

```bash
# Build with no cache
docker-compose build --no-cache

# Run in foreground (see logs)
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Restart after code changes
docker-compose restart

# Rebuild and restart
docker-compose up --build
```

## Testing Your Changes

### Manual Testing

1. **Test API endpoints:**
   ```bash
   # Health check
   curl http://localhost:8000/api/health

   # Get listings
   curl http://localhost:8000/api/listings | jq

   # Trigger scan
   curl -X POST http://localhost:8000/api/scan

   # Test filters
   curl "http://localhost:8000/api/deals?threshold=5&metal_type=gold"
   ```

2. **Test dashboard:**
   - Open http://localhost:8000
   - Click "Scan Now"
   - Verify listings appear
   - Test all filters
   - Check sorting
   - Verify links work

3. **Test rate limiting:**
   ```bash
   # Check rate limit status
   curl http://localhost:8000/api/rate-limits

   # Should show usage
   ```

### Database Testing

```bash
# Connect to database
docker exec -it metals-scanner sqlite3 /app/data/metals_scanner.db

# Verify data
SELECT COUNT(*) FROM listings;
SELECT * FROM listings LIMIT 5;
SELECT * FROM spot_prices ORDER BY fetched_at DESC LIMIT 5;
SELECT * FROM rate_limit_tracker;
```

### Log Inspection

```bash
# View application logs
tail -f logs/metals_scanner.log

# Filter for errors
grep ERROR logs/metals_scanner.log

# Watch in real-time
docker-compose logs -f | grep -i "error\|warning"
```

## Common Modifications

### Change Scan Frequency

Edit `.env`:
```bash
SCAN_INTERVAL_HOURS=4  # Change from 2 to 4 hours
```

Restart:
```bash
docker-compose restart
```

### Add Search Terms

Edit `app/scrapers/ebay.py`:

```python
def scrape(self, search_terms=None, max_results=100, db=None):
    if search_terms is None:
        search_terms = [
            "gold bullion",
            "silver bullion",
            "gold eagle",
            "silver eagle",
            "gold maple leaf",      # Add custom terms
            "silver philharmonic"
        ]
```

### Customize Weight Patterns

Edit `app/scrapers/ebay.py`:

```python
WEIGHT_PATTERNS = [
    # Add custom pattern
    (r'(\d+\.?\d*)\s*grams?', 0.0321507),  # Already exists
    (r'approx\.?\s*(\d+\.?\d*)\s*oz', 1.0),  # Add: "approx 1oz"
    (r'(\d+\.?\d*)\s*t\.?oz', 1.0),          # Add: "1 t.oz"
    # ... existing patterns
]
```

### Adjust Cache Duration

Edit `.env`:

```bash
# More aggressive caching (fewer API calls)
CACHE_MARKET_HOURS=30    # 30 minutes (was 15)
CACHE_OFF_HOURS=120      # 2 hours (was 1)
CACHE_WEEKEND=480        # 8 hours (was 4)
```

### Add Notification System

Create `app/notifier.py`:

```python
import smtplib
from email.mime.text import MIMEText

def send_deal_alert(listing: dict):
    """Send email alert for good deal"""
    if listing['spread_percentage'] > 10:  # >10% profit
        msg = MIMEText(f"Great deal found: {listing['title']} - {listing['spread_percentage']}% margin")
        msg['Subject'] = 'Metals Scanner Alert'
        msg['From'] = 'scanner@example.com'
        msg['To'] = 'your@email.com'

        # Send email (configure SMTP)
        # ...
```

Integrate in `app/main.py`:

```python
from app.notifier import send_deal_alert

def perform_scan(db: Session):
    # ... after processing listing
    if spread and spread > 10:
        send_deal_alert(listing_data)
```

### Change Port

Edit `docker-compose.yml`:

```yaml
ports:
  - "8080:8000"  # Change from 8000:8000
```

Access at: http://localhost:8080

## Pull Request Guidelines

When contributing code:

1. **Create feature branch:**
   ```bash
   git checkout -b feature/add-amazon-scraper
   ```

2. **Make changes:**
   - Write clear commit messages
   - Keep commits atomic (one feature per commit)
   - Follow existing code style

3. **Test thoroughly:**
   - Test all endpoints
   - Verify dashboard works
   - Check logs for errors

4. **Document changes:**
   - Update README.md if needed
   - Add comments for complex logic
   - Update CONTRIBUTING.md for new patterns

5. **Submit PR:**
   - Describe what changed and why
   - Reference any related issues
   - Include screenshots for UI changes

## Code Style

- **Python:** Follow PEP 8
- **JavaScript:** Use semicolons, camelCase
- **HTML:** Indent with 4 spaces
- **Comments:** Explain "why", not "what"

## Questions?

- **Issues:** Create GitHub issue
- **Discord:** Join our community (if available)
- **Email:** Contact maintainers

Thank you for contributing! 🙏

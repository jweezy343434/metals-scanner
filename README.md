# Metals Arbitrage Scanner 🏆

> **Find profitable precious metals deals automatically by comparing live eBay listings against current spot prices.**

A production-ready web application that scans eBay for gold, silver, and platinum listings, compares them to real-time spot prices, and identifies arbitrage opportunities where items are listed below market value.

## 💰 Value Proposition

**The Problem:** Manually searching eBay and calculating whether precious metals listings are good deals is time-consuming and error-prone.

**The Solution:** This scanner automates the entire process:
- ✅ Scans eBay every 2 hours automatically
- ✅ Fetches real-time spot prices with intelligent caching
- ✅ Calculates profit margins instantly
- ✅ Filters and sorts deals by profitability
- ✅ Respects API rate limits (won't exhaust your quotas)
- ✅ Works 24/7 in the background

**Real Example:**
```
eBay Listing: 1 oz Gold Eagle - $2,050
Current Spot: $2,150/oz
Margin: 4.7% profit = $100 savings ✅
```

## 🚀 Quick Start

Get up and running in 3 commands:

```bash
# 1. Setup environment
cp .env.example .env && nano .env  # Add your API keys

# 2. Build and start
docker-compose up --build

# 3. Open browser
# Visit http://localhost:8000
```

That's it! The scanner will start working immediately.

## 📋 Prerequisites

### Required
1. **Docker & Docker Compose** - [Install Docker](https://docs.docker.com/get-docker/)
2. **eBay API Key** (Free) - See below ⬇️
3. **Metals API Key** (Free) - See below ⬇️

### System Requirements
- 1 GB RAM minimum
- 500 MB disk space
- Linux, macOS, or Windows (with WSL2)

## 🔑 How to Get API Keys

### eBay Developer API Key (5,000 calls/day - FREE)

1. **Create Account**
   - Visit [eBay Developers Program](https://developer.ebay.com/)
   - Click "Register" and create a free account
   - Verify your email

2. **Create Application**
   - Go to [My Account](https://developer.ebay.com/my/keys)
   - Click "Create a keyset" or "Get your Application Keys"
   - Choose **Production Keys** (not sandbox)
   - Fill in basic app details (any name works)

3. **Get Your App ID**
   - Copy the **App ID** (looks like: `YourName-YourApp-PRD-1234567890-abcdefgh`)
   - This is your `EBAY_API_KEY`

**Important:** Use **Production** keys, not Sandbox keys!

### Metals-API.com API Key (50 calls/month - FREE)

1. **Sign Up**
   - Visit [metals-api.com](https://metals-api.com/signup/free)
   - Choose the **Free Plan**
   - Enter your email and create password

2. **Get API Key**
   - Log in to your [Dashboard](https://metals-api.com/dashboard)
   - Copy your **API Key** (32-character string)
   - This is your `METALS_API_KEY`

3. **Verify Limits**
   - Free plan: 50 API calls/month
   - Our smart caching uses only 60-120 calls/month (within limit)

## ⚙️ Configuration

### 1. Environment Setup

Copy the example file and edit it:

```bash
cp .env.example .env
nano .env  # or use any text editor
```

### 2. Required Settings

Edit `.env` and add your API keys:

```bash
# eBay API (from developer.ebay.com)
EBAY_API_KEY=YourName-YourApp-PRD-1234567890-abcdefgh

# Metals API (from metals-api.com)
METALS_API_KEY=your_32_character_api_key_here
```

### 3. Optional Settings

Customize behavior (defaults work great):

```bash
# Scanning
ENABLE_AUTO_SCAN=true           # Auto-scan every N hours
SCAN_INTERVAL_HOURS=2           # How often to scan (1-24)

# Rate Limits (adjust if you have paid plans)
EBAY_DAILY_LIMIT=5000          # eBay calls per day
METALS_API_MONTHLY_LIMIT=50    # Metals API calls per month

# Caching (minutes)
CACHE_MARKET_HOURS=15          # Cache during trading hours
CACHE_OFF_HOURS=60             # Cache after hours
CACHE_WEEKEND=240              # Cache on weekends

# Logging
LOG_LEVEL=INFO                 # DEBUG, INFO, WARNING, ERROR
```

### 4. Advanced Configuration

**Database Location:**
```bash
DATABASE_URL=sqlite:////app/data/metals_scanner.db
```

**API Timeouts:**
```bash
API_TIMEOUT=10                 # Seconds before timeout
API_RETRY_ATTEMPTS=3           # Retry failed requests
```

## 📖 Usage Guide

### Starting the Application

**Option 1: Docker (Recommended)**
```bash
docker-compose up -d
# -d flag runs in background
```

**Option 2: Local Python**
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Using the Dashboard

1. **Open Browser**
   - Navigate to `http://localhost:8000`
   - You'll see the dashboard immediately

2. **Run First Scan**
   - Click **"🔄 Scan Now"** button
   - Wait 20-30 seconds
   - Listings will populate the table

3. **Filter Deals**
   - **Metal Type**: Choose Gold, Silver, or All
   - **Min Margin**: Drag slider to set minimum profit %
   - **Source**: Check/uncheck eBay (or future sources)

4. **Sort Results**
   - Click any column header to sort
   - Click again to reverse order
   - Default: Sorted by highest margin first

5. **View Listings**
   - Click **"View →"** to open eBay listing
   - Check seller ratings before buying
   - Verify item condition and authenticity

### API Endpoints

The scanner provides a REST API:

```bash
# Get all listings
curl http://localhost:8000/api/listings

# Get deals above 5% margin
curl "http://localhost:8000/api/deals?threshold=5"

# Trigger manual scan
curl -X POST http://localhost:8000/api/scan

# Get spot prices
curl http://localhost:8000/api/spot-prices

# Check health
curl http://localhost:8000/api/health

# View API usage
curl http://localhost:8000/api/rate-limits
```

### Auto-Refresh

Enable automatic dashboard updates:
- Check **"Auto-refresh (5 min)"** checkbox
- Dashboard will update every 5 minutes
- Useful for monitoring deals throughout the day

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │   Web Dashboard (Tailwind CSS + Vanilla JS)        │   │
│  │   - Sortable table  - Filters  - Auto-refresh      │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FASTAPI APPLICATION                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Endpoints  │  │  Scheduler   │  │ Rate Limiter │     │
│  │   /api/*     │  │  (2 hours)   │  │ (5000/day)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   SCRAPERS  │  │   PRICE API │  │  DATABASE   │
│             │  │             │  │             │
│  ┌────────┐ │  │  metals-api │  │  SQLite     │
│  │ eBay   │ │  │  .com       │  │  with WAL   │
│  │ Scraper│ │  │             │  │             │
│  └────────┘ │  │  Smart      │  │  - Listings │
│             │  │  Caching    │  │  - Prices   │
│  Rate       │  │  (15min-4hr)│  │  - Logs     │
│  Limited    │  │             │  │  - Limits   │
└─────────────┘  └─────────────┘  └─────────────┘
      │                 │
      ▼                 ▼
┌─────────────┐  ┌─────────────┐
│ eBay API    │  │ Metals API  │
│ Finding     │  │ Spot Prices │
│ Service     │  │ XAU/XAG     │
└─────────────┘  └─────────────┘
```

### Data Flow

1. **Scheduled Scan** (every 2 hours)
   - Scheduler triggers `perform_scan()`
   - Checks eBay rate limit (5000/day)

2. **eBay Scraping**
   - Searches: "gold bullion", "silver bullion", etc.
   - Extracts: Title, Price, Weight, URL
   - Regex parses weight (handles oz, grams, fractions)

3. **Price Fetching**
   - Checks cache validity (based on market hours)
   - If stale: Fetch from metals-api.com
   - If fresh: Use cached price

4. **Spread Calculation**
   ```python
   spot_value = weight_oz × spot_price_per_oz
   margin_% = ((spot_value - asking_price) / spot_value) × 100
   ```

5. **Storage**
   - Save listing to database
   - Update spot prices
   - Log API calls

6. **Dashboard Display**
   - Frontend fetches `/api/deals`
   - Applies client-side filters
   - Sorts by margin (best first)

### Database Schema

**listings** (eBay listings)
```sql
id, source, external_id, title, price,
metal_type, weight_oz, weight_extraction_failed,
url, fetched_at, spread_percentage
```

**spot_prices** (Metal prices)
```sql
id, metal_type, price_per_oz, fetched_at
```

**rate_limit_tracker** (API quotas)
```sql
id, api_name, daily_limit, daily_calls_used,
monthly_limit, monthly_calls_used, reset_at
```

**api_call_logs** (Monitoring)
```sql
id, api_name, endpoint, status_code, success,
error_message, response_time_ms, called_at
```

## 🔧 How to Add New Scrapers

Want to scrape additional marketplaces? Follow this guide:

### Step 1: Create Scraper Class

Create `app/scrapers/amazon.py`:

```python
from app.scrapers.base import BaseScraper
from app.rate_limiter import rate_limiter

class AmazonScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            api_name="amazon",
            base_url="https://api.amazon.com"
        )

    def scrape(self, search_terms=None, max_results=100, db=None):
        """
        Scrape Amazon for metal listings
        Returns list of standardized dictionaries
        """
        # Check rate limit
        rate_limiter.check_and_increment("amazon", db)

        # Make API request
        response = self.make_request("/search", params={
            "keywords": "gold bullion",
            "limit": max_results
        })

        # Parse response
        listings = []
        for item in response.json()['items']:
            listings.append({
                'source': 'amazon',
                'external_id': item['asin'],
                'title': item['title'],
                'price': float(item['price']),
                'metal_type': 'gold',  # Determine from title
                'weight_oz': self._extract_weight(item['title']),
                'weight_extraction_failed': False,
                'url': item['url']
            })

        return listings

    def _extract_weight(self, title):
        """Extract weight from title (reuse eBay logic)"""
        # Copy weight extraction from ebay.py
        pass
```

### Step 2: Register Scraper

Edit `app/scrapers/__init__.py`:

```python
from app.scrapers.base import BaseScraper
from app.scrapers.ebay import EbayScraper
from app.scrapers.amazon import AmazonScraper  # Add this

__all__ = ['BaseScraper', 'EbayScraper', 'AmazonScraper']  # Add here
```

### Step 3: Add Rate Limit Tracker

Edit `app/database.py` in `init_db()`:

```python
# Amazon tracker
amazon_tracker = db.query(RateLimitTracker).filter(
    RateLimitTracker.api_name == "amazon"
).first()
if not amazon_tracker:
    amazon_tracker = RateLimitTracker(
        api_name="amazon",
        daily_limit=10000,  # Adjust based on your plan
        daily_calls_used=0,
        reset_at=datetime.utcnow().replace(hour=0, minute=0, second=0)
    )
    db.add(amazon_tracker)
db.commit()
```

### Step 4: Use in Main App

Edit `app/main.py` in `perform_scan()`:

```python
def perform_scan(db: Session, search_terms=None, max_results=100):
    # ... existing eBay scraping ...

    # Add Amazon scraping
    try:
        amazon_scraper = AmazonScraper()
        amazon_listings = amazon_scraper.scrape(
            search_terms=search_terms,
            max_results=max_results,
            db=db
        )
        listings.extend(amazon_listings)
    except Exception as e:
        logger.error(f"Amazon scraping failed: {e}")

    # ... rest of function ...
```

### Step 5: Update Dashboard

Edit `app/static/index.html` to add Amazon checkbox:

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

That's it! Your new scraper will now run automatically.

## 🐛 Troubleshooting

### Issue: "Rate limit exceeded"

**Symptom:** Dashboard shows error "Rate limit exceeded for ebay"

**Solution:**
1. Check current usage:
   ```bash
   curl http://localhost:8000/api/rate-limits
   ```
2. Wait until reset time (shown in error message)
3. Reduce scan frequency:
   ```bash
   SCAN_INTERVAL_HOURS=4  # Change from 2 to 4 hours
   ```
4. For eBay: 5000 calls/day = ~200 scans/day max

### Issue: "No spot prices available"

**Symptom:** Dashboard shows "$--" for gold/silver prices

**Solution:**
1. Verify Metals API key is correct:
   ```bash
   # Test manually
   curl "https://metals-api.com/api/latest?access_key=YOUR_KEY&base=USD&symbols=XAU,XAG"
   ```
2. Check if you've exceeded monthly limit (50 calls)
3. Application will use cached prices as fallback
4. Logs will show: `/app/logs/metals_scanner.log`

### Issue: "No deals found"

**Symptom:** Table shows "No listings match your filters"

**Possible Causes:**

1. **No scan yet:**
   - Click "Scan Now" button
   - Wait 20-30 seconds

2. **Filters too strict:**
   - Lower minimum margin slider to 0%
   - Select "All Metals"
   - Ensure eBay checkbox is checked

3. **Invalid eBay API key:**
   ```bash
   # Check logs
   docker-compose logs | grep -i "ebay"
   # Look for authentication errors
   ```

4. **No actual deals:**
   - Real arbitrage opportunities are rare
   - Try lowering threshold to see all listings
   - Check during market volatility periods

### Issue: "Database locked"

**Symptom:** Error "database is locked"

**Solution:**
1. Ensure only one instance is running:
   ```bash
   docker-compose down
   docker-compose up -d
   ```
2. SQLite WAL mode should prevent this
3. If persistent, check file permissions:
   ```bash
   chmod 777 data/
   ```

### Issue: "Container won't start"

**Symptom:** `docker-compose up` fails

**Solution:**

1. **Check logs:**
   ```bash
   docker-compose logs
   ```

2. **Common fixes:**
   ```bash
   # Port already in use
   # Change in docker-compose.yml: "8080:8000"

   # Permission issues
   chmod 777 data/ logs/

   # Old image cached
   docker-compose down
   docker-compose build --no-cache
   docker-compose up
   ```

3. **Verify .env file:**
   ```bash
   # Must have EBAY_API_KEY and METALS_API_KEY set
   cat .env
   ```

### Issue: "Weight extraction failed"

**Symptom:** Many listings show "Unknown" weight

**Explanation:** Weight parsing uses regex and may fail for:
- Non-standard formats ("approx 1oz")
- Foreign languages
- Lots without individual weights

**Solution:**
- This is expected for some listings
- Filter by weight if needed
- Add custom regex patterns in `app/scrapers/ebay.py`:

```python
WEIGHT_PATTERNS = [
    # Add your pattern here
    (r'(\d+\.?\d*)\s*ounce', 1.0),
    # existing patterns...
]
```

### Issue: "High memory usage"

**Symptom:** Container using >500MB RAM

**Solution:**
1. Limit query results:
   ```python
   # In app/main.py
   max_results_per_search: int = 50  # Reduce from 100
   ```
2. Clean old data:
   ```bash
   docker exec -it metals-scanner sqlite3 /app/data/metals_scanner.db
   DELETE FROM listings WHERE fetched_at < datetime('now', '-7 days');
   ```

### Issue: "Slow dashboard loading"

**Symptom:** Dashboard takes >5 seconds to load

**Solution:**
1. Database indexes should prevent this
2. Reduce listing limit:
   ```javascript
   // In index.html, line ~265
   const response = await fetch('/api/listings?limit=200');
   ```
3. Add pagination (future enhancement)

## 📊 Monitoring & Maintenance

### View Logs

```bash
# Real-time logs
docker-compose logs -f

# Application logs
tail -f logs/metals_scanner.log

# Filter for errors
grep ERROR logs/metals_scanner.log
```

### Database Inspection

```bash
# Connect to database
docker exec -it metals-scanner sqlite3 /app/data/metals_scanner.db

# Useful queries
.tables                                    # List tables
SELECT COUNT(*) FROM listings;            # Total listings
SELECT * FROM rate_limit_tracker;         # API usage
SELECT metal_type, AVG(spread_percentage) # Average margins
  FROM listings GROUP BY metal_type;
```

### Backup Database

```bash
# Create backup
cp data/metals_scanner.db data/backup_$(date +%Y%m%d).db

# Restore backup
cp data/backup_20240125.db data/metals_scanner.db
docker-compose restart
```

### Performance Metrics

Check system health:
```bash
curl http://localhost:8000/api/health | jq
```

Example output:
```json
{
  "status": "healthy",
  "database": "ok",
  "last_scan": "2024-01-25T10:30:00",
  "ebay_rate_limit_remaining": 4850,
  "metals_api_rate_limit_remaining": 45
}
```

## 🔒 Security Considerations

### For Local Use (Default)
- No authentication required
- Only accessible on localhost
- API keys in `.env` (not committed to git)

### For Production Deployment

**⚠️ Before exposing to internet:**

1. **Add Authentication:**
   ```python
   # In app/main.py
   from fastapi.security import HTTPBasic, HTTPBasicCredentials
   security = HTTPBasic()
   ```

2. **Use HTTPS:**
   - Deploy behind reverse proxy (Nginx)
   - Use Let's Encrypt for SSL certificates

3. **Restrict CORS:**
   ```python
   # Change in app/main.py
   allow_origins=["https://yourdomain.com"]
   ```

4. **Use PostgreSQL:**
   - SQLite not recommended for production
   - Switch to managed PostgreSQL

5. **Environment Variables:**
   - Use secrets manager (AWS Secrets, HashiCorp Vault)
   - Never commit API keys

6. **Rate Limiting:**
   - Add Nginx rate limiting
   - Implement per-user quotas

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to add new metal types (platinum, palladium)
- Adding new data sources (Amazon, Craigslist)
- Code structure explanation
- Development guidelines

## 📝 License

MIT License - See LICENSE file for details

## ⚠️ Disclaimer

**This tool is for informational purposes only.**

- Always verify listings before purchasing
- Check seller ratings and reviews
- Inspect items for authenticity
- Spot prices are approximate and may vary
- Not responsible for transaction outcomes
- Not financial advice

**Arbitrage Risks:**
- Prices change rapidly
- Shipping costs not included in calculations
- Condition varies (BU vs circulated)
- Premiums for collectible coins
- Potential for counterfeit items

## 🙏 Acknowledgments

- [eBay Developers Program](https://developer.ebay.com/)
- [metals-api.com](https://metals-api.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Tailwind CSS](https://tailwindcss.com/)

## 📞 Support

- **Issues:** Create an issue on GitHub
- **Documentation:** See [AI_CUSTOMIZATION_GUIDE.md](AI_CUSTOMIZATION_GUIDE.md) for using AI to modify the tool
- **Questions:** Check Troubleshooting section above

---

**Built with ❤️ for precious metals enthusiasts**

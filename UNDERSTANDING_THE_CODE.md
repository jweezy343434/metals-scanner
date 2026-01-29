# Understanding the Code

This guide helps you understand how your metals scanner works and how to safely customize it for your needs.

---

## Code Structure Overview

Your scanner is organized into these main parts:

```
metals-scanner/
├── app/                      # Main application code
│   ├── main.py              # API endpoints & scan logic
│   ├── config.py            # Settings from .env file
│   ├── database.py          # Database tables & connections
│   ├── schemas.py           # Data structure definitions
│   ├── rate_limiter.py      # Prevents API quota exhaustion
│   ├── price_cache.py       # Smart price caching
│   ├── price_api.py         # Fetches spot prices
│   ├── scheduler.py         # Automatic scanning every 2 hours
│   ├── scrapers/
│   │   ├── base.py          # Scraper template
│   │   ├── ebay.py          # eBay marketplace scraper
│   │   └── __init__.py
│   └── static/
│       └── index.html       # Web dashboard (HTML/CSS/JS)
├── data/                    # Database file (created automatically)
├── logs/                    # Application logs
├── docker-compose.yml       # Docker configuration
├── Dockerfile              # How to build the container
├── requirements.txt        # Python packages needed
└── .env                    # Your API keys and settings
```

### What Each File Does

**main.py** - The heart of your scanner
- Defines web endpoints (`/api/scan`, `/api/listings`, etc.)
- Contains the `perform_scan()` function that orchestrates scanning
- Handles incoming requests from the dashboard

**database.py** - Data storage
- Defines database tables (listings, spot_prices, rate_limit_tracker)
- SQLite database (simple, file-based)
- Creates tables automatically on first run

**ebay.py** - eBay scraper
- Searches eBay using their Finding API
- Extracts weight from listing titles using regex patterns
- Returns standardized listing data

**price_api.py** - Spot price fetcher
- Calls metals-api.com to get gold/silver prices
- Works with price_cache.py to minimize API calls
- Returns prices in $/oz

**price_cache.py** - Smart caching
- Caches prices for 15 minutes (market hours) to 4 hours (weekends)
- Reduces Metals API calls from ~300/month to ~60-120/month
- Automatically handles market hours vs off-hours

**index.html** - Your dashboard
- Single HTML file with embedded CSS and JavaScript
- No build step needed - just edit and refresh browser
- Fetches data from API endpoints and displays it

---

## Safe Modifications

These changes are safe and won't break your scanner.

### Change Scan Frequency

**Location:** `.env` file

```bash
# Edit .env
nano .env
```

Change this line:
```bash
SCAN_INTERVAL_HOURS=2
```

To:
```bash
SCAN_INTERVAL_HOURS=4    # Scan every 4 hours instead of 2
```

Save, then restart:
```bash
docker compose restart
```

**When to change:**
- Reduce API usage
- Scan only during certain hours
- Range: 1-24 hours

---

### Add More eBay Search Terms

**Location:** `app/scrapers/ebay.py`

**What it does:** Searches eBay for specific keywords

Find this section (around line 50):
```python
def scrape(self, search_terms=None, max_results=100, db=None):
    if search_terms is None:
        search_terms = [
            "gold bullion",
            "silver bullion",
            "gold eagle",
            "silver eagle"
        ]
```

Add your terms:
```python
def scrape(self, search_terms=None, max_results=100, db=None):
    if search_terms is None:
        search_terms = [
            "gold bullion",
            "silver bullion",
            "gold eagle",
            "silver eagle",
            "gold maple leaf",      # Canadian coins
            "silver philharmonic",  # Austrian coins
            "gold krugerrand",      # South African coins
            "silver britannia"      # British coins
        ]
```

Restart:
```bash
docker compose restart
```

**Note:** More search terms = more API calls = hits rate limit faster.

---

### Change Dashboard Colors

**Location:** `app/static/index.html`

Find the header section (around line 40):
```html
<div class="bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg">
```

Change colors:
```html
<!-- Green theme -->
<div class="bg-gradient-to-r from-green-600 to-green-700 text-white shadow-lg">

<!-- Purple theme -->
<div class="bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg">

<!-- Dark theme -->
<div class="bg-gradient-to-r from-gray-800 to-gray-900 text-white shadow-lg">
```

Save and refresh browser. No restart needed.

**Tailwind colors available:**
- `gray`, `red`, `yellow`, `green`, `blue`, `indigo`, `purple`, `pink`
- Shades: `50`, `100`, `200`, `300`, `400`, `500`, `600`, `700`, `800`, `900`

---

### Adjust Minimum Margin Filter Default

**Location:** `app/static/index.html`

Find the margin slider (around line 120):
```html
<input
    type="range"
    id="minMarginSlider"
    min="-10"
    max="20"
    value="0"    <!-- Change this -->
    step="0.5"
>
```

Change `value="0"` to `value="5"` to default to 5% minimum margin.

Save and refresh browser.

---

### Change Auto-Refresh Interval

**Location:** `app/static/index.html`

Find the `toggleAutoRefresh()` function (around line 450):
```javascript
autoRefreshInterval = setInterval(() => {
    loadSpotPrices();
    loadListings();
}, 300000);  // 5 minutes in milliseconds
```

Change to 3 minutes:
```javascript
}, 180000);  // 3 minutes
```

Or 10 minutes:
```javascript
}, 600000);  // 10 minutes
```

Save and refresh browser.

---

### Add Custom Weight Patterns

**Location:** `app/scrapers/ebay.py`

Some eBay listings use non-standard weight formats. Add patterns to recognize them.

Find `WEIGHT_PATTERNS` (around line 20):
```python
WEIGHT_PATTERNS = [
    (r'(\d+\.?\d*)\s*oz', 1.0),
    (r'(\d+\.?\d*)\s*ounce', 1.0),
    (r'(\d+\.?\d*)\s*grams?', 0.0321507),
    # ... more patterns
]
```

Add your pattern:
```python
WEIGHT_PATTERNS = [
    (r'(\d+\.?\d*)\s*oz', 1.0),
    (r'(\d+\.?\d*)\s*ounce', 1.0),
    (r'(\d+\.?\d*)\s*grams?', 0.0321507),
    (r'approx\.?\s*(\d+\.?\d*)\s*oz', 1.0),    # Matches "approx 1oz"
    (r'(\d+\.?\d*)\s*t\.?oz', 1.0),            # Matches "1 t.oz"
    # ... more patterns
]
```

**Pattern format:**
- First part: regex pattern to match
- Second part: conversion to ounces (1.0 for oz, 0.0321507 for grams)

Restart:
```bash
docker compose restart
```

Test by running a scan and checking if more weights are extracted.

---

### Change Cache Duration

**Location:** `.env` file

Adjust how long spot prices are cached:

```bash
# Edit .env
nano .env
```

Change these lines:
```bash
# Current settings (conservative, uses ~60-120 API calls/month)
CACHE_MARKET_HOURS=15       # 15 minutes during trading hours
CACHE_OFF_HOURS=60          # 1 hour after market close
CACHE_WEEKEND=240           # 4 hours on weekends

# More aggressive caching (uses ~30-60 API calls/month)
CACHE_MARKET_HOURS=30       # 30 minutes
CACHE_OFF_HOURS=120         # 2 hours
CACHE_WEEKEND=480           # 8 hours

# Minimal caching (uses ~200+ API calls/month - will exceed free tier!)
CACHE_MARKET_HOURS=5        # 5 minutes
CACHE_OFF_HOURS=15          # 15 minutes
CACHE_WEEKEND=60            # 1 hour
```

Restart:
```bash
docker compose restart
```

**Trade-off:**
- Shorter cache = more accurate prices but more API calls
- Longer cache = fewer API calls but older prices

---

### Change Log Level

**Location:** `.env` file

Control how much detail appears in logs:

```bash
# Edit .env
nano .env
```

Change:
```bash
LOG_LEVEL=INFO
```

To:
```bash
LOG_LEVEL=DEBUG    # Show everything (useful for troubleshooting)
# or
LOG_LEVEL=WARNING  # Show only warnings and errors (quieter)
# or
LOG_LEVEL=ERROR    # Show only errors (very quiet)
```

Restart:
```bash
docker compose restart
```

---

## Moderately Safe Modifications

These changes require more understanding but are still relatively safe.

### Add a New Metal Type (e.g., Platinum)

This requires changes in multiple files. Only attempt if comfortable editing code.

**Step 1: Update schemas** (`app/schemas.py`)

Find `class MetalType`:
```python
class MetalType(str, Enum):
    GOLD = "gold"
    SILVER = "silver"
    PLATINUM = "platinum"    # Add this if not present
    ALL = "all"
```

**Step 2: Update price fetching** (`app/price_api.py`)

Find `get_spot_prices()` function and add:
```python
# Get platinum price
try:
    platinum_result = price_cache.get_or_fetch_price(
        'platinum',
        lambda _: self._fetch_price('XPT', db),
        db
    )
    prices['platinum'] = platinum_result['price_per_oz']
except Exception as e:
    logger.error(f"Failed to get platinum price: {e}")
    prices['platinum'] = None
```

**Step 3: Update eBay searches** (`app/scrapers/ebay.py`)

Add search term:
```python
search_terms = [
    "gold bullion",
    "silver bullion",
    "platinum bullion",    # Add this
    "gold eagle",
    "silver eagle",
]
```

Update metal detection:
```python
def _determine_metal_type(self, keyword: str, title: str) -> str:
    # ... existing code ...
    elif 'platinum' in keyword_lower or 'platinum' in title_lower:
        return 'platinum'
    # ... rest of code ...
```

**Step 4: Update dashboard** (`app/static/index.html`)

Add spot price display (find the spot prices section):
```html
<div class="text-center">
    <p class="text-blue-200 text-sm mb-1">Platinum Spot</p>
    <p class="text-3xl font-bold" id="platinumSpotPrice">$--</p>
    <p class="text-blue-200 text-xs" id="platinumSpotAge">Loading...</p>
</div>
```

Add to filter dropdown:
```html
<select id="metalTypeFilter" onchange="applyFilters()">
    <option value="all">All Metals</option>
    <option value="gold">Gold</option>
    <option value="silver">Silver</option>
    <option value="platinum">Platinum</option>
</select>
```

Update JavaScript (find `loadSpotPrices()` function):
```javascript
else if (price.metal_type === 'platinum') {
    document.getElementById('platinumSpotPrice').textContent =
        `$${price.price_per_oz.toFixed(2)}`;
    document.getElementById('platinumSpotAge').textContent =
        `Updated ${price.age_minutes} min ago`;
}
```

Update color coding:
```javascript
const metalColors = {
    gold: 'bg-yellow-100 text-yellow-800',
    silver: 'bg-gray-200 text-gray-800',
    platinum: 'bg-blue-100 text-blue-800'
};
```

**Step 5: Test**

```bash
docker compose restart
docker compose logs -f
```

Open dashboard and run a scan. Check for platinum listings.

---

## Advanced Modifications

These changes are more complex. Consider testing locally first (see [LOCAL_TESTING.md](LOCAL_TESTING.md)).

### Add Email Notifications

Get an email when good deals are found.

**Create notification module** (`app/notifier.py`):

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

def send_deal_alert(listing: dict, threshold: float = 10.0):
    """Send email alert for deals above threshold"""

    if listing.get('spread_percentage', 0) < threshold:
        return  # Not good enough to alert

    # Email configuration (use your Gmail or SMTP server)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "your_email@gmail.com"
    sender_password = "your_app_password"  # Use app-specific password
    receiver_email = "your_email@gmail.com"

    # Create message
    subject = f"Great Deal: {listing['spread_percentage']:.1f}% margin on {listing['metal_type']}"

    body = f"""
    A great deal was found:

    Title: {listing['title']}
    Metal: {listing['metal_type']}
    Weight: {listing['weight_oz']} oz
    Price: ${listing['price']:.2f}
    Margin: {listing['spread_percentage']:.1f}%

    View listing: {listing['url']}
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        logger.info(f"Alert sent for: {listing['title']}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
```

**Integrate into main.py:**

```python
from app.notifier import send_deal_alert

# In perform_scan() function, after saving listing:
if spread and spread > 10:  # Alert for deals > 10%
    send_deal_alert({
        'title': listing_data['title'],
        'metal_type': listing_data['metal_type'],
        'weight_oz': listing_data['weight_oz'],
        'price': listing_data['price'],
        'spread_percentage': spread,
        'url': listing_data['url']
    })
```

**Setup Gmail App Password:**

1. Enable 2-factor authentication on Gmail
2. Go to Google Account → Security → App Passwords
3. Generate password for "Mail"
4. Use this password in notifier.py

Test by running a scan with threshold lowered temporarily.

---

### Change Database to PostgreSQL

For production use or multiple instances, PostgreSQL is better than SQLite.

**This is complex.** Call me (the developer) before attempting.

---

## Risky Changes - Call Before Making

These changes can break your scanner. Contact me before attempting:

### Don't Change These Without Help:

**Database Schema** (`database.py`)
- Adding/removing columns
- Changing primary keys
- Modifying relationships
- Will corrupt existing data if done wrong

**Rate Limiting Logic** (`rate_limiter.py`)
- Could exhaust API quotas quickly
- May get your API keys banned
- Hard to debug if broken

**Authentication/Security**
- Exposing scanner to public internet
- Adding login systems
- SSL/HTTPS configuration beyond domain setup

**Docker Configuration**
- Changing base images
- Modifying port mappings incorrectly
- Altering volume mounts

### Danger Zones

**Never do these:**
- Delete `.env` file (contains your API keys)
- Commit `.env` to Git (exposes API keys publicly)
- Run scanner with `LOG_LEVEL=DEBUG` in production (performance hit)
- Set `SCAN_INTERVAL_HOURS=1` or less (will hit rate limits)
- Disable rate limiting (will exhaust API quotas)
- Set cache durations to 0 (will exceed API limits)

---

## Testing Your Changes

### Local Testing First

Before deploying changes to your server, test locally:

1. See [LOCAL_TESTING.md](LOCAL_TESTING.md) for setup
2. Make changes on your laptop
3. Test thoroughly
4. Deploy to server when working

### How to Test Changes

**After changing .env:**
```bash
# Just restart
docker compose restart
```

**After changing Python code:**
```bash
# Rebuild and restart
docker compose down
docker compose up --build -d
```

**After changing HTML:**
```bash
# No restart needed
# Just refresh browser
```

### Check Logs After Changes

```bash
# Watch logs in real-time
docker compose logs -f

# Look for errors
docker compose logs | grep ERROR

# Check last 50 lines
docker compose logs --tail=50
```

### Verify Functionality

After changes:
1. Open dashboard
2. Click "Scan Now"
3. Verify listings appear
4. Check spot prices display
5. Test filters
6. Check logs for errors

---

## Rollback Changes

If something breaks, rollback:

### Rollback Code Changes

```bash
# If using Git
git status
git checkout -- app/scrapers/ebay.py  # Replace with changed file
docker compose restart
```

### Rollback .env Changes

```bash
# Restore from backup
cp .env.backup .env
docker compose restart
```

### Rollback Database

```bash
docker compose down
cp data/backup_20240125.db data/metals_scanner.db
docker compose up -d
```

### Complete Reset

```bash
# Nuclear option - start fresh
docker compose down
git reset --hard HEAD
cp .env.backup .env
docker compose build --no-cache
docker compose up -d
```

---

## Understanding Error Messages

### Common Errors and Meanings

**"Rate limit exceeded"**
- Meaning: Used too many API calls
- Solution: Wait for reset or reduce scan frequency

**"Authentication failed"**
- Meaning: API key is wrong or expired
- Solution: Check .env file, regenerate keys if needed

**"Database is locked"**
- Meaning: Multiple processes accessing database
- Solution: Ensure only one instance running

**"Weight extraction failed"**
- Meaning: Couldn't parse weight from title
- Solution: Normal, ignore or add custom pattern

**"Connection timeout"**
- Meaning: API server not responding
- Solution: Usually temporary, wait and retry

---

## When to Call the Developer

Contact me if you want to:

1. **Add major features**
   - New marketplaces (Amazon, Craigslist, etc.)
   - Different database (PostgreSQL, MySQL)
   - Authentication system
   - Mobile app

2. **Make risky changes**
   - Database schema modifications
   - Rate limiting changes
   - Security configurations
   - Production hardening

3. **Something broke and you can't fix it**
   - Tried all troubleshooting steps
   - Rollback didn't work
   - Data corruption
   - Can't access server

4. **Want guidance on custom modifications**
   - Not sure if change is safe
   - Need architecture advice
   - Want code review before deploying

---

## Additional Resources

- **Setup:** [SETUP_GUIDE.md](SETUP_GUIDE.md) - Initial installation
- **Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Fix problems
- **Maintenance:** [MAINTENANCE.md](MAINTENANCE.md) - Ongoing care
- **Local Testing:** [LOCAL_TESTING.md](LOCAL_TESTING.md) - Test changes safely
- **Domain Setup:** [DOMAIN_SETUP.md](DOMAIN_SETUP.md) - Add custom domain

---

## Summary: What's Safe vs Risky

### ✅ Safe (Go ahead)
- Change scan frequency
- Add eBay search terms
- Modify dashboard colors
- Adjust cache duration
- Change log level
- Add weight patterns
- Adjust default filters

### ⚠️ Moderate (Be careful)
- Add new metal types
- Modify price thresholds
- Change data retention periods
- Add custom filters
- Modify search logic

### ❌ Risky (Call me first)
- Change database schema
- Modify rate limiting
- Add authentication
- Change Docker config
- Expose to public internet
- Switch to different database
- Add new data sources

When in doubt, test locally first or ask me!

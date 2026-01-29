# Metals Arbitrage Scanner

Your automated system for finding precious metals deals on eBay by comparing listing prices against real-time spot prices.

---

## What This System Does

Your metals scanner automatically:

- Searches eBay for gold and silver bullion every 2 hours
- Fetches current spot prices from metals-api.com
- Calculates profit margins for each listing
- Displays opportunities in an easy-to-read dashboard
- Runs 24/7 in the cloud without your intervention

**Example:**
```
eBay Listing: 1 oz Gold Eagle - $2,050
Current Spot: $2,150/oz
Margin: 4.7% = $100 potential profit
```

---

## What You'll Have When Done

After completing the setup:

1. **Cloud Server** - $6/month DigitalOcean droplet running 24/7
2. **Web Dashboard** - Access from any browser, anywhere
3. **Automated Scanning** - No manual work required
4. **Real-time Pricing** - Always up-to-date spot prices
5. **Deal Notifications** - See profitable opportunities immediately

**Access your dashboard:**
- From your laptop: `http://YOUR_SERVER_IP:8000`
- From your phone: Same URL works everywhere
- Optional: Use a custom domain like `https://metals.yourdomain.com`

---

## High-Level Architecture

```
┌─────────────────────────────────────────────┐
│         Web Dashboard (Browser)            │
│    - View deals  - Set filters  - Scan    │
└──────────────────┬──────────────────────────┘
                   │ HTTPS
                   ▼
┌─────────────────────────────────────────────┐
│      FastAPI Application (Python)          │
│    - Automatic scanning every 2 hours      │
│    - Rate limiting & smart caching         │
└──────────────────┬──────────────────────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
    ┌──────────┐      ┌──────────┐
    │   eBay   │      │  Metals  │
    │ Finding  │      │   API    │
    │   API    │      │  (Spot   │
    │          │      │  Prices) │
    └──────────┘      └──────────┘
```

**How it works:**

1. **Scheduler** triggers scan every 2 hours
2. **eBay scraper** searches for gold/silver bullion listings
3. **Price API** fetches current spot prices (with smart caching)
4. **Calculator** determines profit margin for each listing
5. **Database** stores listings and prices
6. **Dashboard** displays deals sorted by profitability

---

## Getting Started

Follow the setup guide to deploy your scanner:

**→ [SETUP_GUIDE.md](SETUP_GUIDE.md)** - Start here!

The guide walks you through:
1. Creating a cloud server ($6/month)
2. Installing Docker and dependencies
3. Configuring your API keys
4. Launching the scanner
5. Accessing your dashboard

**Time required:** ~90 minutes
**Technical level:** Beginner-friendly with step-by-step instructions
**Cost:** $6/month for server + free API keys

---

## System Requirements

### Server Requirements (DigitalOcean)
- Ubuntu 22.04 LTS
- 1 GB RAM minimum
- 25 GB disk space
- $6/month basic droplet

### API Requirements (Free)
- **eBay Developer Account** - Free, 5,000 API calls/day
- **Metals-API Account** - Free, 50 API calls/month

### Your Computer
- Any device with a web browser
- Internet connection
- That's it!

---

## Key Features

### Automated Scanning
- Runs every 2 hours automatically
- No manual intervention needed
- Smart scheduling respects API rate limits

### Real-time Pricing
- Gold and silver spot prices
- Market-aware caching (15 min - 4 hours)
- Automatically handles trading hours vs. weekends

### Smart Rate Limiting
- Never exceeds eBay's 5,000 calls/day limit
- Caching reduces Metals API calls to ~60-120/month
- Tracks usage and prevents quota exhaustion

### Web Dashboard
- Clean, modern interface
- Filter by metal type, margin, source
- Sortable columns
- Direct links to eBay listings
- Auto-refresh option (5 minutes)

### Data Persistence
- SQLite database stores all listings
- Historical spot prices
- API usage tracking
- Survives restarts and reboots

---

## Usage

### Accessing Your Dashboard

Open any web browser:
```
http://YOUR_SERVER_IP:8000
```

Or with custom domain (optional):
```
https://metals.yourdomain.com
```

### Running a Manual Scan

Click the **"Scan Now"** button in the dashboard, or use the API:

```bash
curl -X POST http://YOUR_SERVER_IP:8000/api/scan
```

### Filtering Results

- **Metal Type:** Gold, Silver, or All
- **Min Margin:** Slider from -10% to +20%
- **Source:** eBay (more sources can be added)

### Understanding Margins

- **Positive margin (green):** Listing below spot price = potential profit
- **Near zero (yellow):** Break-even, no arbitrage opportunity
- **Negative (red):** Above spot price, typical premium

**Remember:** Positive margins don't account for:
- Shipping costs
- Authentication/grading fees
- Seller premiums
- Condition (circulated vs. uncirculated)

Always verify listings carefully before purchasing.

---

## Documentation

Your system includes comprehensive documentation:

| Guide | Purpose | When to Use |
|-------|---------|-------------|
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Initial deployment | Setting up for the first time |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Fix problems | When something's not working |
| [MAINTENANCE.md](MAINTENANCE.md) | Ongoing care | Weekly/monthly checkups |
| [UNDERSTANDING_THE_CODE.md](UNDERSTANDING_THE_CODE.md) | Code customization | When you want to modify behavior |
| [DOMAIN_SETUP.md](DOMAIN_SETUP.md) | Add custom domain | Optional HTTPS enhancement |
| [LOCAL_TESTING.md](LOCAL_TESTING.md) | Test changes safely | Before deploying modifications |

**Start with:** [SETUP_GUIDE.md](SETUP_GUIDE.md)

---

## Typical Workflow

### Initial Setup (One Time)
1. Follow [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. Get API keys from eBay and Metals-API
3. Deploy to DigitalOcean server
4. Access dashboard and run first scan

### Daily Operation (Automatic)
1. Scanner runs automatically every 2 hours
2. You check dashboard when convenient
3. Review deals and margins
4. Visit eBay to purchase if interested

### Weekly Maintenance (5 minutes)
1. Check that scanner is running
2. Verify API quotas are within limits
3. Review logs for any errors
4. See [MAINTENANCE.md](MAINTENANCE.md)

### Monthly Tasks (15 minutes)
1. Clean old data from database
2. Update system packages
3. Create backup
4. Review monthly costs
5. See [MAINTENANCE.md](MAINTENANCE.md)

---

## Cost Breakdown

### Monthly Costs
- **DigitalOcean Server:** $6/month (1GB RAM droplet)
- **eBay API:** Free (5,000 calls/day)
- **Metals API:** Free (50 calls/month)
- **Domain (optional):** ~$1/month ($12/year)
- **Total:** $6-7/month

### API Usage
With default settings (2-hour scans):
- **eBay:** ~48 calls/day (well under 5,000 limit)
- **Metals API:** ~60-120 calls/month (slightly over free tier, uses caching)

### Scaling Costs
If you need more:
- **2GB RAM server:** $12/month
- **Metals API paid plan:** $10/month (500 calls)
- **Additional domains:** $10-15/year each

---

## Customization Examples

Your scanner is customizable. See [UNDERSTANDING_THE_CODE.md](UNDERSTANDING_THE_CODE.md) for details.

### Easy Modifications
- Change scan frequency (every 1-24 hours)
- Add more eBay search terms
- Adjust dashboard colors
- Modify cache duration
- Change default filters

### Moderate Modifications
- Add new metal types (platinum, palladium)
- Add weight patterns for extraction
- Customize email notifications
- Add data retention rules

### Advanced Modifications
- Add new data sources (Amazon, Craigslist)
- Switch to PostgreSQL database
- Add authentication
- Create mobile app interface

**Always test locally first:** [LOCAL_TESTING.md](LOCAL_TESTING.md)

---

## API Endpoints

Your scanner provides a REST API:

```bash
# Get all listings
curl http://YOUR_IP:8000/api/listings

# Get deals above 5% margin
curl http://YOUR_IP:8000/api/deals?threshold=5

# Trigger manual scan
curl -X POST http://YOUR_IP:8000/api/scan

# Get current spot prices
curl http://YOUR_IP:8000/api/spot-prices

# Check system health
curl http://YOUR_IP:8000/api/health

# View API usage
curl http://YOUR_IP:8000/api/rate-limits
```

**Interactive docs:** `http://YOUR_IP:8000/docs` (FastAPI auto-generated)

---

## Database Structure

Your data is stored in SQLite (`data/metals_scanner.db`):

**Tables:**
- `listings` - eBay listings with prices and margins
- `spot_prices` - Historical gold/silver prices
- `rate_limit_tracker` - API usage tracking
- `api_call_logs` - Request logs for monitoring

**Inspect your database:**
```bash
# SSH into server
ssh root@YOUR_SERVER_IP

# Connect to database
docker exec -it metals-scanner sqlite3 /app/data/metals_scanner.db

# Example queries
SELECT COUNT(*) FROM listings;
SELECT metal_type, AVG(spread_percentage) FROM listings GROUP BY metal_type;
.exit
```

---

## Security Considerations

### Current Setup (Good for Personal Use)
- Scanner runs on private server
- No authentication required
- Access via IP address (HTTP)
- API keys in `.env` file (not committed to Git)
- Firewall restricts access to ports 22, 80, 443

### Optional Enhancements
- **Custom domain + HTTPS:** See [DOMAIN_SETUP.md](DOMAIN_SETUP.md)
- **Restrict access to your IP:** Configure firewall rules
- **Add basic authentication:** Contact developer for help
- **Use VPN:** Access server through VPN connection

For personal use from home, current security is adequate.

---

## Troubleshooting

### Common Issues

**"Can't connect to dashboard"**
- Check server is running: `docker compose ps`
- Verify firewall allows port 80: `sudo ufw status`
- Confirm correct IP address

**"No prices showing"**
- Verify Metals API key is correct in `.env`
- Check API quota: `curl http://localhost:8000/api/rate-limits`
- Review logs: `docker compose logs | grep metal`

**"No listings found"**
- Click "Scan Now" to trigger first scan
- Lower minimum margin filter to 0%
- Check eBay API key in `.env`
- Verify logs: `docker compose logs | grep ebay`

**Full troubleshooting guide:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Getting Help

### Documentation
- Start with the relevant guide above
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for your specific issue
- Review [MAINTENANCE.md](MAINTENANCE.md) for ongoing tasks

### Contact Developer
If you need help:
- **Email:** [Your email here]
- **GitHub Issues:** [Your repo URL]/issues

**Before contacting, gather:**
- What you're trying to do
- What you expected to happen
- What actually happened
- Error messages (exact text)
- Output from: `docker compose ps` and `docker compose logs`

---

## Disclaimer

**This tool is for informational purposes only.**

- Always verify listings before purchasing
- Check seller ratings and reviews
- Inspect items for authenticity
- Spot prices are approximate and may vary
- Not responsible for transaction outcomes
- Not financial advice

**Arbitrage considerations:**
- Prices change rapidly
- Shipping costs reduce margins
- Condition varies (BU vs circulated)
- Premium for collectible coins
- Potential for counterfeit items
- Competition from other buyers

Use this scanner as a research tool, not an investment guarantee.

---

## Technical Stack

**Backend:**
- Python 3.11
- FastAPI (web framework)
- SQLAlchemy (database ORM)
- Pydantic (data validation)
- APScheduler (background tasks)
- Uvicorn (ASGI server)

**Frontend:**
- HTML5, CSS3, JavaScript (vanilla)
- Tailwind CSS (styling)
- No build step required

**Infrastructure:**
- Docker + Docker Compose
- Ubuntu 22.04 LTS
- SQLite database
- Nginx (optional, for domain/HTTPS)

**External APIs:**
- eBay Finding API
- Metals-API.com

---

## Version Information

**Current Version:** 1.0.0
**Last Updated:** January 2026
**Python Version:** 3.11+
**License:** MIT License

---

## Acknowledgments

**APIs and Services:**
- [eBay Developers Program](https://developer.ebay.com/) - Marketplace data
- [Metals-API](https://metals-api.com/) - Spot price data
- [DigitalOcean](https://www.digitalocean.com/) - Cloud hosting
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Tailwind CSS](https://tailwindcss.com/) - UI styling

---

## Quick Links

- **Setup:** [SETUP_GUIDE.md](SETUP_GUIDE.md) - Start here
- **Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Maintenance:** [MAINTENANCE.md](MAINTENANCE.md)
- **Customization:** [UNDERSTANDING_THE_CODE.md](UNDERSTANDING_THE_CODE.md)
- **Domain Setup:** [DOMAIN_SETUP.md](DOMAIN_SETUP.md)
- **Local Testing:** [LOCAL_TESTING.md](LOCAL_TESTING.md)

---

**Your metals arbitrage scanner - finding deals 24/7.**

Built for precious metals enthusiasts who want to automate the search for below-market opportunities.

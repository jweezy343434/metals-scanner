# Frequently Asked Questions (FAQ)

## General Questions

### What is this tool?
The Metals Arbitrage Scanner automatically searches eBay for precious metals (gold, silver, platinum) and compares prices against current spot prices to identify buying opportunities below market value.

### Is this tool free?
Yes, the software is free and open source (MIT License). However, you'll need free API keys from eBay and metals-api.com. Running costs depend on deployment:
- **Local use:** FREE (runs on your computer)
- **Cloud hosting:** ~$6/month (DigitalOcean droplet)

### Is arbitrage legal?
Yes, buying underpriced items and reselling them is perfectly legal. However:
- Always verify item authenticity
- Check seller ratings
- Factor in shipping costs
- Be aware of local sales tax
- Understand eBay/seller return policies

### How often does it find deals?
Real arbitrage opportunities (>10% profit) are rare. Typical results:
- **5-10% margin:** A few per day
- **10-20% margin:** A few per week
- **>20% margin:** Very rare (often mistakes or scams)

Always verify listings carefully before purchasing.

### Can I make money with this?
Potentially, but consider:
- Shipping costs reduce margins
- Authentication/grading costs
- Time to verify and purchase
- Risk of counterfeits
- Competition from other buyers
- eBay seller fees if reselling

This tool is best for:
- Finding deals for personal collection
- Learning about market pricing
- Monitoring precious metals markets

## Installation & Setup

### Do I need programming knowledge?
No! The tool includes:
- Automated setup script for deployment
- Docker for easy installation
- Pre-built dashboard
- AI customization guide for modifications

### What operating systems are supported?
- **Production (recommended):** Ubuntu 22.04 on DigitalOcean
- **Development/Local:**
  - Linux (any modern distribution)
  - macOS (Intel or Apple Silicon)
  - Windows (via WSL2 or Docker Desktop)

### How long does setup take?
- **Automated script:** 5-10 minutes
- **Manual setup:** 20-30 minutes
- **Local development:** 10 minutes

### What are the system requirements?
**Minimum:**
- 512 MB RAM
- 500 MB disk space
- Python 3.11+ (if running locally)
- Docker (recommended)

**Recommended:**
- 1 GB RAM
- 2 GB disk space
- Docker + Docker Compose

### Do I need Docker?
Not strictly required, but **highly recommended**:
- ✅ Easier setup
- ✅ Consistent environment
- ✅ No Python dependency issues
- ✅ Simple deployment

**Without Docker:** Install Python 3.11, dependencies, and run with `uvicorn`.

## API Keys & Configuration

### How do I get eBay API keys?
1. Create account at [developer.ebay.com](https://developer.ebay.com/)
2. Go to "My Account" → "Application Keys"
3. Create Production keyset (not Sandbox)
4. Copy the **App ID** (this is your `EBAY_API_KEY`)

**Free tier:** 5,000 calls/day

### How do I get Metals API keys?
1. Sign up at [metals-api.com](https://metals-api.com/signup/free)
2. Choose Free Plan
3. Copy API key from dashboard

**Free tier:** 50 calls/month (our smart caching uses ~60-120/month)

### What if I exceed API limits?
**eBay (5000/day):**
- Scanner uses ~4 calls per scan
- Default: 2-hour interval = 48 calls/day
- You're well within limits

**Metals API (50/month):**
- Smart caching reduces calls significantly
- Market hours: 15-min cache
- Off-hours: 1-hour cache
- Weekends: 4-hour cache
- Estimated usage: 60-120 calls/month

**If exceeded:**
- eBay: Wait until daily reset (midnight UTC)
- Metals API: Upgrade to paid plan or wait for monthly reset
- Scanner uses cached prices if API unavailable

### Can I use different API providers?
Yes! The code is modular. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add alternative price APIs.

## Usage Questions

### How do I start my first scan?
1. Open dashboard: `http://localhost:8000`
2. Click **"🔄 Scan Now"** button
3. Wait 20-30 seconds
4. Listings appear in table

Or via API:
```bash
curl -X POST http://localhost:8000/api/scan
```

### What do the colors mean?
**Margin percentage colors:**
- 🟢 **Green (>5%):** Good deal, potential profit
- 🟡 **Yellow (0-5%):** Break-even or small margin
- 🔴 **Red (negative):** Above spot price, no arbitrage

### Why do some listings show "Unknown" weight?
Weight extraction uses regex patterns to parse titles. It fails when:
- Weight not mentioned in title
- Non-standard formats ("approximately 1oz")
- Foreign languages
- Bulk lots without individual weights

**Solution:** Filter these out or add custom patterns (see CONTRIBUTING.md).

### How accurate are the prices?
**Spot prices:**
- Fetched from metals-api.com
- Updated based on market hours (15min-4hr cache)
- Within pennies of actual spot price

**Listing prices:**
- Exact eBay "Buy It Now" prices
- Does NOT include shipping
- May change after scanning

**Always verify on eBay before purchasing!**

### Can I filter by seller rating?
Not currently, but this is easy to add. See [AI_CUSTOMIZATION_GUIDE.md](AI_CUSTOMIZATION_GUIDE.md) for example prompts.

### Can I get email notifications for deals?
Not built-in, but you can add this feature:
1. See [CONTRIBUTING.md](CONTRIBUTING.md) - "Add Notification System"
2. Or use [AI_CUSTOMIZATION_GUIDE.md](AI_CUSTOMIZATION_GUIDE.md) with prompt:
   ```
   Add email notifications when deals are found with >10% margin.
   Use Gmail SMTP.
   ```

## Troubleshooting

### The dashboard shows "No deals found"
**Possible causes:**
1. **No scan run yet** - Click "Scan Now"
2. **Filters too strict** - Lower margin slider to 0%
3. **Invalid API keys** - Check `.env` file
4. **No actual deals** - Real arbitrage is rare
5. **Rate limit exceeded** - Check `/api/rate-limits`

### Dashboard shows "$--" for spot prices
**Causes:**
1. Invalid Metals API key
2. Monthly API limit exceeded (50 calls)
3. Network connectivity issue

**Solution:**
- Verify API key in `.env`
- Check logs: `docker compose logs | grep metal`
- Scanner will use cached prices as fallback

### Container won't start
**Diagnosis:**
```bash
# Check logs
docker compose logs

# Common issues:
# 1. Port 8000 already in use
# 2. Missing .env file
# 3. Permission issues on data/ logs/
```

**Solutions:**
```bash
# Change port in docker-compose.yml
ports: "8080:8000"

# Verify .env exists
ls -la .env

# Fix permissions
chmod 777 data/ logs/
```

### Getting "Rate limit exceeded" error
**Check current usage:**
```bash
curl http://localhost:8000/api/rate-limits
```

**Solutions:**
- Wait for reset time (shown in error)
- Increase scan interval: `SCAN_INTERVAL_HOURS=4`
- For development: Reduce scans

### Database is locked
**Cause:** Multiple instances or improper shutdown

**Solution:**
```bash
docker compose down
docker compose up -d
```

SQLite WAL mode should prevent this, but can happen if forced shutdown.

### Scans are very slow
**Normal scan time:** 20-30 seconds

**If slower:**
- Check network speed
- eBay API may be slow
- Increase timeout: `API_TIMEOUT=30` in `.env`

### Getting authentication errors
**eBay:**
- Ensure using **Production** keys, not Sandbox
- App ID format: `YourName-YourApp-PRD-1234567890-abcdefgh`

**Metals API:**
- 32-character hex string
- Test manually: `curl "https://metals-api.com/api/latest?access_key=YOUR_KEY&base=USD&symbols=XAU"`

## Development & Customization

### How do I add more metal types?
See [CONTRIBUTING.md - Adding New Metal Types](CONTRIBUTING.md#adding-new-metal-types)

Example: Adding Palladium takes ~15 minutes.

### Can I add Amazon or other sources?
Yes! See [CONTRIBUTING.md - Adding New Data Sources](CONTRIBUTING.md#adding-new-data-sources)

### How do I modify the dashboard?
**Simple changes (colors, layout):**
- Edit `app/static/index.html`
- Changes appear on browser refresh

**Backend changes:**
- Edit Python files in `app/`
- Restart: `docker compose restart`

See [AI_CUSTOMIZATION_GUIDE.md](AI_CUSTOMIZATION_GUIDE.md) for using AI to help.

### Can I run this without Docker?
Yes:

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env  # Add API keys

# Run application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### How do I contribute code?
1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Deployment Questions

### Should I deploy to the cloud?
**Pros:**
- Runs 24/7
- Always available
- Automatic scans
- Access from anywhere

**Cons:**
- ~$6/month cost
- Requires basic server management
- Potential security considerations

**Recommendation:**
- Start locally for testing
- Deploy to cloud if you want 24/7 operation

### Why DigitalOcean?
- Simple, beginner-friendly interface
- Competitive pricing ($6/month for 1GB)
- Good documentation
- Free $200 credit for new users
- Fast provisioning (60 seconds)

**Alternatives:** AWS EC2, Linode, Vultr, Google Cloud (all work with same Docker setup)

### Do I need a domain name?
**No!** You can access via IP address:
- `http://165.232.123.45:8000`

**But a domain is nice:**
- Easier to remember
- Required for SSL/HTTPS
- Professional appearance

### How do I secure my deployment?
See [DEPLOYMENT.md - Security Best Practices](DEPLOYMENT.md#security-best-practices):
1. SSH key authentication
2. Firewall (UFW)
3. SSL certificate (Let's Encrypt)
4. Non-root user
5. Automatic security updates
6. Fail2Ban (brute-force protection)

### Can I deploy to Heroku/Vercel/Netlify?
- **Heroku:** Yes (requires Dockerfile modification)
- **Vercel/Netlify:** No (they don't support long-running processes)
- **Railway:** Yes
- **Fly.io:** Yes

DigitalOcean is recommended for simplicity.

## Data & Privacy

### What data is stored?
**Database contains:**
- eBay listing details (title, price, weight, URL)
- Spot prices history
- API call logs
- Rate limit tracking

**NOT stored:**
- Your API keys (only in `.env` file)
- Personal information
- Payment details
- eBay buyer data

### Is my data secure?
**Local deployment:** Data only on your computer

**Cloud deployment:**
- Data in your private droplet
- Use HTTPS with SSL
- Restrict firewall access
- Regular backups recommended

### Can I delete old data?
Yes:

```bash
# Connect to database
docker exec -it metals-scanner sqlite3 /app/data/metals_scanner.db

# Delete old listings
DELETE FROM listings WHERE fetched_at < datetime('now', '-7 days');

# Exit
.exit
```

Or delete entire database:
```bash
docker compose down
rm data/metals_scanner.db
docker compose up -d
```

### How do I backup my data?
```bash
# Backup database
cp data/metals_scanner.db data/backup_$(date +%Y%m%d).db

# Download from server
scp user@server:~/metals-scanner/data/metals_scanner.db ~/backups/
```

## Performance

### How much RAM does it use?
- **Idle:** ~50 MB
- **During scan:** ~100-150 MB
- **Database:** Grows over time (~10 MB per 1000 listings)

### How much disk space is needed?
- **Application:** ~50 MB
- **Database:** ~10-50 MB (depends on scan history)
- **Logs:** ~5-20 MB
- **Total:** 500 MB recommended, 100 MB minimum

### Can I run multiple instances?
Not recommended with SQLite (database locking issues).

**For multiple instances:**
- Switch to PostgreSQL
- Use separate databases
- See [CONTRIBUTING.md](CONTRIBUTING.md)

### How do I improve performance?
1. **Reduce scan frequency:** `SCAN_INTERVAL_HOURS=4`
2. **Limit results:** `max_results_per_search=50`
3. **Clean old data:** Delete listings >7 days old
4. **Add indexes:** Already optimized
5. **Upgrade droplet:** Move to 2GB RAM plan

## Costs & Billing

### What are the actual monthly costs?
**Self-hosted (local):** $0

**Cloud deployment:**
| Item | Cost |
|------|------|
| DigitalOcean Droplet | $6/month |
| Domain (optional) | ~$1.25/month |
| SSL Certificate | FREE |
| **Total** | **$6-7/month** |

### Are there hidden costs?
No hidden costs, but consider:
- Bandwidth (included: 1TB/month)
- Backups ($1.20/month if enabled)
- Domain renewal ($10-15/year)
- API upgrades if needed

### How do I cancel?
1. Stop application: `docker compose down`
2. Destroy DigitalOcean droplet
3. Billing stops immediately (prorated)

## Legal & Compliance

### Is web scraping legal?
**eBay API:** Legal - you have explicit permission via API keys

**Not scraping:** Using official eBay Finding API, not scraping HTML

### Do I need to disclose I'm using an API?
No disclosure required for personal use.

If reselling items found via the scanner, follow standard eBay seller rules.

### What's the license?
MIT License - Free for personal and commercial use. See [LICENSE](LICENSE) file.

### Can I sell this tool?
Yes, MIT license allows commercial use. However:
- Must include original license
- No warranty provided
- Can't use project name in marketing

## Getting Help

### Where do I report bugs?
1. Check [FAQ.md](FAQ.md) (this file)
2. Check [TROUBLESHOOTING](README.md#troubleshooting) in README
3. Search existing GitHub Issues
4. Open new issue with:
   - Error message
   - Steps to reproduce
   - System info
   - Logs

### How do I request features?
Open a GitHub Issue with:
- Clear description
- Use case
- Example/mockup if UI change

Or implement yourself! See [CONTRIBUTING.md](CONTRIBUTING.md)

### How do I get help with customization?
1. See [AI_CUSTOMIZATION_GUIDE.md](AI_CUSTOMIZATION_GUIDE.md)
2. Use Claude Code to help modify
3. Ask in GitHub Discussions
4. Review [CONTRIBUTING.md](CONTRIBUTING.md) examples

### Is there a community?
Check the GitHub repository for:
- Discussions
- Issues
- Pull requests
- Wiki (if available)

### Can I hire someone to customize this?
Yes! This is open source software. You can:
- Hire a developer
- Use AI tools (Claude Code)
- Modify yourself following guides

---

**Still have questions?** Open a GitHub Issue or Discussion!

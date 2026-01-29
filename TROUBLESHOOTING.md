# Troubleshooting Guide

When something goes wrong with your metals scanner, this guide will help you diagnose and fix the problem.

## Quick Diagnostics

Run these commands first to gather information:

```bash
# SSH into your server
ssh root@YOUR_DROPLET_IP

# Navigate to application directory
cd ~/metals-scanner

# Check if container is running
docker compose ps

# Check recent logs
docker compose logs --tail=100

# Check application health
curl http://localhost:8000/api/health

# Check API rate limits
curl http://localhost:8000/api/rate-limits
```

---

## Common Problems

### Server Won't Start

**Symptoms:**
- Can't access dashboard at `http://YOUR_IP:8000`
- `docker compose ps` shows container is not running or "Exited"
- Browser shows "Unable to connect"

**Solutions:**

1. **Check if container is running:**
   ```bash
   cd ~/metals-scanner
   docker compose ps
   ```
   If status is "Exited", check logs:
   ```bash
   docker compose logs
   ```

2. **Restart the application:**
   ```bash
   docker compose down
   docker compose up -d
   ```

3. **Check for port conflicts:**
   ```bash
   sudo lsof -i :8000
   ```
   If another process is using port 8000, stop it or change the port in `docker-compose.yml`.

4. **Verify .env file exists:**
   ```bash
   ls -la .env
   ```
   If missing:
   ```bash
   cp .env.example .env
   nano .env  # Add your API keys
   ```

5. **Check directory permissions:**
   ```bash
   chmod 777 data logs
   ```

6. **Rebuild from scratch:**
   ```bash
   docker compose down
   docker compose build --no-cache
   docker compose up -d
   ```

---

### Can't Connect to Dashboard

**Symptoms:**
- Browser shows "This site can't be reached"
- "Connection timed out"
- "Connection refused"

**Solutions:**

1. **Verify container is running:**
   ```bash
   docker compose ps
   ```
   Status should be "Up".

2. **Check firewall settings:**
   ```bash
   sudo ufw status
   ```
   Ensure port 80 is allowed:
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw reload
   ```

3. **Try accessing locally first:**
   On the server:
   ```bash
   curl http://localhost:8000/api/health
   ```
   If this works but browser doesn't, it's a firewall issue.

4. **Verify you're using the correct IP:**
   ```bash
   # Check your droplet's IP address
   curl -4 icanhazip.com
   ```
   Use this IP in your browser: `http://SHOWN_IP:8000`

5. **Check if port is exposed:**
   ```bash
   docker compose ps
   ```
   Should show: `0.0.0.0:8000->8000/tcp` in PORTS column

6. **Restart Docker service:**
   ```bash
   sudo systemctl restart docker
   docker compose up -d
   ```

---

### No Prices Showing

**Symptoms:**
- Dashboard shows "$--" for gold/silver spot prices
- Listings appear but no margin calculations
- "No spot prices available" error

**Solutions:**

1. **Check Metals API key:**
   ```bash
   grep METALS_API_KEY .env
   ```
   Verify it's a 32-character string (no quotes).

2. **Test API key manually:**
   ```bash
   curl "https://metals-api.com/api/latest?access_key=YOUR_KEY&base=USD&symbols=XAU,XAG"
   ```
   Replace `YOUR_KEY` with your actual key.

   Should return JSON with gold (XAU) and silver (XAG) prices.

   If error: "Invalid authentication credentials" - your key is wrong.

3. **Check if you've exceeded monthly limit:**
   ```bash
   curl http://localhost:8000/api/rate-limits | jq
   ```
   Look for `metals_api_monthly_calls_used`. If >= 50, you've hit the free tier limit.

   **Wait until next month** or upgrade to paid plan at metals-api.com.

4. **Check logs for API errors:**
   ```bash
   docker compose logs | grep -i "metal"
   ```
   Look for error messages about API calls.

5. **Restart to retry API fetch:**
   ```bash
   docker compose restart
   ```

6. **Manually trigger a scan:**
   ```bash
   curl -X POST http://localhost:8000/api/scan
   ```
   Check dashboard - prices should update.

**Note:** Scanner uses cached prices as fallback. If cache is empty and API fails, no prices will show.

---

### No Listings Found

**Symptoms:**
- Table shows "No listings match your filters"
- Scan completes but no results
- Dashboard is empty after clicking "Scan Now"

**Possible Causes & Solutions:**

1. **No scan has run yet:**
   - Click **"Scan Now"** button
   - Wait 20-30 seconds for results

2. **Filters are too restrictive:**
   - Lower minimum margin slider to 0%
   - Select "All Metals" in metal type filter
   - Ensure eBay checkbox is checked
   - Refresh page

3. **Invalid eBay API key:**
   ```bash
   grep EBAY_API_KEY .env
   ```
   Verify format: `YourName-YourApp-PRD-1234567890-abcdefgh`

   **Check logs for authentication errors:**
   ```bash
   docker compose logs | grep -i "ebay"
   ```
   Look for: "Authentication failed" or "Invalid API key"

   If invalid, update .env:
   ```bash
   nano .env
   # Fix EBAY_API_KEY line
   docker compose restart
   ```

4. **Rate limit exceeded:**
   ```bash
   curl http://localhost:8000/api/rate-limits
   ```
   If eBay daily limit is reached (5000 calls), wait until reset time shown in response.

5. **No actual deals available:**
   Real arbitrage opportunities are rare. Try:
   - Lowering margin threshold to see all listings
   - Checking during market volatility periods
   - Waiting for next automatic scan

6. **eBay API is down:**
   Check eBay Developer status: https://developer.ebay.com/support/status

---

### Database Locked Error

**Symptoms:**
- Error message: "database is locked"
- Can't save listings
- Application crashes when scanning

**Solutions:**

1. **Only one instance should run:**
   ```bash
   # Stop any running instances
   docker compose down

   # Start fresh
   docker compose up -d
   ```

2. **Check for orphaned processes:**
   ```bash
   ps aux | grep metals
   ```
   If you see multiple processes, kill them:
   ```bash
   docker compose down
   sudo systemctl restart docker
   docker compose up -d
   ```

3. **Fix database file permissions:**
   ```bash
   chmod 666 data/metals_scanner.db
   chmod 777 data/
   ```

4. **Last resort - reset database:**
   **WARNING: This deletes all data**
   ```bash
   docker compose down
   rm data/metals_scanner.db
   docker compose up -d
   ```
   A fresh database will be created automatically.

---

### Rate Limit Exceeded

**Symptoms:**
- Error: "Rate limit exceeded for ebay"
- Error: "Rate limit exceeded for metals_api"
- Scan button disabled or grayed out

**Solutions:**

1. **Check current usage:**
   ```bash
   curl http://localhost:8000/api/rate-limits | jq
   ```

   Look at:
   - `ebay_daily_calls_used` (limit: 5000/day)
   - `metals_api_monthly_calls_used` (limit: 50/month)

2. **eBay rate limit (5000/day):**
   - Wait until daily reset at midnight UTC
   - Reduce scan frequency:
     ```bash
     nano .env
     # Change: SCAN_INTERVAL_HOURS=4
     docker compose restart
     ```

3. **Metals API limit (50/month):**
   - Wait until monthly reset (1st of month)
   - Or upgrade to paid plan at metals-api.com
   - Scanner will use cached prices in the meantime

4. **Verify reset time:**
   Check logs for next reset time:
   ```bash
   docker compose logs | grep "reset"
   ```

---

### Weight Extraction Failed

**Symptoms:**
- Many listings show "Unknown" weight
- Can't calculate margins for some items
- Weight column is empty

**Explanation:**

Weight extraction uses pattern matching on titles. It fails when:
- Weight not mentioned in title
- Non-standard formats ("approx 1oz", "1 t.oz")
- Foreign languages
- Bulk lots without individual weights
- Typos in listing titles

**This is normal and expected** for some listings.

**Solutions:**

1. **Filter out unknown weights:**
   Sort by weight column and ignore items with "Unknown"

2. **Add custom patterns (advanced):**
   If you notice a common pattern that's not recognized, you can add it.
   See [UNDERSTANDING_THE_CODE.md](UNDERSTANDING_THE_CODE.md) for how to modify weight patterns.

3. **Check manually:**
   Click "View" to see the eBay listing and find the weight yourself.

---

### High Memory Usage

**Symptoms:**
- Container using >500MB RAM
- Server becomes slow
- Out of memory errors

**Solutions:**

1. **Check current usage:**
   ```bash
   docker stats
   ```
   Scanner should use ~50-150MB.

2. **Restart to free memory:**
   ```bash
   docker compose restart
   ```

3. **Clean old data:**
   ```bash
   docker exec -it metals-scanner sqlite3 /app/data/metals_scanner.db
   ```
   In SQLite prompt:
   ```sql
   DELETE FROM listings WHERE fetched_at < datetime('now', '-7 days');
   DELETE FROM api_call_logs WHERE called_at < datetime('now', '-30 days');
   .exit
   ```

4. **Limit scan results:**
   ```bash
   nano .env
   ```
   Add or modify:
   ```bash
   MAX_RESULTS_PER_SEARCH=50
   ```
   ```bash
   docker compose restart
   ```

5. **Upgrade droplet:**
   If consistently high, upgrade to 2GB RAM plan in DigitalOcean ($12/month).

---

### Slow Dashboard Loading

**Symptoms:**
- Dashboard takes >5 seconds to load
- Table is sluggish
- Browser freezes when scrolling

**Solutions:**

1. **Clean old data:**
   Too many listings in database.
   ```bash
   docker exec -it metals-scanner sqlite3 /app/data/metals_scanner.db
   DELETE FROM listings WHERE fetched_at < datetime('now', '-7 days');
   .exit
   ```

2. **Check database size:**
   ```bash
   du -h data/metals_scanner.db
   ```
   If >100MB, clean old data more aggressively.

3. **Clear browser cache:**
   - Chrome/Edge: Ctrl+Shift+Delete
   - Firefox: Ctrl+Shift+Delete
   - Safari: Cmd+Option+E

4. **Check server resources:**
   ```bash
   htop
   ```
   Press F10 to exit.

   If CPU or memory is maxed out, restart:
   ```bash
   docker compose restart
   ```

---

### Scans Are Very Slow

**Symptoms:**
- Scan takes >60 seconds
- "Scan Now" button stuck in loading state
- Timeout errors

**Normal scan time:** 20-30 seconds

**Solutions:**

1. **Check network speed:**
   On server:
   ```bash
   curl -o /dev/null -s -w 'Download speed: %{speed_download} bytes/sec\n' https://www.google.com
   ```

2. **Check eBay API response time:**
   Look at logs during a scan:
   ```bash
   docker compose logs -f
   ```
   If eBay responses are slow, nothing you can do - wait it out.

3. **Increase timeout:**
   ```bash
   nano .env
   ```
   Add:
   ```bash
   API_TIMEOUT=30
   ```
   ```bash
   docker compose restart
   ```

4. **Reduce results per search:**
   ```bash
   nano .env
   ```
   Add:
   ```bash
   MAX_RESULTS_PER_SEARCH=50
   ```

---

### Authentication Errors

**Symptoms:**
- "Authentication failed"
- "Invalid API key"
- "Unauthorized" errors

**Solutions:**

1. **eBay authentication errors:**

   Verify key format:
   ```bash
   grep EBAY_API_KEY .env
   ```

   Should look like: `YourName-YourApp-PRD-1234567890-abcdefgh`

   **Common mistakes:**
   - Using Sandbox key instead of Production key
   - Extra quotes around the key
   - Spaces or newlines in the key
   - Wrong key (Client ID vs App ID)

   **Fix:**
   ```bash
   nano .env
   # Ensure format: EBAY_API_KEY=YourName-YourApp-PRD-1234567890-abcdefgh
   # No quotes, no spaces
   docker compose restart
   ```

2. **Metals API authentication errors:**

   Test key manually:
   ```bash
   curl "https://metals-api.com/api/latest?access_key=YOUR_KEY&base=USD&symbols=XAU"
   ```

   Should return JSON, not error.

   If error: Get new key from [metals-api.com/dashboard](https://metals-api.com/dashboard)

   Update .env:
   ```bash
   nano .env
   docker compose restart
   ```

---

### Container Won't Start After Reboot

**Symptoms:**
- Server restarted but scanner not running
- Container status is "Exited"
- Dashboard inaccessible after server reboot

**Solutions:**

1. **Verify Docker is enabled:**
   ```bash
   sudo systemctl status docker
   ```
   Should be "active (running)".

   If not:
   ```bash
   sudo systemctl enable docker
   sudo systemctl start docker
   ```

2. **Restart container:**
   ```bash
   cd ~/metals-scanner
   docker compose up -d
   ```

3. **Check restart policy:**
   Verify `docker-compose.yml` contains:
   ```yaml
   restart: unless-stopped
   ```

4. **Check logs for startup errors:**
   ```bash
   docker compose logs
   ```

---

## Understanding Log Messages

### How to View Logs

```bash
# Real-time logs (press Ctrl+C to exit)
docker compose logs -f

# Last 100 lines
docker compose logs --tail=100

# Only errors
docker compose logs | grep ERROR

# Only warnings and errors
docker compose logs | grep -E "WARNING|ERROR"

# Application log file
tail -f logs/metals_scanner.log
```

### Normal Log Messages

These indicate everything is working:

```
INFO: Application startup complete
INFO: Performing scheduled scan
INFO: Found 45 eBay listings for 'gold bullion'
INFO: Fetched spot prices: gold=$2150.00, silver=$25.50
INFO: Processed 120 total listings
INFO: Scan completed in 22.3 seconds
INFO: Using cached spot price (age: 12 minutes)
```

### Warning Messages

Not critical, but informational:

```
WARNING: Weight extraction failed for listing: [title]
WARNING: Using cached spot price (API limit approaching)
WARNING: No spot price found for platinum
```

**Action:** Usually none needed. These are expected occasionally.

### Error Messages

Need attention:

```
ERROR: eBay API authentication failed
ERROR: Metals API request failed: Invalid API key
ERROR: Rate limit exceeded for ebay
ERROR: Database connection failed
ERROR: Failed to fetch spot prices
```

**Action:** See specific solutions above based on the error type.

---

## When to Contact the Developer

You should reach out to me (the developer) if:

1. **None of the solutions above work**
   - You've tried all troubleshooting steps
   - Problem persists after restart
   - Error messages don't match any above

2. **Data loss or corruption**
   - Database file is corrupted
   - Lost important configuration
   - Can't recover from backup

3. **Security concerns**
   - Suspicious activity in logs
   - Unexpected server behavior
   - Potential breach

4. **Feature not working as described**
   - Something that should work doesn't
   - Behavior differs from documentation
   - Critical functionality broken

5. **You want to make significant changes**
   - Before modifying core code
   - Adding new APIs or sources
   - Changing database structure

### Before Contacting

Please gather this information:

```bash
# System info
uname -a
docker --version
docker compose version

# Container status
docker compose ps

# Recent logs (last 100 lines)
docker compose logs --tail=100

# Rate limit status
curl http://localhost:8000/api/rate-limits

# Health check
curl http://localhost:8000/api/health
```

Save this output to a text file and include it with your question.

### How to Contact

- **GitHub Issues:** [Create an issue](https://github.com/YOUR_USERNAME/metals-scanner/issues)
- **Email:** your@email.com (see README.md for actual contact)
- **Include:**
  - What you're trying to do
  - What you expected to happen
  - What actually happened
  - Error messages (copy exact text)
  - What you've already tried

---

## Preventive Measures

### Weekly Health Check (5 minutes)

```bash
# SSH into server
ssh root@YOUR_DROPLET_IP
cd ~/metals-scanner

# Check status
docker compose ps

# Check logs for errors
docker compose logs --tail=50 | grep ERROR

# Check rate limits
curl http://localhost:8000/api/rate-limits

# Check disk space
df -h

# Exit
exit
```

If all checks pass, everything is healthy.

### Monthly Maintenance

See [MAINTENANCE.md](MAINTENANCE.md) for detailed monthly tasks.

### Backup Before Changes

Before making any changes:

```bash
# Backup database
cp data/metals_scanner.db data/backup_$(date +%Y%m%d).db

# Backup .env file
cp .env .env.backup
```

You can restore from these if something breaks.

---

## Emergency Reset

If nothing else works and you want to start fresh:

**WARNING: This deletes all data**

```bash
# Stop everything
cd ~/metals-scanner
docker compose down

# Remove all data
rm -rf data logs

# Recreate directories
mkdir -p data logs
chmod 777 data logs

# Verify .env is correct
cat .env

# Rebuild from scratch
docker compose build --no-cache
docker compose up -d

# Check logs
docker compose logs -f
```

This gives you a completely fresh installation.

---

## Still Having Problems?

If you've tried everything in this guide:

1. Check [MAINTENANCE.md](MAINTENANCE.md) for ongoing care tasks
2. Review [SETUP_GUIDE.md](SETUP_GUIDE.md) to ensure setup was correct
3. See [UNDERSTANDING_THE_CODE.md](UNDERSTANDING_THE_CODE.md) if modifying code
4. Contact the developer (info in README.md)

**Include in your question:**
- What you're trying to do
- Steps you've already taken
- Complete error messages
- Output from diagnostic commands above

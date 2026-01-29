# Maintenance Guide

Your metals scanner requires minimal ongoing maintenance. This guide covers weekly checks, monthly tasks, updates, backups, and cost monitoring.

---

## Weekly Checks (5 minutes)

Perform these checks once a week to ensure everything is running smoothly.

### Quick Health Check

```bash
# SSH into your server
ssh root@YOUR_DROPLET_IP

# Navigate to application
cd ~/metals-scanner

# Check container status
docker compose ps
```

**Expected result:** Status should show "Up" (not "Exited")

### Check Dashboard

1. Open `http://YOUR_DROPLET_IP:8000` in your browser
2. Verify:
   - Gold and silver prices are displayed
   - "Last Updated" timestamp is recent (within last 2 hours)
   - Listings are present in the table
   - No error messages

### Review Logs for Errors

```bash
# Check for errors in last week
docker compose logs --since 168h | grep ERROR

# If no output, everything is fine
```

If you see errors, refer to [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

### Check API Usage

```bash
# Check rate limit status
curl http://localhost:8000/api/rate-limits | jq
```

**What to look for:**
- `ebay_daily_calls_used` should be well below 5000
- `metals_api_monthly_calls_used` should be below 50
- No warnings about approaching limits

### Check Disk Space

```bash
# Check available disk space
df -h
```

**What to look for:**
- `/` (root) should have at least 5GB free
- If below 2GB free, clean old data (see Monthly Tasks below)

### Exit

```bash
exit
```

**Weekly checklist:**
- ✅ Container is running
- ✅ Dashboard loads and shows data
- ✅ No errors in logs
- ✅ API usage within limits
- ✅ Sufficient disk space

If all checks pass, your scanner is healthy!

---

## Monthly Maintenance (15 minutes)

Perform these tasks once a month to keep your scanner running optimally.

### 1. Clean Old Data

Your database grows over time. Clean listings older than 7 days:

```bash
# SSH into your server
ssh root@YOUR_DROPLET_IP
cd ~/metals-scanner

# Connect to database
docker exec -it metals-scanner sqlite3 /app/data/metals_scanner.db
```

Run these SQL commands:

```sql
-- Delete old listings (older than 7 days)
DELETE FROM listings WHERE fetched_at < datetime('now', '-7 days');

-- Delete old spot prices (older than 7 days)
DELETE FROM spot_prices WHERE fetched_at < datetime('now', '-7 days');

-- Delete old API logs (older than 30 days)
DELETE FROM api_call_logs WHERE called_at < datetime('now', '-30 days');

-- Check how much you cleaned
SELECT COUNT(*) FROM listings;
SELECT COUNT(*) FROM spot_prices;
SELECT COUNT(*) FROM api_call_logs;

-- Exit database
.exit
```

### 2. Check Database Size

```bash
# Check database file size
du -h data/metals_scanner.db
```

**Typical size:** 10-50 MB

**If larger than 100 MB:** Run the cleanup above more frequently or set shorter retention.

### 3. Update System Packages

Keep your Ubuntu server secure and up-to-date:

```bash
# Update package list
sudo apt update

# Upgrade packages
sudo apt upgrade -y

# Remove unused packages
sudo apt autoremove -y

# Reboot if kernel was updated
# Check if reboot is required:
ls /var/run/reboot-required
# If file exists, reboot:
sudo reboot

# Wait 1-2 minutes, then SSH back in
ssh root@YOUR_DROPLET_IP
cd ~/metals-scanner

# Verify scanner restarted automatically
docker compose ps
```

### 4. Backup Database

Create a monthly backup:

```bash
# Create backup with date
cp data/metals_scanner.db data/backup_$(date +%Y%m%d).db

# List backups
ls -lh data/backup_*.db

# Keep only last 3 months (delete older backups)
cd data
ls -t backup_*.db | tail -n +4 | xargs -r rm

# Verify current backup exists
ls -lh backup_$(date +%Y%m%d).db
```

### 5. Download Backup to Local Computer

**On your local computer:**

```bash
# Download backup
scp root@YOUR_DROPLET_IP:~/metals-scanner/data/backup_$(date +%Y%m%d).db ~/Downloads/

# Verify download
ls -lh ~/Downloads/backup_*.db
```

Store this somewhere safe (external drive, cloud storage).

### 6. Review Monthly Costs

Check your DigitalOcean billing:

1. Log in to [DigitalOcean](https://cloud.digitalocean.com/)
2. Click **"Account"** → **"Billing"**
3. Review current month charges

**Expected:** ~$6/month

**If higher:** Check for:
- Extra snapshots
- Backups enabled ($1.20/month)
- Bandwidth overages (unlikely)
- Multiple droplets

### 7. Check API Quotas

```bash
# Check if you're close to API limits
curl http://localhost:8000/api/rate-limits | jq
```

**eBay:** Should reset daily (5000 calls/day)
**Metals API:** Should reset monthly (50 calls/month)

If you consistently hit Metals API limit, consider:
- Increasing cache duration in `.env`
- Upgrading to paid plan ($10/month for 500 calls)

### Monthly Checklist

- ✅ Cleaned old data from database
- ✅ Checked database size
- ✅ Updated system packages
- ✅ Created and downloaded backup
- ✅ Reviewed billing charges
- ✅ Checked API quota usage

---

## Updating the Application

When you receive code updates from the developer, follow these steps.

### When to Update

Update when:
- Developer notifies you of bug fixes
- New features are available
- Security patches are released
- You want to pull the latest version

### Update Procedure

```bash
# SSH into your server
ssh root@YOUR_DROPLET_IP
cd ~/metals-scanner

# Stop the application
docker compose down

# Backup current version
cp .env .env.backup
cp data/metals_scanner.db data/backup_before_update.db

# Pull latest code from GitHub
git pull

# If you have local changes you want to keep:
# git stash
# git pull
# git stash pop

# Check if .env has new variables
diff .env.example .env

# If there are new variables, add them:
nano .env
# Add any new settings, save with Ctrl+X, Y, Enter

# Rebuild Docker image
docker compose build --no-cache

# Start application
docker compose up -d

# Check logs for errors
docker compose logs -f
# Press Ctrl+C to exit logs

# Test dashboard
curl http://localhost:8000/api/health
```

Open `http://YOUR_DROPLET_IP:8000` in browser and verify everything works.

### If Update Fails

Rollback to previous version:

```bash
# Stop new version
docker compose down

# Restore backup
cp data/backup_before_update.db data/metals_scanner.db
cp .env.backup .env

# Revert code changes
git reset --hard HEAD~1

# Rebuild and start
docker compose build
docker compose up -d
```

Contact the developer if update consistently fails.

---

## Backup and Restore

### Creating Backups

**Automatic backup (recommended):**

Create a script to automate backups:

```bash
# Create backup script
nano ~/backup.sh
```

Paste:

```bash
#!/bin/bash
# Metals Scanner Backup Script

BACKUP_DIR=~/metals-scanner/data
DATE=$(date +%Y%m%d)

# Create backup
cp $BACKUP_DIR/metals_scanner.db $BACKUP_DIR/backup_$DATE.db

# Remove backups older than 30 days
find $BACKUP_DIR -name "backup_*.db" -mtime +30 -delete

echo "Backup completed: backup_$DATE.db"
```

Make executable:

```bash
chmod +x ~/backup.sh
```

Schedule daily backups:

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 2 AM):
0 2 * * * /root/backup.sh >> /var/log/metals_backup.log 2>&1
```

### Restoring from Backup

If you need to restore a previous version:

```bash
# Stop application
cd ~/metals-scanner
docker compose down

# List available backups
ls -lh data/backup_*.db

# Restore specific backup (replace date)
cp data/backup_20240125.db data/metals_scanner.db

# Start application
docker compose up -d

# Verify
docker compose logs -f
```

### Downloading Backups Locally

**Option 1: Manual download**

```bash
# On your local computer
scp root@YOUR_DROPLET_IP:~/metals-scanner/data/backup_*.db ~/Documents/metals-backups/
```

**Option 2: Sync all backups**

```bash
# Install rsync (if not installed)
# On server:
sudo apt install -y rsync

# On local computer:
rsync -avz root@YOUR_DROPLET_IP:~/metals-scanner/data/backup_*.db ~/Documents/metals-backups/
```

### Restoring from Local Backup

If you need to upload a backup from your computer:

```bash
# On your local computer
scp ~/Documents/metals-backups/backup_20240125.db root@YOUR_DROPLET_IP:~/metals-scanner/data/

# SSH into server
ssh root@YOUR_DROPLET_IP
cd ~/metals-scanner

# Stop application
docker compose down

# Restore uploaded backup
cp data/backup_20240125.db data/metals_scanner.db

# Start application
docker compose up -d
```

---

## Cost Monitoring

### Current Costs Breakdown

| Service | Plan | Cost |
|---------|------|------|
| DigitalOcean Droplet | 1GB RAM, 25GB SSD | $6.00/month |
| eBay API | Free tier | $0/month |
| Metals API | Free tier (50 calls) | $0/month |
| **Total** | | **$6.00/month** |

### Monitoring DigitalOcean Billing

1. Log in to [DigitalOcean](https://cloud.digitalocean.com/)
2. Click **"Account"** → **"Billing"**
3. View **"Current Month Balance"**

**Set up billing alerts:**

1. Go to **"Settings"** → **"Billing"**
2. Click **"Email Preferences"**
3. Enable: "Send billing alerts when my balance exceeds:"
4. Set threshold: $10
5. Save

You'll receive email if charges exceed $10/month.

### Monitoring Bandwidth Usage

Your droplet includes 1TB/month transfer. To check usage:

1. DigitalOcean Dashboard
2. Click your droplet
3. Go to **"Graphs"** tab
4. View **"Bandwidth"** section

**Typical usage:** 1-5 GB/month (well within limit)

### Monitoring API Costs

**eBay API:**
- Free: 5,000 calls/day
- Your usage: ~4 calls per scan × 12 scans/day = ~48 calls/day
- Well within free tier

**Metals API:**
- Free: 50 calls/month
- Your usage: ~2-5 calls/day (with caching) = ~60-150 calls/month
- May occasionally exceed (uses cached prices as fallback)

If you consistently exceed Metals API limit:

**Option 1: Increase cache duration**

```bash
nano .env
```

Change:
```bash
CACHE_MARKET_HOURS=30     # Increase from 15
CACHE_OFF_HOURS=120       # Increase from 60
CACHE_WEEKEND=480         # Increase from 240
```

```bash
docker compose restart
```

**Option 2: Upgrade to paid plan**

- Basic: $10/month (500 calls)
- Pro: $50/month (5000 calls)

Upgrade at: https://metals-api.com/product

### Cost Optimization Tips

**Reduce DigitalOcean costs:**
- Current plan ($6/month) is already the cheapest for 1GB RAM
- $4/month plan available but only has 512MB (may be too little)

**Reduce API costs:**
- Adjust cache settings to reduce API calls
- Reduce scan frequency: `SCAN_INTERVAL_HOURS=4` instead of 2

**Snapshot costs:**
- Avoid creating snapshots unless needed
- Snapshots cost $0.05/GB/month (~$1-2/month)
- Use database backups instead (free)

---

## Monitoring and Alerts

### Enable DigitalOcean Monitoring

Your droplet should have monitoring enabled (you enabled this during setup).

View metrics:

1. DigitalOcean Dashboard
2. Click your droplet
3. **"Graphs"** tab shows:
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network traffic

### Set Up Alerts

Create alerts for issues:

1. DigitalOcean Dashboard
2. Click **"Manage"** → **"Alerts"**
3. Click **"Create Alert Policy"**
4. Configure:
   - **Metric:** CPU utilization
   - **Threshold:** Above 90%
   - **Duration:** 5 minutes
   - **Notify:** Your email
5. Save

Repeat for:
- Memory usage > 90%
- Disk usage > 90%

### Custom Health Check Script

Create a script to check scanner health:

```bash
nano ~/check-health.sh
```

Paste:

```bash
#!/bin/bash

# Check if scanner is healthy
HEALTH=$(curl -s http://localhost:8000/api/health)
STATUS=$(echo $HEALTH | jq -r '.status' 2>/dev/null)

if [ "$STATUS" != "healthy" ]; then
    echo "$(date): Scanner is unhealthy!" >> ~/scanner-alerts.log
    echo "Health response: $HEALTH" >> ~/scanner-alerts.log

    # Optionally send email (requires mail setup)
    # echo "Scanner is unhealthy: $HEALTH" | mail -s "Scanner Alert" your@email.com

    # Attempt restart
    cd ~/metals-scanner
    docker compose restart >> ~/scanner-alerts.log 2>&1
fi
```

Make executable:

```bash
chmod +x ~/check-health.sh
```

Schedule to run every 5 minutes:

```bash
crontab -e

# Add this line:
*/5 * * * * /root/check-health.sh
```

### View Alert Log

```bash
tail -f ~/scanner-alerts.log
```

---

## Scaling and Upgrades

### When to Upgrade

Consider upgrading if:
- CPU consistently above 80%
- Memory consistently above 80%
- Slow response times
- Adding more data sources (Amazon, etc.)
- Increasing scan frequency significantly

### How to Upgrade Droplet

**Resize to 2GB RAM ($12/month):**

1. DigitalOcean Dashboard
2. Click your droplet
3. Click **"Resize"** (left menu)
4. Select **"2 GB / 1 CPU / $12/month"**
5. Click **"Resize Droplet"**
6. Wait 1-2 minutes

Your droplet will reboot. Scanner restarts automatically.

**Note:** You can only resize up, not down. Backup first.

### When to Add Backups

DigitalOcean offers automated backups for $1.20/month (20% of droplet cost).

**Backups include:**
- Entire droplet image
- Weekly automated snapshots
- Easy restore

**Enable backups:**

1. DigitalOcean Dashboard
2. Click your droplet
3. Click **"Backups"**
4. Toggle **"Enable Backups"**

**Do you need this?**
- **No** - if you backup database regularly (covered above)
- **Yes** - if you want entire system snapshots

---

## Security Maintenance

### Update System Regularly

```bash
# Run monthly (or more often)
sudo apt update && sudo apt upgrade -y
```

### Review SSH Access

Check who's connected:

```bash
# Show current SSH sessions
who

# Show SSH login attempts
sudo cat /var/log/auth.log | grep sshd
```

### Update SSH Key

If your laptop is compromised, remove old key and add new one:

```bash
# On server, edit authorized keys
nano ~/.ssh/authorized_keys

# Remove old key line, add new one
# Save and exit
```

### Monitor for Suspicious Activity

```bash
# Check system logs
sudo tail -f /var/log/syslog

# Check Docker logs
docker compose logs --tail=100

# Check for unusual processes
ps aux | grep -v "docker\|metals"
```

---

## Troubleshooting Maintenance Tasks

### Backup Script Not Running

Check cron log:

```bash
sudo grep backup /var/log/syslog
```

Test script manually:

```bash
~/backup.sh
```

### Can't Connect to Database

```bash
# Check if container is running
docker compose ps

# Check file permissions
ls -l data/metals_scanner.db

# Fix permissions
chmod 666 data/metals_scanner.db
```

### Disk Space Issues

```bash
# Find large files
du -sh /* | sort -h

# Clean Docker images
docker system prune -a

# Clean old logs
truncate -s 0 logs/metals_scanner.log
```

---

## Maintenance Calendar

### Daily (Automatic)
- ✅ Scans run every 2 hours automatically
- ✅ Health checks (if configured)
- ✅ Automatic backups (if configured)

### Weekly (5 minutes)
- ⏱️ Check container status
- ⏱️ Review logs for errors
- ⏱️ Verify API usage
- ⏱️ Check disk space

### Monthly (15 minutes)
- ⏱️ Clean old data
- ⏱️ Update system packages
- ⏱️ Create and download backup
- ⏱️ Review costs and usage
- ⏱️ Check for application updates

### Quarterly (30 minutes)
- ⏱️ Review security settings
- ⏱️ Audit access logs
- ⏱️ Test backup restoration
- ⏱️ Consider optimizations

### Annually (1 hour)
- ⏱️ Review overall architecture
- ⏱️ Consider upgrades or changes
- ⏱️ Renew domain (if applicable)
- ⏱️ Review and update documentation

---

## Need Help?

- **Maintenance issues:** Check this guide again
- **Application errors:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Code changes:** See [UNDERSTANDING_THE_CODE.md](UNDERSTANDING_THE_CODE.md)
- **Can't solve it:** Contact the developer (info in README.md)

Your scanner is designed to run with minimal maintenance. Following the weekly and monthly checklists above will keep it running smoothly for years.

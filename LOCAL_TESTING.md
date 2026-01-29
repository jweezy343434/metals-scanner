# Local Testing Guide

This guide shows you how to run your metals scanner on your personal computer (laptop) to test changes before deploying them to your production server.

**Why test locally?**
- Safe experimentation without breaking your live scanner
- Faster iteration (no need to SSH into server)
- See changes immediately
- Easy to rollback if something breaks

---

## Prerequisites

Install these on your **local computer** (laptop):

- **Python 3.11 or higher** ([Download](https://www.python.org/downloads/))
- **Git** (usually pre-installed on Mac/Linux, [download for Windows](https://git-scm.com/downloads))
- **Text editor** (VS Code, Sublime, or any editor you like)

---

## Quick Start (10 minutes)

### Step 1: Download the Code

**If you have the code from GitHub:**

```bash
# Open terminal on your local computer
cd ~/Documents  # or wherever you want to store it

# Clone from GitHub
git clone https://github.com/YOUR_USERNAME/metals-scanner.git
cd metals-scanner
```

**If you uploaded code directly to server (without GitHub):**

```bash
# Download from your server to local computer
scp -r root@YOUR_DROPLET_IP:~/metals-scanner ~/Documents/

# Navigate to directory
cd ~/Documents/metals-scanner
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate

# On Windows (Command Prompt):
venv\Scripts\activate.bat

# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# On Windows (Git Bash):
source venv/Scripts/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

This installs all Python packages your scanner needs.

### Step 4: Configure for Local Testing

```bash
# Copy example configuration
cp .env.example .env

# Edit with your API keys
# Mac/Linux:
nano .env

# Windows:
notepad .env

# Or use VS Code:
code .env
```

**Add your API keys:**
```bash
EBAY_API_KEY=YourName-YourApp-PRD-1234567890-abcdefgh
METALS_API_KEY=your_actual_32_character_api_key
```

**IMPORTANT:** Use the same API keys as your production server. This ensures you're testing with real data.

Save and close the file.

### Step 5: Create Local Directories

```bash
# Create data and logs directories
mkdir -p data logs

# On Windows (Command Prompt):
mkdir data
mkdir logs
```

### Step 6: Run the Scanner Locally

```bash
# Start the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Will watch for changes in these directories: ['/path/to/metals-scanner']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

### Step 7: Open Dashboard

Open your web browser and go to:
```
http://localhost:8000
```

**CHECKPOINT:** You should see your metals scanner dashboard!

### Step 8: Test It Works

1. Click **"Scan Now"** button
2. Wait 20-30 seconds
3. Listings should appear

**You're now running the scanner locally!**

To stop it: Press `Ctrl + C` in the terminal.

---

## Making and Testing Changes

### Workflow: Test → Deploy

**Good workflow:**
1. Make changes on your laptop
2. Test changes locally
3. Verify everything works
4. Deploy to server

**Bad workflow:**
1. Make changes directly on server
2. Hope it works
3. Break production scanner
4. Panic

### Example: Change Scan Frequency

**Step 1: Make change on local computer**

Edit `.env` file:
```bash
# Change from:
SCAN_INTERVAL_HOURS=2

# To:
SCAN_INTERVAL_HOURS=4
```

Save the file.

**Step 2: Restart local scanner**

In terminal (where scanner is running):
- Press `Ctrl + C` to stop
- Press `Up Arrow` to recall last command
- Press `Enter` to restart

Or just run:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Step 3: Verify change**

Check logs in terminal - should show new interval.

**Step 4: Test thoroughly**

- Open dashboard
- Run a scan
- Check logs for errors
- Verify everything still works

**Step 5: Deploy to server**

```bash
# Copy .env file to server
scp .env root@YOUR_DROPLET_IP:~/metals-scanner/

# SSH into server
ssh root@YOUR_DROPLET_IP
cd ~/metals-scanner

# Restart scanner
docker compose restart

# Check logs
docker compose logs -f
```

**CHECKPOINT:** Production scanner now has your tested change!

---

## Types of Changes and Testing

### Configuration Changes (.env file)

**Changes:**
- Scan frequency
- Cache duration
- Log level
- API limits

**Testing:**
```bash
# Stop scanner (Ctrl+C)
# Edit .env
nano .env

# Restart scanner
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Verify in logs that new settings are applied
```

**Deploy:**
```bash
scp .env root@YOUR_DROPLET_IP:~/metals-scanner/
ssh root@YOUR_DROPLET_IP "cd ~/metals-scanner && docker compose restart"
```

### Python Code Changes (app/*.py files)

**Changes:**
- Adding search terms
- Modifying scrapers
- Adding features
- Fixing bugs

**Testing:**
```bash
# Scanner should be running with --reload flag
# Edit Python file (e.g., app/scrapers/ebay.py)
code app/scrapers/ebay.py

# Save changes
# Scanner automatically restarts (thanks to --reload)
# Check terminal for restart confirmation and errors

# Test functionality in dashboard
```

**Deploy:**
```bash
# If using GitHub:
git add app/scrapers/ebay.py
git commit -m "Added new search terms"
git push

# On server:
ssh root@YOUR_DROPLET_IP
cd ~/metals-scanner
git pull
docker compose restart

# If not using GitHub:
scp app/scrapers/ebay.py root@YOUR_DROPLET_IP:~/metals-scanner/app/scrapers/
ssh root@YOUR_DROPLET_IP "cd ~/metals-scanner && docker compose restart"
```

### Dashboard Changes (app/static/index.html)

**Changes:**
- Colors
- Layout
- Filters
- JavaScript logic

**Testing:**
```bash
# Scanner should be running
# Edit HTML file
code app/static/index.html

# Save changes
# No restart needed!
# Just refresh browser (Ctrl+R or Cmd+R)

# Test all functionality:
# - Scan button
# - Filters
# - Sorting
# - Links
```

**Deploy:**
```bash
scp app/static/index.html root@YOUR_DROPLET_IP:~/metals-scanner/app/static/
# No restart needed - changes apply immediately
```

---

## Local vs Production Differences

### What's the Same

- Same code
- Same API keys
- Same database structure
- Same functionality

### What's Different

| Aspect | Local | Production |
|--------|-------|------------|
| **Location** | Your laptop | DigitalOcean server |
| **Access** | `localhost:8000` | `http://YOUR_IP:8000` or your domain |
| **Database** | Local file (`data/metals_scanner.db`) | Server file |
| **Uptime** | Only when you run it | 24/7 |
| **Data** | Your test data | Real accumulated data |
| **Environment** | Development | Production |
| **Auto-reload** | Yes (with `--reload` flag) | No |

### Important Notes

**Separate databases:**
- Local database: `~/Documents/metals-scanner/data/metals_scanner.db`
- Server database: `~/metals-scanner/data/metals_scanner.db`
- They don't sync automatically
- This is good - keeps test data separate

**API quotas are shared:**
- Both local and server use the same API keys
- API calls count toward the same limits
- Don't run both at the same time during testing to avoid hitting limits

**Test data:**
- Scans you run locally create test data
- This data only exists on your laptop
- Doesn't affect production data

---

## Testing Checklist

Before deploying changes to production:

### Functional Testing
- ✅ Scanner starts without errors
- ✅ Dashboard loads in browser
- ✅ "Scan Now" button works
- ✅ Listings appear in table
- ✅ Spot prices display correctly
- ✅ Filters work
- ✅ Sorting works
- ✅ Links to eBay work

### Error Checking
- ✅ No errors in terminal logs
- ✅ No JavaScript errors in browser console (F12)
- ✅ Check `logs/metals_scanner.log` for errors

### Edge Cases
- ✅ What happens if no deals found?
- ✅ What if API is slow?
- ✅ What if rate limit is reached?

### Code Review
- ✅ Did you break anything else?
- ✅ Are there any obvious bugs?
- ✅ Does it make sense?

If all checks pass, deploy to production!

---

## Common Local Testing Tasks

### Test a New Search Term

**Edit:** `app/scrapers/ebay.py`

```python
search_terms = [
    "gold bullion",
    "silver bullion",
    "gold maple leaf",  # Add this
]
```

**Test:**
- Save file (scanner auto-restarts)
- Click "Scan Now" in dashboard
- Check logs: Should show "Found X listings for 'gold maple leaf'"
- Verify new listings appear

**Deploy if working:**
```bash
scp app/scrapers/ebay.py root@YOUR_DROPLET_IP:~/metals-scanner/app/scrapers/
ssh root@YOUR_DROPLET_IP "cd ~/metals-scanner && docker compose restart"
```

### Test Dashboard Color Change

**Edit:** `app/static/index.html`

Find:
```html
<div class="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
```

Change to:
```html
<div class="bg-gradient-to-r from-green-600 to-green-700 text-white">
```

**Test:**
- Save file
- Refresh browser
- Header should be green

**Deploy if you like it:**
```bash
scp app/static/index.html root@YOUR_DROPLET_IP:~/metals-scanner/app/static/
```

### Test Increasing Cache Duration

**Edit:** `.env`

```bash
CACHE_MARKET_HOURS=30  # Increase from 15 to 30
```

**Test:**
- Restart scanner
- Run two scans 20 minutes apart
- Check logs - second scan should use cached prices
- Verify: "Using cached spot price (age: XX minutes)"

**Deploy if working:**
```bash
scp .env root@YOUR_DROPLET_IP:~/metals-scanner/
ssh root@YOUR_DROPLET_IP "cd ~/metals-scanner && docker compose restart"
```

---

## Troubleshooting Local Testing

### "Module not found" errors

```bash
# Make sure virtual environment is activated
# You should see (venv) in prompt

# If not:
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### "Port 8000 already in use"

```bash
# Find what's using port 8000
# Mac/Linux:
lsof -i :8000

# Windows:
netstat -ano | findstr :8000

# Kill the process or use different port:
uvicorn app.main:app --reload --port 8001
```

### "Permission denied" errors

```bash
# Fix directory permissions
chmod 755 data logs

# On Windows, run terminal as Administrator
```

### "Can't connect to database"

```bash
# Make sure only one instance is running
# Stop server version:
ssh root@YOUR_DROPLET_IP "cd ~/metals-scanner && docker compose down"

# Or use different database file for local testing
# Edit .env:
DATABASE_URL=sqlite:////app/data/metals_scanner_local.db
```

### Changes Not Appearing

**Python code changes:**
- Check terminal - scanner should auto-restart
- Look for "Reloading..." message
- If not restarting, stop (Ctrl+C) and start again

**HTML changes:**
- Hard refresh browser: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
- Clear browser cache
- Try incognito/private browsing window

**Configuration changes:**
- Must restart scanner after editing .env
- Changes don't apply automatically

---

## Switching Between Local and Production

### Stop Local, Check Production

```bash
# On local computer:
# Stop local scanner (Ctrl+C in terminal)

# Check production is still running:
# Open browser: http://YOUR_DROPLET_IP:8000
```

### Stop Production, Test Locally

```bash
# Stop production (to avoid API quota conflicts)
ssh root@YOUR_DROPLET_IP "cd ~/metals-scanner && docker compose down"

# Run locally
cd ~/Documents/metals-scanner
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Resume Production After Testing

```bash
# Stop local (Ctrl+C)

# Restart production
ssh root@YOUR_DROPLET_IP "cd ~/metals-scanner && docker compose up -d"
```

---

## Advanced: Using Docker Locally

If you want to test the exact production environment locally, use Docker.

### Prerequisites

- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Build and Run

```bash
cd ~/Documents/metals-scanner

# Build Docker image
docker compose build

# Run container
docker compose up -d

# View logs
docker compose logs -f

# Open browser: http://localhost:8000

# Stop
docker compose down
```

This runs the exact same setup as production on your laptop.

---

## Best Practices

### Do's ✅
- Always test changes locally first
- Keep separate databases (local vs production)
- Use version control (Git) for tracking changes
- Test thoroughly before deploying
- Keep notes of what changes you made
- Back up production before deploying big changes

### Don'ts ❌
- Don't run local and production simultaneously (API quota conflicts)
- Don't use production database locally (risk of corruption)
- Don't skip testing "small" changes
- Don't deploy untested code to production
- Don't forget to restart after configuration changes

---

## Cleaning Up

### When Done Testing

```bash
# Stop local scanner (Ctrl+C in terminal)

# Deactivate virtual environment
deactivate

# Clear test data if desired
cd ~/Documents/metals-scanner
rm -rf data logs

# Keep the code for future testing
```

### Removing Local Setup Completely

```bash
# Delete entire local setup
rm -rf ~/Documents/metals-scanner

# Uninstall Python packages (optional)
# They're in the virtual environment, so they're already isolated
```

---

## Quick Reference

### Starting Local Scanner

```bash
cd ~/Documents/metals-scanner
source venv/bin/activate  # Mac/Linux
# or: venv\Scripts\activate  # Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Stopping Local Scanner

```
Press Ctrl+C in terminal
```

### Deploying to Production

```bash
# Copy files
scp [file] root@YOUR_DROPLET_IP:~/metals-scanner/[path]

# Restart production
ssh root@YOUR_DROPLET_IP "cd ~/metals-scanner && docker compose restart"
```

---

## When to Test Locally vs. Directly on Server

### Test Locally First (Recommended)
- Adding new features
- Changing core logic
- Trying experimental changes
- Learning how something works
- Major refactoring

### Can Change Directly on Server (If Confident)
- Small config changes (scan frequency, log level)
- Dashboard color tweaks
- Minor text changes
- Adding a single search term

Even "safe" changes benefit from local testing!

---

## Next Steps

Now that you can test locally:

1. **Experiment safely** - Try changes without fear
2. **Iterate quickly** - No waiting for server deploys
3. **Learn the code** - See how changes affect behavior
4. **Customize confidently** - Test before deploying

### Additional Resources

- **Code Understanding:** [UNDERSTANDING_THE_CODE.md](UNDERSTANDING_THE_CODE.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Maintenance:** [MAINTENANCE.md](MAINTENANCE.md)
- **Domain Setup:** [DOMAIN_SETUP.md](DOMAIN_SETUP.md)

---

## Summary

**What you learned:**
- ✅ How to run scanner on your laptop
- ✅ Test changes before deploying
- ✅ Iterate quickly on modifications
- ✅ Keep production safe while experimenting

**Key workflow:**
1. Make changes locally
2. Test thoroughly
3. Deploy to production
4. Verify on server

**Remember:** Local testing saves you from breaking your production scanner. Always test first!

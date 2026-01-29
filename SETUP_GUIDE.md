# Setup Guide: Your Metals Arbitrage Scanner

This guide will set up YOUR metals arbitrage scanner. Follow each step in order. The whole process takes about 90 minutes. By the end, you'll have a system running 24/7 finding arbitrage opportunities.

## Prerequisites (5 minutes)

Before you begin, you'll need:

1. **Credit card** for DigitalOcean account
2. **eBay Developer account** for API access
3. **Metals-API account** for spot prices

Don't have these yet? Get them now:
- DigitalOcean: [Sign up here](https://www.digitalocean.com/) - New users get $200 free credit
- eBay Developer: [Register here](https://developer.ebay.com/) - Free account
- Metals-API: [Sign up here](https://metals-api.com/signup/free) - Free plan (50 calls/month)

### Monthly Cost
- DigitalOcean Droplet: $6/month (1GB RAM, 25GB SSD)
- eBay API: FREE (5,000 calls/day)
- Metals-API: FREE (50 calls/month)
- **Total: $6/month**

---

## Part 1: Server Creation (15 minutes)

You'll create a cloud server (called a "droplet") on DigitalOcean.

### 1.1 Create DigitalOcean Account

1. Go to [DigitalOcean](https://www.digitalocean.com/)
2. Click "Sign Up"
3. Enter your email and password
4. Verify your email
5. Add a payment method (credit card)
   - New users receive $200 in credits
   - Charges begin after credits run out or after 60 days

### 1.2 Create Your Droplet

1. Log in to [DigitalOcean Dashboard](https://cloud.digitalocean.com/)
2. Click the green **"Create"** button (top right)
3. Select **"Droplets"**

### 1.3 Choose Droplet Configuration

Follow these exact settings:

**Region:**
- Choose datacenter closest to you
- Example: "New York 1" for US East Coast

**Image:**
- Click **"Ubuntu"**
- Select **"22.04 (LTS) x64"**

**Droplet Size:**
- Click **"Basic"** plan
- Select **"Regular"** CPU option
- Choose **$6/month** plan:
  - 1 GB RAM
  - 1 vCPU
  - 25 GB SSD Disk
  - 1000 GB Transfer

This is sufficient for your scanner (uses ~50-100MB RAM).

**Authentication:**
- Select **"SSH Key"** (recommended and more secure)
- Click **"New SSH Key"**
- Keep this browser tab open, then follow Step 1.4

### 1.4 Generate SSH Key

On your **local computer** (Mac/Windows/Linux), open Terminal (Mac/Linux) or PowerShell (Windows):

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Press Enter to accept default location
# Press Enter twice to skip passphrase (or set one for extra security)
```

Now copy your public key:

**Mac/Linux:**
```bash
cat ~/.ssh/id_ed25519.pub
```

**Windows PowerShell:**
```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub
```

**Windows Git Bash:**
```bash
cat ~/.ssh/id_ed25519.pub
```

Copy the entire output (starts with `ssh-ed25519`).

### 1.5 Add SSH Key to DigitalOcean

1. Back in the DigitalOcean browser tab
2. Paste your public key into the text box
3. Give it a name: "My Laptop"
4. Click **"Add SSH Key"**
5. Ensure the checkbox next to your key is checked

### 1.6 Finalize Droplet Settings

**Hostname:**
- Enter: `metals-scanner`

**Tags:**
- Add tag: `metals-scanner` (helps you find it later)

**Advanced Options:**
- Check **"Monitoring"** (free, shows CPU/RAM graphs)
- Leave everything else unchecked

### 1.7 Create Droplet

1. Click green **"Create Droplet"** button (bottom right)
2. Wait 30-60 seconds for creation
3. Your droplet will appear with an IP address (example: `165.232.123.45`)
4. **Write down this IP address** - you'll need it throughout this guide

**CHECKPOINT:** You should see your droplet listed with a green "Active" status and an IP address.

---

## Part 2: Server Preparation (20 minutes)

Now you'll connect to your server and install the necessary software.

### 2.1 Connect to Your Server

On your **local computer**, open Terminal/PowerShell:

```bash
ssh root@YOUR_DROPLET_IP
# Replace YOUR_DROPLET_IP with the actual IP from Step 1.7
# Example: ssh root@165.232.123.45
```

If asked "Are you sure you want to continue connecting?", type `yes` and press Enter.

**CHECKPOINT:** You should see a welcome message:
```
Welcome to Ubuntu 22.04.3 LTS (GNU/Linux ...)
```

Your terminal prompt should now show: `root@metals-scanner:~#`

### 2.2 Update the System

Run these commands one at a time:

```bash
# Update package list (takes ~10 seconds)
apt update

# Upgrade installed packages (takes 2-5 minutes)
apt upgrade -y

# Install basic utilities (takes ~30 seconds)
apt install -y curl wget git ufw
```

Wait for each command to complete before running the next one.

### 2.3 Configure Firewall

Secure your server by allowing only necessary traffic:

```bash
# Allow SSH (IMPORTANT: Do this first!)
ufw allow 22/tcp

# Allow HTTP (for your web dashboard)
ufw allow 80/tcp

# Enable firewall (type 'y' when prompted)
ufw enable

# Verify it's working
ufw status
```

**CHECKPOINT:** You should see:
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
```

### 2.4 Install Docker

Docker will run your application in a container:

```bash
# Add Docker's official GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package list
apt update

# Install Docker (takes 1-2 minutes)
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

**Test Docker installation:**

```bash
# Check Docker version
docker --version

# Should show: Docker version 24.x.x or higher

# Check Docker Compose version
docker compose version

# Should show: Docker Compose version v2.x.x
```

**CHECKPOINT:** Both commands should show version numbers without errors.

### 2.5 Test Docker

```bash
# Run test container
docker run hello-world
```

**CHECKPOINT:** You should see "Hello from Docker!" message. This confirms Docker is working correctly.

---

## Part 3: Application Setup (30 minutes)

Now you'll get your application code and configure it with your API keys.

### 3.1 Get API Keys

Before cloning the code, gather your API keys.

#### 3.1.1 Get eBay API Key

1. Go to [eBay Developer Program](https://developer.ebay.com/)
2. Click **"Register"** (or log in if you already have an account)
3. Verify your email
4. Go to [Application Keys](https://developer.ebay.com/my/keys)
5. Click **"Create a keyset"** or **"Get your Application Keys"**
6. **IMPORTANT:** Choose **Production** (not Sandbox)
7. Fill in application details:
   - Application Title: "Metals Scanner"
   - Short Description: "Personal metals arbitrage scanner"
8. Click **"Continue"**
9. You'll see your **App ID** (looks like: `YourName-MetalsSc-PRD-1234567890-abcdefgh`)
10. **Copy this App ID** - this is your `EBAY_API_KEY`

#### 3.1.2 Get Metals-API Key

1. Go to [Metals-API](https://metals-api.com/signup/free)
2. Choose **Free Plan**
3. Enter your email and create a password
4. Verify your email
5. Log in to your [Dashboard](https://metals-api.com/dashboard)
6. You'll see your **API Key** (32-character string)
7. **Copy this key** - this is your `METALS_API_KEY`

**Save both keys** in a text file on your local computer for now. You'll use them in Step 3.4.

### 3.2 Clone the Repository

Back on your **server** (in the SSH session):

```bash
# Navigate to home directory
cd ~

# Clone the repository
git clone https://github.com/YOUR_USERNAME/metals-scanner.git

# Navigate into the directory
cd metals-scanner

# Verify files are there
ls -la
```

**CHECKPOINT:** You should see files including:
- `app/` (directory)
- `docker-compose.yml`
- `Dockerfile`
- `.env.example`
- `README.md`

**Note:** Replace `YOUR_USERNAME` with your actual GitHub username. If you haven't uploaded this to GitHub yet, see the note at the end of this section.

### 3.3 Create Data Directories

```bash
# Still in ~/metals-scanner directory
mkdir -p data logs
chmod 777 data logs
```

### 3.4 Configure Environment Variables

Create your configuration file:

```bash
# Copy the example file
cp .env.example .env

# Edit with nano text editor
nano .env
```

You're now in the nano text editor. **Edit these lines:**

Replace this:
```bash
EBAY_API_KEY=your_ebay_app_id_here
METALS_API_KEY=your_metals_api_key_here
```

With your actual keys (from Step 3.1):
```bash
EBAY_API_KEY=YourName-MetalsSc-PRD-1234567890-abcdefgh
METALS_API_KEY=your_actual_32_character_api_key_from_metals_api
```

**Leave everything else as-is.** The defaults are already optimized.

**Save and exit nano:**
1. Press `Ctrl + X`
2. Press `Y` (yes, save)
3. Press `Enter` (confirm filename)

**Verify your configuration:**

```bash
# Check that keys are set (values will be hidden)
grep -E "EBAY_API_KEY|METALS_API_KEY" .env | sed 's/=.*/=***HIDDEN***/'
```

**CHECKPOINT:** You should see:
```
EBAY_API_KEY=***HIDDEN***
METALS_API_KEY=***HIDDEN***
```

Your `.env` file should have exactly 15 lines of configuration.

### 3.5 Alternative: Upload Code Without GitHub

If you haven't uploaded to GitHub, you can transfer files directly:

**On your local computer** (in the metals-scanner directory):
```bash
# Create archive (excluding unnecessary files)
tar -czf metals-scanner.tar.gz --exclude='.git' --exclude='data' --exclude='logs' --exclude='__pycache__' --exclude='.env' .

# Upload to your server
scp metals-scanner.tar.gz root@YOUR_DROPLET_IP:~/

# SSH into your server
ssh root@YOUR_DROPLET_IP

# Extract files
cd ~
mkdir -p metals-scanner
cd metals-scanner
tar -xzf ~/metals-scanner.tar.gz

# Then continue with Step 3.3
```

---

## Part 4: Launch (10 minutes)

Time to start your scanner!

### 4.1 Build the Application

```bash
# Make sure you're in the metals-scanner directory
cd ~/metals-scanner

# Build Docker image (takes 2-3 minutes)
docker compose build
```

You'll see lots of output. Wait for it to complete.

**CHECKPOINT:** Final line should say: `Successfully tagged metals-scanner:latest` or similar.

### 4.2 Start the Application

```bash
# Start in background mode
docker compose up -d
```

**CHECKPOINT:** You should see:
```
[+] Running 1/1
✔ Container metals-scanner  Started
```

### 4.3 Verify It's Running

```bash
# Check container status
docker compose ps
```

**CHECKPOINT:** Should show:
```
NAME                STATUS          PORTS
metals-scanner      Up X seconds    0.0.0.0:8000->8000/tcp
```

Status should be "Up" (not "Exited").

```bash
# Check application health
curl http://localhost:8000/api/health
```

**CHECKPOINT:** Should return JSON with `"status": "healthy"`.

### 4.4 View Logs

```bash
# View real-time logs
docker compose logs -f

# Press Ctrl+C to exit (application keeps running)
```

Look for lines like:
```
INFO:     Started server process
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4.5 Access Your Dashboard

On your **local computer**, open a web browser and go to:

```
http://YOUR_DROPLET_IP:8000
```

Replace `YOUR_DROPLET_IP` with your actual IP from Part 1.

Example: `http://165.232.123.45:8000`

**CHECKPOINT:** You should see the Metals Arbitrage Scanner dashboard with:
- Gold and silver spot prices (may show $-- until first scan)
- "Scan Now" button
- Empty listings table

### 4.6 Run Your First Scan

1. Click the **"Scan Now"** button in your dashboard
2. Wait 20-30 seconds
3. Watch as listings populate the table
4. You should see:
   - Metal type badges (gold/silver)
   - Prices
   - Margins (positive = profit opportunity)
   - "View" links to eBay listings

**CHECKPOINT:** You see gold and silver prices updating and listings appearing in the table.

**Troubleshooting:** If no listings appear:
- Check logs: `docker compose logs`
- Verify API keys are correct: `nano .env`
- Check rate limits: `curl http://localhost:8000/api/rate-limits`

---

## Part 5: Ongoing Operation

Your scanner is now running 24/7 in the cloud!

### 5.1 How the Scanner Works

**Automatic Scans:**
- Runs every 2 hours automatically
- Checks eBay for new listings
- Updates spot prices (with smart caching)
- Calculates margins

**No action needed** - it just runs in the background.

### 5.2 Checking If It's Running

From your **local computer**:

```bash
# SSH into your server
ssh root@YOUR_DROPLET_IP

# Check container status
cd ~/metals-scanner
docker compose ps

# View recent activity
docker compose logs --tail=50

# Exit SSH
exit
```

Or just open `http://YOUR_DROPLET_IP:8000` in your browser - if it loads, it's running!

### 5.3 When to Expect Data Updates

**eBay Listings:**
- Scanned every 2 hours
- Check "Last Updated" timestamp in dashboard

**Spot Prices:**
- **Market hours (weekdays 9am-5pm):** Updated every 15 minutes
- **After hours:** Updated every 60 minutes
- **Weekends:** Updated every 4 hours
- Caching saves API calls and money

### 5.4 Normal vs Abnormal Log Messages

**Normal messages** (everything is fine):
```
INFO: Performing scheduled scan
INFO: Found 45 eBay listings for 'gold bullion'
INFO: Fetched spot prices: gold=$2150.00, silver=$25.50
INFO: Scan completed in 22.3 seconds
```

**Warning messages** (not critical):
```
WARNING: Weight extraction failed for listing
WARNING: Using cached spot price (API limit reached)
```

**Error messages** (need attention):
```
ERROR: eBay API authentication failed
ERROR: Database connection failed
ERROR: Rate limit exceeded for ebay
```

If you see errors, check the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide.

### 5.5 Auto-Restart on Server Reboot

Your scanner is configured to automatically restart if the server reboots. No action needed.

To verify:
```bash
# Check Docker auto-start
sudo systemctl is-enabled docker
# Should show: enabled
```

### 5.6 Accessing Your Dashboard

Bookmark this URL on your devices:
```
http://YOUR_DROPLET_IP:8000
```

You can access it from:
- Your laptop
- Your phone
- Any browser
- Anywhere with internet

**Note:** Using just the IP address means your connection is not encrypted (HTTP, not HTTPS). For your personal use, this is fine. If you want a custom domain and HTTPS encryption, see [DOMAIN_SETUP.md](DOMAIN_SETUP.md).

---

## Next Steps

Your metals arbitrage scanner is now fully operational! Here's what you can do next:

### Optional Enhancements

1. **Add Custom Domain & HTTPS**
   - See [DOMAIN_SETUP.md](DOMAIN_SETUP.md)
   - Get a memorable URL like `https://metals.yourdomain.com`
   - Encrypted connection (HTTPS)
   - Estimated time: 30 minutes

2. **Test Changes Locally Before Deploying**
   - See [LOCAL_TESTING.md](LOCAL_TESTING.md)
   - Run scanner on your laptop
   - Make customizations safely
   - Deploy to server when ready

3. **Understand the Code**
   - See [UNDERSTANDING_THE_CODE.md](UNDERSTANDING_THE_CODE.md)
   - Learn how the scanner works
   - Make safe customizations
   - Add new metals or features

4. **Set Up Monitoring**
   - See [MAINTENANCE.md](MAINTENANCE.md)
   - Weekly health checks
   - Backup procedures
   - Cost monitoring

### Using Your Scanner

- **Dashboard:** Access anytime at `http://YOUR_DROPLET_IP:8000`
- **Filters:** Adjust minimum margin, metal type, and source
- **Sorting:** Click column headers to sort by price, margin, etc.
- **Auto-refresh:** Enable 5-minute auto-refresh for live monitoring
- **Deals:** Positive margins are opportunities - verify on eBay before buying

### Getting Help

- **Common issues:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Ongoing maintenance:** See [MAINTENANCE.md](MAINTENANCE.md)
- **Code questions:** See [UNDERSTANDING_THE_CODE.md](UNDERSTANDING_THE_CODE.md)
- **Can't find answer:** Contact me (developer contact info in README.md)

---

## Summary

**What you accomplished:**
- ✅ Created a cloud server ($6/month)
- ✅ Installed and secured Ubuntu Linux
- ✅ Set up Docker containerization
- ✅ Configured eBay and Metals API access
- ✅ Deployed your metals scanner application
- ✅ Verified it's working with live data

**What you have now:**
- 24/7 automated eBay scanning
- Real-time precious metals pricing
- Web dashboard accessible anywhere
- Automatic margin calculations
- No ongoing maintenance required

**Your scanner runs automatically.** Just visit your dashboard URL anytime to check for deals.

**Total setup time:** ~90 minutes
**Monthly cost:** $6
**Value:** Automated deal-finding 24/7

Congratulations! Your metals arbitrage scanner is live! 🎉

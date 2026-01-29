# Deployment Guide - DigitalOcean Droplet

> **Deploy the Metals Arbitrage Scanner to a DigitalOcean server for 24/7 operation**

This guide walks you through deploying to a $6/month DigitalOcean droplet. Total setup time: ~20 minutes.

## Prerequisites

- DigitalOcean account ([Sign up here](https://www.digitalocean.com/) - $200 free credit available)
- eBay API key ([Get here](https://developer.ebay.com/))
- Metals API key ([Get here](https://metals-api.com/))
- Domain name (optional, for custom URL and SSL)

## Cost Estimate

| Item | Cost | Notes |
|------|------|-------|
| Droplet | $6/month | Basic plan (1GB RAM, 25GB SSD) |
| Domain | $10-15/year | Optional, use IP address without |
| SSL Certificate | FREE | Let's Encrypt |
| **Total** | **$6-7/month** | Plus one-time domain cost |

## Step 1: Create a DigitalOcean Droplet

### 1.1 Log in and Create Droplet

1. Log in to [DigitalOcean](https://cloud.digitalocean.com/)
2. Click **"Create"** → **"Droplets"**
3. Choose a region close to you (e.g., "New York" for US East Coast)

### 1.2 Choose Configuration

**Image:**
- Select **Ubuntu 22.04 LTS** (Long Term Support)

**Droplet Type:**
- Select **Basic**
- Choose **Regular** CPU option

**Size:**
- Select **$6/month** plan
  - 1 GB RAM
  - 1 vCPU
  - 25 GB SSD
  - 1000 GB transfer

This is sufficient for the scanner (uses ~50-100MB RAM).

### 1.3 Authentication Method

**Recommended: SSH Key (More Secure)**

1. On your local computer, generate SSH key (if you don't have one):
   ```bash
   # Run on YOUR LOCAL computer
   ssh-keygen -t ed25519 -C "your_email@example.com"
   # Press Enter to accept default location
   # Press Enter twice for no passphrase (or set one for extra security)
   ```

2. Copy your public key:
   ```bash
   # macOS/Linux
   cat ~/.ssh/id_ed25519.pub

   # Windows (Git Bash)
   cat ~/.ssh/id_ed25519.pub

   # Windows (PowerShell)
   type $env:USERPROFILE\.ssh\id_ed25519.pub
   ```

3. In DigitalOcean, click **"New SSH Key"**
4. Paste the public key content
5. Name it (e.g., "My Laptop")
6. Click **"Add SSH Key"**

**Alternative: Password (Less Secure)**
- You'll receive root password via email
- Change it immediately after first login

### 1.4 Additional Options

**Hostname:**
- Enter a memorable name: `metals-scanner`

**Tags:**
- Add tag: `metals-scanner` (helps organize)

**Backups:**
- **Skip** (adds $1.20/month) - Not needed initially

**Monitoring:**
- **Enable** (free) - Check "Monitoring"

### 1.5 Create Droplet

1. Click **"Create Droplet"**
2. Wait 30-60 seconds for creation
3. Note your droplet's **IP address** (e.g., `165.232.123.45`)

## Step 2: Initial Server Setup & Security

### 2.1 Connect via SSH

**Using SSH Key:**
```bash
ssh root@YOUR_DROPLET_IP
# Example: ssh root@165.232.123.45
```

**Using Password:**
```bash
ssh root@YOUR_DROPLET_IP
# Enter password from email
# Change password immediately:
passwd
```

You should see:
```
Welcome to Ubuntu 22.04.3 LTS
```

### 2.2 Update System

Run these commands on the server:

```bash
# Update package list
apt update

# Upgrade installed packages (takes 2-5 minutes)
apt upgrade -y

# Install basic utilities
apt install -y curl wget git htop ufw
```

### 2.3 Configure Firewall

Secure your server with UFW (Uncomplicated Firewall):

```bash
# Allow SSH (IMPORTANT: Do this first!)
ufw allow 22/tcp

# Allow HTTP (for web dashboard)
ufw allow 80/tcp

# Allow HTTPS (for SSL, if using domain)
ufw allow 443/tcp

# Enable firewall
ufw enable
# Type 'y' and press Enter

# Verify rules
ufw status
```

Expected output:
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
```

### 2.4 Create Non-Root User (Recommended)

```bash
# Create user
adduser scanner
# Enter password and information (can skip optional fields)

# Add to sudo group
usermod -aG sudo scanner

# Copy SSH keys to new user
rsync --archive --chown=scanner:scanner ~/.ssh /home/scanner

# Test login (open NEW terminal, don't close current one)
# ssh scanner@YOUR_DROPLET_IP

# If successful, use 'scanner' user for remaining steps
```

From now on, use the `scanner` user instead of `root`.

## Step 3: Install Docker & Docker Compose

You can either:
- **Option A:** Run our automated script (easiest)
- **Option B:** Install manually (more control)

### Option A: Automated Installation (Recommended)

```bash
# Download and run setup script
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/metals-scanner/main/setup.sh -o setup.sh
chmod +x setup.sh
sudo ./setup.sh
```

Skip to **Step 7** if using automated script.

### Option B: Manual Installation

#### 3.1 Install Docker

```bash
# Install prerequisites
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to docker group (avoid sudo for docker commands)
sudo usermod -aG docker $USER

# Apply group changes (log out and back in, or run):
newgrp docker

# Verify installation
docker --version
# Should show: Docker version 24.x.x

docker compose version
# Should show: Docker Compose version v2.x.x
```

#### 3.2 Test Docker

```bash
# Run test container
docker run hello-world

# Should see: "Hello from Docker!"
```

## Step 4: Clone from GitHub

### 4.1 Upload to GitHub (If Not Already Done)

On your **LOCAL** computer:

```bash
cd /path/to/metals-scanner

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit"

# Create repo on GitHub (via web interface)
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/metals-scanner.git
git branch -M main
git push -u origin main
```

**Important:** Ensure `.gitignore` includes `.env` so API keys aren't committed!

### 4.2 Clone on Server

On your **DROPLET**:

```bash
# Navigate to home directory
cd ~

# Clone repository
git clone https://github.com/YOUR_USERNAME/metals-scanner.git

# Enter directory
cd metals-scanner

# Verify files
ls -la
# Should see: app/, docker-compose.yml, Dockerfile, etc.
```

### 4.3 Alternative: Manual Upload

If not using GitHub:

```bash
# On LOCAL computer, create archive:
cd /path/to/metals-scanner
tar -czf metals-scanner.tar.gz --exclude='.git' --exclude='data' --exclude='logs' --exclude='__pycache__' .

# Upload to droplet:
scp metals-scanner.tar.gz scanner@YOUR_DROPLET_IP:~/

# On DROPLET, extract:
mkdir -p ~/metals-scanner
cd ~/metals-scanner
tar -xzf ~/metals-scanner.tar.gz
```

## Step 5: Set Environment Variables

### 5.1 Create .env File

```bash
cd ~/metals-scanner

# Copy example
cp .env.example .env

# Edit with nano
nano .env
```

### 5.2 Configure API Keys

Edit the `.env` file:

```bash
# eBay API (REQUIRED)
EBAY_API_KEY=YourActual-EbayAppID-PRD-1234567890-abcdefgh

# Metals API (REQUIRED)
METALS_API_KEY=your_actual_32_character_metals_api_key

# Database
DATABASE_URL=sqlite:////app/data/metals_scanner.db

# Scheduler
ENABLE_AUTO_SCAN=true
SCAN_INTERVAL_HOURS=2

# Logging
LOG_LEVEL=INFO

# Rate Limits (adjust if you have paid plans)
EBAY_DAILY_LIMIT=5000
METALS_API_MONTHLY_LIMIT=50
```

**Save and exit:**
- Press `Ctrl + X`
- Press `Y` to confirm
- Press `Enter` to save

### 5.3 Verify Configuration

```bash
# Check that API keys are set (don't show actual values)
grep -E "EBAY_API_KEY|METALS_API_KEY" .env | sed 's/=.*/=***HIDDEN***/'

# Should show:
# EBAY_API_KEY=***HIDDEN***
# METALS_API_KEY=***HIDDEN***
```

## Step 6: Run the Application

### 6.1 Create Data Directories

```bash
cd ~/metals-scanner

# Create directories with proper permissions
mkdir -p data logs
chmod 777 data logs
```

### 6.2 Build and Start

```bash
# Build Docker image
docker compose build

# Start application in background
docker compose up -d

# Check logs
docker compose logs -f
# Press Ctrl+C to exit logs (app keeps running)
```

### 6.3 Verify Running

```bash
# Check container status
docker compose ps
# Should show: metals-scanner running

# Check health
curl http://localhost:8000/api/health

# Should return JSON with "status": "healthy"
```

### 6.4 Access Dashboard

In your web browser:
```
http://YOUR_DROPLET_IP:8000
```

For example: `http://165.232.123.45:8000`

You should see the dashboard! 🎉

### 6.5 Run First Scan

1. Click **"🔄 Scan Now"** button
2. Wait 20-30 seconds
3. Listings should populate

## Step 7: Setup Domain (Optional)

Skip this section if you're happy using the IP address.

### 7.1 Point Domain to Droplet

In your domain registrar (Namecheap, GoDaddy, etc.):

1. Go to DNS settings
2. Add **A Record**:
   - **Type:** A
   - **Host:** @ (or subdomain like "scanner")
   - **Value:** YOUR_DROPLET_IP
   - **TTL:** 300 (5 minutes)

Example for subdomain:
```
Type: A
Host: scanner
Value: 165.232.123.45
TTL: 300
```

Wait 5-10 minutes for DNS propagation.

### 7.2 Test Domain Resolution

```bash
# On your local computer
ping scanner.yourdomain.com

# Should show your droplet IP
```

### 7.3 Install Nginx Reverse Proxy

On your **DROPLET**:

```bash
# Install Nginx
sudo apt install -y nginx

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Create configuration
sudo nano /etc/nginx/sites-available/metals-scanner
```

Paste this configuration (replace `scanner.yourdomain.com`):

```nginx
server {
    listen 80;
    server_name scanner.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Save and enable:

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/metals-scanner /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 7.4 Test Domain Access

Open browser:
```
http://scanner.yourdomain.com
```

Should show your dashboard without port number!

## Step 8: SSL with Let's Encrypt (Optional)

Secure your domain with free HTTPS certificate.

### 8.1 Install Certbot

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx
```

### 8.2 Obtain Certificate

```bash
# Get certificate (replace email and domain)
sudo certbot --nginx -d scanner.yourdomain.com --non-interactive --agree-tos -m your_email@example.com

# Certbot automatically configures Nginx for HTTPS
```

### 8.3 Test Auto-Renewal

```bash
# Test renewal process (dry run)
sudo certbot renew --dry-run

# Should show: "Congratulations, all simulated renewals succeeded"
```

Certificates auto-renew every 60 days.

### 8.4 Verify HTTPS

Open browser:
```
https://scanner.yourdomain.com
```

Should show 🔒 padlock icon!

## Step 9: Auto-Restart on Reboot

Ensure the scanner starts automatically after server reboots.

### 9.1 Configure Docker Compose

The `docker-compose.yml` already includes:
```yaml
restart: unless-stopped
```

This ensures the container restarts automatically.

### 9.2 Enable Docker Service

```bash
# Enable Docker to start on boot
sudo systemctl enable docker

# Verify
sudo systemctl is-enabled docker
# Should show: enabled
```

### 9.3 Test Reboot

```bash
# Reboot server
sudo reboot

# Wait 1-2 minutes, then SSH back in
ssh scanner@YOUR_DROPLET_IP

# Check if scanner is running
docker compose ps -C ~/metals-scanner

# Should show container running
```

### 9.4 Alternative: Systemd Service

For more control, create a systemd service:

```bash
# Create service file
sudo nano /etc/systemd/system/metals-scanner.service
```

Paste:

```ini
[Unit]
Description=Metals Arbitrage Scanner
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/scanner/metals-scanner
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
User=scanner

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable metals-scanner
sudo systemctl start metals-scanner

# Check status
sudo systemctl status metals-scanner
```

## Step 10: Basic Monitoring

### 10.1 Health Check Endpoint

```bash
# Check application health
curl http://localhost:8000/api/health | jq

# Returns:
# {
#   "status": "healthy",
#   "database": "ok",
#   "last_scan": "2024-01-25T10:30:00",
#   "ebay_rate_limit_remaining": 4850,
#   "metals_api_rate_limit_remaining": 45
# }
```

### 10.2 Setup Health Check Script

```bash
# Create monitoring script
nano ~/check-health.sh
```

Paste:

```bash
#!/bin/bash

# Check if scanner is healthy
HEALTH=$(curl -s http://localhost:8000/api/health)
STATUS=$(echo $HEALTH | jq -r '.status')

if [ "$STATUS" != "healthy" ]; then
    echo "$(date): Scanner is unhealthy!" >> ~/scanner-alerts.log
    # Optional: Send email alert
    # echo "Scanner is unhealthy: $HEALTH" | mail -s "Scanner Alert" your@email.com
fi
```

Make executable:

```bash
chmod +x ~/check-health.sh
```

### 10.3 Schedule Health Checks

```bash
# Add to crontab
crontab -e

# Add this line (checks every 5 minutes):
*/5 * * * * /home/scanner/check-health.sh
```

### 10.4 View Logs

```bash
# Real-time logs
docker compose logs -f -C ~/metals-scanner

# Last 100 lines
docker compose logs --tail=100 -C ~/metals-scanner

# Application logs
tail -f ~/metals-scanner/logs/metals_scanner.log

# Errors only
grep ERROR ~/metals-scanner/logs/metals_scanner.log
```

### 10.5 Monitor Resources

```bash
# Install htop if not already installed
sudo apt install -y htop

# View system resources
htop
# Press F10 to exit

# Docker stats
docker stats

# Disk usage
df -h

# Check database size
du -sh ~/metals-scanner/data/
```

### 10.6 DigitalOcean Monitoring

1. Go to DigitalOcean dashboard
2. Click on your droplet
3. Click **"Graphs"** tab
4. View:
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network traffic

Set up **alerts** (optional):
1. Click **"Create Alert Policy"**
2. Set thresholds (e.g., CPU > 90% for 5 minutes)
3. Enter email for notifications

## Maintenance Tasks

### Update Application

```bash
# Navigate to directory
cd ~/metals-scanner

# Pull latest changes from GitHub
git pull

# Rebuild and restart
docker compose down
docker compose build
docker compose up -d

# Check logs
docker compose logs -f
```

### Backup Database

```bash
# Create backup
cp ~/metals-scanner/data/metals_scanner.db ~/metals_scanner_backup_$(date +%Y%m%d).db

# Download to local computer
# Run on LOCAL computer:
scp scanner@YOUR_DROPLET_IP:~/metals_scanner_backup_*.db ~/Downloads/
```

### Clean Old Data

```bash
# Connect to database
docker exec -it metals-scanner sqlite3 /app/data/metals_scanner.db

# Delete old listings (older than 7 days)
DELETE FROM listings WHERE fetched_at < datetime('now', '-7 days');

# Delete old spot prices
DELETE FROM spot_prices WHERE fetched_at < datetime('now', '-7 days');

# Delete old API logs
DELETE FROM api_call_logs WHERE called_at < datetime('now', '-30 days');

# Exit
.exit
```

### View Rate Limits

```bash
# Check API usage
curl http://localhost:8000/api/rate-limits | jq
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs

# Check if port is in use
sudo lsof -i :8000

# Restart
docker compose restart
```

### Can't Connect to Dashboard

```bash
# Check firewall
sudo ufw status

# Verify container is running
docker compose ps

# Check Nginx (if using domain)
sudo systemctl status nginx
sudo nginx -t
```

### High Memory Usage

```bash
# Check memory
free -h

# Restart scanner to free memory
docker compose restart
```

### Database Locked

```bash
# Usually caused by multiple instances
docker compose down
docker compose up -d
```

### SSL Certificate Issues

```bash
# Renew manually
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

## Security Best Practices

1. **Keep System Updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Change SSH Port (Optional):**
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Change: Port 22 → Port 2222
   sudo systemctl restart sshd
   # Update firewall: sudo ufw allow 2222/tcp
   ```

3. **Disable Root Login:**
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Change: PermitRootLogin yes → no
   sudo systemctl restart sshd
   ```

4. **Enable Automatic Security Updates:**
   ```bash
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

5. **Install Fail2Ban (Prevent Brute Force):**
   ```bash
   sudo apt install -y fail2ban
   sudo systemctl enable fail2ban
   ```

## Cost Optimization

### Resize Droplet

If $6/month is too expensive:
- **$4/month plan** available (512MB RAM)
- Scanner uses ~50-100MB, should work
- Less headroom for spikes

### Destroy When Not Needed

If only needed occasionally:
```bash
# Backup data first!
scp -r scanner@YOUR_IP:~/metals-scanner/data ~/backup/

# Destroy droplet in DigitalOcean dashboard
# Create new one when needed and restore data
```

### Use DigitalOcean Snapshots

- Create snapshot before major changes
- Cost: $0.05/GB/month (~$1-2/month)
- Quick restore if something breaks

## Next Steps

Now that your scanner is deployed:

1. **Configure notifications** - Add email alerts for good deals
2. **Add more sources** - Implement Amazon, other marketplaces
3. **Customize dashboard** - Modify colors, layout
4. **Set up backups** - Automate database backups
5. **Monitor usage** - Track API quota consumption

See [CONTRIBUTING.md](CONTRIBUTING.md) for customization ideas.

## Support

- **Issues:** GitHub Issues
- **Questions:** Check [README.md](README.md) and [AI_CUSTOMIZATION_GUIDE.md](AI_CUSTOMIZATION_GUIDE.md)
- **DigitalOcean Help:** [Community Tutorials](https://www.digitalocean.com/community/tutorials)

---

**Congratulations! Your metals scanner is now running 24/7 in the cloud! 🎉**

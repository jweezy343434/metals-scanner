# Quick Start - DigitalOcean Deployment

> **⚡ Get the scanner running in 10 minutes**

This is a condensed version of DEPLOYMENT.md for experienced users. For detailed explanations, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Prerequisites

- DigitalOcean account
- eBay API key: [developer.ebay.com](https://developer.ebay.com/)
- Metals API key: [metals-api.com](https://metals-api.com/signup/free)

## 1. Create Droplet (2 min)

```
DigitalOcean Dashboard:
1. Create → Droplets
2. Ubuntu 22.04 LTS
3. Basic / Regular / $6/month (1GB RAM)
4. Add SSH key (or use password)
5. Hostname: metals-scanner
6. Create Droplet
7. Note IP address
```

## 2. Connect & Secure (1 min)

```bash
# SSH into droplet
ssh root@YOUR_DROPLET_IP

# Configure firewall
ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp && ufw enable
```

## 3. Automated Setup (5 min)

### Option A: Using Setup Script (Recommended)

```bash
# Download and run setup script
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/metals-scanner/main/setup.sh -o setup.sh
chmod +x setup.sh
sudo ./setup.sh
```

The script will:
- Install Docker & Docker Compose
- Clone repository
- Prompt for API keys
- Build and start the application

### Option B: Manual Setup

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone repository
git clone https://github.com/YOUR_USERNAME/metals-scanner.git
cd metals-scanner

# Configure environment
cp .env.example .env
nano .env  # Add your API keys

# Create directories
mkdir -p data logs && chmod 777 data logs

# Build and start
docker compose up -d
```

## 4. Verify (1 min)

```bash
# Check container is running
docker compose ps

# Test health endpoint
curl http://localhost:8000/api/health

# Open in browser
# http://YOUR_DROPLET_IP:8000
```

## 5. Optional: Domain & SSL

### Setup Domain

```bash
# Point your domain A record to droplet IP
# Wait 5-10 minutes for DNS propagation

# Install Nginx
sudo apt install -y nginx

# Create Nginx config
sudo nano /etc/nginx/sites-available/metals-scanner
```

Paste:
```nginx
server {
    listen 80;
    server_name your.domain.com;
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/metals-scanner /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### Add SSL

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your.domain.com -m your@email.com --agree-tos
```

Access: `https://your.domain.com`

## Common Commands

```bash
# View logs
docker compose logs -f

# Restart
docker compose restart

# Stop
docker compose down

# Update
cd ~/metals-scanner
git pull
docker compose up -d --build

# Check health
curl http://localhost:8000/api/health | jq
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't connect | Check firewall: `sudo ufw status` |
| Container won't start | Check logs: `docker compose logs` |
| Out of memory | Restart: `docker compose restart` |
| Database locked | Stop & start: `docker compose down && docker compose up -d` |

## Security Checklist

- [ ] SSH key authentication enabled
- [ ] Firewall configured (UFW)
- [ ] Non-root user created
- [ ] Root login disabled
- [ ] Automatic updates enabled
- [ ] SSL certificate installed
- [ ] Strong passwords set

## Monitoring

```bash
# System resources
htop

# Docker stats
docker stats

# Disk usage
df -h

# Application logs
tail -f ~/metals-scanner/logs/metals_scanner.log
```

## Cost

| Item | Monthly Cost |
|------|--------------|
| Droplet (1GB) | $6.00 |
| Domain (optional) | ~$1.25 (if $15/year) |
| SSL Certificate | FREE |
| **Total** | **~$6-7/month** |

## Next Steps

1. Click "Scan Now" in dashboard
2. Set up monitoring (see DEPLOYMENT.md Step 10)
3. Configure notifications (see CONTRIBUTING.md)
4. Customize (see AI_CUSTOMIZATION_GUIDE.md)

## Full Documentation

- **Detailed setup:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **User guide:** [README.md](README.md)
- **AI customization:** [AI_CUSTOMIZATION_GUIDE.md](AI_CUSTOMIZATION_GUIDE.md)

---

**Need help?** See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting.

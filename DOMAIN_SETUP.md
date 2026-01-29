# Domain Setup Guide

This optional guide shows you how to add a custom domain name and HTTPS (SSL) encryption to your metals scanner.

**Prerequisites:**
- You must have completed [SETUP_GUIDE.md](SETUP_GUIDE.md) first
- Your scanner must be running and accessible at `http://YOUR_IP:8000`
- Estimated time: 30 minutes
- Additional cost: $10-15/year for domain

---

## Why Add a Domain?

### Current Setup (IP Address)
```
http://165.232.123.45:8000
```

**Pros:**
- Free
- Works immediately
- Fine for personal use

**Cons:**
- Hard to remember
- No encryption (HTTP not HTTPS)
- Looks unprofessional
- Can't get SSL certificate

### With Custom Domain
```
https://metals.yourdomain.com
```

**Pros:**
- Easy to remember: `metals.yourdomain.com`
- Encrypted connection (HTTPS)
- SSL padlock icon in browser
- Professional appearance
- No port number needed (`:8000`)

**Cons:**
- Costs $10-15/year for domain
- 30 minutes to set up
- Requires domain renewal annually

**Decision:** If you access your scanner frequently and want encryption, add a domain. Otherwise, IP address works fine.

---

## Part 1: Get a Domain Name (10 minutes)

### Option 1: Buy a New Domain

**Recommended registrars:**
1. [Namecheap](https://www.namecheap.com/) - $8-12/year
2. [Google Domains](https://domains.google/) - $12/year
3. [Cloudflare](https://www.cloudflare.com/products/registrar/) - At-cost pricing

**Steps:**

1. Go to registrar website
2. Search for available domain
   - Example: `yourname-metals.com`
   - Or: `metals-scanner.net`
3. Purchase domain (typically $10-15/year)
4. Note: You can skip privacy protection for personal use

### Option 2: Use Existing Domain (Subdomain)

If you already own a domain like `yourdomain.com`, you can create a subdomain:

```
metals.yourdomain.com
```

This is free and recommended if you already own a domain.

### Option 3: Free Domain (Not Recommended)

Services like Freenom offer free domains (.tk, .ml, etc.), but:
- Often blocked by browsers
- Unreliable
- May be reclaimed
- Not professional

**Recommendation:** Spend $10/year for a real domain.

---

## Part 2: Point Domain to Your Server (5 minutes)

You'll create a DNS record that points your domain to your DigitalOcean droplet IP.

### Get Your Droplet IP

From [SETUP_GUIDE.md](SETUP_GUIDE.md) Part 1, you should have written down your IP address.

If you forgot:
```bash
# SSH into your server
ssh root@YOUR_DROPLET_IP

# Get IP address
curl -4 icanhazip.com

# Note this IP address
```

### Configure DNS

**For a full domain** (e.g., `metals-scanner.com`):

1. Log in to your domain registrar (Namecheap, Google Domains, etc.)
2. Find DNS settings (sometimes called "Advanced DNS" or "DNS Management")
3. Add an **A Record**:
   - **Type:** A
   - **Host:** @ (means root domain)
   - **Value:** YOUR_DROPLET_IP
   - **TTL:** 300 (5 minutes)
4. Save changes

**For a subdomain** (e.g., `metals.yourdomain.com`):

1. Log in to your domain registrar
2. Go to DNS settings
3. Add an **A Record**:
   - **Type:** A
   - **Host:** metals (the subdomain part)
   - **Value:** YOUR_DROPLET_IP
   - **TTL:** 300
4. Save changes

**Example:**
```
Type: A
Host: metals
Value: 165.232.123.45
TTL: 300
```

This creates: `metals.yourdomain.com` → `165.232.123.45`

### Wait for DNS Propagation

DNS changes take 5-60 minutes to propagate globally.

**Test DNS resolution:**

On your **local computer**:
```bash
# Replace with your domain
ping metals.yourdomain.com

# Should show your droplet IP
```

Or use online tool: https://www.whatsmydns.net/

**CHECKPOINT:** Your domain should resolve to your droplet IP before continuing.

---

## Part 3: Install Nginx (5 minutes)

Nginx will act as a reverse proxy, forwarding requests from port 80 (HTTP) to your scanner on port 8000.

**SSH into your server:**

```bash
ssh root@YOUR_DROPLET_IP
```

**Install Nginx:**

```bash
# Install Nginx
sudo apt update
sudo apt install -y nginx

# Verify installation
nginx -v
# Should show: nginx version: nginx/1.x.x

# Check status
sudo systemctl status nginx
# Should show: active (running)
```

**CHECKPOINT:** Nginx should be running. Test by visiting `http://YOUR_DROPLET_IP` in browser - you should see "Welcome to nginx" page.

---

## Part 4: Configure Nginx for Your Scanner (5 minutes)

Now configure Nginx to forward traffic to your scanner.

### Remove Default Site

```bash
# Remove default nginx page
sudo rm /etc/nginx/sites-enabled/default
```

### Create Configuration for Your Scanner

```bash
# Create new configuration file
sudo nano /etc/nginx/sites-available/metals-scanner
```

**Paste this configuration** (replace `metals.yourdomain.com` with your actual domain):

```nginx
server {
    listen 80;
    server_name metals.yourdomain.com;

    # Increase timeout for long scans
    proxy_read_timeout 300;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Save and exit:**
- Press `Ctrl + X`
- Press `Y` (yes)
- Press `Enter`

### Enable Site

```bash
# Create symbolic link to enable site
sudo ln -s /etc/nginx/sites-available/metals-scanner /etc/nginx/sites-enabled/

# Test configuration for syntax errors
sudo nginx -t

# Should show: "syntax is ok" and "test is successful"

# Reload Nginx to apply changes
sudo systemctl reload nginx
```

### Test HTTP Access

Open your browser and visit:
```
http://metals.yourdomain.com
```

**CHECKPOINT:** You should see your metals scanner dashboard without needing `:8000` in the URL!

**Troubleshooting:**
- If you see "502 Bad Gateway": Scanner isn't running
  - Check: `cd ~/metals-scanner && docker compose ps`
- If you see "nginx default page": DNS not updated yet
  - Wait 10 more minutes
- If page won't load: Check firewall
  - Run: `sudo ufw status`
  - Ensure port 80 is allowed

---

## Part 5: Add HTTPS with Let's Encrypt (10 minutes)

Now add a free SSL certificate to enable HTTPS encryption.

### Install Certbot

Certbot automatically obtains and installs SSL certificates:

```bash
# Install Certbot and Nginx plugin
sudo apt install -y certbot python3-certbot-nginx
```

### Obtain SSL Certificate

Run Certbot (replace email and domain):

```bash
sudo certbot --nginx -d metals.yourdomain.com --non-interactive --agree-tos -m your_email@example.com
```

Replace:
- `metals.yourdomain.com` with your actual domain
- `your_email@example.com` with your actual email (for renewal reminders)

**What Certbot does:**
1. Contacts Let's Encrypt
2. Verifies you own the domain
3. Downloads SSL certificate
4. Automatically modifies Nginx config
5. Sets up auto-renewal

**Expected output:**
```
Congratulations! You have successfully enabled HTTPS on https://metals.yourdomain.com
```

**CHECKPOINT:** You should see success message.

### Verify HTTPS is Working

Open your browser and visit:
```
https://metals.yourdomain.com
```

**What to check:**
- ✅ URL shows `https://` (not `http://`)
- ✅ Padlock icon appears in address bar
- ✅ Dashboard loads correctly
- ✅ Clicking padlock shows certificate is valid

### Test Auto-Renewal

SSL certificates expire after 90 days. Certbot sets up automatic renewal.

```bash
# Test renewal process (doesn't actually renew, just simulates)
sudo certbot renew --dry-run
```

**Expected output:**
```
Congratulations, all simulated renewals succeeded
```

**CHECKPOINT:** Renewal test should succeed.

### Configure Firewall for HTTPS

```bash
# Allow HTTPS traffic
sudo ufw allow 443/tcp

# Verify firewall rules
sudo ufw status
```

Should show:
```
443/tcp         ALLOW       Anywhere
```

---

## Part 6: Verification and Testing (5 minutes)

### Test All Access Methods

**1. HTTPS (Recommended - Encrypted):**
```
https://metals.yourdomain.com
```
✅ Should work, show padlock

**2. HTTP (Redirects to HTTPS):**
```
http://metals.yourdomain.com
```
✅ Should auto-redirect to HTTPS

**3. IP Address with Port (Still works):**
```
http://YOUR_DROPLET_IP:8000
```
✅ Should still work as backup

### Check Certificate Details

In your browser:
1. Click the padlock icon
2. Click "Certificate" or "Connection is secure"
3. Verify:
   - Issued by: Let's Encrypt
   - Valid for: 90 days
   - Domain matches your domain

### Test Scanning

1. Open: `https://metals.yourdomain.com`
2. Click **"Scan Now"**
3. Wait 20-30 seconds
4. Verify listings appear
5. Check spot prices display

**CHECKPOINT:** Everything should work exactly as before, but now with HTTPS.

---

## Bookmark Your New URL

Update your bookmarks:

**Before:** `http://165.232.123.45:8000`
**After:** `https://metals.yourdomain.com`

You can now access your scanner from:
- Your laptop
- Your phone
- Any device
- Anywhere

All connections are now encrypted!

---

## Ongoing Maintenance

### Certificate Auto-Renewal

Certbot installed a cron job that automatically renews your certificate before it expires (every 90 days).

**Verify auto-renewal is scheduled:**

```bash
# Check systemd timer
sudo systemctl status certbot.timer

# Should show: active
```

You don't need to do anything - renewal is automatic.

### Check Certificate Expiration

To see when your certificate expires:

```bash
sudo certbot certificates
```

Shows expiration date and renewal settings.

### Manual Renewal (If Needed)

If auto-renewal fails (you'll receive email warning):

```bash
sudo certbot renew

# Reload Nginx
sudo systemctl reload nginx
```

### Domain Renewal

Don't forget to renew your domain name annually!

Set a calendar reminder for 1-2 weeks before expiration.

Most registrars send email reminders.

---

## Troubleshooting

### "DNS_PROBE_FINISHED_NXDOMAIN"

**Problem:** Domain doesn't resolve

**Solutions:**
1. Wait longer (DNS can take up to 24 hours)
2. Check DNS records at registrar
3. Verify A record points to correct IP
4. Try from different device/network
5. Use DNS checker: https://www.whatsmydns.net/

### "502 Bad Gateway"

**Problem:** Nginx can't reach scanner

**Solutions:**
```bash
# Check if scanner is running
cd ~/metals-scanner
docker compose ps

# Restart scanner
docker compose restart

# Check logs
docker compose logs -f
```

### "Certificate Error" or "Not Secure"

**Problem:** SSL certificate issue

**Solutions:**
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew --force-renewal

# Reload Nginx
sudo systemctl reload nginx
```

### HTTP Works But HTTPS Doesn't

**Problem:** Port 443 not open

**Solutions:**
```bash
# Allow HTTPS through firewall
sudo ufw allow 443/tcp

# Reload firewall
sudo ufw reload

# Check Nginx is listening on 443
sudo netstat -tlnp | grep :443
```

### Auto-Renewal Not Working

**Problem:** Certificate expired

**Solutions:**
```bash
# Check timer status
sudo systemctl status certbot.timer

# Enable timer if stopped
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Test renewal
sudo certbot renew --dry-run
```

---

## Reverting to IP Address Only

If you want to remove the domain and go back to IP address:

```bash
# Stop Nginx
sudo systemctl stop nginx
sudo systemctl disable nginx

# Scanner is still accessible at:
# http://YOUR_DROPLET_IP:8000
```

Or keep both working (domain + IP) - no action needed.

---

## Security Considerations

### Your Setup is Now:

✅ **Encrypted:** HTTPS protects data in transit
✅ **Authenticated:** Certificate proves domain ownership
✅ **Modern:** Uses TLS 1.2+ (secure protocols)

### Still Consider:

**Authentication:** Your scanner has no login/password. Anyone with the URL can access it.

For personal use from home, this is usually fine. For additional security:

**Option 1: Firewall to your IP only**

```bash
# Replace 1.2.3.4 with your home IP address
sudo ufw allow from 1.2.3.4 to any port 80
sudo ufw allow from 1.2.3.4 to any port 443
```

Find your IP: https://whatismyipaddress.com/

**Option 2: Add basic authentication**

This is advanced - contact me (the developer) for help.

**Option 3: Use VPN**

Access your server through a VPN for added security.

---

## Cost Summary

### One-Time Costs
- Domain: $10-15 (first year)
- SSL: FREE (Let's Encrypt)
- Setup: 30 minutes of your time

### Ongoing Costs
- Domain renewal: $10-15/year
- SSL renewal: FREE (automatic)
- Server: Still $6/month (unchanged)

**Total: $6-7/month** (same as before, plus annual domain renewal)

---

## Next Steps

Now that you have a custom domain:

1. **Update bookmarks** with your new HTTPS URL
2. **Share your scanner** securely (if desired)
3. **Set reminder** for domain renewal
4. **Test from different devices** to ensure it works everywhere

### Other Enhancements

- **Local Testing:** See [LOCAL_TESTING.md](LOCAL_TESTING.md)
- **Code Customization:** See [UNDERSTANDING_THE_CODE.md](UNDERSTANDING_THE_CODE.md)
- **Ongoing Maintenance:** See [MAINTENANCE.md](MAINTENANCE.md)
- **Troubleshooting:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Summary

**What you accomplished:**
- ✅ Purchased and configured a domain name
- ✅ Set up Nginx as reverse proxy
- ✅ Obtained free SSL certificate from Let's Encrypt
- ✅ Enabled HTTPS encryption
- ✅ Configured automatic certificate renewal

**What you have now:**
- Easy-to-remember URL: `https://metals.yourdomain.com`
- Encrypted connections (HTTPS)
- Professional appearance
- No port numbers in URL
- Automatic SSL renewal

**Your scanner is now fully production-ready!** 🎉

Access it anytime at: `https://metals.yourdomain.com`

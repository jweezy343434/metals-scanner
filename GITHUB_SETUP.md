# GitHub Setup Guide

> **Complete guide to uploading your Metals Arbitrage Scanner to GitHub**

This guide walks you through creating a GitHub repository and uploading your project, making it easy to share, deploy, and collaborate.

## Why Use GitHub?

- ✅ **Easy deployment** - Clone to servers with one command
- ✅ **Version control** - Track all changes over time
- ✅ **Collaboration** - Others can contribute improvements
- ✅ **Backup** - Cloud storage for your code
- ✅ **Documentation** - READMEs display beautifully
- ✅ **Professional** - Showcase your projects

## Prerequisites

- GitHub account (free) - [Sign up here](https://github.com/signup)
- Git installed on your computer
- Your metals-scanner project directory

## Quick Start (5 Steps)

```bash
# 1. Initialize git repository
cd /root/metals-scanner
git init

# 2. Add all files
git add .

# 3. Create initial commit
git commit -m "Initial commit - Metals Arbitrage Scanner MVP"

# 4. Create GitHub repo (via web) and add remote
git remote add origin https://github.com/YOUR_USERNAME/metals-scanner.git

# 5. Push to GitHub
git branch -M main
git push -u origin main
```

## Detailed Instructions

### Step 1: Install Git (If Not Already Installed)

#### Check if Git is installed:
```bash
git --version
```

If you see a version number (e.g., `git version 2.39.0`), Git is installed. Skip to Step 2.

#### Install Git:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y git
```

**macOS:**
```bash
# Using Homebrew
brew install git

# Or install Xcode Command Line Tools
xcode-select --install
```

**Windows:**
1. Download from [git-scm.com](https://git-scm.com/download/win)
2. Run installer
3. Use default settings

**Verify installation:**
```bash
git --version
```

### Step 2: Configure Git

Set your name and email (shows up in commits):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify
git config --list
```

### Step 3: Create GitHub Account

1. Go to [github.com/signup](https://github.com/signup)
2. Enter email, create password, choose username
3. Verify email address
4. Choose Free plan

### Step 4: Prepare Your Project

#### 4.1 Navigate to Project Directory

```bash
cd /root/metals-scanner

# Or wherever your project is located
cd /path/to/metals-scanner
```

#### 4.2 Verify .gitignore Exists

Check that `.gitignore` is present and properly configured:

```bash
cat .gitignore
```

Should include:
```
.env
__pycache__/
*.pyc
*.db
*.db-journal
*.db-wal
*.db-shm
data/
logs/
```

**If `.gitignore` is missing**, create it:
```bash
cat > .gitignore << 'EOF'
# Environment variables
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Database
*.db
*.db-journal
*.db-wal
*.db-shm
data/

# Logs
*.log
logs/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
EOF
```

#### 4.3 Verify API Keys Are NOT in Repository

**CRITICAL:** Ensure `.env` file is NOT tracked:

```bash
# This should show .env is ignored
git status --ignored | grep .env
```

**If .env appears in untracked files:**
```bash
# Add to .gitignore
echo ".env" >> .gitignore
```

**Never commit API keys!** They should only be in `.env` file, which is in `.gitignore`.

### Step 5: Initialize Git Repository

```bash
# Initialize git repository (if not already done)
git init

# You should see: "Initialized empty Git repository in /path/to/metals-scanner/.git/"
```

### Step 6: Add Files to Git

```bash
# Check status (see what will be added)
git status

# Add all files
git add .

# Verify what was staged
git status
```

You should see files like:
- ✅ `README.md`
- ✅ `requirements.txt`
- ✅ `Dockerfile`
- ✅ `docker-compose.yml`
- ✅ `.env.example` (template, no secrets)
- ✅ `app/` directory
- ❌ `.env` (should NOT appear - contains secrets)
- ❌ `data/` (should NOT appear - database files)

If `.env` appears, **STOP** and add it to `.gitignore`.

### Step 7: Create Initial Commit

```bash
# Create commit with message
git commit -m "Initial commit - Metals Arbitrage Scanner MVP

- Complete FastAPI backend with rate limiting
- Web dashboard with Tailwind CSS
- eBay scraper with weight extraction
- Spot price caching from metals-api.com
- Docker deployment configuration
- Comprehensive documentation"

# Verify commit
git log --oneline
```

### Step 8: Create GitHub Repository

#### 8.1 Via GitHub Web Interface (Easier)

1. **Log in to GitHub**
2. **Click "+" icon** in top right → "New repository"
3. **Repository name:** `metals-scanner`
4. **Description:** "Automated precious metals arbitrage scanner - finds deals on eBay below spot price"
5. **Visibility:**
   - **Public** - Anyone can see (recommended for sharing)
   - **Private** - Only you can see
6. **DO NOT initialize with:**
   - ❌ README (you already have one)
   - ❌ .gitignore (you already have one)
   - ❌ License (you already have one)
7. **Click "Create repository"**

#### 8.2 Via GitHub CLI (Alternative)

```bash
# Install GitHub CLI
# macOS:
brew install gh

# Ubuntu/Debian:
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Authenticate
gh auth login

# Create repository
gh repo create metals-scanner --public --source=. --remote=origin --push
```

### Step 9: Connect Local Repository to GitHub

After creating the repo on GitHub, you'll see commands. Use these:

```bash
# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/metals-scanner.git

# Verify remote
git remote -v
# Should show:
# origin  https://github.com/YOUR_USERNAME/metals-scanner.git (fetch)
# origin  https://github.com/YOUR_USERNAME/metals-scanner.git (push)
```

**Replace YOUR_USERNAME with your actual GitHub username!**

### Step 10: Push to GitHub

```bash
# Rename branch to 'main' (GitHub default)
git branch -M main

# Push to GitHub
git push -u origin main

# Enter GitHub credentials if prompted
```

**Authentication Methods:**

**HTTPS (easier):**
- Username: Your GitHub username
- Password: **Personal Access Token** (not your account password)
  - Create at: Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
  - Give it `repo` permissions
  - Copy the token (you won't see it again!)

**SSH (more secure, no password prompts):**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
# Paste the public key

# Change remote to SSH
git remote set-url origin git@github.com:YOUR_USERNAME/metals-scanner.git
```

### Step 11: Verify Upload

1. **Visit your repository**
   - `https://github.com/YOUR_USERNAME/metals-scanner`

2. **You should see:**
   - ✅ README.md displayed on main page
   - ✅ All your files
   - ✅ Folder structure (app/, etc.)
   - ✅ Documentation files
   - ❌ **NO .env file** (check this!)

3. **Check that .env is not visible:**
   - If you see `.env` file: **IMMEDIATELY DELETE THE REPOSITORY**
   - Remove sensitive file: `git rm --cached .env`
   - Add to `.gitignore`
   - Commit and push again
   - **Change your API keys** (they're now compromised)

## Updating Your Repository

### After Making Changes

```bash
# 1. Check what changed
git status

# 2. Add changed files
git add .

# Or add specific files:
git add app/main.py
git add README.md

# 3. Commit with descriptive message
git commit -m "Add email notification feature"

# 4. Push to GitHub
git push

# Done! Changes are on GitHub
```

### Good Commit Messages

**Good:**
- ✅ "Add email notifications for deals >10% margin"
- ✅ "Fix weight extraction for fractional ounces"
- ✅ "Update dashboard with platinum support"
- ✅ "Improve error handling in eBay scraper"

**Bad:**
- ❌ "Update"
- ❌ "Fix bug"
- ❌ "Changes"
- ❌ "WIP"

### Viewing Change History

```bash
# View commit history
git log

# Compact view
git log --oneline

# See changes in last commit
git show

# See changes in specific file
git log -p app/main.py
```

## Sharing Your Project

### Share Repository Link

Give people this link:
```
https://github.com/YOUR_USERNAME/metals-scanner
```

They can:
1. **View code** in browser
2. **Clone** to their computer:
   ```bash
   git clone https://github.com/YOUR_USERNAME/metals-scanner.git
   ```
3. **Deploy** using the README instructions

### Update README with Your GitHub URL

Edit `README.md`, `DEPLOYMENT.md`, and `setup.sh` to replace `YOUR_USERNAME`:

```bash
# Find and replace
find . -type f \( -name "*.md" -o -name "*.sh" \) -exec sed -i 's/YOUR_USERNAME/your-actual-username/g' {} +

# Commit the change
git add .
git commit -m "Update URLs with actual GitHub username"
git push
```

### Add Repository Topics

On GitHub:
1. Go to your repository
2. Click ⚙️ (gear icon) next to "About"
3. Add topics:
   - `precious-metals`
   - `arbitrage`
   - `ebay`
   - `fastapi`
   - `python`
   - `docker`
   - `scraper`
   - `trading`
4. Click "Save changes"

This helps people discover your project!

### Enable GitHub Pages (Optional)

Host documentation as a website:

1. **Settings** → **Pages**
2. **Source:** Deploy from a branch
3. **Branch:** main → /docs
4. Click **Save**

Your docs will be available at:
`https://YOUR_USERNAME.github.io/metals-scanner/`

## Deployment from GitHub

### Deploy to DigitalOcean

Now anyone can deploy with:

```bash
# SSH into droplet
ssh root@DROPLET_IP

# Clone repository
git clone https://github.com/YOUR_USERNAME/metals-scanner.git
cd metals-scanner

# Run setup script
sudo ./setup.sh
```

Or use the automated setup:

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/metals-scanner/main/setup.sh -o setup.sh
chmod +x setup.sh
sudo ./setup.sh https://github.com/YOUR_USERNAME/metals-scanner.git
```

### Update Deployment

When you push changes to GitHub:

```bash
# On server
cd ~/metals-scanner
git pull
docker compose up -d --build
```

## GitHub Features to Enable

### 1. Issues

Track bugs and feature requests:
- **Enable:** Settings → General → Features → ✅ Issues
- Templates already created in `.github/ISSUE_TEMPLATE/`

### 2. Discussions

Community Q&A:
- **Enable:** Settings → General → Features → ✅ Discussions
- Create categories: General, Ideas, Q&A, Show and Tell

### 3. Wiki

Additional documentation:
- **Enable:** Settings → General → Features → ✅ Wiki
- Create pages for:
  - Deployment guides
  - Troubleshooting
  - API documentation

### 4. Security

#### Enable Dependabot

Automatic dependency updates:
1. **Settings** → **Code security and analysis**
2. Enable **Dependabot alerts**
3. Enable **Dependabot security updates**

#### Add Security Policy

Create `SECURITY.md`:
```bash
cat > SECURITY.md << 'EOF'
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

## Reporting a Vulnerability

**DO NOT open a public issue for security vulnerabilities.**

Instead, email: your.email@example.com

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You'll receive a response within 48 hours.
EOF

git add SECURITY.md
git commit -m "Add security policy"
git push
```

### 5. GitHub Actions (Optional)

Automate testing/deployment:

Create `.github/workflows/test.yml`:
```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run health check
        run: |
          python -c "from app.config import settings; print('Config loaded successfully')"
```

## Best Practices

### Commit Often

- Commit after completing a feature
- Commit before making risky changes
- Small, focused commits are better

### Write Meaningful Messages

```bash
# Good format:
git commit -m "Add feature: email notifications

- Implemented SMTP email sending
- Added configuration for Gmail
- Created notification triggers for >10% deals
- Updated documentation

Closes #123"
```

### Create Branches for Features

```bash
# Create new branch
git checkout -b feature/amazon-scraper

# Make changes
# ... edit files ...

# Commit
git add .
git commit -m "Add Amazon scraper"

# Push branch
git push -u origin feature/amazon-scraper

# Create Pull Request on GitHub
# Merge when ready
```

### Don't Commit These

- ❌ `.env` files (API keys)
- ❌ `data/` directory (database)
- ❌ `logs/` directory
- ❌ `__pycache__/` directories
- ❌ IDE-specific files (`.vscode/`, `.idea/`)
- ❌ OS files (`.DS_Store`, `Thumbs.db`)

All these should be in `.gitignore`.

### Regular Backups

GitHub is a backup, but also:
```bash
# Local backup
tar -czf metals-scanner-backup.tar.gz metals-scanner/

# Or clone to another location
git clone https://github.com/YOUR_USERNAME/metals-scanner.git ~/backups/metals-scanner
```

## Troubleshooting

### "Permission denied (publickey)"

**Using HTTPS:**
- Ensure you're using Personal Access Token, not password
- Token needs `repo` scope

**Using SSH:**
```bash
# Test SSH connection
ssh -T git@github.com

# Add SSH key to agent
ssh-add ~/.ssh/id_ed25519

# Verify key is on GitHub
# Settings → SSH and GPG keys
```

### "Remote already exists"

```bash
# Remove old remote
git remote remove origin

# Add new one
git remote add origin https://github.com/YOUR_USERNAME/metals-scanner.git
```

### "Merge conflicts"

```bash
# If you edited on GitHub and locally
git pull --rebase

# Fix conflicts in files
# Then:
git add .
git rebase --continue
git push
```

### Large File Errors

```bash
# If you accidentally added large files
git rm --cached large_file.db
echo "large_file.db" >> .gitignore
git commit -m "Remove large file"
git push --force  # Use carefully!
```

### Accidentally Committed .env

**URGENT - API Keys Compromised:**

1. **Delete repository** immediately
2. **Regenerate all API keys**
3. Fix `.gitignore`
4. Create new repository
5. Start fresh

```bash
# Remove from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
```

But **always regenerate compromised keys!**

## Next Steps

Now that your project is on GitHub:

1. ✅ **Update all documentation** to use your GitHub username
2. ✅ **Enable Issues and Discussions**
3. ✅ **Add repository topics**
4. ✅ **Star your own repo** (😄)
5. ✅ **Share with friends** or on social media
6. ✅ **Deploy to DigitalOcean** using GitHub URL
7. ✅ **Set up Dependabot** for security updates

## Resources

- **GitHub Docs:** [docs.github.com](https://docs.github.com/)
- **Git Handbook:** [guides.github.com/introduction/git-handbook/](https://guides.github.com/introduction/git-handbook/)
- **Markdown Guide:** [guides.github.com/features/mastering-markdown/](https://guides.github.com/features/mastering-markdown/)

---

**Congratulations! Your project is now on GitHub! 🎉**

Share it with the world: `https://github.com/YOUR_USERNAME/metals-scanner`

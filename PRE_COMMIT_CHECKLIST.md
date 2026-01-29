# Pre-Commit Checklist

> **Use this checklist before pushing to GitHub to ensure everything is ready**

## 🔒 Security Check (CRITICAL)

- [ ] `.env` file is listed in `.gitignore`
- [ ] `.env` file does NOT appear in `git status`
- [ ] No API keys in any committed files
- [ ] No passwords or secrets in code
- [ ] `data/` directory is in `.gitignore` (contains database)
- [ ] `logs/` directory is in `.gitignore`
- [ ] Run: `git grep -i "api.key\|password\|secret" -- ':!*.md'` returns nothing

**If any secrets are found: STOP and remove them before committing!**

## 📁 File Structure Check

- [ ] All required files exist:
  ```bash
  ls -1 | grep -E "README|Dockerfile|docker-compose|requirements|LICENSE|.gitignore"
  ```

- [ ] Documentation files present:
  - [ ] `README.md`
  - [ ] `CONTRIBUTING.md`
  - [ ] `DEPLOYMENT.md`
  - [ ] `AI_CUSTOMIZATION_GUIDE.md`
  - [ ] `FAQ.md`
  - [ ] `LOCAL_DEVELOPMENT.md`
  - [ ] `GITHUB_SETUP.md`
  - [ ] `QUICK_START_DIGITALOCEAN.md`
  - [ ] `LICENSE`

- [ ] Application files present:
  - [ ] `app/main.py`
  - [ ] `app/config.py`
  - [ ] `app/database.py`
  - [ ] `app/schemas.py`
  - [ ] `app/scrapers/ebay.py`
  - [ ] `app/static/index.html`

- [ ] Configuration files:
  - [ ] `.env.example` (template only, no secrets)
  - [ ] `requirements.txt`
  - [ ] `Dockerfile`
  - [ ] `docker-compose.yml`
  - [ ] `setup.sh`

- [ ] GitHub files:
  - [ ] `.github/ISSUE_TEMPLATE/bug_report.md`
  - [ ] `.github/ISSUE_TEMPLATE/feature_request.md`
  - [ ] `.github/pull_request_template.md`

## 🔍 Content Verification

### .gitignore Check
```bash
cat .gitignore | grep -E "\.env$|data/|logs/|__pycache__|\.pyc"
```
Should show all these patterns.

### .env.example Check
```bash
cat .env.example | grep -E "EBAY_API_KEY|METALS_API_KEY"
```
Should contain placeholder values like `your_xxx_here`, **NOT** real keys.

### README Check
- [ ] Project description is clear
- [ ] Quick start instructions work
- [ ] API key setup instructions are correct
- [ ] Architecture diagram is present
- [ ] Troubleshooting section is helpful
- [ ] All links work (no broken references)

### Docker Configuration Check
```bash
# Verify docker-compose.yml has correct structure
docker-compose config
```
Should show no errors.

## 🧪 Testing Before Commit

### Local Testing (If Possible)
```bash
# Build Docker image
docker compose build

# Start application
docker compose up -d

# Test health endpoint
curl http://localhost:8000/api/health

# Stop
docker compose down
```

### Syntax Check
```bash
# Check Python syntax
find app -name "*.py" -exec python3 -m py_compile {} \;

# Check shell script syntax
bash -n setup.sh
```

## 📝 Documentation Updates

- [ ] Updated all `YOUR_USERNAME` references to actual username
- [ ] Updated all `YOUR_EMAIL` references
- [ ] Updated all example URLs to real repository URL
- [ ] Version numbers are correct (if using versioning)
- [ ] Dates are current
- [ ] Examples in documentation actually work

### Find and Replace Check
```bash
# Find remaining placeholders
grep -r "YOUR_USERNAME" --include="*.md" --include="*.sh" .
grep -r "YOUR_EMAIL" --include="*.md" .
grep -r "your-actual-username" --include="*.md" .
```
Should return minimal or no results.

## 📊 Code Quality

### Python Code
- [ ] No syntax errors
- [ ] Imports are used
- [ ] No obvious bugs
- [ ] Comments explain complex logic
- [ ] Functions have docstrings
- [ ] Error handling is present

### JavaScript Code
- [ ] No console.log() statements in production
- [ ] Functions are documented
- [ ] No obvious errors

### CSS/Styling
- [ ] Dashboard looks good
- [ ] Mobile responsive (test in browser)
- [ ] No broken layout

## 🔗 Links Verification

Check all links in documentation:
```bash
# Find all markdown links
grep -r "\[.*\](.*)" --include="*.md" .
```

Common links to verify:
- [ ] GitHub repository URLs
- [ ] eBay Developer portal: https://developer.ebay.com/
- [ ] Metals API: https://metals-api.com/
- [ ] DigitalOcean: https://www.digitalocean.com/
- [ ] Docker docs: https://docs.docker.com/
- [ ] Internal doc references (README.md, CONTRIBUTING.md, etc.)

## 📦 Dependencies Check

```bash
# Verify requirements.txt is up to date
pip freeze > requirements-check.txt
diff requirements.txt requirements-check.txt
rm requirements-check.txt
```

Should show no differences (or only expected differences).

## 🚀 Deployment Readiness

### setup.sh Script
- [ ] Has execution permissions: `chmod +x setup.sh`
- [ ] Repository URL is configurable
- [ ] Error handling works
- [ ] Can run idempotently (safe to run multiple times)

### Docker Configuration
- [ ] Dockerfile builds successfully
- [ ] docker-compose.yml is valid
- [ ] Health check is configured
- [ ] Restart policy is set
- [ ] Volumes are properly configured

### Environment Configuration
- [ ] `.env.example` has all required variables
- [ ] `.env.example` has helpful comments
- [ ] No default values that would break the app
- [ ] Clear instructions for getting API keys

## 📄 License Check

- [ ] `LICENSE` file exists
- [ ] License type is MIT (or your choice)
- [ ] Year is current
- [ ] Author name is correct

## 🎨 README Quality

- [ ] Has clear title and description
- [ ] Has badges (optional but nice)
- [ ] Has table of contents
- [ ] Quick start works in 3 commands or less
- [ ] Screenshots or demo GIF (optional)
- [ ] Clear contribution guidelines link
- [ ] Contact information
- [ ] License mentioned

## 🔄 Git Status Check

```bash
# Verify git status before commit
git status
```

Should NOT show:
- ❌ `.env`
- ❌ `data/metals_scanner.db`
- ❌ `*.log` files
- ❌ `__pycache__/` directories

Should show:
- ✅ `.env.example`
- ✅ All documentation files
- ✅ All application files
- ✅ Configuration files

## 📋 Commit Message Preparation

Prepare a good commit message:

**For initial commit:**
```
Initial commit - Metals Arbitrage Scanner MVP

Complete metals arbitrage scanner implementation including:
- FastAPI backend with rate limiting and caching
- eBay scraper with weight extraction
- Spot price integration with metals-api.com
- Responsive web dashboard with Tailwind CSS
- Docker deployment configuration
- Comprehensive documentation
- Automated setup script
- Local development guide

Features:
✅ Automatic scans every 2 hours
✅ Smart caching to conserve API calls
✅ Rate limiting protection
✅ Health monitoring endpoints
✅ Database with optimized indexes
✅ GitHub-ready with issue templates

Documentation includes:
- README with quick start
- Deployment guide for DigitalOcean
- Contribution guidelines
- AI customization guide for non-technical users
- FAQ and troubleshooting
- Local development setup
```

**For updates:**
```
[Type]: Brief description

Detailed explanation of what changed and why.

- Bullet point changes
- More details

Closes #123 (if fixing an issue)
```

## 🎯 Final Pre-Push Checklist

Right before `git push`:

```bash
# 1. One more security check
git diff HEAD --name-only | xargs grep -l "api.key\|password" || echo "✓ No secrets found"

# 2. Verify commit
git log -1 --stat

# 3. Verify remote
git remote -v

# 4. Final check
git status

# 5. Ready to push!
git push -u origin main
```

## ✅ Post-Push Verification

After pushing to GitHub:

1. **Visit Repository:**
   - [ ] README displays correctly
   - [ ] All folders are present
   - [ ] `.env` file is NOT visible
   - [ ] File structure looks correct

2. **Test Clone:**
   ```bash
   # In a different directory
   git clone https://github.com/YOUR_USERNAME/metals-scanner.git test-clone
   cd test-clone
   ls -la
   ```
   - [ ] All files present
   - [ ] `.env` is NOT cloned
   - [ ] Can follow setup instructions

3. **Check Issues/PRs:**
   - [ ] Issue templates work
   - [ ] PR template works

4. **Test Setup Script:**
   ```bash
   # Download and verify
   curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/metals-scanner/main/setup.sh
   ```
   - [ ] Script downloads successfully
   - [ ] No syntax errors

## 🚨 If Something Goes Wrong

### Committed Secrets by Accident

**IMMEDIATE ACTION:**
1. Delete the repository on GitHub
2. Regenerate ALL API keys
3. Fix `.gitignore`
4. Create fresh repository
5. Never commit secrets again

### Wrong Files Committed

```bash
# Remove from git but keep locally
git rm --cached filename

# Remove from history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch filename" \
  --prune-empty --tag-name-filter cat -- --all

git push --force
```

### Need to Undo Last Commit

```bash
# Undo commit but keep changes
git reset --soft HEAD~1

# Undo commit and discard changes
git reset --hard HEAD~1
```

## 📞 Getting Help

If stuck:
1. Check [GITHUB_SETUP.md](GITHUB_SETUP.md)
2. Review [FAQ.md](FAQ.md)
3. Search GitHub docs
4. Ask in GitHub Discussions

## 🎉 You're Ready!

If all checkboxes are ✅, you're ready to push to GitHub!

```bash
git push -u origin main
```

**Share your project:**
- Tweet about it
- Post on Reddit (r/Python, r/Entrepreneur)
- Share on LinkedIn
- Tell friends

Your link: `https://github.com/YOUR_USERNAME/metals-scanner`

---

**Remember:** Once it's public, the internet is forever. Make sure no secrets are committed!

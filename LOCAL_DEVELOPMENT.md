# Local Development Guide

> **Run the Metals Arbitrage Scanner on your local computer for development and testing**

This guide is for developers who want to run the scanner locally without Docker or cloud deployment.

## Prerequisites

- **Python 3.11 or higher** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))
- **Text editor** (VS Code, PyCharm, or any IDE)
- **eBay API key** ([Get here](https://developer.ebay.com/))
- **Metals API key** ([Get here](https://metals-api.com/))

## Quick Start (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/metals-scanner.git
cd metals-scanner

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your API keys

# 5. Create directories
mkdir -p data logs

# 6. Run application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 7. Open browser
# http://localhost:8000
```

## Detailed Setup

### 1. Install Python

#### macOS
```bash
# Using Homebrew
brew install python@3.11

# Verify
python3 --version
# Should show: Python 3.11.x
```

#### Linux (Ubuntu/Debian)
```bash
# Install Python 3.11
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip

# Verify
python3.11 --version
```

#### Windows
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer
3. **Important:** Check "Add Python to PATH"
4. Verify in Command Prompt:
   ```cmd
   python --version
   ```

### 2. Clone Repository

```bash
# HTTPS (easier)
git clone https://github.com/YOUR_USERNAME/metals-scanner.git

# SSH (if you have keys setup)
git clone git@github.com:YOUR_USERNAME/metals-scanner.git

# Navigate to directory
cd metals-scanner
```

### 3. Create Virtual Environment

**Why?** Isolates project dependencies from system Python.

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# macOS/Linux:
source venv/bin/activate

# Windows (Command Prompt):
venv\Scripts\activate.bat

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Windows (Git Bash):
source venv/Scripts/activate
```

You should see `(venv)` in your terminal prompt.

### 4. Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

**Expected packages:**
- fastapi
- uvicorn
- sqlalchemy
- requests
- pydantic
- apscheduler
- python-dotenv
- pytz

### 5. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit with your favorite editor
# macOS/Linux:
nano .env
# or
code .env  # VS Code
# or
vim .env

# Windows:
notepad .env
```

**Add your API keys:**
```bash
EBAY_API_KEY=YourActual-EbayAppID-PRD-1234567890-abcdefgh
METALS_API_KEY=your_actual_32_character_metals_api_key
```

### 6. Create Data Directories

```bash
# Create directories for database and logs
mkdir -p data logs

# On Windows (Command Prompt):
mkdir data
mkdir logs
```

### 7. Run Application

```bash
# Run with auto-reload (development mode)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# The --reload flag makes the server restart when you edit files
```

**Expected output:**
```
INFO:     Will watch for changes in these directories: ['/path/to/metals-scanner']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 8. Test Application

Open your browser and visit:
- **Dashboard:** http://localhost:8000
- **API Health:** http://localhost:8000/api/health
- **API Docs:** http://localhost:8000/docs (FastAPI auto-generated)

## Development Workflow

### Making Changes

#### Backend Changes (Python)

1. **Edit files** in `app/` directory
2. **Save** - Uvicorn auto-reloads with `--reload` flag
3. **Refresh browser** to see changes
4. **Check logs** in terminal for errors

Example:
```bash
# Edit a file
code app/main.py

# Save changes (Ctrl+S)
# Terminal shows: INFO: Reloading...
# Changes are live immediately
```

#### Frontend Changes (HTML/CSS/JS)

1. **Edit** `app/static/index.html`
2. **Save**
3. **Refresh browser** (Ctrl+R or Cmd+R)
4. No restart needed!

### Viewing Logs

**In terminal:**
```bash
# Real-time application logs
# (Just watch the terminal where uvicorn is running)
```

**In log file:**
```bash
# View log file
tail -f logs/metals_scanner.log

# On Windows:
Get-Content logs\metals_scanner.log -Wait
```

### Database Inspection

```bash
# Install SQLite browser (optional but helpful)
# macOS:
brew install sqlite
brew install --cask db-browser-for-sqlite

# Linux:
sudo apt install sqlite3 sqlitebrowser

# Windows: Download DB Browser for SQLite
# https://sqlitebrowser.org/
```

**Command line:**
```bash
# Open database
sqlite3 data/metals_scanner.db

# Useful queries
.tables
SELECT COUNT(*) FROM listings;
SELECT * FROM spot_prices ORDER BY fetched_at DESC LIMIT 5;
.exit
```

### Running Tests (When Added)

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## Common Development Tasks

### Trigger Manual Scan

```bash
# Using curl
curl -X POST http://localhost:8000/api/scan

# Or click "Scan Now" in dashboard
```

### Reset Database

```bash
# Stop application (Ctrl+C)

# Delete database
rm data/metals_scanner.db

# Restart application
uvicorn app.main:app --reload
# Fresh database will be created
```

### Clear Logs

```bash
# Truncate log file
> logs/metals_scanner.log

# Or delete and recreate
rm logs/metals_scanner.log
touch logs/metals_scanner.log
```

### Add New Dependency

```bash
# Install package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### Debugging

#### Enable Debug Logging

Edit `.env`:
```bash
LOG_LEVEL=DEBUG
```

Restart application.

#### Python Debugger

Add breakpoint in code:
```python
import pdb; pdb.set_trace()
```

#### VS Code Debugging

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true
    }
  ]
}
```

Press F5 to start debugging.

## IDE Setup

### VS Code (Recommended)

**Install Extensions:**
1. Python (Microsoft)
2. Pylance (Microsoft)
3. Docker (Microsoft)
4. SQLite Viewer
5. GitLens

**Settings:**
Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

### PyCharm

1. **Open Project:** File → Open → Select `metals-scanner/`
2. **Configure Interpreter:** Settings → Project → Python Interpreter → Add → Virtualenv → Existing environment → Select `venv/bin/python`
3. **Mark directories:**
   - Right-click `app/` → Mark Directory As → Sources Root

## Platform-Specific Notes

### macOS

**Install Xcode Command Line Tools** (if you get compilation errors):
```bash
xcode-select --install
```

**Use Python 3.11 specifically:**
```bash
python3.11 -m venv venv
```

### Linux

**Install build tools** (for some Python packages):
```bash
sudo apt install -y build-essential python3-dev
```

**Use system Python:**
```bash
python3 -m venv venv
```

### Windows

**PowerShell Execution Policy:**
If you can't activate venv:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Use Python from Microsoft Store** (easiest):
```powershell
python -m venv venv
```

**Git Bash recommended** over Command Prompt for Unix-like commands.

## Switching to Docker

Already developing locally and want to try Docker?

```bash
# Stop local development server (Ctrl+C)

# Build Docker image
docker compose build

# Run with Docker
docker compose up -d

# View logs
docker compose logs -f

# Stop Docker
docker compose down

# Switch back to local:
source venv/bin/activate  # Reactivate venv
uvicorn app.main:app --reload
```

## Troubleshooting

### "Module not found" errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Should see (venv) in prompt

# Reinstall dependencies
pip install -r requirements.txt
```

### "Permission denied" on logs/data

```bash
# Fix permissions
chmod 755 data logs

# On Windows, run as Administrator if needed
```

### "Port 8000 already in use"

```bash
# Find process using port
# macOS/Linux:
lsof -i :8000

# Windows:
netstat -ano | findstr :8000

# Kill process or use different port:
uvicorn app.main:app --reload --port 8001
```

### "Can't find .env file"

```bash
# Create it
cp .env.example .env

# Edit with API keys
nano .env
```

### Database locked errors

```bash
# Only run one instance at a time
# Stop Docker if running:
docker compose down

# Then start local:
uvicorn app.main:app --reload
```

## Next Steps

- Read [CONTRIBUTING.md](CONTRIBUTING.md) for code structure
- Check [AI_CUSTOMIZATION_GUIDE.md](AI_CUSTOMIZATION_GUIDE.md) for AI-assisted development
- See [FAQ.md](FAQ.md) for common questions
- Join development discussions on GitHub

## Getting Help

- **Local issues:** Check [FAQ.md](FAQ.md)
- **Development questions:** See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Bug reports:** Open GitHub Issue
- **Feature ideas:** Open GitHub Discussion

---

**Happy developing! 🚀**

#!/bin/bash

################################################################################
# Metals Arbitrage Scanner - Automated Setup Script
#
# This script automates deployment on Ubuntu 22.04 (DigitalOcean Droplet)
#
# What it does:
# 1. Installs Docker and Docker Compose
# 2. Clones repository (or uses current directory)
# 3. Configures environment variables
# 4. Creates necessary directories
# 5. Builds and starts the application
#
# Usage:
#   # Option 1: With repository URL
#   sudo ./setup.sh https://github.com/YOUR_USERNAME/metals-scanner.git
#
#   # Option 2: Auto-detect from current git repo
#   sudo ./setup.sh
#
#   # Option 3: Download and run
#   curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/metals-scanner/main/setup.sh -o setup.sh
#   chmod +x setup.sh
#   sudo ./setup.sh https://github.com/YOUR_USERNAME/metals-scanner.git
#
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="$HOME/metals-scanner"
REPO_URL="${1:-}"  # First argument, or empty

# Try to auto-detect repo URL from current directory if in git repo
if [ -z "$REPO_URL" ] && [ -d ".git" ]; then
    REPO_URL=$(git remote get-url origin 2>/dev/null || echo "")
    if [ -n "$REPO_URL" ]; then
        print_info "Auto-detected repository URL: $REPO_URL"
    fi
fi

# If still empty, use placeholder
if [ -z "$REPO_URL" ]; then
    REPO_URL="https://github.com/YOUR_USERNAME/metals-scanner.git"
fi

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo ""
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if running as root or with sudo
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run with sudo"
        echo "Usage: sudo ./setup.sh"
        exit 1
    fi
}

# Get the actual user (not root when using sudo)
get_actual_user() {
    if [ -n "$SUDO_USER" ]; then
        echo "$SUDO_USER"
    else
        echo "$USER"
    fi
}

################################################################################
# Installation Steps
################################################################################

# Step 1: System Update
update_system() {
    print_header "Step 1: Updating System Packages"

    apt update -qq
    print_success "Package list updated"

    DEBIAN_FRONTEND=noninteractive apt upgrade -y -qq
    print_success "System packages upgraded"

    apt install -y -qq curl wget git ca-certificates gnupg lsb-release jq
    print_success "Essential utilities installed"
}

# Step 2: Install Docker
install_docker() {
    print_header "Step 2: Installing Docker"

    # Check if Docker is already installed
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d ' ' -f3 | cut -d ',' -f1)
        print_warning "Docker $DOCKER_VERSION is already installed"
        print_info "Skipping Docker installation"
        return 0
    fi

    print_info "Adding Docker repository..."

    # Add Docker's official GPG key
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Set up Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    print_success "Docker repository added"

    # Install Docker
    print_info "Installing Docker Engine..."
    apt update -qq
    apt install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # Add user to docker group
    ACTUAL_USER=$(get_actual_user)
    usermod -aG docker "$ACTUAL_USER"

    print_success "Docker installed successfully"

    # Verify installation
    DOCKER_VERSION=$(docker --version | cut -d ' ' -f3 | cut -d ',' -f1)
    COMPOSE_VERSION=$(docker compose version | cut -d ' ' -f4)
    print_success "Docker version: $DOCKER_VERSION"
    print_success "Docker Compose version: $COMPOSE_VERSION"

    # Start Docker service
    systemctl start docker
    systemctl enable docker
    print_success "Docker service started and enabled"
}

# Step 3: Setup Application Directory
setup_directory() {
    print_header "Step 3: Setting Up Application Directory"

    ACTUAL_USER=$(get_actual_user)

    # Check if we're already in the metals-scanner directory
    if [ -f "docker-compose.yml" ] && [ -f "Dockerfile" ]; then
        INSTALL_DIR=$(pwd)
        print_warning "Already in metals-scanner directory: $INSTALL_DIR"
        print_info "Using current directory"
        return 0
    fi

    # Check if directory already exists
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Directory $INSTALL_DIR already exists"

        # Check if it's a git repository
        if [ -d "$INSTALL_DIR/.git" ]; then
            print_info "Updating existing repository..."
            cd "$INSTALL_DIR"
            sudo -u "$ACTUAL_USER" git pull
            print_success "Repository updated"
        else
            print_info "Using existing directory"
            cd "$INSTALL_DIR"
        fi
    else
        # Clone repository
        print_info "Cloning repository from GitHub..."
        print_warning "Note: If this fails, you need to update REPO_URL in the script"

        # Clone as the actual user, not root
        sudo -u "$ACTUAL_USER" git clone "$REPO_URL" "$INSTALL_DIR" 2>/dev/null || {
            print_error "Failed to clone repository"
            print_info "Creating directory manually..."
            mkdir -p "$INSTALL_DIR"
            chown "$ACTUAL_USER:$ACTUAL_USER" "$INSTALL_DIR"
            print_warning "You'll need to manually add the application files to $INSTALL_DIR"
        }

        cd "$INSTALL_DIR"
        print_success "Repository cloned to $INSTALL_DIR"
    fi

    # Ensure proper ownership
    chown -R "$ACTUAL_USER:$ACTUAL_USER" "$INSTALL_DIR"
}

# Step 4: Configure Environment Variables
configure_env() {
    print_header "Step 4: Configuring Environment Variables"

    ACTUAL_USER=$(get_actual_user)

    if [ -f ".env" ]; then
        print_warning ".env file already exists"
        read -p "Do you want to reconfigure? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Keeping existing .env file"
            return 0
        fi
    fi

    # Copy example if it exists
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Copied .env.example to .env"
    else
        print_warning ".env.example not found, creating new .env"
        touch .env
    fi

    echo ""
    print_info "Please provide your API keys:"
    echo ""

    # Prompt for eBay API Key
    echo -e "${YELLOW}eBay API Key:${NC}"
    echo "  Get it from: https://developer.ebay.com/"
    echo "  (Production App ID, not Sandbox)"
    read -p "Enter your eBay API Key: " EBAY_KEY

    echo ""

    # Prompt for Metals API Key
    echo -e "${YELLOW}Metals API Key:${NC}"
    echo "  Get it from: https://metals-api.com/signup/free"
    read -p "Enter your Metals API Key: " METALS_KEY

    echo ""

    # Validate inputs
    if [ -z "$EBAY_KEY" ] || [ -z "$METALS_KEY" ]; then
        print_error "API keys cannot be empty"
        exit 1
    fi

    # Write to .env file
    cat > .env << EOF
# eBay API Configuration
EBAY_API_KEY=$EBAY_KEY

# Metals API Configuration
METALS_API_KEY=$METALS_KEY

# Database Configuration
DATABASE_URL=sqlite:////app/data/metals_scanner.db

# Scheduler Configuration
ENABLE_AUTO_SCAN=true
SCAN_INTERVAL_HOURS=2

# Logging Configuration
LOG_LEVEL=INFO

# Rate Limits
EBAY_DAILY_LIMIT=5000
METALS_API_MONTHLY_LIMIT=50

# Cache Duration (minutes)
CACHE_MARKET_HOURS=15
CACHE_OFF_HOURS=60
CACHE_WEEKEND=240

# API Settings
API_TIMEOUT=10
API_RETRY_ATTEMPTS=3
EOF

    chown "$ACTUAL_USER:$ACTUAL_USER" .env
    chmod 600 .env  # Secure permissions

    print_success "Environment variables configured"
    print_info "API keys saved securely to .env file"
}

# Step 5: Create Directories
create_directories() {
    print_header "Step 5: Creating Data Directories"

    ACTUAL_USER=$(get_actual_user)

    mkdir -p data logs
    chmod 777 data logs  # Docker needs write access
    chown "$ACTUAL_USER:$ACTUAL_USER" data logs

    print_success "Created data/ directory for database"
    print_success "Created logs/ directory for application logs"
}

# Step 6: Build Application
build_application() {
    print_header "Step 6: Building Docker Image"

    ACTUAL_USER=$(get_actual_user)

    print_info "This may take 2-3 minutes..."

    # Build as actual user
    sudo -u "$ACTUAL_USER" docker compose build --quiet

    print_success "Docker image built successfully"
}

# Step 7: Start Application
start_application() {
    print_header "Step 7: Starting Application"

    ACTUAL_USER=$(get_actual_user)

    # Stop if already running
    sudo -u "$ACTUAL_USER" docker compose down 2>/dev/null || true

    # Start in detached mode
    sudo -u "$ACTUAL_USER" docker compose up -d

    print_success "Application started in background"

    # Wait for application to be ready
    print_info "Waiting for application to start..."
    sleep 5

    # Check if container is running
    if sudo -u "$ACTUAL_USER" docker compose ps | grep -q "running"; then
        print_success "Container is running"
    else
        print_error "Container failed to start"
        print_info "Check logs with: docker compose logs"
        exit 1
    fi

    # Test health endpoint
    print_info "Testing health endpoint..."
    for i in {1..10}; do
        if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
            print_success "Application is healthy"
            break
        fi
        if [ $i -eq 10 ]; then
            print_warning "Health check timeout (app may still be starting)"
        fi
        sleep 2
    done
}

# Step 8: Display Summary
display_summary() {
    print_header "Installation Complete! 🎉"

    # Get server IP
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_SERVER_IP")

    echo ""
    print_success "Metals Arbitrage Scanner is now running!"
    echo ""

    echo -e "${BLUE}Access the dashboard:${NC}"
    echo "  http://$SERVER_IP:8000"
    echo ""

    echo -e "${BLUE}Useful commands:${NC}"
    echo "  View logs:       docker compose logs -f"
    echo "  Stop scanner:    docker compose down"
    echo "  Start scanner:   docker compose up -d"
    echo "  Restart:         docker compose restart"
    echo "  Check status:    docker compose ps"
    echo ""

    echo -e "${BLUE}Test the scanner:${NC}"
    echo "  curl http://localhost:8000/api/health"
    echo ""

    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Open http://$SERVER_IP:8000 in your browser"
    echo "  2. Click 'Scan Now' to start your first scan"
    echo "  3. Check logs with: docker compose logs -f"
    echo ""

    print_warning "Note: If you just created this user, log out and back in for Docker permissions"
    print_info "For security, consider setting up a firewall (see DEPLOYMENT.md)"

    echo ""
    print_success "Setup complete! Happy scanning! 🔍💰"
    echo ""
}

################################################################################
# Main Execution
################################################################################

main() {
    print_header "Metals Arbitrage Scanner - Automated Setup"

    echo "This script will install and configure the Metals Arbitrage Scanner."
    echo "It will install Docker and set up the application in: $INSTALL_DIR"
    echo ""

    # Check if running with sudo
    check_root

    # Confirm before proceeding
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installation cancelled"
        exit 0
    fi

    # Run installation steps
    update_system
    install_docker
    setup_directory
    configure_env
    create_directories
    build_application
    start_application
    display_summary
}

# Run main function
main "$@"

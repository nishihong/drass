#!/bin/bash

# ======================================================
# Drass Deployment System - One-Click Deployment Script
# ======================================================
# This script automatically sets up everything needed for deployment
# including Python virtual environment and all dependencies
# ======================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/.venv-deploy"
PYTHON_CMD=""
PIP_CMD=""

# Function to print colored messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_section() {
    echo
    echo -e "${MAGENTA}========================================${NC}"
    echo -e "${MAGENTA}  $1${NC}"
    echo -e "${MAGENTA}========================================${NC}"
    echo
}

# Function to display the banner
show_banner() {
    clear
    echo -e "${CYAN}"
    cat << "EOF"
    ____
   / __ \_________ ___________
  / / / / ___/ __ `/ ___/ ___/
 / /_/ / /  / /_/ (__  |__  )
/_____/_/   \__,_/____/____/

EOF
    echo -e "${NC}"
    echo -e "${BOLD}Deployment Configuration System v1.0${NC}"
    echo -e "Intelligent deployment for any environment"
    echo
}

# Function to check command existence
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect Python
detect_python() {
    print_section "Detecting Python Installation"

    # Check for Python 3
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
        MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f2)

        if [ "$MAJOR_VERSION" -eq 3 ] && [ "$MINOR_VERSION" -ge 8 ]; then
            PYTHON_CMD="python3"
            print_success "Found Python $PYTHON_VERSION"
        else
            print_warning "Python $PYTHON_VERSION is too old (need 3.8+)"
            return 1
        fi
    elif command_exists python; then
        PYTHON_VERSION=$(python --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
        MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f2)

        if [ "$MAJOR_VERSION" -eq 3 ] && [ "$MINOR_VERSION" -ge 8 ]; then
            PYTHON_CMD="python"
            print_success "Found Python $PYTHON_VERSION"
        else
            print_warning "Python $PYTHON_VERSION is too old (need 3.8+)"
            return 1
        fi
    else
        print_error "Python 3.8+ is not installed"
        return 1
    fi

    return 0
}

# Function to install Python if needed
install_python() {
    print_warning "Python 3.8+ is required but not found"

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            print_status "Installing Python via Homebrew..."
            brew install python@3.11
            PYTHON_CMD="python3.11"
        else
            print_error "Please install Homebrew first: https://brew.sh"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            print_status "Installing Python via apt..."
            sudo apt-get update
            sudo apt-get install -y python3.11 python3.11-venv python3-pip
            PYTHON_CMD="python3.11"
        elif command_exists yum; then
            print_status "Installing Python via yum..."
            sudo yum install -y python311 python311-pip
            PYTHON_CMD="python3.11"
        else
            print_error "Please install Python 3.8+ manually"
            exit 1
        fi
    else
        print_error "Unsupported OS. Please install Python 3.8+ manually"
        exit 1
    fi
}

# Function to setup virtual environment
setup_venv() {
    print_section "Setting Up Python Environment"

    # Check if venv already exists
    if [ -d "$VENV_DIR" ]; then
        print_status "Virtual environment already exists"

        # Ask if user wants to recreate
        echo -n "Do you want to recreate it? (y/N): "
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            print_status "Removing existing virtual environment..."
            rm -rf "$VENV_DIR"
        else
            print_status "Using existing virtual environment"
            return 0
        fi
    fi

    # Create virtual environment
    print_status "Creating virtual environment..."
    $PYTHON_CMD -m venv "$VENV_DIR"

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip >/dev/null 2>&1

    print_success "Virtual environment created"
}

# Function to install Python dependencies
install_dependencies() {
    print_section "Installing Dependencies"

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Core dependencies for deployment system
    print_status "Installing core dependencies..."
    pip install --quiet \
        rich>=13.0.0 \
        click>=8.1.0 \
        pyyaml>=6.0 \
        pydantic>=2.0.0 \
        pydantic-settings>=2.0.0 \
        psutil>=5.9.0

    # Optional dependencies based on deployment type
    print_status "Installing optional dependencies..."

    # Check if user wants additional features
    echo -n "Install AWS deployment support? (y/N): "
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        pip install --quiet boto3>=1.28.0
        print_success "AWS support installed"
    fi

    echo -n "Install Docker support? (y/N): "
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        pip install --quiet docker>=6.1.0
        print_success "Docker support installed"
    fi

    print_success "All dependencies installed"
}

# Function to run configuration wizard
run_configurator() {
    print_section "Deployment Configuration Wizard"

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Run the configurator (use simple version if main one fails)
    if [ -f "$SCRIPT_DIR/deployment/scripts/configure_simple.py" ]; then
        python "$SCRIPT_DIR/deployment/scripts/configure_simple.py"
    else
        python "$SCRIPT_DIR/deployment/scripts/configure.py"
    fi
}

# Function to run deployment
run_deployment() {
    print_section "Deployment"

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Check for existing configs
    CONFIG_DIR="$SCRIPT_DIR/deployment/configs/user"
    if [ -d "$CONFIG_DIR" ]; then
        CONFIGS=$(find "$CONFIG_DIR" -name "*.yaml" -o -name "*.yml" 2>/dev/null | head -5)

        if [ -n "$CONFIGS" ]; then
            print_status "Found existing configurations:"
            echo

            # List configs with numbers
            i=1
            declare -a CONFIG_ARRAY
            while IFS= read -r config; do
                CONFIG_NAME=$(basename "$config")
                echo "  $i) $CONFIG_NAME"
                CONFIG_ARRAY[$i]="$config"
                ((i++))
            done <<< "$CONFIGS"

            echo "  $i) Use preset configuration"
            echo "  $((i+1))) Create new configuration"
            echo

            echo -n "Select configuration (1-$((i+1))): "
            read -r choice

            if [ "$choice" -eq "$i" ] 2>/dev/null; then
                # Use preset
                use_preset_deployment
            elif [ "$choice" -eq "$((i+1))" ] 2>/dev/null; then
                # Create new
                run_configurator
                run_deployment
            elif [ "$choice" -ge 1 ] && [ "$choice" -lt "$i" ] 2>/dev/null; then
                # Use selected config
                CONFIG_FILE="${CONFIG_ARRAY[$choice]}"
                print_status "Using configuration: $(basename "$CONFIG_FILE")"
                python "$SCRIPT_DIR/deployment/scripts/deploy.py" --config "$CONFIG_FILE"
            else
                print_error "Invalid selection"
                exit 1
            fi
        else
            # No configs found
            echo "No existing configurations found."
            echo
            echo "1) Use preset configuration"
            echo "2) Create new configuration"
            echo
            echo -n "Select option (1-2): "
            read -r choice

            if [ "$choice" -eq 1 ]; then
                use_preset_deployment
            else
                run_configurator
                run_deployment
            fi
        fi
    else
        # First time - create new config
        run_configurator
        run_deployment
    fi
}

# Function to use preset deployment
use_preset_deployment() {
    print_status "Available presets:"
    echo
    echo "  1) dev-macos    - MacOS development (Apple Silicon optimized)"
    echo "  2) docker-local - Docker Compose (local development)"
    echo "  3) aws-prod     - AWS production deployment"
    echo

    echo -n "Select preset (1-3): "
    read -r choice

    case $choice in
        1)
            PRESET="dev-macos"
            ;;
        2)
            PRESET="docker-local"
            ;;
        3)
            PRESET="aws-prod"
            ;;
        *)
            print_error "Invalid selection"
            exit 1
            ;;
    esac

    # Check if preset exists
    PRESET_FILE="$SCRIPT_DIR/deployment/configs/presets/${PRESET}.yaml"
    if [ ! -f "$PRESET_FILE" ]; then
        print_warning "Preset $PRESET not found, creating it..."
        create_missing_preset "$PRESET"
    fi

    print_status "Deploying with preset: $PRESET"
    python "$SCRIPT_DIR/deployment/scripts/deploy.py" --preset "$PRESET"
}

# Function to create missing preset
create_missing_preset() {
    local preset=$1
    local preset_file="$SCRIPT_DIR/deployment/configs/presets/${preset}.yaml"

    case $preset in
        "docker-local")
            cp "$SCRIPT_DIR/deployment/configs/templates/docker-compose.yaml" "$preset_file"
            print_success "Created docker-local preset"
            ;;
        "aws-prod")
            cp "$SCRIPT_DIR/deployment/configs/templates/aws.yaml" "$preset_file"
            print_success "Created aws-prod preset"
            ;;
        *)
            print_error "Unknown preset: $preset"
            exit 1
            ;;
    esac
}

# Function to show management menu
show_management_menu() {
    print_section "Deployment Management"

    echo "1) Check deployment status"
    echo "2) Stop deployment"
    echo "3) View logs"
    echo "4) Clean up"
    echo "5) Exit"
    echo

    echo -n "Select option (1-5): "
    read -r choice

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    case $choice in
        1)
            # Get latest config
            CONFIG=$(find "$SCRIPT_DIR/deployment/configs/user" -name "*.yaml" -o -name "*.yml" 2>/dev/null | head -1)
            if [ -n "$CONFIG" ]; then
                python "$SCRIPT_DIR/deployment/scripts/deploy.py" --config "$CONFIG" --status
            else
                print_warning "No configuration found"
            fi
            ;;
        2)
            CONFIG=$(find "$SCRIPT_DIR/deployment/configs/user" -name "*.yaml" -o -name "*.yml" 2>/dev/null | head -1)
            if [ -n "$CONFIG" ]; then
                python "$SCRIPT_DIR/deployment/scripts/deploy.py" --config "$CONFIG" --stop
            else
                print_warning "No configuration found"
            fi
            ;;
        3)
            if [ -d "$SCRIPT_DIR/logs" ]; then
                tail -f "$SCRIPT_DIR/logs/"*.log
            else
                print_warning "No logs found"
            fi
            ;;
        4)
            cleanup
            ;;
        5)
            exit 0
            ;;
        *)
            print_error "Invalid selection"
            ;;
    esac
}

# Function to cleanup
cleanup() {
    print_section "Cleanup"

    echo "This will remove:"
    echo "  - Virtual environment"
    echo "  - Generated configurations"
    echo "  - Temporary files"
    echo
    echo -n "Are you sure? (y/N): "
    read -r response

    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_status "Cleaning up..."

        # Remove virtual environment
        if [ -d "$VENV_DIR" ]; then
            rm -rf "$VENV_DIR"
            print_success "Removed virtual environment"
        fi

        # Remove generated files
        rm -f "$SCRIPT_DIR"/.env.generated
        rm -f "$SCRIPT_DIR"/docker-compose.generated.yml

        print_success "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Main menu function
show_main_menu() {
    print_section "Main Menu"

    echo "What would you like to do?"
    echo
    echo "1) 🚀 Quick Deploy (use smart defaults)"
    echo "2) ⚙️  Configure & Deploy (interactive setup)"
    echo "3) 📦 Deploy with existing configuration"
    echo "4) 🔧 Manage deployment (status/stop/logs)"
    echo "5) 🧹 Clean up"
    echo "6) ❌ Exit"
    echo

    echo -n "Select option (1-6): "
    read -r choice

    case $choice in
        1)
            quick_deploy
            ;;
        2)
            run_configurator
            run_deployment
            ;;
        3)
            run_deployment
            ;;
        4)
            show_management_menu
            ;;
        5)
            cleanup
            ;;
        6)
            print_status "Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid selection"
            show_main_menu
            ;;
    esac
}

# Quick deploy function
quick_deploy() {
    print_section "Quick Deploy"

    # Detect hardware
    print_status "Detecting hardware..."

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Use Python to detect hardware and select preset
    HARDWARE_INFO=$(python -c "
import platform
import subprocess
import sys

system = platform.system()
machine = platform.machine()

if system == 'Darwin' and 'arm64' in machine.lower():
    print('dev-macos')
elif system == 'Linux':
    # Check for NVIDIA GPU
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, check=False)
        if result.returncode == 0:
            print('local-gpu-nvidia')
        else:
            print('docker-local')
    except:
        print('docker-local')
else:
    print('docker-local')
" 2>/dev/null)

    if [ -z "$HARDWARE_INFO" ]; then
        HARDWARE_INFO="docker-local"
    fi

    print_success "Detected environment: $HARDWARE_INFO"

    # Check if preset exists
    PRESET_FILE="$SCRIPT_DIR/deployment/configs/presets/${HARDWARE_INFO}.yaml"
    if [ ! -f "$PRESET_FILE" ]; then
        # Use docker-local as fallback
        HARDWARE_INFO="docker-local"
        create_missing_preset "$HARDWARE_INFO"
    fi

    print_status "Starting quick deployment with preset: $HARDWARE_INFO"
    python "$SCRIPT_DIR/deployment/scripts/deploy.py" --preset "$HARDWARE_INFO"
}

# Function to check system requirements
check_requirements() {
    print_section "Checking System Requirements"

    local requirements_met=true

    # Check Git
    if command_exists git; then
        print_success "Git is installed"
    else
        print_warning "Git is not installed (optional)"
    fi

    # Check Docker (optional)
    if command_exists docker; then
        print_success "Docker is installed"
    else
        print_warning "Docker is not installed (required for Docker deployment)"
    fi

    # Check Node.js (optional)
    if command_exists node; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        print_success "Node.js $NODE_VERSION is installed"
    else
        print_warning "Node.js is not installed (required for frontend)"
    fi

    # Check disk space
    AVAILABLE_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$AVAILABLE_SPACE" -lt 10 ] 2>/dev/null; then
        print_warning "Low disk space: ${AVAILABLE_SPACE}GB available (recommend 10GB+)"
    else
        print_success "Disk space: ${AVAILABLE_SPACE}GB available"
    fi

    return 0
}

# Main script execution
main() {
    show_banner

    # Check Python installation
    if ! detect_python; then
        install_python
    fi

    # Setup virtual environment
    setup_venv

    # Install dependencies
    install_dependencies

    # Check other requirements
    check_requirements

    # Show main menu
    while true; do
        show_main_menu
        echo
        echo -n "Press Enter to continue..."
        read -r
    done
}

# Handle script arguments
case "${1:-}" in
    quick)
        show_banner
        if ! detect_python; then
            install_python
        fi
        setup_venv
        install_dependencies
        quick_deploy
        ;;
    configure)
        show_banner
        if ! detect_python; then
            install_python
        fi
        setup_venv
        install_dependencies
        run_configurator
        ;;
    deploy)
        show_banner
        if ! detect_python; then
            install_python
        fi
        setup_venv
        install_dependencies
        run_deployment
        ;;
    status|stop|clean)
        if [ ! -d "$VENV_DIR" ]; then
            print_error "Please run './deploy.sh' first to set up the environment"
            exit 1
        fi
        source "$VENV_DIR/bin/activate"

        case "$1" in
            status)
                CONFIG=$(find "$SCRIPT_DIR/deployment/configs/user" -name "*.yaml" -o -name "*.yml" 2>/dev/null | head -1)
                if [ -n "$CONFIG" ]; then
                    python "$SCRIPT_DIR/deployment/scripts/deploy.py" --config "$CONFIG" --status
                else
                    print_warning "No configuration found"
                fi
                ;;
            stop)
                CONFIG=$(find "$SCRIPT_DIR/deployment/configs/user" -name "*.yaml" -o -name "*.yml" 2>/dev/null | head -1)
                if [ -n "$CONFIG" ]; then
                    python "$SCRIPT_DIR/deployment/scripts/deploy.py" --config "$CONFIG" --stop
                else
                    print_warning "No configuration found"
                fi
                ;;
            clean)
                cleanup
                ;;
        esac
        ;;
    help|--help|-h)
        echo "Drass Deployment System"
        echo
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  quick      - Quick deploy with auto-detected settings"
        echo "  configure  - Run configuration wizard"
        echo "  deploy     - Deploy with existing configuration"
        echo "  status     - Check deployment status"
        echo "  stop       - Stop deployment"
        echo "  clean      - Clean up environment"
        echo "  help       - Show this help message"
        echo
        echo "Without arguments, launches interactive menu"
        ;;
    *)
        main
        ;;
esac
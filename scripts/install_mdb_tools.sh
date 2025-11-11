#!/bin/bash
# Install mdb-tools for Microsoft Access database conversion
#
# This script installs the mdb-tools package which provides utilities
# for reading Microsoft Access database files (.mdb format)

set -e

echo "Installing mdb-tools for Microsoft Access database support..."

# Detect the operating system
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        echo "Installing on Debian/Ubuntu..."
        sudo apt-get update
        sudo apt-get install -y mdbtools
    elif command -v yum &> /dev/null; then
        # RHEL/CentOS
        echo "Installing on RHEL/CentOS..."
        sudo yum install -y mdb-tools
    elif command -v dnf &> /dev/null; then
        # Fedora
        echo "Installing on Fedora..."
        sudo dnf install -y mdb-tools
    else
        echo "Unsupported Linux distribution. Please install mdb-tools manually."
        exit 1
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Installing on macOS..."
    if command -v brew &> /dev/null; then
        brew install mdb-tools
    else
        echo "Homebrew not found. Please install Homebrew first:"
        echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
else
    echo "Unsupported operating system: $OSTYPE"
    echo "Please install mdb-tools manually for your system."
    exit 1
fi

# Verify installation
if command -v mdb-ver &> /dev/null; then
    echo "✓ mdb-tools installed successfully!"
    echo "Version: $(mdb-ver)"
else
    echo "✗ mdb-tools installation failed!"
    exit 1
fi
#!/bin/bash

#############################################################################
#  Quantum Lock Judge Demo - Startup Script
#  Runs on Raspberry Pi 3
#  
#  This script starts the FastAPI backend on port 8001
#  Then opens the web UI on port 8000 (or manual browser access)
#############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8001
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Quantum Lock Judge Demonstration - Startup Script          ║${NC}"
echo -e "${BLUE}║   Raspberry Pi 3 Backend Server                              ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    cd "$PROJECT_ROOT"
    python3 -m venv venv
    source venv/bin/activate
    pip install -q fastapi uvicorn requests
else
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Check if backend file exists
if [ ! -f "$SCRIPT_DIR/judge_backend.py" ]; then
    echo -e "${RED}ERROR: judge_backend.py not found at $SCRIPT_DIR${NC}"
    exit 1
fi

# Check if HTML file exists
if [ ! -f "$SCRIPT_DIR/judge_demo_ui.html" ]; then
    echo -e "${RED}ERROR: judge_demo_ui.html not found at $SCRIPT_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All files found${NC}"
echo ""

# Display configuration
echo -e "${BLUE}Configuration:${NC}"
echo "  Backend Port: $BACKEND_PORT"
echo "  Backend Script: $SCRIPT_DIR/judge_backend.py"
echo "  Frontend HTML: $SCRIPT_DIR/judge_demo_ui.html"
echo "  Virtual Env: $PROJECT_ROOT/venv"
echo ""

# Optional: Set judge password
if [ -z "$JUDGE_PASSWORD" ]; then
    echo -e "${YELLOW}Note: Using default password 'quantum2026'${NC}"
    echo "       To set custom password: export JUDGE_PASSWORD='yourpassword'${NC}"
    export JUDGE_PASSWORD="quantum2026"
else
    echo -e "${GREEN}✓ Judge password set from environment${NC}"
fi

echo ""
echo -e "${GREEN}Starting backend server...${NC}"
echo ""

# Start the backend
cd "$SCRIPT_DIR"
python3 judge_backend.py

# If we reach here, backend stopped
echo ""
echo -e "${YELLOW}Backend stopped. Press Ctrl+C to exit.${NC}"

#!/bin/bash

# ============================================
# Isha Return Gifts - Quick Start Script
# Run: bash run.sh
# ============================================

GOLD='\033[0;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${GOLD}🎁 Starting Isha Return Gifts...${NC}"
echo ""

# Activate venv
if [ -d "venv" ]; then
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
else
    echo -e "\033[0;31m❌ venv not found. Run: bash setup_project.sh first${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🌐 Website:      ${NC}http://127.0.0.1:8000/"
echo -e "${GREEN}🎛️  Dashboard:    ${NC}http://127.0.0.1:8000/dashboard/"
echo -e "${GREEN}⚙️  Django Admin: ${NC}http://127.0.0.1:8000/admin/"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
echo ""

python manage.py runserver

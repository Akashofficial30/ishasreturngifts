#!/bin/bash
set -e
GREEN='\033[0;32m'; GOLD='\033[0;33m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'

echo ""
echo -e "${GOLD}╔═════════════════════════════════════════╗${NC}"
echo -e "${GOLD}║   🎁 Isha's Return Gifts - Setup        ║${NC}"
echo -e "${GOLD}╚═════════════════════════════════════════╝${NC}"
echo ""

# Python check
if command -v python3 &>/dev/null; then PYTHON=python3; else echo -e "${RED}❌ Python not found${NC}"; exit 1; fi
echo -e "${GREEN}✅ $(python3 --version)${NC}"

# venv
if [ ! -d "venv" ]; then $PYTHON -m venv venv; echo -e "${GREEN}✅ venv created${NC}"; else echo -e "${GOLD}⚠️  venv exists${NC}"; fi
source venv/bin/activate
echo -e "${GREEN}✅ venv activated${NC}"

# Install
pip install --upgrade pip --quiet
pip install -r requirements.txt
echo -e "${GREEN}✅ Packages installed${NC}"

# Migrations
echo ""
echo -e "${BLUE}Running migrations...${NC}"
python manage.py makemigrations products 2>/dev/null || true
python manage.py makemigrations orders 2>/dev/null || true
python manage.py makemigrations payments 2>/dev/null || true
python manage.py makemigrations users 2>/dev/null || true
python manage.py makemigrations contact 2>/dev/null || true
python manage.py makemigrations 2>/dev/null || true
python manage.py migrate
echo -e "${GREEN}✅ Database ready${NC}"

# Seed
python setup.py

echo ""
echo -e "${GOLD}╔═════════════════════════════════════════╗${NC}"
echo -e "${GOLD}║           ✅ Setup Complete!             ║${NC}"
echo -e "${GOLD}╚═════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${GREEN}Website:    ${NC}http://127.0.0.1:8000/"
echo -e "  ${GREEN}Contact:    ${NC}http://127.0.0.1:8000/contact/"
echo -e "  ${GREEN}Dashboard:  ${NC}http://127.0.0.1:8000/dashboard/"
echo -e "  ${GOLD}Login: admin / admin@12345${NC}"
echo ""
echo -e "${BLUE}▶ Next time: source venv/bin/activate && python manage.py runserver${NC}"

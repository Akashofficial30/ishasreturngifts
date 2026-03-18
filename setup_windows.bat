@echo off
REM ============================================
REM Isha Return Gifts - Windows Setup Script
REM Run: setup_windows.bat
REM ============================================

echo.
echo ============================================
echo   🎁 Isha Return Gifts - Setup Script
echo ============================================
echo.

REM Step 1: Check Python
echo [1/7] Checking Python...
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ERROR: Python not found. Install from python.org
    pause
    exit /b 1
)
python --version
echo.

REM Step 2: Create venv
echo [2/7] Creating virtual environment...
IF EXIST venv (
    echo venv already exists. Skipping.
) ELSE (
    python -m venv venv
    echo Virtual environment created.
)
echo.

REM Step 3: Activate venv
echo [3/7] Activating virtual environment...
call venv\Scripts\activate.bat
echo Activated: %VIRTUAL_ENV%
echo.

REM Step 4: Upgrade pip
echo [4/7] Upgrading pip...
pip install --upgrade pip --quiet
echo.

REM Step 5: Install packages
echo [5/7] Installing dependencies...
pip install -r requirements.txt
echo.

REM Step 6: Migrations
echo [6/7] Running migrations...
python manage.py makemigrations products
python manage.py makemigrations orders
python manage.py makemigrations payments
python manage.py makemigrations users
python manage.py migrate
echo.

REM Step 7: Seed data
echo [7/7] Seeding sample data...
python setup.py
echo.

echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo  Website:      http://127.0.0.1:8000/
echo  Admin Panel:  http://127.0.0.1:8000/dashboard/
echo  Django Admin: http://127.0.0.1:8000/admin/
echo.
echo  Login: admin / admin@12345
echo.
echo  To start the server:
echo    venv\Scripts\activate
echo    python manage.py runserver
echo.
pause

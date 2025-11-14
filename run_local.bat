@echo off
REM Snowflake Well-Architected Framework Review - Local Runner (Windows)

echo ❄️  Snowflake Well-Architected Framework Review - Local Setup
echo ==============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python found
python --version
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
    echo.
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo 📦 Installing dependencies...
pip install -q -r requirements-local.txt
echo ✅ Dependencies installed
echo.

REM Check if secrets file exists
if not exist ".streamlit\secrets.toml" (
    echo ⚠️  WARNING: Secrets file not found!
    echo.
    echo Creating .streamlit directory and template...
    
    if not exist ".streamlit\" mkdir .streamlit
    
    if exist ".streamlit\secrets.toml.template" (
        copy .streamlit\secrets.toml.template .streamlit\secrets.toml >nul
        echo ✅ Created secrets.toml from template
    ) else (
        REM Create basic template
        (
            echo [snowflake]
            echo account = "your_account_identifier"
            echo user = "your_username"
            echo password = "your_password"
            echo role = "ACCOUNTADMIN"
            echo warehouse = "COMPUTE_WH"
        ) > .streamlit\secrets.toml
        echo ✅ Created basic secrets.toml template
    )
    
    echo.
    echo 📝 IMPORTANT: Edit .streamlit\secrets.toml with your Snowflake credentials!
    echo.
    echo Example:
    echo   account = "xy12345.us-east-1"
    echo   user = "john.doe@company.com"
    echo   password = "YourPassword123!"
    echo   role = "ACCOUNTADMIN"
    echo   warehouse = "COMPUTE_WH"
    echo.
    pause
)

REM Check if secrets are configured
findstr /C:"your_account_identifier" .streamlit\secrets.toml >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  WARNING: secrets.toml still has default values!
    echo Please update .streamlit\secrets.toml with your actual Snowflake credentials.
    echo.
    pause
)

REM Run Streamlit
echo.
echo 🚀 Starting Streamlit application...
echo 📊 Opening browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo ==============================================================
echo.

streamlit run app_local.py


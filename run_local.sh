#!/bin/bash

# Snowflake Well-Architected Framework Review - Local Runner
# This script helps you run the application locally

echo "❄️  Snowflake Well-Architected Framework Review - Local Setup"
echo "=============================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements-local.txt
echo "✅ Dependencies installed"
echo ""

# Check if secrets file exists
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "⚠️  WARNING: Secrets file not found!"
    echo ""
    echo "Creating .streamlit directory and template..."
    mkdir -p .streamlit
    
    if [ -f ".streamlit/secrets.toml.template" ]; then
        cp .streamlit/secrets.toml.template .streamlit/secrets.toml
        echo "✅ Created secrets.toml from template"
    else
        # Create basic template
        cat > .streamlit/secrets.toml << 'EOF'
[snowflake]
account = "your_account_identifier"
user = "your_username"
password = "your_password"
role = "ACCOUNTADMIN"
warehouse = "COMPUTE_WH"
EOF
        echo "✅ Created basic secrets.toml template"
    fi
    
    echo ""
    echo "📝 IMPORTANT: Edit .streamlit/secrets.toml with your Snowflake credentials before running!"
    echo ""
    echo "Example:"
    echo "  account = \"xy12345.us-east-1\""
    echo "  user = \"john.doe@company.com\""
    echo "  password = \"YourPassword123!\""
    echo "  role = \"ACCOUNTADMIN\""
    echo "  warehouse = \"COMPUTE_WH\""
    echo ""
    read -p "Press Enter after updating secrets.toml to continue..."
fi

# Check if secrets are configured (basic check)
if grep -q "your_account_identifier" .streamlit/secrets.toml; then
    echo "⚠️  WARNING: It looks like secrets.toml still has default values!"
    echo "Please update .streamlit/secrets.toml with your actual Snowflake credentials."
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
fi

# Run Streamlit
echo ""
echo "🚀 Starting Streamlit application..."
echo "📊 Opening browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo "=============================================================="
echo ""

streamlit run app_local.py


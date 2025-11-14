# Running Locally - Snowflake Well-Architected Framework Review

This guide explains how to run the Streamlit application locally on your machine.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Snowflake account with `ACCOUNTADMIN` role or access to `ACCOUNT_USAGE` views
- pip (Python package manager)

### Step 1: Clone or Download the Repository

```bash
cd snowflake-readiness-review
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements-local.txt
```

This will install:
- `streamlit` - Web framework
- `pandas` - Data manipulation
- `plotly` - Interactive visualizations
- `snowflake-connector-python` - Snowflake connection

### Step 4: Configure Snowflake Connection

Create a secrets file for your Snowflake credentials:

```bash
# Create the .streamlit directory if it doesn't exist
mkdir -p .streamlit

# Copy the template
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` with your credentials:

```toml
[snowflake]
account = "your_account_identifier"  # e.g., "xy12345.us-east-1"
user = "your_username"
password = "your_password"
role = "ACCOUNTADMIN"
warehouse = "COMPUTE_WH"
```

**⚠️ IMPORTANT**: Never commit `secrets.toml` to version control! It's already in `.gitignore`.

### Step 5: Run the Application

```bash
streamlit run app_local.py
```

The application will open in your default browser at `http://localhost:8501`

## 🔧 Configuration Options

### Connection Parameters

The application requires these Snowflake connection parameters:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `account` | Snowflake account identifier | `xy12345.us-east-1` or `orgname-accountname` |
| `user` | Snowflake username | `john.doe@company.com` |
| `password` | User password | `YourSecurePassword123!` |
| `role` | Role with ACCOUNT_USAGE access | `ACCOUNTADMIN` or `CUSTOM_ROLE` |
| `warehouse` | Compute warehouse to use | `COMPUTE_WH` |

### Finding Your Account Identifier

```sql
-- Run this in Snowflake to get your account identifier
SELECT CURRENT_ACCOUNT();
```

For the full account locator format, check your Snowflake URL:
- Old format: `https://xy12345.snowflakecomputing.com` → Account: `xy12345`
- New format: `https://orgname-accountname.snowflakecomputing.com` → Account: `orgname-accountname`

### Using SSO/MFA

If your organization uses SSO or MFA, add this to your `secrets.toml`:

```toml
[snowflake]
account = "your_account"
user = "your_username"
authenticator = "externalbrowser"
role = "ACCOUNTADMIN"
warehouse = "COMPUTE_WH"
```

Then remove the `password` line. The browser will open for authentication.

## 📋 Required Permissions

Your Snowflake role needs access to these views:

```sql
-- Grant access to ACCOUNT_USAGE
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE YOUR_ROLE;

-- Or if using ACCOUNTADMIN
USE ROLE ACCOUNTADMIN;
```

## 🐛 Troubleshooting

### Error: "Missing configuration in secrets.toml"

**Solution**: Ensure `.streamlit/secrets.toml` exists and contains all required fields.

```bash
# Check if file exists
ls -la .streamlit/

# Verify contents
cat .streamlit/secrets.toml
```

### Error: "Unable to connect to Snowflake"

**Solutions**:

1. **Verify credentials** - Test in SnowSQL or Snowflake Web UI
2. **Check account identifier** - Make sure format is correct
3. **Network/Firewall** - Ensure ports 443 and 80 are open
4. **Role permissions** - Verify role has ACCOUNT_USAGE access

```sql
-- Test in Snowflake
SHOW GRANTS TO ROLE YOUR_ROLE;
```

### Error: "No data available"

**Solutions**:

1. **ACCOUNT_USAGE latency** - Views have 45 min - 3 hours delay
2. **Increase time range** - Try 30 or 60 days in the slider
3. **Empty account** - Run some queries first to generate data

### Connection Timeout

Add timeout settings to `secrets.toml`:

```toml
[snowflake]
account = "your_account"
user = "your_username"
password = "your_password"
role = "ACCOUNTADMIN"
warehouse = "COMPUTE_WH"
login_timeout = 30
network_timeout = 60
```

## 🔄 Differences from Snowflake-Native Version

| Feature | Local (`app_local.py`) | Snowflake Native (`app.py`) |
|---------|------------------------|------------------------------|
| **Connection** | snowflake-connector-python | Snowpark Session |
| **Authentication** | Manual credentials | Automatic (session-based) |
| **Deployment** | Local machine | Snowflake account |
| **Updates** | Manual restart | Automatic |
| **Security** | Credentials in secrets file | No credentials needed |

**Note**: The local version (`app_local.py`) is a lightweight demo. For full functionality with all metrics and visualizations, use the Snowflake-native version (`app.py`).

## 📦 Updating the Application

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements-local.txt --upgrade

# Restart Streamlit
streamlit run app_local.py
```

## 🔒 Security Best Practices

1. **Never commit secrets.toml** - Already in `.gitignore`
2. **Use strong passwords** - Or preferably SSO
3. **Rotate credentials regularly** - Change passwords periodically
4. **Limit role permissions** - Use least-privilege principle
5. **Use environment variables** - For CI/CD environments

### Using Environment Variables (Alternative)

Instead of `secrets.toml`, set environment variables:

```bash
export SNOWFLAKE_ACCOUNT="your_account"
export SNOWFLAKE_USER="your_user"
export SNOWFLAKE_PASSWORD="your_password"
export SNOWFLAKE_ROLE="ACCOUNTADMIN"
export SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
```

Then modify the connection code to read from environment variables.

## 📊 Performance Tips

1. **Use appropriate warehouse** - XSMALL is usually sufficient
2. **Limit time range** - Start with 7-30 days
3. **Cache results** - Streamlit caches connection and queries
4. **Close unused tabs** - Browser performance

## 🆘 Getting Help

- **Snowflake Documentation**: https://docs.snowflake.com
- **Streamlit Documentation**: https://docs.streamlit.io
- **Well-Architected Framework**: https://www.snowflake.com/en/developers/guides/well-architected-framework/

## 📝 Next Steps

Once you've tested locally, consider:

1. **Deploy to Snowflake** - Use `app.py` for native Streamlit in Snowflake
2. **Customize queries** - Add organization-specific metrics
3. **Schedule reviews** - Run weekly or monthly
4. **Share insights** - Export screenshots or create reports

---

**Happy Analyzing!** ❄️


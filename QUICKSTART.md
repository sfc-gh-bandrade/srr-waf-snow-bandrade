# Quick Start Guide

This guide will help you deploy the Snowflake Well-Architected Framework Review application in minutes.

## Prerequisites

- Snowflake account with `ACCOUNTADMIN` role or equivalent privileges
- SnowSQL installed (for command-line deployment) OR access to Snowflake Web UI

## Option A: Deploy Using Snowflake Web UI (Easiest)

### Step 1: Create a Streamlit App in Snowsight

1. Log into your Snowflake account via Snowsight (Web UI)
2. Navigate to **Streamlit** in the left sidebar
3. Click **+ Streamlit App**
4. Configure:
   - **App name**: `snowflake_waf_review`
   - **Warehouse**: Select or create a warehouse (recommend XSMALL with auto-suspend)
   - **App location**: Choose a database and schema

### Step 2: Upload the Code

1. In the Streamlit editor, delete the default code
2. Copy and paste the entire contents of `app.py` from this repository
3. Click **Run** to deploy the app

### Step 3: Verify Access

The app will automatically use the current session, which should have access to `ACCOUNT_USAGE` if you're using `ACCOUNTADMIN`.

**Done!** Your app should now be running.

---

## Option B: Deploy Using SnowSQL (Advanced)

### Step 1: Prepare Your Environment

```bash
# Clone or download this repository
cd snowflake-readiness-review

# Verify files
ls -la
# You should see: app.py, requirements.txt, deploy.sql
```

### Step 2: Connect to Snowflake

```bash
snowsql -a <your_account> -u <your_username>
```

### Step 3: Run Deployment Script

```sql
-- Update the placeholders in deploy.sql first
USE ROLE ACCOUNTADMIN;
USE DATABASE your_database;
USE SCHEMA your_schema;

-- Create stage
CREATE STAGE IF NOT EXISTS streamlit_stage
    DIRECTORY = (ENABLE = TRUE);

-- Create warehouse
CREATE WAREHOUSE IF NOT EXISTS streamlit_wh
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;
```

### Step 4: Upload Files

```bash
# From your local terminal
snowsql -a <account> -u <username> -q "PUT file://$(pwd)/app.py @your_database.your_schema.streamlit_stage/waf_review/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
```

### Step 5: Create the Streamlit App

```sql
CREATE OR REPLACE STREAMLIT snowflake_waf_review
    ROOT_LOCATION = '@streamlit_stage/waf_review'
    MAIN_FILE = 'app.py'
    QUERY_WAREHOUSE = streamlit_wh;
```

### Step 6: Open the App

```sql
-- Get the app URL
SELECT SYSTEM$GET_STREAMLIT_URL('snowflake_waf_review');
```

Open the returned URL in your browser.

---

## Option C: Run Locally (For Development)

### Step 1: Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Configure Connection

```bash
# Create secrets directory
mkdir -p .streamlit

# Copy template and edit
cp .streamlit/secrets.toml.template .streamlit/secrets.toml

# Edit .streamlit/secrets.toml with your credentials
nano .streamlit/secrets.toml
```

**Example secrets.toml:**

```toml
[connections.snowflake]
account = "xy12345.us-east-1"
user = "john_doe"
password = "your_password"
role = "ACCOUNTADMIN"
warehouse = "COMPUTE_WH"
```

### Step 3: Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## Troubleshooting

### ❌ "Unable to connect to Snowflake"

**Solution**: Verify your credentials in `.streamlit/secrets.toml` or ensure you're running in Snowflake Streamlit with proper permissions.

### ❌ "Error fetching data from ACCOUNT_USAGE"

**Solutions**:
1. Grant imported privileges: `GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE ACCOUNTADMIN;`
2. Wait 45 minutes after first queries (ACCOUNT_USAGE has latency)
3. Ensure your role has access to the SNOWFLAKE database

### ❌ "No data available"

**Solutions**:
1. Increase the analysis period using the slider (ACCOUNT_USAGE may not have recent data)
2. Check if the account has been actively used
3. Verify that queries have been executed in the time period selected

### ❌ "PUT command failed"

**Solution**: Ensure you have write access to the stage and the file path is correct. Use absolute paths.

---

## Next Steps

Once deployed:

1. **Explore the Tabs**: Navigate through all 5 pillars to understand your account health
2. **Adjust Time Range**: Use the sidebar slider to analyze different time periods
3. **Review Recommendations**: Pay attention to warning and critical alerts
4. **Export Insights**: Take screenshots or export data tables for reporting
5. **Schedule Regular Reviews**: Run this analysis monthly or quarterly

---

## Security Best Practices

- ✅ **Never commit** `.streamlit/secrets.toml` to version control
- ✅ **Use least privilege**: Create a dedicated role instead of ACCOUNTADMIN for production use
- ✅ **Rotate credentials**: Change passwords regularly
- ✅ **Enable MFA**: Enforce multi-factor authentication for all users
- ✅ **Audit access**: Monitor who accesses the Streamlit app

---

## Getting Help

- 📖 [Snowflake Well-Architected Framework](https://www.snowflake.com/en/developers/guides/well-architected-framework/)
- 📖 [Snowflake ACCOUNT_USAGE Views](https://docs.snowflake.com/en/sql-reference/account-usage.html)
- 📖 [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)

---

**Happy Analyzing!** ❄️


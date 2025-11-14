# Quick Start Guide - Local Version

## 🎯 Choose Your Deployment

### Option A: Local Development (This Guide)
**Use this if you want to:**
- ✅ Run on your local machine
- ✅ Test before deploying to Snowflake
- ✅ Have full control over the environment
- ✅ Develop and customize locally

### Option B: Snowflake Native (See QUICKSTART.md)
**Use this if you want to:**
- ✅ Run directly in Snowflake
- ✅ Share with team easily
- ✅ No local setup required
- ✅ Automatic authentication

---

## 🚀 Quick Start - 3 Steps

### 1️⃣ Install Dependencies

**macOS/Linux:**
```bash
./run_local.sh
```

**Windows:**
```bash
run_local.bat
```

**Or manually:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements-local.txt
```

### 2️⃣ Configure Connection

Create `.streamlit/secrets.toml`:

```toml
[snowflake]
account = "xy12345.us-east-1"
user = "your.email@company.com"
password = "YourPassword123!"
role = "ACCOUNTADMIN"
warehouse = "COMPUTE_WH"
```

### 3️⃣ Run the App

```bash
streamlit run app_local.py
```

Opens at: http://localhost:8501

---

## 🔑 Finding Your Account Identifier

### Method 1: From Snowflake URL
- **Old format**: `https://xy12345.snowflakecomputing.com` → Use: `xy12345`
- **New format**: `https://orgname-accountname.snowflakecomputing.com` → Use: `orgname-accountname`

### Method 2: Query Snowflake
```sql
SELECT CURRENT_ACCOUNT();
-- Result: XY12345

-- With region
SELECT CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME();
-- Result: orgname-accountname
```

---

## 🔒 Using SSO/MFA

If your organization uses SSO, update `secrets.toml`:

```toml
[snowflake]
account = "orgname-accountname"
user = "your.email@company.com"
authenticator = "externalbrowser"  # This line enables SSO
role = "ACCOUNTADMIN"
warehouse = "COMPUTE_WH"
# No password needed!
```

When you run the app, your browser will open for authentication.

---

## ⚡ One-Command Setup

### macOS/Linux
```bash
curl -o- https://raw.githubusercontent.com/your-repo/install.sh | bash
```

### Using Docker (Coming Soon)
```bash
docker run -p 8501:8501 \
  -e SNOWFLAKE_ACCOUNT=xy12345 \
  -e SNOWFLAKE_USER=user@company.com \
  -e SNOWFLAKE_PASSWORD=pass \
  snowflake-waf-review:latest
```

---

## 🐛 Common Issues

### Issue 1: "Module not found: snowflake"
```bash
# Solution: Install dependencies
pip install -r requirements-local.txt
```

### Issue 2: "Unable to connect to Snowflake"
```bash
# Solution: Check your credentials
# Test connection:
python3 -c "
import snowflake.connector
conn = snowflake.connector.connect(
    account='xy12345',
    user='user@company.com',
    password='password',
    role='ACCOUNTADMIN',
    warehouse='COMPUTE_WH'
)
print('✅ Connection successful!')
print(f'Current role: {conn.cursor().execute(\"SELECT CURRENT_ROLE()\").fetchone()[0]}')
conn.close()
"
```

### Issue 3: "Permission denied: run_local.sh"
```bash
# Solution: Make script executable
chmod +x run_local.sh
./run_local.sh
```

### Issue 4: "No data available"
- Wait 45-180 minutes after first use (ACCOUNT_USAGE latency)
- Increase time range slider to 30-60 days
- Verify role has ACCOUNT_USAGE access:
  ```sql
  SHOW GRANTS TO ROLE YOUR_ROLE;
  ```

---

## 📊 What's Included

The local version (`app_local.py`) includes:

✅ **Performance Tab**
- Warehouse utilization demo
- Query performance examples

⚠️ **Limited Functionality**
- This is a lightweight demo version
- Full app available in `app.py` (for Snowflake deployment)

### Full Features (app.py):
- 🚀 Performance: 4 detailed analyses
- 🛡️ Reliability: 5 comprehensive checks
- ⚙️ Operational Excellence: 4 governance reviews
- 🔒 Security & Governance: 5 security audits
- 💰 Cost Optimization: 5 cost analyses

---

## 🔄 Development Workflow

### 1. Edit Code
```bash
# Edit app_local.py in your favorite editor
code app_local.py
```

### 2. Test Locally
```bash
streamlit run app_local.py
```

### 3. Deploy to Snowflake
```bash
# Upload to Snowflake stage
snowsql -q "PUT file://app.py @my_stage AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"

# Create/Update Streamlit app
snowsql -q "CREATE OR REPLACE STREAMLIT my_app ROOT_LOCATION='@my_stage' MAIN_FILE='app.py';"
```

---

## 📈 Performance Tips

1. **Use XSMALL warehouse** - Sufficient for most analyses
2. **Start with 7-30 days** - Reduce initial load time
3. **Cache enabled** - Results cached automatically
4. **Close unused tabs** - Frees browser memory

---

## 🆘 Need Help?

### Documentation
- 📖 [Full README](README.md)
- 📖 [Local Setup Guide](README_LOCAL.md)
- 📖 [Snowflake Docs](https://docs.snowflake.com)
- 📖 [Streamlit Docs](https://docs.streamlit.io)

### Support
- 💬 Open an issue on GitHub
- 📧 Contact your Snowflake SE
- 🌐 [Snowflake Community](https://community.snowflake.com)

---

## ✨ Next Steps

1. ✅ Test locally (you are here!)
2. 📝 Customize queries for your organization
3. 🚀 Deploy to Snowflake for team access
4. 📊 Schedule regular reviews (weekly/monthly)
5. 📤 Share insights with stakeholders

---

**Happy Analyzing!** ❄️

*Want the full-featured version? Deploy `app.py` to Snowflake Streamlit!*


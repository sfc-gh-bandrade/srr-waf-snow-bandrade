# Testing Snowflake Connection

This document explains how to test your Snowflake connection before running the main Streamlit application.

## Prerequisites

1. **Secrets File**: Ensure `.streamlit/secrets.toml` is configured with your Snowflake credentials
2. **Python Packages**: Install required dependencies

## Available Test Scripts

We provide two test scripts with different approaches:

### 1. `test_connection_snowpark.py` (Recommended)

Uses **Snowpark** - the same library used by the main Streamlit app.

**Usage:**

```bash
python test_connection_snowpark.py
```

**Advantages:**
- Uses the same connection method as the main app
- Tests Pandas conversion (used by the app)
- More comprehensive testing
- Better error messages

### 2. `test_connection.py`

Uses **snowflake-connector-python** - the base Snowflake connector.

**Usage:**

```bash
python test_connection.py
```

**Advantages:**
- Lighter weight
- Faster execution
- Good for basic connectivity tests

## Installation

### Option 1: Install all dependencies

```bash
pip install -r requirements-local.txt
```

### Option 2: Install only test script dependencies

For Snowpark version (recommended):
```bash
pip install snowflake-snowpark-python toml
```

For connector version:
```bash
pip install snowflake-connector-python toml
```

## Configuration

Ensure your `.streamlit/secrets.toml` file is properly configured:

```toml
[snowflake]
account = "xy12345.us-east-1"  # Your Snowflake account
user = "your_username"
password = "your_password"
role = "ACCOUNTADMIN"  # Or role with ACCOUNT_USAGE access
warehouse = "COMPUTE_WH"

# Optional
# database = "your_database"
# schema = "your_schema"
# authenticator = "externalbrowser"  # For SSO
```

## What the Tests Check

Both scripts perform comprehensive tests:

### ✅ Connection Tests
1. **Account connectivity** - Verifies you can connect to Snowflake
2. **Authentication** - Confirms credentials are valid
3. **Current context** - Shows your account, user, role, warehouse, region

### ✅ Permission Tests
4. **ACCOUNT_USAGE access** - Critical for the app to function
5. **Warehouse access** - Confirms you can use the specified warehouse
6. **Query execution** - Tests ability to run queries

### ✅ Data Access Tests
7. **Database access** - Lists available databases
8. **User information** - Shows user and MFA statistics
9. **Query history** - Counts recent queries (tests ACCOUNT_USAGE)

### ✅ Technical Tests (Snowpark version only)
10. **Pandas conversion** - Tests DataFrame operations
11. **Data operations** - Verifies computation capabilities

## Expected Output

### Successful Connection

```
======================================================================
🔗 SNOWFLAKE CONNECTION TEST (Snowpark)
======================================================================

📋 Configuration:
  Account:   xy12345.us-east-1
  User:      your_username
  Role:      ACCOUNTADMIN
  Warehouse: COMPUTE_WH
  Password:  ******** (configured)

----------------------------------------------------------------------

🔄 Attempting to connect to Snowflake using Snowpark...
✅ Snowpark session created successfully!

----------------------------------------------------------------------

🧪 Running test queries...

1️⃣  Testing current context...
   ✅ Account: XY12345
   ✅ User: YOUR_USERNAME
   ✅ Role: ACCOUNTADMIN
   ✅ Warehouse: COMPUTE_WH
   ✅ Region: AWS_US_EAST_1

2️⃣  Checking warehouse status...
   ✅ Warehouse: COMPUTE_WH
   ✅ Status: STARTED
   ✅ Size: XSMALL
   ✅ Type: STANDARD

... (more tests) ...

======================================================================
✅ ALL TESTS PASSED!
======================================================================

🎉 Your Snowflake connection is working correctly with Snowpark!
   You can now run the Streamlit application.
```

### Failed Connection

The scripts provide detailed error messages and troubleshooting guidance:

```
❌ Error: Incorrect username or password was specified.

🔍 Troubleshooting:
  - Check your username and password in .streamlit/secrets.toml
```

## Common Issues and Solutions

### ❌ "Incorrect username or password"
**Solution:** Verify credentials in `.streamlit/secrets.toml`

### ❌ "Account name is incorrect"
**Solution:** Check account format. Should be:
- `account_name.region` (e.g., `xy12345.us-east-1`)
- `orgname-accountname` (e.g., `myorg-myaccount`)

### ❌ "Role does not exist"
**Solution:** 
- Verify the role name is correct
- Ensure the role is granted to your user
- Try using `ACCOUNTADMIN` if you have access

### ❌ "Warehouse does not exist"
**Solution:**
- Check warehouse name spelling
- Verify the warehouse exists: `SHOW WAREHOUSES;`
- Ensure your role has USAGE privilege on the warehouse

### ❌ "Cannot access ACCOUNT_USAGE"
**Solution:**
- Use `ACCOUNTADMIN` role, OR
- Grant imported privileges:
  ```sql
  GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE your_role;
  ```

### ❌ "No module named 'toml'"
**Solution:**
```bash
pip install toml
```

### ❌ "No module named 'snowflake'"
**Solution:**
```bash
pip install snowflake-snowpark-python
# or
pip install snowflake-connector-python
```

## Running with Virtual Environment

If you're using a virtual environment (recommended):

```bash
# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements-local.txt

# Run test
python test_connection_snowpark.py

# Deactivate when done
deactivate
```

## Next Steps

After successful connection test:

1. ✅ **Connection confirmed** - All tests passed
2. 🚀 **Run the app** - Use `streamlit run app_local.py`
3. 📊 **Explore insights** - Navigate through the Well-Architected Framework tabs

## Troubleshooting Tips

1. **Check network connectivity**
   ```bash
   ping your-account.snowflakecomputing.com
   ```

2. **Test with SnowSQL** (if installed)
   ```bash
   snowsql -a your_account -u your_user
   ```

3. **Verify account status**
   - Ensure your Snowflake account is active
   - Check for any account-level issues in Snowflake UI

4. **Check firewall/proxy**
   - Snowflake requires HTTPS (port 443) access
   - Some corporate networks may block Snowflake connections

## Support

If you continue to have connection issues:

1. Check [Snowflake Documentation](https://docs.snowflake.com/en/user-guide/python-connector-install.html)
2. Verify [Network Connectivity](https://docs.snowflake.com/en/user-guide/network-policies.html)
3. Contact your Snowflake administrator
4. Open an issue in this repository

---

**Last Updated:** January 11, 2026


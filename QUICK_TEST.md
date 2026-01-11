# Quick Connection Test

## 🚀 Quick Start

Test your Snowflake connection in 3 steps:

### 1. Install Dependencies

```bash
pip install snowflake-snowpark-python toml
```

### 2. Configure Secrets

Edit `.streamlit/secrets.toml`:

```toml
[snowflake]
account = "your-account.region"
user = "your_username"
password = "your_password"
role = "ACCOUNTADMIN"
warehouse = "COMPUTE_WH"
```

### 3. Run Test

```bash
python test_connection_snowpark.py
```

## ✅ Success Output

```
======================================================================
✅ ALL TESTS PASSED!
======================================================================

🎉 Your Snowflake connection is working correctly with Snowpark!
   You can now run the Streamlit application.
```

## 🚀 Next: Run the App

```bash
streamlit run app_local.py
```

## 📚 Need Help?

See [TEST_CONNECTION.md](TEST_CONNECTION.md) for detailed troubleshooting.

---

**Quick Tip:** If you see `❌ Missing required package`, run:
```bash
pip install -r requirements-local.txt
```


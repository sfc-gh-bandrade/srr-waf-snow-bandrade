# Project Structure

Complete overview of the Snowflake Well-Architected Framework Review application.

## 📁 Directory Structure

```
snowflake-readiness-review/
│
├── app.py                      # Main Streamlit application (PRIMARY FILE)
├── requirements.txt            # Python dependencies
├── deploy.sql                  # Snowflake deployment script
├── .gitignore                  # Git ignore rules
│
├── .streamlit/
│   └── secrets.toml.template  # Configuration template for local dev
│
├── README.md                   # Project overview and setup
├── QUICKSTART.md              # Quick deployment guide
├── ARCHITECTURE.md            # Technical architecture documentation
├── METRICS.md                 # Complete metrics reference
├── CHANGELOG.md               # Version history
└── PROJECT_STRUCTURE.md       # This file
```

---

## 📄 File Descriptions

### Core Application Files

#### `app.py` (Primary Application)
**Size**: ~1000 lines  
**Purpose**: Complete Streamlit application with all 5 pillars

**Structure**:
```python
# Imports and configuration
import streamlit as st
import pandas as pd
import plotly
from snowflake.snowpark import Session

# Page configuration
st.set_page_config(...)

# Session management
@st.cache_resource
def get_snowflake_session()

# UI Layout
- Sidebar (date range selector)
- Tab navigation (5 pillars)

# Tab 1: Performance (Lines ~100-400)
- Warehouse utilization
- Query performance
- Clustering analysis
- Cache hit rate

# Tab 2: Reliability (Lines ~400-550)
- Replication status
- Query failures
- Pipeline reliability
- Task reliability

# Tab 3: Operational Excellence (Lines ~550-700)
- Resource monitors
- Warehouse configuration
- Long-running queries
- Query patterns

# Tab 4: Security & Governance (Lines ~700-850)
- MFA adoption
- Network policies
- Privileged access
- Data masking
- Failed logins

# Tab 5: Cost Optimization (Lines ~850-1000)
- Credit usage
- Warehouse costs
- Storage analysis
- Idle warehouses
- Storage optimization
```

**Key Features**:
- ✅ 5 tabs covering all WAF pillars
- ✅ 25+ SQL queries against ACCOUNT_USAGE
- ✅ 30+ visualizations using Plotly
- ✅ Automated threshold checking
- ✅ Color-coded alerts (success/warning/critical)
- ✅ Configurable date range (7-90 days)

---

#### `requirements.txt`
**Purpose**: Python package dependencies

```
snowflake-snowpark-python>=1.11.1  # Snowflake connector
streamlit>=1.28.0                   # Web framework
pandas>=2.0.0                       # Data manipulation
plotly>=5.17.0                      # Visualizations
```

**Installation**:
```bash
pip install -r requirements.txt
```

---

#### `deploy.sql`
**Purpose**: SQL script for deploying to Snowflake

**Contents**:
- Database/schema setup
- Stage creation
- Warehouse creation
- Streamlit app deployment
- Permission grants
- Optional: Role creation
- Cleanup script (commented)

**Usage**:
```sql
-- Update placeholders first
USE ROLE ACCOUNTADMIN;
USE DATABASE your_database;
USE SCHEMA your_schema;

-- Then run the script
```

---

### Documentation Files

#### `README.md`
**Sections**:
1. Overview
2. Features by pillar
3. Prerequisites
4. Installation (Snowflake & Local)
5. Required permissions
6. Usage instructions
7. Key metrics & recommendations
8. Troubleshooting
9. Customization
10. Contributing
11. License

**Target Audience**: All users (developers, admins, solution engineers)

---

#### `QUICKSTART.md`
**Sections**:
1. Prerequisites
2. Option A: Snowflake Web UI (easiest)
3. Option B: SnowSQL deployment
4. Option C: Local development
5. Troubleshooting
6. Next steps
7. Security best practices

**Target Audience**: Users wanting rapid deployment

---

#### `ARCHITECTURE.md`
**Sections**:
1. System architecture diagram
2. Component architecture
3. Query architecture by pillar
4. Data flow diagrams
5. Deployment architectures
6. Security architecture
7. Performance considerations
8. Scalability
9. Monitoring & observability
10. Technology stack
11. Design principles

**Target Audience**: Technical architects, developers

---

#### `METRICS.md`
**Sections**:
- Data sources overview
- Detailed metrics for each pillar:
  - Purpose
  - Source views
  - Key metrics
  - Thresholds
  - Recommendations
- Recommended review cadence
- Additional resources

**Target Audience**: Analysts, operations teams

---

#### `CHANGELOG.md`
**Sections**:
1. Version 1.0.0 release notes
2. Feature list by category
3. Best practices alignment
4. Technical details
5. Known limitations
6. Planned features
7. Version history table
8. Upgrade guide

**Target Audience**: All users tracking changes

---

#### `PROJECT_STRUCTURE.md`
**This file** - Complete project overview and organization

---

### Configuration Files

#### `.streamlit/secrets.toml.template`
**Purpose**: Template for local development credentials

**Structure**:
```toml
[connections.snowflake]
account = "your_account_identifier"
user = "your_username"
password = "your_password"
role = "ACCOUNTADMIN"
warehouse = "your_warehouse"
```

**Usage**:
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit with your credentials
# NEVER commit secrets.toml!
```

---

#### `.gitignore`
**Purpose**: Prevent sensitive files from being committed

**Key Exclusions**:
- `.streamlit/secrets.toml` (credentials)
- Python cache files
- Virtual environments
- IDE configuration
- Log files

---

## 🎯 Application Components

### 1. Performance Pillar

| Component | Lines | Queries | Charts |
|-----------|-------|---------|--------|
| Warehouse Utilization | ~50 | 1 | 2 |
| Query Performance | ~60 | 1 | 2 |
| Clustering Analysis | ~40 | 1 | 1 table |
| Cache Hit Rate | ~50 | 1 | 1 |

**Total**: ~200 lines, 4 queries, 5 visualizations

---

### 2. Reliability Pillar

| Component | Lines | Queries | Charts |
|-----------|-------|---------|--------|
| Replication Status | ~45 | 1 | 1 pie + 1 table |
| Query Failures | ~50 | 1 | 1 line + 1 table |
| Pipeline Reliability | ~35 | 1 | 1 table |
| Task Reliability | ~40 | 1 | Metrics |

**Total**: ~170 lines, 4 queries, 4 visualizations

---

### 3. Operational Excellence Pillar

| Component | Lines | Queries | Charts |
|-----------|-------|---------|--------|
| Resource Monitors | ~30 | 1 | 1 table |
| Warehouse Config | ~60 | 1 | 1 table + metrics |
| Long-Running Queries | ~50 | 1 | 1 histogram + 1 table |
| Query Patterns | ~40 | 1 | 1 bar + 1 table |

**Total**: ~180 lines, 4 queries, 5 visualizations

---

### 4. Security & Governance Pillar

| Component | Lines | Queries | Charts |
|-----------|-------|---------|--------|
| MFA Adoption | ~45 | 1 | 1 pie + metrics |
| Network Policies | ~30 | 1 | 1 table |
| Privileged Access | ~45 | 1 | 1 bar + 1 table |
| Data Masking | ~40 | 1 | 1 table + metrics |
| Failed Logins | ~55 | 1 | 1 bar + 1 table |

**Total**: ~215 lines, 5 queries, 7 visualizations

---

### 5. Cost Optimization Pillar

| Component | Lines | Queries | Charts |
|-----------|-------|---------|--------|
| Credit Usage | ~50 | 1 | 2 (pie + area) |
| Warehouse Costs | ~55 | 1 | 1 bar + 1 table |
| Storage Analysis | ~50 | 1 | 1 area + metrics |
| Idle Warehouses | ~45 | 1 | 1 table |
| Storage Optimization | ~60 | 1 | 1 scatter + 1 table |

**Total**: ~260 lines, 5 queries, 8 visualizations

---

## 📊 Application Statistics

### Overall Metrics

```
Total Lines of Code:       ~1,050
Total SQL Queries:         22
Total Visualizations:      29
  - Charts:                20
  - Tables:                18
  - Metric Cards:          25+

Snowflake Views Used:      14
  - QUERY_HISTORY
  - WAREHOUSE_METERING_HISTORY
  - STORAGE_USAGE
  - DATABASES
  - WAREHOUSES
  - USERS
  - NETWORK_POLICIES
  - SESSIONS
  - LOGIN_HISTORY
  - RESOURCE_MONITORS
  - PIPES
  - TASKS
  - POLICY_REFERENCES
  - AUTOMATIC_CLUSTERING_HISTORY
  - METERING_DAILY_HISTORY
  - TABLE_STORAGE_METRICS
  - ACCESS_HISTORY

Tabs:                      5
Configuration Options:     1 (date range)
Alert Types:              3 (success, warning, critical)
```

---

## 🚀 Deployment Options

### Option 1: Snowflake Streamlit (Recommended)

**Deployment Steps**:
1. Copy `app.py` to Snowflake Streamlit editor
2. Click "Run"
3. Done!

**Pros**:
- ✅ Zero infrastructure
- ✅ Native authentication
- ✅ Direct ACCOUNT_USAGE access
- ✅ Secure by default

**Cons**:
- ❌ Requires Streamlit feature

---

### Option 2: Local Development

**Deployment Steps**:
1. Clone repository
2. Install dependencies
3. Configure secrets.toml
4. Run `streamlit run app.py`

**Pros**:
- ✅ Fast iteration
- ✅ Full control
- ✅ Easy debugging

**Cons**:
- ❌ Requires local setup
- ❌ Credential management

---

### Option 3: SnowSQL Deployment

**Deployment Steps**:
1. Run `deploy.sql`
2. Upload files with PUT
3. Create Streamlit object
4. Access via URL

**Pros**:
- ✅ Scriptable deployment
- ✅ Version control friendly
- ✅ Repeatable process

**Cons**:
- ❌ Requires SnowSQL
- ❌ More complex setup

---

## 🔐 Security Considerations

### Permissions Required

```sql
-- Minimum required permissions
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE your_role;
GRANT USAGE ON DATABASE your_db TO ROLE your_role;
GRANT USAGE ON SCHEMA your_schema TO ROLE your_role;
GRANT USAGE ON WAREHOUSE your_wh TO ROLE your_role;
```

### Data Access

- ✅ Read-only queries
- ✅ No data modification
- ✅ ACCOUNT_USAGE metadata only
- ✅ No user data accessed
- ✅ No PII/PHI exposed

### Credentials

- ✅ Never hardcoded
- ✅ Session-based auth
- ✅ secrets.toml gitignored
- ✅ Snowpark handles connections

---

## 🎨 Customization Guide

### 1. Adjust Thresholds

```python
# In app.py, find threshold checks like:
if queue_time_pct > 20:  # Change threshold here
    st.warning("...")
```

### 2. Add Custom Queries

```python
# Add a new section in any tab
st.subheader("My Custom Analysis")

query = """
SELECT ...
FROM snowflake.account_usage...
"""

df = session.sql(query).to_pandas()
st.dataframe(df)
```

### 3. Modify Styling

```python
# Update CSS in st.markdown() section
st.markdown("""
<style>
    .main-header {
        color: #YOUR_COLOR;
    }
</style>
""", unsafe_allow_html=True)
```

### 4. Add New Tabs

```python
# Add to tab creation
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([...])

with tab6:
    st.header("My Custom Pillar")
    # Your code here
```

---

## 📈 Usage Patterns

### Daily Usage (Operations Teams)
- Monitor queue times
- Check failed queries
- Review credit usage

### Weekly Usage (Administrators)
- Review warehouse configuration
- Check security alerts
- Analyze cost trends

### Monthly Usage (Leadership)
- Overall account health
- Cost optimization opportunities
- Compliance status

### Quarterly Usage (Architects)
- Architecture optimization
- Capacity planning
- Strategic improvements

---

## 🛠️ Maintenance

### Regular Updates

1. **Dependencies**: Update `requirements.txt` quarterly
2. **Queries**: Review for new ACCOUNT_USAGE views
3. **Thresholds**: Adjust based on organization standards
4. **Documentation**: Keep aligned with Snowflake updates

### Monitoring the App

```sql
-- Check app warehouse usage
SELECT *
FROM snowflake.account_usage.warehouse_metering_history
WHERE warehouse_name = 'STREAMLIT_WH';

-- Check app query performance
SELECT *
FROM snowflake.account_usage.query_history
WHERE user_name = CURRENT_USER()
  AND query_text LIKE '%account_usage%';
```

---

## 🤝 Contributing

### How to Contribute

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes
4. Test thoroughly
5. Update documentation
6. Submit pull request

### Contribution Areas

- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🎨 UI/UX enhancements
- ⚡ Performance optimizations
- 🔒 Security improvements

---

## 📚 Additional Resources

### Snowflake Documentation
- [Well-Architected Framework](https://www.snowflake.com/en/developers/guides/well-architected-framework/)
- [ACCOUNT_USAGE Views](https://docs.snowflake.com/en/sql-reference/account-usage.html)
- [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)

### External Resources
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

---

## 📞 Support

### Issues
- Open an issue in the repository
- Include error messages and screenshots
- Specify Snowflake edition and region

### Questions
- Check documentation first
- Review QUICKSTART.md for common issues
- Contact your Snowflake Solution Engineer

---

## 📝 License

MIT License - See repository for full license text

---

**Project Maintained By**: Snowflake Solution Engineering Team  
**Last Updated**: November 12, 2025  
**Version**: 1.0.0


# ❄️ Snowflake Well-Architected Framework Review

A comprehensive Streamlit application for analyzing Snowflake accounts based on the [Snowflake Well-Architected Framework](https://www.snowflake.com/en/developers/guides/well-architected-framework/) best practices.

## Overview

This application provides actionable insights across the five pillars of the Well-Architected Framework:

### 🚀 Performance Efficiency
- Warehouse utilization and efficiency analysis
- Query performance trends and optimization opportunities
- Table clustering health monitoring
- Result cache hit rate analysis

**Best Practices Reference**: [Performance Framework Guide](https://www.snowflake.com/en/developers/guides/well-architected-framework-performance/)

### 🛡️ Reliability & Resilience
- Database replication status monitoring
- Query failure and error analysis
- Data pipeline (Snowpipe) reliability
- Task execution monitoring

**Best Practices Reference**: [Reliability Framework Guide](https://www.snowflake.com/en/developers/guides/well-architected-framework-reliability/)

### ⚙️ Operational Excellence
- Resource monitor configuration
- Warehouse auto-suspend/resume settings
- Long-running query detection
- Query execution pattern analysis

**Best Practices Reference**: [Operational Excellence Framework Guide](https://www.snowflake.com/en/developers/guides/well-architected-framework-operational-excellence/)

### 🔒 Security & Governance
- Multi-Factor Authentication (MFA) adoption tracking
- Network policy configuration review
- Privileged role access monitoring
- Data masking and row access policies
- Failed authentication attempt tracking

**Best Practices Reference**: [Security & Governance Framework Guide](https://www.snowflake.com/en/developers/guides/well-architected-framework-security-and-governance/)

### 💰 Cost Optimization & FinOps
- Credit consumption by service type
- Warehouse cost breakdown analysis
- Storage cost trends and optimization
- Idle warehouse detection
- Storage optimization opportunities (unused large tables)

**Best Practices Reference**: [Cost Optimization Framework Guide](https://www.snowflake.com/en/developers/guides/well-architected-framework-cost-optimization-and-finops/)

## Features

- **Visual Analytics**: Interactive charts and graphs using Plotly
- **Actionable Recommendations**: Automated detection of improvement opportunities
- **Configurable Analysis Period**: Adjust the time range (7-90 days) for analysis
- **Real-time Data**: Queries Snowflake's `ACCOUNT_USAGE` views for up-to-date metrics
- **Color-coded Alerts**: Success, warning, and critical alerts for easy identification

## Prerequisites

- Snowflake account with appropriate permissions
- Access to `SNOWFLAKE.ACCOUNT_USAGE` schema (requires `ACCOUNTADMIN` or granted privileges)
- Snowflake Streamlit environment or local Snowflake connection

## Installation

### Option 1: Deploy to Snowflake (Recommended)

1. **Create a Streamlit app in Snowflake:**

```sql
USE ROLE ACCOUNTADMIN;
USE DATABASE <YOUR_DATABASE>;
USE SCHEMA <YOUR_SCHEMA>;

CREATE STREAMLIT snowflake_waf_review
  ROOT_LOCATION = '@<YOUR_STAGE>'
  MAIN_FILE = 'app.py'
  QUERY_WAREHOUSE = <YOUR_WAREHOUSE>;
```

2. **Upload the files:**

```sql
PUT file:///path/to/app.py @<YOUR_STAGE>/app.py AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
```

3. **Grant necessary privileges:**

```sql
-- Grant access to ACCOUNT_USAGE
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE <YOUR_ROLE>;
```

### Option 2: Run Locally

1. **Clone the repository:**

```bash
git clone <your-repo-url>
cd snowflake-readiness-review
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Configure Snowflake connection:**

Create a `.streamlit/secrets.toml` file:

```toml
[connections.snowflake]
account = "your_account"
user = "your_username"
password = "your_password"
role = "ACCOUNTADMIN"
warehouse = "your_warehouse"
```

4. **Run the application:**

```bash
streamlit run app.py
```

## Required Permissions

The application requires access to the following Snowflake views:

- `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE`
- `SNOWFLAKE.ACCOUNT_USAGE.DATABASES`
- `SNOWFLAKE.ACCOUNT_USAGE.USERS`
- `SNOWFLAKE.ACCOUNT_USAGE.NETWORK_POLICIES`
- `SNOWFLAKE.ACCOUNT_USAGE.SESSIONS`
- `SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.RESOURCE_MONITORS`
- `SNOWFLAKE.ACCOUNT_USAGE.PIPES`
- `SNOWFLAKE.ACCOUNT_USAGE.TASKS`
- `SNOWFLAKE.ACCOUNT_USAGE.POLICY_REFERENCES`
- `SNOWFLAKE.ACCOUNT_USAGE.AUTOMATIC_CLUSTERING_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS`
- `SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY`

**Note**: `ACCOUNT_USAGE` views have latency (45 minutes to 3 hours). For real-time data, consider using `INFORMATION_SCHEMA` views where applicable.

## Usage

1. **Launch the application** in your Snowflake environment or locally
2. **Configure the analysis period** using the sidebar slider (7-90 days)
3. **Navigate through the tabs** to explore each pillar of the Well-Architected Framework
4. **Review recommendations** highlighted in warning and critical alert boxes
5. **Export insights** by taking screenshots or copying data tables

## Key Metrics & Recommendations

### Performance
- ✅ Queue time should be <20% of execution time
- ✅ Cache hit rate should be >50%
- ✅ Clustering depth should be <3 for optimal performance

### Reliability
- ✅ Enable replication for critical databases
- ✅ Monitor and resolve pipeline errors
- ✅ Set up error notifications for tasks

### Operational Excellence
- ✅ Configure resource monitors
- ✅ Set auto-suspend to 60-300 seconds
- ✅ Enable auto-resume for all warehouses

### Security & Governance
- ✅ Enforce MFA for all users
- ✅ Implement network policies
- ✅ Apply masking policies to sensitive data
- ✅ Monitor privileged role usage

### Cost Optimization
- ✅ Identify and suspend idle warehouses
- ✅ Monitor cloud services credit usage (<10%)
- ✅ Archive or drop unused large tables
- ✅ Review data retention policies

## Troubleshooting

### "Unable to connect to Snowflake"
- Ensure you're running in a Snowflake Streamlit environment, or
- Verify your connection configuration in `.streamlit/secrets.toml`

### "Error fetching data"
- Check that your role has `IMPORTED PRIVILEGES` on `SNOWFLAKE` database
- Verify the role has access to `ACCOUNT_USAGE` schema
- Some views may require `ACCOUNTADMIN` role

### "No data available"
- `ACCOUNT_USAGE` views have latency (45 min - 3 hours)
- Ensure the account has been active during the analysis period
- Try increasing the analysis period using the sidebar slider

## Customization

You can customize the application by:

1. **Adjusting thresholds**: Modify warning thresholds in the code (e.g., queue time %, cache hit rate)
2. **Adding custom queries**: Extend each tab with additional analysis specific to your use case
3. **Styling**: Modify the CSS in the `st.markdown()` section for custom branding
4. **Adding tabs**: Create new tabs for custom analysis or specific workload types

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License.

## Support

For questions or issues:
- Review the [Snowflake Well-Architected Framework documentation](https://www.snowflake.com/en/developers/guides/well-architected-framework/)
- Check Snowflake's [ACCOUNT_USAGE views documentation](https://docs.snowflake.com/en/sql-reference/account-usage.html)
- Open an issue in this repository

## Acknowledgments

Built with:
- [Snowflake](https://www.snowflake.com/)
- [Streamlit](https://streamlit.io/)
- [Plotly](https://plotly.com/)
- Based on [Snowflake Well-Architected Framework](https://www.snowflake.com/en/developers/guides/well-architected-framework/)

---

**Built by Snowflake Solution Engineers for the Snowflake Community** ❄️


# Metrics & Queries Reference

This document outlines all the metrics tracked by the Well-Architected Framework Review application and the Snowflake views used.

## 📊 Data Sources

All queries use Snowflake's `ACCOUNT_USAGE` schema, which provides historical usage data:

- **Latency**: 45 minutes to 3 hours
- **Retention**: 1 year of historical data
- **Access**: Requires `IMPORTED PRIVILEGES` on `SNOWFLAKE` database

---

## 🚀 Performance Efficiency Metrics

### 1. Warehouse Utilization & Efficiency

**Purpose**: Identify warehouse sizing issues and queueing problems

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`

**Key Metrics**:
- Total queries per warehouse
- Average execution time (seconds)
- Average queue time (seconds)
- Queue time as percentage of execution time
- Cloud services credits consumed

**Thresholds**:
- ⚠️ Warning: Queue time > 20% of execution time
- ✅ Good: Queue time < 10% of execution time

**Recommendations**:
- Increase warehouse size for high queue times
- Enable multi-cluster warehouses for variable workloads
- Consider separating workloads by warehouse

---

### 2. Query Performance Analysis

**Purpose**: Track query efficiency and identify optimization opportunities

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`

**Key Metrics**:
- Query count trends
- Average execution time
- Data scanned (GB)
- Partitions scanned vs. total partitions
- Slow queries (>1 minute)

**Thresholds**:
- ⚠️ Warning: >50% of partitions scanned on average
- ✅ Good: <30% of partitions scanned (good pruning)

**Recommendations**:
- Add clustering keys to large tables
- Implement search optimization for point lookups
- Use materialized views for repeated aggregations
- Add filters to reduce data scanned

---

### 3. Table Clustering Analysis

**Purpose**: Monitor clustering health and maintenance needs

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.AUTOMATIC_CLUSTERING_HISTORY`

**Key Metrics**:
- Average clustering depth
- Average overlaps
- Tables with suboptimal clustering

**Thresholds**:
- ⚠️ Warning: Clustering depth > 3
- ✅ Good: Clustering depth < 2

**Recommendations**:
- Re-cluster tables with depth > 3
- Review clustering key selection
- Enable automatic clustering for large, frequently updated tables

---

### 4. Result Cache Efficiency

**Purpose**: Measure cache utilization and identify repeated queries

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`

**Key Metrics**:
- Cache hit rate (%)
- Total queries vs. cached queries
- Cache hit trends over time

**Thresholds**:
- ⚠️ Warning: Cache hit rate < 30%
- ✅ Good: Cache hit rate > 50%

**Recommendations**:
- Identify and cache common query patterns
- Extend query result retention if needed
- Use persisted query results for BI tools

---

## 🛡️ Reliability & Resilience Metrics

### 1. Database Replication Status

**Purpose**: Ensure business continuity through replication

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.DATABASES`

**Key Metrics**:
- Databases with replication enabled
- Databases without replication
- Replication schedules

**Thresholds**:
- ⚠️ Warning: Critical databases without replication
- ✅ Good: All critical databases replicated

**Recommendations**:
- Enable replication for production databases
- Set appropriate replication schedules (hourly, daily)
- Test failover procedures regularly

---

### 2. Query Failures & Error Analysis

**Purpose**: Track reliability issues and error patterns

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`

**Key Metrics**:
- Failed query count
- Error codes and messages
- Failure trends over time

**Thresholds**:
- ⚠️ Warning: >100 failures per day
- ✅ Good: <10 failures per day

**Recommendations**:
- Implement error handling and retries
- Set up alerts for critical errors
- Review error patterns for systemic issues

---

### 3. Data Pipeline Reliability (Snowpipe)

**Purpose**: Monitor data ingestion pipeline health

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.PIPES`

**Key Metrics**:
- Pipes with errors
- Error counts per pipe
- Last error messages

**Thresholds**:
- ⚠️ Warning: Any pipe with errors
- ✅ Good: All pipes running without errors

**Recommendations**:
- Configure error notifications
- Monitor pipe load times
- Validate data before loading

---

### 4. Task Execution Reliability

**Purpose**: Ensure scheduled tasks are configured for monitoring

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.TASKS`

**Key Metrics**:
- Total tasks
- Active vs. suspended tasks
- Tasks without error integration

**Thresholds**:
- ⚠️ Warning: Tasks without error notifications
- ✅ Good: All tasks have error integrations

**Recommendations**:
- Set up error notifications for all tasks
- Monitor task execution history
- Implement task dependencies properly

---

## ⚙️ Operational Excellence Metrics

### 1. Resource Monitors

**Purpose**: Control and monitor credit consumption

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.RESOURCE_MONITORS`

**Key Metrics**:
- Number of resource monitors
- Credit quotas
- Alert and suspend thresholds

**Thresholds**:
- ⚠️ Warning: No resource monitors configured
- ✅ Good: At least one account-level monitor

**Recommendations**:
- Create account-level resource monitor
- Set warehouse-specific monitors for high-usage warehouses
- Configure suspend-at and notify-at thresholds

---

### 2. Warehouse Auto-Suspend & Auto-Resume

**Purpose**: Optimize warehouse runtime to reduce costs

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSES`

**Key Metrics**:
- Warehouses without auto-suspend
- Auto-suspend timeout values
- Auto-resume configuration

**Thresholds**:
- ⚠️ Critical: No auto-suspend (warehouse runs indefinitely)
- ⚠️ Warning: Auto-suspend > 10 minutes
- ✅ Good: Auto-suspend = 60-300 seconds

**Recommendations**:
- Set auto-suspend to 60-300 seconds for most warehouses
- Enable auto-resume for all warehouses
- Consider shorter timeouts for ETL warehouses

---

### 3. Long-Running Query Detection

**Purpose**: Identify queries that may need optimization

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`

**Key Metrics**:
- Queries running >5 minutes
- Execution time distribution
- Data scanned by long queries

**Thresholds**:
- ⚠️ Warning: Queries >5 minutes
- ⚠️ Critical: Queries >1 hour

**Recommendations**:
- Review query plans (EXPLAIN)
- Add appropriate filters and predicates
- Consider query result caching or materialized views

---

### 4. Query Execution Patterns

**Purpose**: Understand workload patterns and user behavior

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`

**Key Metrics**:
- Query count by user
- Query types (SELECT, INSERT, UPDATE, etc.)
- Warehouses used per user

**Recommendations**:
- Assign users to appropriate warehouses
- Implement workload management policies
- Monitor for unusual patterns

---

## 🔒 Security & Governance Metrics

### 1. Multi-Factor Authentication (MFA)

**Purpose**: Ensure secure authentication practices

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.USERS`

**Key Metrics**:
- Users with MFA enabled
- Users without MFA
- MFA adoption rate (%)

**Thresholds**:
- ⚠️ Critical: <100% MFA adoption
- ✅ Good: 100% MFA adoption

**Recommendations**:
- Require MFA for all users
- Use SCIM for automatic provisioning
- Implement SSO with MFA

---

### 2. Network Policy Configuration

**Purpose**: Restrict access to trusted networks

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.NETWORK_POLICIES`

**Key Metrics**:
- Number of network policies
- Allowed IP ranges
- Blocked IP ranges

**Thresholds**:
- ⚠️ Warning: No network policies configured
- ✅ Good: Account-level or user-level policies active

**Recommendations**:
- Implement network policies for production accounts
- Use IP whitelisting for known locations
- Consider VPN or PrivateLink for enhanced security

---

### 3. Privileged Access Monitoring

**Purpose**: Track usage of sensitive roles

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.SESSIONS`

**Key Metrics**:
- ACCOUNTADMIN role usage
- SECURITYADMIN role usage
- SYSADMIN role usage
- Login frequency by privileged role

**Thresholds**:
- ⚠️ Warning: Frequent ACCOUNTADMIN usage
- ✅ Good: Privileged roles used only when necessary

**Recommendations**:
- Limit ACCOUNTADMIN access
- Use custom roles with least privilege
- Implement approval workflows for privileged access
- Monitor and audit privileged sessions

---

### 4. Data Protection & Masking

**Purpose**: Ensure sensitive data is protected

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.POLICY_REFERENCES`

**Key Metrics**:
- Masking policies applied
- Row access policies applied
- Policy coverage

**Thresholds**:
- ⚠️ Warning: No masking policies for PII/PHI data
- ✅ Good: Masking policies on all sensitive columns

**Recommendations**:
- Implement masking policies for PII (SSN, email, phone)
- Use row access policies for data segmentation
- Tag sensitive data for governance
- Regular policy compliance audits

---

### 5. Failed Authentication Attempts

**Purpose**: Detect potential security threats

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY`

**Key Metrics**:
- Failed login attempts by user
- Error messages
- Failed login trends

**Thresholds**:
- ⚠️ Warning: >10 failed attempts per user
- ⚠️ Critical: >100 failed attempts from same source

**Recommendations**:
- Implement account lockout policies
- Monitor for brute force attacks
- Set up alerts for suspicious login activity
- Review IP addresses of failed attempts

---

## 💰 Cost Optimization & FinOps Metrics

### 1. Credit Consumption Overview

**Purpose**: Track overall credit usage across services

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY`

**Key Metrics**:
- Total credits by service type
- Daily credit consumption trends
- Credit distribution (compute, storage, cloud services)

**Recommendations**:
- Monitor credit trends daily
- Set budget alerts
- Compare month-over-month usage

---

### 2. Warehouse Cost Analysis

**Purpose**: Identify high-cost warehouses

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY`

**Key Metrics**:
- Credits per warehouse
- Compute vs. cloud services credits
- Cloud services credit percentage

**Thresholds**:
- ⚠️ Warning: Cloud services credits >10% (may be billed)
- ✅ Good: Cloud services credits <10%

**Recommendations**:
- Right-size warehouses based on workload
- Reduce cloud services credit usage
- Consolidate underutilized warehouses

---

### 3. Storage Cost Analysis

**Purpose**: Monitor and optimize storage consumption

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE`

**Key Metrics**:
- Total storage (TB)
- Database storage
- Stage storage
- Failsafe storage
- Storage growth rate

**Thresholds**:
- ⚠️ Warning: Storage growth >10% per week
- ⚠️ Critical: Excessive stage or failsafe storage

**Recommendations**:
- Remove old stage files
- Implement data retention policies
- Drop unused tables and databases
- Consider external stages for archival data

---

### 4. Idle Warehouse Detection

**Purpose**: Identify and eliminate wasted compute

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSES` + `QUERY_HISTORY`

**Key Metrics**:
- Warehouses not used in 7+ days
- Last usage timestamp
- Days since last use

**Thresholds**:
- ⚠️ Warning: Warehouse unused for 7+ days
- ✅ Good: All warehouses actively used

**Recommendations**:
- Suspend or drop unused warehouses
- Consolidate similar workloads
- Review warehouse creation policies

---

### 5. Storage Optimization Opportunities

**Purpose**: Find tables consuming storage without access

**Source**: `SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS` + `ACCESS_HISTORY`

**Key Metrics**:
- Large tables (>10 GB) with no access
- Active, time travel, and failsafe storage breakdown
- Access frequency

**Thresholds**:
- ⚠️ Warning: Tables >10 GB with 0 access in 30 days
- ✅ Good: All large tables accessed regularly

**Recommendations**:
- Archive or drop unused tables
- Reduce time travel retention for non-critical tables
- Move cold data to external storage
- Implement lifecycle management policies

---

## 📈 Recommended Review Cadence

| Pillar | Daily | Weekly | Monthly | Quarterly |
|--------|-------|--------|---------|-----------|
| **Performance** | Queue times, Cache hit rate | Long queries, Clustering | Warehouse sizing | Architecture review |
| **Reliability** | Failed queries, Pipe errors | Task failures | Replication status | DR testing |
| **Operational Excellence** | Long queries | Warehouse configs | Resource monitors | Process improvements |
| **Security** | Failed logins | Privileged access | MFA adoption, Policies | Security audit |
| **Cost** | Credit usage | Warehouse costs | Storage growth | Optimization initiatives |

---

## 🔗 Additional Resources

- [Snowflake ACCOUNT_USAGE Views Documentation](https://docs.snowflake.com/en/sql-reference/account-usage.html)
- [Snowflake Well-Architected Framework](https://www.snowflake.com/en/developers/guides/well-architected-framework/)
- [Snowflake Best Practices](https://docs.snowflake.com/en/user-guide/best-practices.html)
- [Snowflake Security Best Practices](https://docs.snowflake.com/en/user-guide/security-best-practices.html)

---

**Last Updated**: November 2025


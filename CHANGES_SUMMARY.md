# Changes Summary - January 11, 2026

## Overview
This document summarizes all changes made to the Snowflake Readiness Review application based on user feedback and Snowflake documentation updates.

## Changes Applied

### 1. ✅ SSO View Enhancement (Security Tab)
**Files**: `app.py`, `app_local.py`

- Added SSO toggle checkbox to distinguish SSO vs MFA adoption
- Filters out service accounts (`SF$SERVICE` pattern) from user lists
- Fixed `query_mfa` scoping error by properly indenting the try-except block
- **Location**: Security & Governance Tab, Section 1

**Changes**:
- Added `AND login_name NOT LIKE '%SF$SERVICE%'` to both SSO and MFA queries
- Moved MFA query inside `else` block with proper indentation
- Added comprehensive SSO user detection logic

### 2. ✅ System User Filtering (Performance Tab)
**Files**: `app.py`, `app_local.py`

- Filtered system users from Query Latency SLO Monitoring
- Excluded `SYSTEM`, `dataplane_service`, and `dataplatform_admin` from metrics
- **Location**: Performance Tab, Section 1

**Changes**:
```sql
AND user_name NOT IN ('SYSTEM', 'dataplane_service', 'dataplatform_admin')
```

### 3. ✅ Query Execution Pattern Filter (Operational Excellence Tab)
**Files**: `app.py`, `app_local.py`

- Already filtered `SYSTEM` and `dataplane_service` from query patterns
- **Location**: Operational Excellence Tab, Section 4

### 4. ✅ Data Metric Functions - Updated View (Operational Excellence Tab)
**Files**: `app.py`, `app_local.py`

- Changed from `DATA_METRIC_FUNCTIONS` to `DATA_METRIC_FUNCTION_REFERENCES`
- Updated query to use correct columns per [Snowflake Documentation](https://docs.snowflake.com/en/sql-reference/account-usage/data_metric_function_references)
- Shows active DMF references with schedule status
- **Location**: Operational Excellence Tab, Section 5

**New Columns**:
- `METRIC_DATABASE_NAME`, `METRIC_SCHEMA_NAME`, `METRIC_NAME`
- `REF_ENTITY_DATABASE_NAME`, `REF_ENTITY_SCHEMA_NAME`, `REF_ENTITY_NAME`
- `SCHEDULE`, `SCHEDULE_STATUS`

### 5. ✅ Alert Usages (Operational Excellence Tab)
**Files**: `app.py`, `app_local.py`

- **Replaced** "Task Failure Notifications" with "Alert Configuration & History"
- Uses `SHOW ALERTS` to display configured alerts
- Uses `ALERT_HISTORY` from [Account Usage](https://docs.snowflake.com/en/sql-reference/account-usage/alert_history)
- Shows alert execution success/failure metrics
- **Location**: Operational Excellence Tab, Section 6

**Features**:
- Displays total alerts, active alerts, and suspended alerts
- Shows recent alert execution history with state tracking
- Provides alert creation examples

### 6. ✅ Account Timezone Configuration Fix (Operational Excellence Tab)
**Files**: `app.py`, `app_local.py`

- Fixed `'value'` column name error in `SHOW PARAMETERS` output
- Added dynamic column name detection (handles `VALUE` vs `value`)
- **Location**: Operational Excellence Tab, Section 7

**Fix**:
```python
value_col = 'VALUE' if 'VALUE' in df_tz_param.columns else 'value'
timezone = df_tz_param.iloc[0][value_col]
```

### 7. ✅ Notification Contacts - SHOW CONTACTS (Security Tab)
**Files**: `app.py`, `app_local.py`

- Changed from `SYSTEM$GET_ACCOUNT_NOTIFICATION_EMAILS()` to `SHOW CONTACTS`
- Simplified display to show all configured contacts
- **Location**: Security & Governance Tab, Section 5

**Benefits**:
- More reliable query execution
- Better alignment with Snowflake's contact management
- Shows all contact types configured in the account

### 8. ✅ Event Table Monitoring (Reliability Tab)
**Files**: `app.py`, `app_local.py`

- **Added new section** for Event Table monitoring
- Checks for configured event tables using `ACCOUNT_USAGE.EVENT_TABLES`
- Explains importance of event tables for observability
- Provides setup examples and documentation links
- **Location**: Reliability & Resilience Tab, Section 5 (new)

**Features**:
- Displays configured event tables
- Shows monitored objects count
- Comprehensive setup guide
- Links to [Event Tables Documentation](https://docs.snowflake.com/en/developer-guide/logging-tracing/event-table-setting-up)

### 9. ✅ MIT LICENSE
**File**: `LICENSE`

- Created MIT License file for the repository
- Copyright 2026 Snowflake Readiness Review Contributors

## Technical Details

### Files Modified
- ✅ `app.py` - Main application (compiled successfully)
- ✅ `app_local.py` - Local development version (compiled successfully)
- ✅ `LICENSE` - New MIT License file
- ✅ `CHANGES_SUMMARY.md` - This file

### Dependencies
No new dependencies were added. All changes use existing Snowflake Account Usage views and SQL capabilities.

### Breaking Changes
None. All changes are backward compatible.

### Compilation Status
```bash
✅ app.py - Compiled successfully
✅ app_local.py - Compiled successfully
```

## Testing Recommendations

### For `app.py` (Production)
1. Deploy to Snowflake Streamlit
2. Test SSO toggle functionality
3. Verify DMF references query works (requires Enterprise Edition)
4. Check Alert Usages section with configured alerts
5. Validate SHOW CONTACTS output
6. Verify Event Table section displays correctly

### For `app_local.py` (Development)
1. Run locally: `./run_local.sh`
2. Test all modified sections with mock data
3. Verify UI components render correctly
4. Check error handling for missing data

## Documentation References

All changes align with official Snowflake documentation (as of January 2026):

1. [DATA_METRIC_FUNCTION_REFERENCES](https://docs.snowflake.com/en/sql-reference/account-usage/data_metric_function_references)
2. [ALERT_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/alert_history)
3. [Event Tables](https://docs.snowflake.com/en/developer-guide/logging-tracing/event-table-setting-up)
4. [Contacts](https://docs.snowflake.com/en/sql-reference/sql/show-contacts)
5. [Data Metric Functions](https://docs.snowflake.com/en/user-guide/data-quality-intro)

## Next Steps

1. **Deploy**: Push changes to your Snowflake Streamlit application
2. **Test**: Validate all sections with real data
3. **Monitor**: Check for any runtime errors in production
4. **Iterate**: Gather user feedback and make adjustments

## Notes

- All SQL queries follow Snowflake best practices
- Error handling implemented for all new sections
- Consistent UI/UX patterns maintained throughout
- Both files maintain feature parity

---

**Last Updated**: January 11, 2026  
**Status**: ✅ All changes applied and compiled successfully


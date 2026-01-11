# Fixes Applied - January 11, 2026

## Status Summary

### ✅ Completed Fixes

1. **Event Tables** - Changed from `ACCOUNT_USAGE.EVENT_TABLES` to `SHOW EVENT TABLES IN ACCOUNT`
   - Filters out SNOWFLAKE-owned event tables
   - Applied to both `app.py` and `app_local.py`

2. **DMF Column Names** - Updated to match documentation
   - Changed `ref_entity_database_name` → `ref_database_name`
   - Changed `ref_entity_schema_name` → `ref_schema_name`
   - Applied to both `app.py` and `app_local.py`

3. **Timezone Configuration** - Enhanced error handling
   - Added robust column detection for 'VALUE' column
   - Handles quoted column names
   - Better error messages
   - Applied to both `app.py` and `app_local.py`

### ⚠️ Pending Fix

4. **Move Snowpipe to Operational Excellence** - IN PROGRESS
   - **Current Issue**: Snowpipe code is in Reliability tab (lines 1141-1307 in app.py)
   - **Current State**: Header was changed but Snowpipe code is still there
   - **Solution Needed**: 
     - Remove Snowpipe section from Reliability tab
     - Renumber "Task Execution Reliability" from section 4 to section 3
     - Add Snowpipe as new section 3 in Operational Excellence
     - Renumber remaining Operational Excellence sections (3→4, 4→5, etc.)

## Files Modified

- ✅ `app.py` - Fixes 1, 2, 3 applied (Fix 4 partially done)
- ✅ `app_local.py` - Fixes 1, 2, 3 applied (Fix 4 pending)
- ✅ Both files compile successfully

## Testing Recommendations

1. Test Event Tables section - verify SHOW command works and filters correctly
2. Test DMF section - verify column names match actual query results
3. Test Timezone section - verify error handling shows meaningful messages
4. After Snowpipe is moved, test both Reliability and Operational Excellence tabs

## Next Steps

Complete the Snowpipe reorganization in both files.


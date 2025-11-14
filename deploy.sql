-- ============================================================================
-- Snowflake Well-Architected Framework Review - Deployment Script
-- ============================================================================
-- This script creates the necessary objects to deploy the Streamlit application
-- Run this script as ACCOUNTADMIN or a role with appropriate privileges

-- Step 1: Set the context (UPDATE THESE VALUES)
USE ROLE ACCOUNTADMIN;
USE DATABASE <YOUR_DATABASE>; -- Replace with your database name
USE SCHEMA <YOUR_SCHEMA>;     -- Replace with your schema name

-- Step 2: Create a stage for the Streamlit app (if not exists)
CREATE STAGE IF NOT EXISTS streamlit_stage
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Stage for Streamlit applications';

-- Step 3: Create a warehouse for the app (if not exists)
CREATE WAREHOUSE IF NOT EXISTS streamlit_wh
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Warehouse for Streamlit applications';

-- Step 4: Upload the files to the stage
-- Run these commands from your local terminal or SnowSQL:
-- PUT file:///path/to/app.py @streamlit_stage/snowflake_waf_review/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- PUT file:///path/to/requirements.txt @streamlit_stage/snowflake_waf_review/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- Step 5: Create the Streamlit app
CREATE OR REPLACE STREAMLIT snowflake_waf_review
    ROOT_LOCATION = '@streamlit_stage/snowflake_waf_review'
    MAIN_FILE = 'app.py'
    QUERY_WAREHOUSE = streamlit_wh
    COMMENT = 'Snowflake Well-Architected Framework Review Application';

-- Step 6: Grant necessary privileges
-- Grant access to ACCOUNT_USAGE (required for the app to function)
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE ACCOUNTADMIN;

-- Optional: Grant access to other roles
-- GRANT USAGE ON STREAMLIT snowflake_waf_review TO ROLE <YOUR_ROLE>;

-- Step 7: Verify the deployment
SHOW STREAMLITS;

-- To open the Streamlit app:
-- SELECT SYSTEM$GET_STREAMLIT_URL('snowflake_waf_review');

-- ============================================================================
-- Alternative: Create a role specifically for running this app
-- ============================================================================

-- Create a dedicated role for the Well-Architected Framework review
CREATE ROLE IF NOT EXISTS waf_reviewer
    COMMENT = 'Role for running Well-Architected Framework reviews';

-- Grant necessary privileges to the role
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE waf_reviewer;
GRANT USAGE ON DATABASE <YOUR_DATABASE> TO ROLE waf_reviewer;
GRANT USAGE ON SCHEMA <YOUR_SCHEMA> TO ROLE waf_reviewer;
GRANT USAGE ON WAREHOUSE streamlit_wh TO ROLE waf_reviewer;
GRANT USAGE ON STREAMLIT snowflake_waf_review TO ROLE waf_reviewer;

-- Grant the role to users who should have access
-- GRANT ROLE waf_reviewer TO USER <YOUR_USER>;

-- ============================================================================
-- Cleanup Script (if needed)
-- ============================================================================
-- WARNING: This will delete the Streamlit app and related objects
-- Uncomment and run only if you want to remove the application

/*
USE ROLE ACCOUNTADMIN;
USE DATABASE <YOUR_DATABASE>;
USE SCHEMA <YOUR_SCHEMA>;

DROP STREAMLIT IF EXISTS snowflake_waf_review;
DROP WAREHOUSE IF EXISTS streamlit_wh;
DROP STAGE IF EXISTS streamlit_stage;
DROP ROLE IF EXISTS waf_reviewer;
*/


USE ROLE ACCOUNTADMIN;
-- Create databases, schemas and compute pool to host streamlit app
CREATE DATABASE IF NOT EXISTS WAF_METRICS_DB;

CREATE SCHEMA IF NOT EXISTS WAF_METRICS_DB.WAF_METRICS_SCHEMA;

USE DATABASE WAF_METRICS_DB;

USE SCHEMA WAF_METRICS_SCHEMA;

CREATE COMPUTE POOL IF NOT EXISTS WAF_METRICS_COMPUTE_POOL
  MIN_NODES = 1
  MAX_NODES = 2
  INSTANCE_FAMILY = CPU_X64_XS
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  AUTO_SUSPEND_SECS = 600
  COMMENT = 'X-Small compute pool for WAF Streamlit APP';

-- Create EAI (Required for download packages when using compute pool instead of warehouses)

CREATE OR REPLACE NETWORK RULE pypi_api_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('pypi.org','*.pythonhosted.org');

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION pypi_external_access_int
  ALLOWED_NETWORK_RULES = (pypi_api_rule)
  ENABLED = TRUE;  


--

-- Featch WAF Streamlit APP Public repo 

CREATE OR REPLACE API INTEGRATION GIT_API_REPO_WAF
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/sfc-gh-bandrade/')
  ENABLED = TRUE;

-- 2. Create the Git Repository Object
CREATE OR REPLACE GIT REPOSITORY WAF_repo
  API_INTEGRATION = GIT_API_REPO_WAF
  ORIGIN = 'https://github.com/sfc-gh-bandrade/srr-waf-snow-bandrade.git';

-- 3. Fetch the metadata/files
ALTER GIT REPOSITORY WAF_repo FETCH;

--

--CREATE STREAMLIT APP

CREATE STREAMLIT IF NOT EXISTS WAF_SNOWFLAKE
  FROM @WAF_METRICS_DB.WAF_METRICS_SCHEMA.WAF_repo/branches/main
  MAIN_FILE = 'app.py'
  QUERY_WAREHOUSE = COMPUTE_WH
  RUNTIME_NAME = 'SYSTEM$ST_CONTAINER_RUNTIME_PY3_11'
  COMPUTE_POOL = WAF_METRICS_COMPUTE_POOL
  EXTERNAL_ACCESS_INTEGRATIONS = (pypi_external_access_int)
  COMMENT = 'WAF Streamlit APP'
  TITLE = 'Well Architected Framework Analyzer';
  


#!/usr/bin/env python3
"""
Test Snowflake Connection Script (using Snowpark)
Tests connection to Snowflake using credentials from .streamlit/secrets.toml
Uses the same Snowpark approach as the main Streamlit app
"""

import sys
import os
from pathlib import Path

try:
    import toml
    from snowflake.snowpark import Session
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("\nPlease install required packages:")
    print("  pip install snowflake-snowpark-python toml")
    sys.exit(1)


def load_secrets():
    """Load secrets from .streamlit/secrets.toml"""
    secrets_path = Path(__file__).parent / ".streamlit" / "secrets.toml"
    
    if not secrets_path.exists():
        print(f"❌ Secrets file not found: {secrets_path}")
        print("\nPlease create .streamlit/secrets.toml with your Snowflake credentials.")
        sys.exit(1)
    
    try:
        with open(secrets_path, 'r') as f:
            secrets = toml.load(f)
        return secrets.get('snowflake', {})
    except Exception as e:
        print(f"❌ Error loading secrets file: {e}")
        sys.exit(1)


def test_connection_snowpark(config):
    """Test Snowflake connection using Snowpark"""
    print("=" * 70)
    print("🔗 SNOWFLAKE CONNECTION TEST (Snowpark)")
    print("=" * 70)
    
    # Display configuration (mask sensitive data)
    print("\n📋 Configuration:")
    print(f"  Account:   {config.get('account', 'NOT SET')}")
    print(f"  User:      {config.get('user', 'NOT SET')}")
    print(f"  Role:      {config.get('role', 'NOT SET')}")
    print(f"  Warehouse: {config.get('warehouse', 'NOT SET')}")
    
    if 'password' in config:
        print(f"  Password:  {'*' * 8} (configured)")
    else:
        print(f"  Password:  NOT SET")
    
    print("\n" + "-" * 70)
    
    # Attempt connection
    print("\n🔄 Attempting to connect to Snowflake using Snowpark...")
    
    try:
        # Build connection parameters for Snowpark
        connection_parameters = {
            'account': config.get('account'),
            'user': config.get('user'),
            'password': config.get('password'),
            'role': config.get('role'),
            'warehouse': config.get('warehouse'),
        }
        
        # Add optional parameters
        if 'database' in config:
            connection_parameters['database'] = config['database']
        if 'schema' in config:
            connection_parameters['schema'] = config['schema']
        if 'authenticator' in config:
            connection_parameters['authenticator'] = config['authenticator']
        
        # Create Snowpark session
        session = Session.builder.configs(connection_parameters).create()
        
        print("✅ Snowpark session created successfully!")
        
        # Test queries
        print("\n" + "-" * 70)
        print("\n🧪 Running test queries...\n")
        
        # Test 1: Current context
        print("1️⃣  Testing current context...")
        df = session.sql("""
            SELECT 
                CURRENT_ACCOUNT() as account,
                CURRENT_USER() as user,
                CURRENT_ROLE() as role,
                CURRENT_WAREHOUSE() as warehouse,
                CURRENT_REGION() as region
        """).collect()
        
        result = df[0]
        print(f"   ✅ Account: {result['ACCOUNT']}")
        print(f"   ✅ User: {result['USER']}")
        print(f"   ✅ Role: {result['ROLE']}")
        print(f"   ✅ Warehouse: {result['WAREHOUSE']}")
        print(f"   ✅ Region: {result['REGION']}")
        
        # Test 2: Warehouse status
        print("\n2️⃣  Checking warehouse status...")
        df = session.sql(f"""
            SELECT warehouse_name, state, warehouse_size, warehouse_type
            FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSES 
            WHERE warehouse_name = '{config.get('warehouse')}'
            LIMIT 1
        """).collect()
        
        if df:
            result = df[0]
            print(f"   ✅ Warehouse: {result['WAREHOUSE_NAME']}")
            print(f"   ✅ Status: {result['STATE']}")
            print(f"   ✅ Size: {result['WAREHOUSE_SIZE']}")
            print(f"   ✅ Type: {result['WAREHOUSE_TYPE']}")
        else:
            print(f"   ⚠️  Warehouse info not found in ACCOUNT_USAGE (may take time to appear)")
        
        # Test 3: ACCOUNT_USAGE access
        print("\n3️⃣  Testing ACCOUNT_USAGE access...")
        df = session.sql("""
            SELECT COUNT(*) as query_count
            FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY 
            WHERE START_TIME >= DATEADD(day, -1, CURRENT_TIMESTAMP())
        """).collect()
        
        result = df[0]
        print(f"   ✅ Can access ACCOUNT_USAGE")
        print(f"   ✅ Queries in last 24h: {result['QUERY_COUNT']:,}")
        
        # Test 4: Database and schema info
        print("\n4️⃣  Testing database access...")
        df = session.sql("""
            SELECT COUNT(*) as db_count
            FROM SNOWFLAKE.ACCOUNT_USAGE.DATABASES
            WHERE DELETED IS NULL
        """).collect()
        
        result = df[0]
        print(f"   ✅ Active databases: {result['DB_COUNT']:,}")
        
        # Test 5: User info
        print("\n5️⃣  Testing user information...")
        df = session.sql("""
            SELECT 
                COUNT(*) as total_users,
                SUM(CASE WHEN has_mfa THEN 1 ELSE 0 END) as mfa_users
            FROM SNOWFLAKE.ACCOUNT_USAGE.USERS
            WHERE DELETED_ON IS NULL
        """).collect()
        
        result = df[0]
        print(f"   ✅ Total users: {result['TOTAL_USERS']:,}")
        print(f"   ✅ Users with MFA: {result['MFA_USERS']:,}")
        
        # Test 6: Simple computation
        print("\n6️⃣  Testing data frame operations...")
        df = session.sql("SELECT 1 + 1 as result, 'Hello' || ' Snowflake' as greeting").collect()
        result = df[0]
        print(f"   ✅ Math: 1 + 1 = {result['RESULT']}")
        print(f"   ✅ String: {result['GREETING']}")
        
        # Test 7: Pandas conversion
        print("\n7️⃣  Testing Pandas conversion...")
        df_pandas = session.sql("SELECT 1 as col1, 2 as col2, 3 as col3").to_pandas()
        print(f"   ✅ Converted to Pandas: {df_pandas.shape[0]} rows, {df_pandas.shape[1]} columns")
        print(f"   ✅ Columns: {list(df_pandas.columns)}")
        
        # Close session
        session.close()
        
        # Success summary
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\n🎉 Your Snowflake connection is working correctly with Snowpark!")
        print("   You can now run the Streamlit application.\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Provide specific guidance based on error
        error_msg = str(e).lower()
        print("\n🔍 Troubleshooting:")
        
        if 'incorrect username or password' in error_msg:
            print("  - Check your username and password in .streamlit/secrets.toml")
        elif 'account' in error_msg:
            print("  - Verify the account name format (should be like 'xy12345.region')")
        elif 'warehouse' in error_msg:
            print("  - Check that the warehouse exists and you have access to it")
        elif 'role' in error_msg:
            print("  - Verify the role exists and is granted to your user")
        elif 'account_usage' in error_msg:
            print("  - You need IMPORTED PRIVILEGES on SNOWFLAKE database")
            print("  - Or use ACCOUNTADMIN role which has access by default")
        else:
            print("  - Check your network connection")
            print("  - Verify all credentials in .streamlit/secrets.toml")
            print("  - Ensure the Snowflake account is active")
        
        return False


def main():
    """Main function"""
    print("\n")
    
    # Load secrets
    config = load_secrets()
    
    # Validate required fields
    required_fields = ['account', 'user', 'password', 'role', 'warehouse']
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        print(f"❌ Missing required configuration fields: {', '.join(missing_fields)}")
        print("\nPlease update .streamlit/secrets.toml with all required fields.")
        sys.exit(1)
    
    # Test connection
    success = test_connection_snowpark(config)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()


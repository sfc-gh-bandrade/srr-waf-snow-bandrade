#!/usr/bin/env python3
"""
Test Snowflake Connection Script
Tests connection to Snowflake using credentials from .streamlit/secrets.toml
"""

import sys
import os
from pathlib import Path

try:
    import toml
    import snowflake.connector
    from snowflake.connector import DictCursor
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("\nPlease install required packages:")
    print("  pip install snowflake-connector-python toml")
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


def test_connection(config):
    """Test Snowflake connection"""
    print("=" * 70)
    print("🔗 SNOWFLAKE CONNECTION TEST")
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
    print("\n🔄 Attempting to connect to Snowflake...")
    
    try:
        # Build connection parameters
        conn_params = {
            'account': config.get('account'),
            'user': config.get('user'),
            'password': config.get('password'),
            'role': config.get('role'),
            'warehouse': config.get('warehouse'),
        }
        
        # Add optional parameters
        if 'database' in config:
            conn_params['database'] = config['database']
        if 'schema' in config:
            conn_params['schema'] = config['schema']
        if 'authenticator' in config:
            conn_params['authenticator'] = config['authenticator']
        
        # Connect
        conn = snowflake.connector.connect(**conn_params)
        
        print("✅ Connection successful!")
        
        # Test queries
        print("\n" + "-" * 70)
        print("\n🧪 Running test queries...\n")
        
        cursor = conn.cursor(DictCursor)
        
        # Test 1: Current account
        print("1️⃣  Testing CURRENT_ACCOUNT()...")
        cursor.execute("SELECT CURRENT_ACCOUNT() as account")
        result = cursor.fetchone()
        print(f"   ✅ Account: {result['ACCOUNT']}")
        
        # Test 2: Current user and role
        print("\n2️⃣  Testing CURRENT_USER() and CURRENT_ROLE()...")
        cursor.execute("SELECT CURRENT_USER() as user, CURRENT_ROLE() as role")
        result = cursor.fetchone()
        print(f"   ✅ User: {result['USER']}")
        print(f"   ✅ Role: {result['ROLE']}")
        
        # Test 3: Current warehouse
        print("\n3️⃣  Testing CURRENT_WAREHOUSE()...")
        cursor.execute("SELECT CURRENT_WAREHOUSE() as warehouse")
        result = cursor.fetchone()
        print(f"   ✅ Warehouse: {result['WAREHOUSE']}")
        
        # Test 4: Warehouse status
        print("\n4️⃣  Checking warehouse status...")
        cursor.execute(f"""
            SELECT warehouse_name, state, warehouse_size
            FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSES 
            WHERE warehouse_name = '{config.get('warehouse')}'
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            print(f"   ✅ Warehouse: {result['WAREHOUSE_NAME']}")
            print(f"   ✅ Status: {result['STATE']}")
            print(f"   ✅ Size: {result['WAREHOUSE_SIZE']}")
        
        # Test 5: ACCOUNT_USAGE access
        print("\n5️⃣  Testing ACCOUNT_USAGE access...")
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY 
            WHERE START_TIME >= DATEADD(day, -1, CURRENT_TIMESTAMP())
        """)
        result = cursor.fetchone()
        print(f"   ✅ Can access ACCOUNT_USAGE")
        print(f"   ✅ Queries in last 24h: {result['COUNT']:,}")
        
        # Test 6: Simple math operation
        print("\n6️⃣  Testing basic query execution...")
        cursor.execute("SELECT 1 + 1 as result")
        result = cursor.fetchone()
        print(f"   ✅ Query execution: 1 + 1 = {result['RESULT']}")
        
        cursor.close()
        conn.close()
        
        # Success summary
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\n🎉 Your Snowflake connection is working correctly!")
        print("   You can now run the Streamlit application.\n")
        
        return True
        
    except snowflake.connector.errors.ProgrammingError as e:
        print(f"\n❌ Snowflake Programming Error: {e}")
        print("\nPossible causes:")
        print("  - Invalid SQL syntax")
        print("  - Missing permissions (need ACCOUNT_USAGE access)")
        print("  - Role doesn't have access to the warehouse")
        return False
        
    except snowflake.connector.errors.DatabaseError as e:
        print(f"\n❌ Snowflake Database Error: {e}")
        print("\nPossible causes:")
        print("  - Invalid credentials")
        print("  - Account name is incorrect")
        print("  - Network connectivity issues")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        print(f"   Error type: {type(e).__name__}")
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
    success = test_connection(config)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()


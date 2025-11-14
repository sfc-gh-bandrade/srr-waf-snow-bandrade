import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import snowflake.connector

# Page configuration
st.set_page_config(
    page_title="Snowflake Well-Architected Framework Review",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #29B5E8;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #29B5E8;
    }
    .warning-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .success-card {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .danger-card {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Snowflake connection
@st.cache_resource
def get_snowflake_connection():
    """
    Create Snowflake connection using Streamlit secrets.
    
    Configure your connection in .streamlit/secrets.toml:
    [snowflake]
    account = "your_account"
    user = "your_username"
    password = "your_password"
    role = "ACCOUNTADMIN"
    warehouse = "your_warehouse"
    """
    try:
        conn = snowflake.connector.connect(
            account=st.secrets["snowflake"]["account"],
            user=st.secrets["snowflake"]["user"],
            password=st.secrets["snowflake"]["password"],
            role=st.secrets["snowflake"]["role"],
            warehouse=st.secrets["snowflake"]["warehouse"]
        )
        return conn
    except KeyError as e:
        st.error(f"Missing configuration in secrets.toml: {e}")
        st.info("""
        Please create a `.streamlit/secrets.toml` file with your Snowflake credentials:
        
        ```toml
        [snowflake]
        account = "your_account"
        user = "your_username"
        password = "your_password"
        role = "ACCOUNTADMIN"
        warehouse = "your_warehouse"
        ```
        """)
        st.stop()
    except Exception as e:
        st.error(f"Unable to connect to Snowflake: {str(e)}")
        st.stop()

def execute_query(query):
    """Execute a SQL query and return results as a pandas DataFrame"""
    conn = get_snowflake_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=columns)
        cursor.close()
        return df
    except Exception as e:
        st.error(f"Query execution error: {str(e)}")
        return pd.DataFrame()

# Test connection
try:
    conn = get_snowflake_connection()
    st.success("✅ Connected to Snowflake successfully!")
except:
    st.stop()

# Sidebar configuration
with st.sidebar:
    st.image("https://www.snowflake.com/wp-content/themes/snowflake/assets/img/brand-guidelines/logo-sno-blue-example.svg", width=200)
    st.title("Configuration")
    
    # Date range selector
    days_back = st.slider("Analysis Period (days)", 7, 90, 30)
    start_date = datetime.now() - timedelta(days=days_back)
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This application analyzes your Snowflake account based on the 
    **Well-Architected Framework** best practices:
    
    - 🚀 **Performance**
    - 🛡️ **Reliability**
    - ⚙️ **Operational Excellence**
    - 🔒 **Security & Governance**
    - 💰 **Cost Optimization**
    """)
    
    st.markdown("---")
    st.markdown("### Connection Info")
    try:
        conn_info = execute_query("SELECT CURRENT_ACCOUNT() as ACCOUNT, CURRENT_USER() as USER, CURRENT_ROLE() as ROLE, CURRENT_WAREHOUSE() as WAREHOUSE")
        if not conn_info.empty:
            st.text(f"Account: {conn_info['ACCOUNT'][0]}")
            st.text(f"User: {conn_info['USER'][0]}")
            st.text(f"Role: {conn_info['ROLE'][0]}")
            st.text(f"Warehouse: {conn_info['WAREHOUSE'][0]}")
    except:
        pass

# Main header
st.markdown('<p class="main-header">❄️ Snowflake Well-Architected Framework Review</p>', unsafe_allow_html=True)

# Create tabs for each pillar
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 Performance",
    "🛡️ Reliability", 
    "⚙️ Operational Excellence",
    "🔒 Security & Governance",
    "💰 Cost Optimization"
])

# ============================================================================
# TAB 1: PERFORMANCE
# ============================================================================
with tab1:
    st.header("Performance Efficiency")
    st.markdown("""
    Best practices from [Snowflake Well-Architected Framework - Performance](https://www.snowflake.com/en/developers/guides/well-architected-framework-performance/)
    """)
    
    # Query 1: Warehouse Performance and Utilization
    st.subheader("1. Warehouse Utilization & Efficiency")
    
    query_wh_utilization = f"""
    SELECT 
        warehouse_name,
        COUNT(DISTINCT query_id) as total_queries,
        AVG(execution_time) / 1000 as avg_execution_time_sec,
        AVG(queued_overload_time) / 1000 as avg_queue_time_sec,
        SUM(credits_used_cloud_services) as cloud_services_credits,
        AVG(CASE 
            WHEN execution_time > 0 THEN (queued_overload_time / execution_time) * 100 
            ELSE 0 
        END) as queue_time_pct
    FROM snowflake.account_usage.query_history
    WHERE start_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
        AND warehouse_name IS NOT NULL
    GROUP BY warehouse_name
    ORDER BY total_queries DESC
    """
    
    try:
        df_wh_util = execute_query(query_wh_utilization)
        
        if not df_wh_util.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_queries = px.bar(
                    df_wh_util.head(10),
                    x='WAREHOUSE_NAME',
                    y='TOTAL_QUERIES',
                    title='Top 10 Warehouses by Query Volume',
                    labels={'TOTAL_QUERIES': 'Number of Queries', 'WAREHOUSE_NAME': 'Warehouse'}
                )
                st.plotly_chart(fig_queries, use_container_width=True)
            
            with col2:
                fig_queue = px.bar(
                    df_wh_util.head(10),
                    x='WAREHOUSE_NAME',
                    y='QUEUE_TIME_PCT',
                    title='Queue Time as % of Execution Time',
                    labels={'QUEUE_TIME_PCT': 'Queue Time %', 'WAREHOUSE_NAME': 'Warehouse'},
                    color='QUEUE_TIME_PCT',
                    color_continuous_scale=['green', 'yellow', 'red']
                )
                st.plotly_chart(fig_queue, use_container_width=True)
            
            # Recommendations
            high_queue_wh = df_wh_util[df_wh_util['QUEUE_TIME_PCT'] > 20]
            if not high_queue_wh.empty:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning(f"⚠️ **Recommendation**: {len(high_queue_wh)} warehouse(s) have >20% queue time. Consider increasing warehouse size or enabling multi-cluster.")
                st.dataframe(high_queue_wh[['WAREHOUSE_NAME', 'QUEUE_TIME_PCT', 'AVG_QUEUE_TIME_SEC']])
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.success("✅ No warehouses with excessive queue times detected.")
                
    except Exception as e:
        st.error(f"Error fetching warehouse utilization: {str(e)}")
    
    st.markdown("---")
    st.info("💡 **Note**: This is the local version. For full functionality, see app.py for Snowflake-native Streamlit.")
    st.markdown("Additional performance metrics are available in the full application.")

# ============================================================================
# TAB 2: RELIABILITY
# ============================================================================
with tab2:
    st.header("Reliability & Resilience")
    st.markdown("""
    Best practices from [Snowflake Well-Architected Framework - Reliability](https://www.snowflake.com/en/developers/guides/well-architected-framework-reliability/)
    """)
    
    st.info("💡 **Note**: This is the local version. For full functionality, see app.py for Snowflake-native Streamlit.")

# ============================================================================
# TAB 3: OPERATIONAL EXCELLENCE
# ============================================================================
with tab3:
    st.header("Operational Excellence")
    st.markdown("""
    Best practices from [Snowflake Well-Architected Framework - Operational Excellence](https://www.snowflake.com/en/developers/guides/well-architected-framework-operational-excellence/)
    """)
    
    st.info("💡 **Note**: This is the local version. For full functionality, see app.py for Snowflake-native Streamlit.")

# ============================================================================
# TAB 4: SECURITY & GOVERNANCE
# ============================================================================
with tab4:
    st.header("Security & Governance")
    st.markdown("""
    Best practices from [Snowflake Well-Architected Framework - Security & Governance](https://www.snowflake.com/en/developers/guides/well-architected-framework-security-and-governance/)
    """)
    
    st.info("💡 **Note**: This is the local version. For full functionality, see app.py for Snowflake-native Streamlit.")

# ============================================================================
# TAB 5: COST OPTIMIZATION
# ============================================================================
with tab5:
    st.header("Cost Optimization & FinOps")
    st.markdown("""
    Best practices from [Snowflake Well-Architected Framework - Cost Optimization](https://www.snowflake.com/en/developers/guides/well-architected-framework-cost-optimization-and-finops/)
    """)
    
    st.info("💡 **Note**: This is the local version. For full functionality, see app.py for Snowflake-native Streamlit.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with ❄️ Streamlit | Based on Snowflake Well-Architected Framework</p>
    <p><a href="https://www.snowflake.com/en/developers/guides/well-architected-framework/">Learn more about Snowflake Well-Architected Framework</a></p>
    <p><strong>Running in LOCAL mode</strong> - For full app functionality, deploy to Snowflake Streamlit</p>
</div>
""", unsafe_allow_html=True)


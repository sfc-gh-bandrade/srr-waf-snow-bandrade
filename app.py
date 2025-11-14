import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from snowflake.snowpark.context import get_active_session
from datetime import datetime, timedelta

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

# Initialize Snowflake session
@st.cache_resource
def get_snowflake_session():
    try:
        session = get_active_session()
        return session
    except:
        st.error("Unable to connect to Snowflake. Please ensure you're running this in a Snowflake Streamlit app.")
        return None

session = get_snowflake_session()

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

# Main header
st.markdown('<p class="main-header">❄️ Snowflake Well-Architected Framework Review</p>', unsafe_allow_html=True)

if session is None:
    st.stop()

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
        df_wh_util = session.sql(query_wh_utilization).to_pandas()
        
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
    
    # Query 2: Query Performance Analysis
    st.subheader("2. Query Performance Analysis")
    
    query_performance = f"""
    SELECT 
        DATE_TRUNC('day', start_time) as query_date,
        COUNT(*) as query_count,
        AVG(execution_time) / 1000 as avg_exec_time_sec,
        AVG(bytes_scanned) / POWER(1024, 3) as avg_gb_scanned,
        AVG(partitions_scanned) as avg_partitions_scanned,
        AVG(partitions_total) as avg_partitions_total,
        COUNT(CASE WHEN execution_time > 60000 THEN 1 END) as slow_queries_count,
        AVG(CASE 
            WHEN partitions_total > 0 THEN (partitions_scanned::FLOAT / partitions_total) * 100 
            ELSE 0 
        END) as avg_partition_scan_pct
    FROM snowflake.account_usage.query_history
    WHERE start_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
        AND execution_status = 'SUCCESS'
        AND query_type IN ('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'MERGE')
    GROUP BY DATE_TRUNC('day', start_time)
    ORDER BY query_date DESC
    """
    
    try:
        df_perf = session.sql(query_performance).to_pandas()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_exec_time = px.line(
                df_perf,
                x='QUERY_DATE',
                y='AVG_EXEC_TIME_SEC',
                title='Average Query Execution Time Trend',
                labels={'AVG_EXEC_TIME_SEC': 'Avg Execution Time (sec)', 'QUERY_DATE': 'Date'}
            )
            st.plotly_chart(fig_exec_time, use_container_width=True)
        
        with col2:
            fig_partition = px.line(
                df_perf,
                x='QUERY_DATE',
                y='AVG_PARTITION_SCAN_PCT',
                title='Average Partition Scan Efficiency',
                labels={'AVG_PARTITION_SCAN_PCT': 'Partitions Scanned %', 'QUERY_DATE': 'Date'}
            )
            st.plotly_chart(fig_partition, use_container_width=True)
        
        # Show metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Queries", f"{df_perf['QUERY_COUNT'].sum():,.0f}")
        with col2:
            st.metric("Avg Execution Time", f"{df_perf['AVG_EXEC_TIME_SEC'].mean():.2f}s")
        with col3:
            st.metric("Slow Queries (>1min)", f"{df_perf['SLOW_QUERIES_COUNT'].sum():,.0f}")
        with col4:
            st.metric("Avg GB Scanned", f"{df_perf['AVG_GB_SCANNED'].mean():.2f}")
        
        # Recommendations
        avg_partition_pct = df_perf['AVG_PARTITION_SCAN_PCT'].mean()
        if avg_partition_pct > 50:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.warning(f"⚠️ **Recommendation**: Average partition scan is {avg_partition_pct:.1f}%. Consider adding clustering keys to frequently queried large tables to improve pruning.")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success(f"✅ Good partition pruning efficiency: {avg_partition_pct:.1f}% of partitions scanned on average.")
            
    except Exception as e:
        st.error(f"Error fetching query performance: {str(e)}")
    
    st.markdown("---")
    
    # Query 3: Clustering Information
    st.subheader("3. Automatic Clustering Activity")
    
    query_clustering = f"""
    SELECT 
        database_name,
        schema_name,
        table_name,
        COUNT(*) as reclustering_events,
        SUM(credits_used) as total_credits_used,
        SUM(num_bytes_reclustered) / POWER(1024, 3) as total_gb_reclustered,
        SUM(num_rows_reclustered) as total_rows_reclustered,
        AVG(credits_used) as avg_credits_per_event,
        MAX(end_time) as last_reclustered
    FROM snowflake.account_usage.automatic_clustering_history
    WHERE start_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
    GROUP BY database_name, schema_name, table_name
    ORDER BY total_credits_used DESC
    LIMIT 20
    """
    
    try:
        df_clustering = session.sql(query_clustering).to_pandas()
        
        if not df_clustering.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_clustering_credits = px.bar(
                    df_clustering.head(10),
                    x='TABLE_NAME',
                    y='TOTAL_CREDITS_USED',
                    title='Top 10 Tables by Clustering Credits',
                    labels={'TOTAL_CREDITS_USED': 'Credits Used', 'TABLE_NAME': 'Table'},
                    color='TOTAL_CREDITS_USED',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_clustering_credits, use_container_width=True)
            
            with col2:
                fig_clustering_events = px.bar(
                    df_clustering.head(10),
                    x='TABLE_NAME',
                    y='RECLUSTERING_EVENTS',
                    title='Top 10 Tables by Reclustering Events',
                    labels={'RECLUSTERING_EVENTS': 'Number of Events', 'TABLE_NAME': 'Table'}
                )
                st.plotly_chart(fig_clustering_events, use_container_width=True)
            
            # Summary metrics
            total_clustering_credits = df_clustering['TOTAL_CREDITS_USED'].sum()
            total_gb_reclustered = df_clustering['TOTAL_GB_RECLUSTERED'].sum()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Clustering Credits", f"{total_clustering_credits:.2f}")
            with col2:
                st.metric("Total GB Reclustered", f"{total_gb_reclustered:.2f}")
            with col3:
                st.metric("Tables with Clustering", len(df_clustering))
            
            st.markdown("**Detailed Clustering Activity:**")
            st.dataframe(
                df_clustering,
                column_config={
                    "DATABASE_NAME": "Database",
                    "SCHEMA_NAME": "Schema",
                    "TABLE_NAME": "Table",
                    "RECLUSTERING_EVENTS": "Events",
                    "TOTAL_CREDITS_USED": st.column_config.NumberColumn("Total Credits", format="%.2f"),
                    "TOTAL_GB_RECLUSTERED": st.column_config.NumberColumn("GB Reclustered", format="%.2f"),
                    "TOTAL_ROWS_RECLUSTERED": st.column_config.NumberColumn("Rows Reclustered", format="%.0f"),
                    "AVG_CREDITS_PER_EVENT": st.column_config.NumberColumn("Avg Credits/Event", format="%.4f"),
                    "LAST_RECLUSTERED": "Last Reclustered"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Check for high clustering costs
            high_cost_tables = df_clustering[df_clustering['TOTAL_CREDITS_USED'] > 1.0]
            if not high_cost_tables.empty:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning(f"⚠️ **{len(high_cost_tables)} table(s) with >1 credit in clustering costs**. Review clustering key effectiveness and consider manual optimization.")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.info("💡 **Tip**: High reclustering activity may indicate frequent DML operations on clustered tables. Evaluate if clustering keys are optimal for your query patterns.")
        else:
            st.info("ℹ️ No automatic clustering activity detected in the selected period. This may indicate no clustered tables or no reclustering was needed.")
            
    except Exception as e:
        st.info(f"Clustering analysis unavailable: {str(e)}")
    
    st.markdown("---")
    
    # Query 4: Result Cache Hit Rate
    st.subheader("4. Result Cache Efficiency")
    
    query_cache = f"""
    WITH cache_analysis AS (
        SELECT 
            DATE_TRUNC('day', start_time) as query_date,
            query_id,
            query_type,
            execution_status,
            bytes_scanned,
            partitions_scanned,
            execution_time,
            CASE 
                WHEN execution_status = 'SUCCESS' 
                    AND bytes_scanned = 0 
                    AND partitions_scanned = 0
                    AND execution_time < 1000  -- Less than 1 second (likely cache hit)
                THEN 1 
                ELSE 0 
            END as is_cache_hit
        FROM snowflake.account_usage.query_history
        WHERE start_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
            AND query_type = 'SELECT'
            AND execution_status = 'SUCCESS'
    )
    SELECT 
        query_date,
        COUNT(*) as total_queries,
        SUM(is_cache_hit) as cache_hits,
        (SUM(is_cache_hit)::FLOAT / COUNT(*)) * 100 as cache_hit_rate,
        AVG(execution_time) / 1000 as avg_execution_time_sec
    FROM cache_analysis
    GROUP BY query_date
    ORDER BY query_date DESC
    """
    
    try:
        df_cache = session.sql(query_cache).to_pandas()
        
        if not df_cache.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_cache = px.line(
                    df_cache,
                    x='QUERY_DATE',
                    y='CACHE_HIT_RATE',
                    title='Result Cache Hit Rate Over Time',
                    labels={'CACHE_HIT_RATE': 'Cache Hit Rate (%)', 'QUERY_DATE': 'Date'},
                    markers=True
                )
                fig_cache.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Target: >50%")
                st.plotly_chart(fig_cache, use_container_width=True)
            
            with col2:
                # Cache hits vs total queries
                fig_cache_volume = go.Figure()
                fig_cache_volume.add_trace(go.Bar(
                    x=df_cache['QUERY_DATE'],
                    y=df_cache['TOTAL_QUERIES'],
                    name='Total Queries',
                    marker_color='lightblue'
                ))
                fig_cache_volume.add_trace(go.Bar(
                    x=df_cache['QUERY_DATE'],
                    y=df_cache['CACHE_HITS'],
                    name='Cache Hits',
                    marker_color='green'
                ))
                fig_cache_volume.update_layout(
                    title='Query Volume: Total vs Cache Hits',
                    xaxis_title='Date',
                    yaxis_title='Number of Queries',
                    barmode='overlay'
                )
                st.plotly_chart(fig_cache_volume, use_container_width=True)
            
            # Summary metrics
            avg_cache_rate = df_cache['CACHE_HIT_RATE'].mean()
            total_queries = df_cache['TOTAL_QUERIES'].sum()
            total_cache_hits = df_cache['CACHE_HITS'].sum()
            avg_exec_time = df_cache['AVG_EXECUTION_TIME_SEC'].mean()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Cache Hit Rate", f"{avg_cache_rate:.1f}%")
            with col2:
                st.metric("Total Queries", f"{total_queries:,.0f}")
            with col3:
                st.metric("Total Cache Hits", f"{total_cache_hits:,.0f}")
            with col4:
                st.metric("Avg Query Time", f"{avg_exec_time:.2f}s")
            
            # Recommendations
            if avg_cache_rate < 30:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning(f"⚠️ **Recommendation**: Cache hit rate is {avg_cache_rate:.1f}%. This may indicate unique queries or short cache retention. Review query patterns for optimization opportunities.")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.success(f"✅ Good cache utilization: {avg_cache_rate:.1f}% hit rate.")
            
            st.info("💡 **Note**: Result cache hits are identified by queries that scan 0 bytes/partitions and complete in <1 second, indicating data was retrieved from cache rather than storage.")
        else:
            st.info("No cache data available for the selected period.")
            
    except Exception as e:
        st.error(f"Error fetching cache data: {str(e)}")

# ============================================================================
# TAB 2: RELIABILITY
# ============================================================================
with tab2:
    st.header("Reliability & Resilience")
    st.markdown("""
    Best practices from [Snowflake Well-Architected Framework - Reliability](https://www.snowflake.com/en/developers/guides/well-architected-framework-reliability/)
    """)
    
    # Query 1: Database Configuration & Resilience
    st.subheader("1. Database Configuration & Resilience")
    
    query_databases = """
    SELECT 
        database_name,
        database_owner,
        type,
        is_transient,
        retention_time,
        created,
        last_altered,
        CASE 
            WHEN type = 'IMPORTED DATABASE' THEN 'Replicated from Share'
            WHEN type = 'STANDARD' THEN 'Standard Database'
            WHEN type = 'APPLICATION' THEN 'Native App'
            WHEN type = 'APPLICATION_PACKAGE' THEN 'App Package'
            ELSE type
        END as database_type_desc,
        DATEDIFF(day, created, CURRENT_TIMESTAMP()) as age_days
    FROM snowflake.account_usage.databases
    WHERE deleted IS NULL
    ORDER BY database_name
    """
    
    try:
        df_databases = session.sql(query_databases).to_pandas()
        
        if not df_databases.empty:
            # Analyze database types
            type_counts = df_databases['DATABASE_TYPE_DESC'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_db_types = px.pie(
                    values=type_counts.values,
                    names=type_counts.index,
                    title='Database Types Distribution',
                    hole=0.4
                )
                st.plotly_chart(fig_db_types, use_container_width=True)
            
            with col2:
                # Retention time distribution
                fig_retention = px.histogram(
                    df_databases,
                    x='RETENTION_TIME',
                    title='Time Travel Retention Distribution (Days)',
                    labels={'RETENTION_TIME': 'Retention Days', 'count': 'Number of Databases'},
                    nbins=20
                )
                st.plotly_chart(fig_retention, use_container_width=True)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Databases", len(df_databases))
            with col2:
                transient_count = len(df_databases[df_databases['IS_TRANSIENT'] == 'YES'])
                st.metric("Transient Databases", transient_count)
            with col3:
                avg_retention = df_databases['RETENTION_TIME'].mean()
                st.metric("Avg Retention Time", f"{avg_retention:.0f} days")
            with col4:
                imported_count = len(df_databases[df_databases['TYPE'] == 'IMPORTED DATABASE'])
                st.metric("Replicated Databases", imported_count)
            
            # Check for potential issues
            low_retention = df_databases[df_databases['RETENTION_TIME'] < 1]
            transient_dbs = df_databases[df_databases['IS_TRANSIENT'] == 'YES']
            
            if not low_retention.empty:
                st.markdown('<div class="danger-card">', unsafe_allow_html=True)
                st.error(f"⚠️ **Critical**: {len(low_retention)} database(s) have Time Travel retention < 1 day. This limits disaster recovery options!")
                st.dataframe(
                    low_retention[['DATABASE_NAME', 'DATABASE_TYPE_DESC', 'RETENTION_TIME', 'IS_TRANSIENT']],
                    hide_index=True,
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            if not transient_dbs.empty:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning(f"⚠️ **Warning**: {len(transient_dbs)} transient database(s) have reduced Fail-safe protection (0 days vs 7 days for standard databases).")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Detailed database information
            st.markdown("**Database Configuration Details:**")
            st.dataframe(
                df_databases[[
                    'DATABASE_NAME', 'DATABASE_OWNER', 'DATABASE_TYPE_DESC', 
                    'IS_TRANSIENT', 'RETENTION_TIME', 'AGE_DAYS', 'CREATED'
                ]],
                column_config={
                    "DATABASE_NAME": "Database",
                    "DATABASE_OWNER": "Owner Role",
                    "DATABASE_TYPE_DESC": "Type",
                    "IS_TRANSIENT": "Transient",
                    "RETENTION_TIME": st.column_config.NumberColumn("Time Travel (days)", format="%d"),
                    "AGE_DAYS": st.column_config.NumberColumn("Age (days)", format="%d"),
                    "CREATED": "Created Date"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Recommendations
            st.info("""
            💡 **Reliability Best Practices**:
            - **Time Travel**: Standard databases should have 1-90 days retention for disaster recovery
            - **Transient Databases**: Use only for non-critical data (no Fail-safe protection)
            - **Database Replication**: Configure replication to secondary regions for critical databases
            - **Imported Databases**: Monitor share providers for data availability
            """)
            
        else:
            st.info("No databases found in the account.")
            
        # Check for active replication
        st.markdown("---")
        st.markdown("**Database Replication Activity:**")
        
        query_replication_usage = f"""
        SELECT 
            database_name,
            COUNT(*) as replication_events,
            SUM(credits_used) as total_replication_credits,
            SUM(bytes_transferred) / POWER(1024, 3) as total_gb_transferred,
            MAX(end_time) as last_replication_time,
            DATEDIFF(hour, MAX(end_time), CURRENT_TIMESTAMP()) as hours_since_last_replication,
            AVG(credits_used) as avg_credits_per_event
        FROM snowflake.account_usage.database_replication_usage_history
        WHERE start_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
        GROUP BY database_name
        ORDER BY total_replication_credits DESC
        """
        
        try:
            df_replication = session.sql(query_replication_usage).to_pandas()
            
            if not df_replication.empty:
                st.success(f"✅ {len(df_replication)} database(s) have active replication configured")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_rep_credits = px.bar(
                        df_replication.head(10),
                        x='DATABASE_NAME',
                        y='TOTAL_REPLICATION_CREDITS',
                        title='Top 10 Databases by Replication Credits',
                        labels={'TOTAL_REPLICATION_CREDITS': 'Credits Used', 'DATABASE_NAME': 'Database'},
                        color='TOTAL_REPLICATION_CREDITS',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig_rep_credits, use_container_width=True)
                
                with col2:
                    fig_rep_gb = px.bar(
                        df_replication.head(10),
                        x='DATABASE_NAME',
                        y='TOTAL_GB_TRANSFERRED',
                        title='Top 10 Databases by Data Transferred',
                        labels={'TOTAL_GB_TRANSFERRED': 'GB Transferred', 'DATABASE_NAME': 'Database'},
                        color='TOTAL_GB_TRANSFERRED',
                        color_continuous_scale='Greens'
                    )
                    st.plotly_chart(fig_rep_gb, use_container_width=True)
                
                # Summary metrics
                total_credits = df_replication['TOTAL_REPLICATION_CREDITS'].sum()
                total_gb = df_replication['TOTAL_GB_TRANSFERRED'].sum()
                total_events = df_replication['REPLICATION_EVENTS'].sum()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Replication Credits", f"{total_credits:.2f}")
                with col2:
                    st.metric("Total GB Replicated", f"{total_gb:.2f}")
                with col3:
                    st.metric("Total Replication Events", f"{total_events:,.0f}")
                
                st.markdown("**Replication Activity Details:**")
                st.dataframe(
                    df_replication,
                    column_config={
                        "DATABASE_NAME": "Database",
                        "REPLICATION_EVENTS": st.column_config.NumberColumn("Events", format="%d"),
                        "TOTAL_REPLICATION_CREDITS": st.column_config.NumberColumn("Total Credits", format="%.2f"),
                        "TOTAL_GB_TRANSFERRED": st.column_config.NumberColumn("GB Transferred", format="%.2f"),
                        "AVG_CREDITS_PER_EVENT": st.column_config.NumberColumn("Avg Credits/Event", format="%.4f"),
                        "LAST_REPLICATION_TIME": "Last Replication",
                        "HOURS_SINCE_LAST_REPLICATION": st.column_config.NumberColumn("Hours Since Last", format="%d")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # Check for stale replication
                stale_replication = df_replication[df_replication['HOURS_SINCE_LAST_REPLICATION'] > 48]
                if not stale_replication.empty:
                    st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                    st.warning(f"⚠️ **{len(stale_replication)} database(s) haven't replicated in 48+ hours**. Verify replication schedules are active.")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.info("💡 **Note**: This view shows replication activity for **secondary databases** in the target account. Credits are consumed in the source account during replication.")
            else:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning("⚠️ **No database replication activity detected**. Consider enabling replication for critical databases to ensure business continuity and disaster recovery.")
                st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.info(f"Replication usage data unavailable: {str(e)}")
            
    except Exception as e:
        st.error(f"Error fetching database information: {str(e)}")
    
    st.markdown("---")
    
    # Query 2: Failed Queries and Error Analysis
    st.subheader("2. Query Failures & Error Analysis")
    
    query_failures = f"""
    SELECT 
        DATE_TRUNC('day', start_time) as failure_date,
        error_code,
        error_message,
        COUNT(*) as failure_count
    FROM snowflake.account_usage.query_history
    WHERE start_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
        AND execution_status IN ('FAILED', 'INCIDENT')
    GROUP BY DATE_TRUNC('day', start_time), error_code, error_message
    ORDER BY failure_count DESC
    LIMIT 20
    """
    
    try:
        df_failures = session.sql(query_failures).to_pandas()
        
        if not df_failures.empty:
            # Total failures over time
            df_failures_trend = df_failures.groupby('FAILURE_DATE')['FAILURE_COUNT'].sum().reset_index()
            
            fig_failures = px.line(
                df_failures_trend,
                x='FAILURE_DATE',
                y='FAILURE_COUNT',
                title='Query Failures Over Time',
                labels={'FAILURE_COUNT': 'Number of Failures', 'FAILURE_DATE': 'Date'}
            )
            st.plotly_chart(fig_failures, use_container_width=True)
            
            st.markdown('<div class="danger-card">', unsafe_allow_html=True)
            st.error(f"⚠️ **{df_failures['FAILURE_COUNT'].sum():,.0f} query failures** detected in the last {days_back} days")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("**Top Error Messages:**")
            st.dataframe(
                df_failures[['ERROR_CODE', 'ERROR_MESSAGE', 'FAILURE_COUNT']].head(10),
                column_config={
                    "ERROR_CODE": "Error Code",
                    "ERROR_MESSAGE": st.column_config.TextColumn("Error Message", width="large"),
                    "FAILURE_COUNT": "Count"
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.info("💡 **Tip**: Review error patterns and implement proper error handling, retries, and alerting.")
        else:
            st.success("✅ No query failures detected in the selected period.")
            
    except Exception as e:
        st.error(f"Error fetching failure data: {str(e)}")
    
    st.markdown("---")
    
    # Query 3: Data Pipeline Reliability (Snowpipe)
    st.subheader("3. Data Pipeline Reliability (Snowpipe)")
    
    query_pipes = """
    SELECT 
        pipe_catalog,
        pipe_schema,
        pipe_name,
        pipe_owner,
        is_autoingest_enabled,
        created,
        last_altered,
        DATEDIFF(day, last_altered, CURRENT_TIMESTAMP()) as days_since_modified,
        DATEDIFF(day, created, CURRENT_TIMESTAMP()) as pipe_age_days
    FROM snowflake.account_usage.pipes
    WHERE deleted IS NULL
    ORDER BY pipe_catalog, pipe_schema, pipe_name
    """
    
    try:
        df_pipes = session.sql(query_pipes).to_pandas()
        
        if not df_pipes.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Active Pipes", len(df_pipes))
                autoingest_enabled = len(df_pipes[df_pipes['IS_AUTOINGEST_ENABLED'] == 'true'])
                st.metric("Auto-Ingest Enabled", autoingest_enabled)
            
            with col2:
                avg_age = df_pipes['PIPE_AGE_DAYS'].mean()
                st.metric("Avg Pipe Age", f"{avg_age:.0f} days")
                stale_pipes = len(df_pipes[df_pipes['DAYS_SINCE_MODIFIED'] > 90])
                st.metric("Stale Pipes (>90 days)", stale_pipes)
            
            # Pie chart for auto-ingest configuration
            autoingest_counts = df_pipes['IS_AUTOINGEST_ENABLED'].value_counts()
            fig_autoingest = px.pie(
                values=autoingest_counts.values,
                names=['Auto-Ingest: ' + str(name) for name in autoingest_counts.index],
                title='Auto-Ingest Configuration',
                hole=0.4
            )
            st.plotly_chart(fig_autoingest, use_container_width=True)
            
            st.markdown("**Pipe Configuration:**")
            st.dataframe(
                df_pipes,
                column_config={
                    "PIPE_CATALOG": "Database",
                    "PIPE_SCHEMA": "Schema",
                    "PIPE_NAME": "Pipe Name",
                    "PIPE_OWNER": "Owner Role",
                    "IS_AUTOINGEST_ENABLED": "Auto-Ingest",
                    "CREATED": "Created",
                    "LAST_ALTERED": "Last Modified",
                    "DAYS_SINCE_MODIFIED": st.column_config.NumberColumn("Days Since Modified", format="%d"),
                    "PIPE_AGE_DAYS": st.column_config.NumberColumn("Pipe Age (days)", format="%d")
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Check for stale pipes
            if stale_pipes > 0:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning(f"⚠️ **{stale_pipes} pipe(s) haven't been modified in 90+ days**. Review if these pipes are still needed or require maintenance.")
                st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.info("✅ No Snowpipe objects found in the account.")
            
        # Check pipe usage and errors
        st.markdown("---")
        st.markdown("**Snowpipe Usage & Performance:**")
        
        query_pipe_usage = f"""
        SELECT 
            pipe_name,
            COUNT(*) as load_events,
            SUM(files_inserted) as total_files_loaded,
            SUM(rows_inserted) as total_rows_loaded,
            SUM(bytes_inserted) / POWER(1024, 3) as total_gb_loaded,
            SUM(credits_used) as total_credits_used,
            MAX(end_time) as last_load_time,
            DATEDIFF(hour, MAX(end_time), CURRENT_TIMESTAMP()) as hours_since_last_load
        FROM snowflake.account_usage.pipe_usage_history
        WHERE start_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
        GROUP BY pipe_name
        ORDER BY total_credits_used DESC
        LIMIT 20
        """
        
        try:
            df_pipe_usage = session.sql(query_pipe_usage).to_pandas()
            
            if not df_pipe_usage.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_pipe_credits = px.bar(
                        df_pipe_usage.head(10),
                        x='PIPE_NAME',
                        y='TOTAL_CREDITS_USED',
                        title='Top 10 Pipes by Credits Used',
                        labels={'TOTAL_CREDITS_USED': 'Credits Used', 'PIPE_NAME': 'Pipe Name'}
                    )
                    st.plotly_chart(fig_pipe_credits, use_container_width=True)
                
                with col2:
                    fig_pipe_files = px.bar(
                        df_pipe_usage.head(10),
                        x='PIPE_NAME',
                        y='TOTAL_FILES_LOADED',
                        title='Top 10 Pipes by Files Loaded',
                        labels={'TOTAL_FILES_LOADED': 'Files Loaded', 'PIPE_NAME': 'Pipe Name'}
                    )
                    st.plotly_chart(fig_pipe_files, use_container_width=True)
                
                # Summary metrics
                total_files = df_pipe_usage['TOTAL_FILES_LOADED'].sum()
                total_rows = df_pipe_usage['TOTAL_ROWS_LOADED'].sum()
                total_gb = df_pipe_usage['TOTAL_GB_LOADED'].sum()
                total_credits = df_pipe_usage['TOTAL_CREDITS_USED'].sum()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Files Loaded", f"{total_files:,.0f}")
                with col2:
                    st.metric("Total Rows Loaded", f"{total_rows:,.0f}")
                with col3:
                    st.metric("Total GB Loaded", f"{total_gb:.2f}")
                with col4:
                    st.metric("Total Credits", f"{total_credits:.2f}")
                
                st.markdown("**Detailed Pipe Usage:**")
                st.dataframe(
                    df_pipe_usage,
                    column_config={
                        "PIPE_NAME": "Pipe Name",
                        "LOAD_EVENTS": "Load Events",
                        "TOTAL_FILES_LOADED": st.column_config.NumberColumn("Files Loaded", format="%d"),
                        "TOTAL_ROWS_LOADED": st.column_config.NumberColumn("Rows Loaded", format="%d"),
                        "TOTAL_GB_LOADED": st.column_config.NumberColumn("GB Loaded", format="%.2f"),
                        "TOTAL_CREDITS_USED": st.column_config.NumberColumn("Credits Used", format="%.4f"),
                        "LAST_LOAD_TIME": "Last Load",
                        "HOURS_SINCE_LAST_LOAD": st.column_config.NumberColumn("Hours Since Last", format="%d")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # Check for inactive pipes
                inactive_pipes = df_pipe_usage[df_pipe_usage['HOURS_SINCE_LAST_LOAD'] > 168]  # 7 days
                if not inactive_pipes.empty:
                    st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                    st.warning(f"⚠️ **{len(inactive_pipes)} pipe(s) haven't loaded data in 7+ days**. Verify if these pipelines are still operational.")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.info("💡 **Tip**: Monitor Snowpipe activity regularly. Set up notifications for load failures using ERROR_INTEGRATION parameter when creating pipes.")
            else:
                st.info("No Snowpipe activity detected in the selected period.")
                
        except Exception as e:
            st.info(f"Snowpipe usage data unavailable: {str(e)}")
            
    except Exception as e:
        st.error(f"Error fetching pipe data: {str(e)}")
    
    st.markdown("---")
    
    # Query 4: Task Execution Reliability
    st.subheader("4. Task Execution Reliability")
    
    query_task_history = f"""
    SELECT 
        name,
        database_name,
        schema_name,
        state,
        scheduled_time,
        completed_time,
        error_code,
        error_message,
        DATEDIFF(second, scheduled_time, completed_time) as execution_duration_sec,
        scheduled_from,
        attempt_number
    FROM snowflake.account_usage.task_history
    WHERE scheduled_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
    ORDER BY scheduled_time DESC
    """
    
    try:
        df_task_history = session.sql(query_task_history).to_pandas()
        
        if not df_task_history.empty:
            # Calculate success/failure metrics
            state_counts = df_task_history['STATE'].value_counts()
            total_runs = len(df_task_history)
            
            succeeded = len(df_task_history[df_task_history['STATE'] == 'SUCCEEDED'])
            failed = len(df_task_history[df_task_history['STATE'] == 'FAILED'])
            cancelled = len(df_task_history[df_task_history['STATE'] == 'CANCELLED'])
            skipped = len(df_task_history[df_task_history['STATE'] == 'SKIPPED'])
            
            success_rate = (succeeded / total_runs * 100) if total_runs > 0 else 0
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Task Runs", f"{total_runs:,}")
            with col2:
                st.metric("Success Rate", f"{success_rate:.1f}%")
            with col3:
                st.metric("Failed Runs", failed, delta=None if failed == 0 else f"-{failed}")
            with col4:
                avg_duration = df_task_history['EXECUTION_DURATION_SEC'].mean()
                st.metric("Avg Duration", f"{avg_duration:.1f}s")
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # State distribution pie chart
                fig_state = px.pie(
                    values=state_counts.values,
                    names=state_counts.index,
                    title='Task Execution State Distribution',
                    color_discrete_map={
                        'SUCCEEDED': '#28a745',
                        'FAILED': '#dc3545',
                        'CANCELLED': '#ffc107',
                        'SKIPPED': '#6c757d'
                    }
                )
                st.plotly_chart(fig_state, use_container_width=True)
            
            with col2:
                # Daily success rate trend
                df_daily = df_task_history.copy()
                df_daily['DATE'] = pd.to_datetime(df_daily['SCHEDULED_TIME']).dt.date
                daily_stats = df_daily.groupby('DATE').agg({
                    'STATE': lambda x: (x == 'SUCCEEDED').sum() / len(x) * 100
                }).reset_index()
                daily_stats.columns = ['DATE', 'SUCCESS_RATE']
                
                fig_trend = px.line(
                    daily_stats,
                    x='DATE',
                    y='SUCCESS_RATE',
                    title='Daily Task Success Rate',
                    labels={'SUCCESS_RATE': 'Success Rate (%)', 'DATE': 'Date'},
                    markers=True
                )
                fig_trend.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="Target: 95%")
                st.plotly_chart(fig_trend, use_container_width=True)
            
            # Failed tasks analysis
            failed_tasks = df_task_history[df_task_history['STATE'] == 'FAILED']
            
            if not failed_tasks.empty:
                st.markdown('<div class="danger-card">', unsafe_allow_html=True)
                st.error(f"⚠️ **{len(failed_tasks)} task execution(s) failed** in the last {days_back} days")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Top failing tasks
                task_failure_counts = failed_tasks.groupby(['DATABASE_NAME', 'SCHEMA_NAME', 'NAME']).size().reset_index(name='FAILURE_COUNT')
                task_failure_counts = task_failure_counts.sort_values('FAILURE_COUNT', ascending=False).head(10)
                
                fig_failures = px.bar(
                    task_failure_counts,
                    x='NAME',
                    y='FAILURE_COUNT',
                    title='Top 10 Tasks by Failure Count',
                    labels={'FAILURE_COUNT': 'Failures', 'NAME': 'Task Name'},
                    color='FAILURE_COUNT',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig_failures, use_container_width=True)
                
                st.markdown("**Recent Failed Task Runs:**")
                st.dataframe(
                    failed_tasks[['NAME', 'DATABASE_NAME', 'SCHEMA_NAME', 'SCHEDULED_TIME', 
                                  'ERROR_CODE', 'ERROR_MESSAGE', 'ATTEMPT_NUMBER']].head(20),
                    column_config={
                        "NAME": "Task Name",
                        "DATABASE_NAME": "Database",
                        "SCHEMA_NAME": "Schema",
                        "SCHEDULED_TIME": "Scheduled Time",
                        "ERROR_CODE": "Error Code",
                        "ERROR_MESSAGE": st.column_config.TextColumn("Error Message", width="large"),
                        "ATTEMPT_NUMBER": "Attempt"
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                st.info("💡 **Tip**: Review error patterns and implement proper retry logic. Configure error notifications using notification integrations.")
            else:
                st.success("✅ All task executions succeeded in the selected period.")
            
            # Tasks with retries
            retried_tasks = df_task_history[df_task_history['ATTEMPT_NUMBER'] > 1]
            if not retried_tasks.empty:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning(f"⚠️ **{len(retried_tasks)} task run(s) required retries**")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Execution performance by task
            st.markdown("---")
            st.markdown("**Task Performance Summary:**")
            
            task_perf = df_task_history.groupby(['DATABASE_NAME', 'SCHEMA_NAME', 'NAME']).agg({
                'STATE': lambda x: (x == 'SUCCEEDED').sum() / len(x) * 100,
                'EXECUTION_DURATION_SEC': 'mean',
                'SCHEDULED_TIME': 'count'
            }).reset_index()
            task_perf.columns = ['DATABASE_NAME', 'SCHEMA_NAME', 'NAME', 'SUCCESS_RATE', 'AVG_DURATION_SEC', 'RUN_COUNT']
            task_perf = task_perf.sort_values('RUN_COUNT', ascending=False).head(20)
            
            st.dataframe(
                task_perf,
                column_config={
                    "DATABASE_NAME": "Database",
                    "SCHEMA_NAME": "Schema",
                    "NAME": "Task Name",
                    "RUN_COUNT": st.column_config.NumberColumn("Run Count", format="%d"),
                    "SUCCESS_RATE": st.column_config.NumberColumn("Success Rate (%)", format="%.1f"),
                    "AVG_DURATION_SEC": st.column_config.NumberColumn("Avg Duration (sec)", format="%.2f")
                },
                hide_index=True,
                use_container_width=True
            )
            
        else:
            st.info("No task execution history found in the selected period.")
            
    except Exception as e:
        st.error(f"Error fetching task history: {str(e)}")

# ============================================================================
# TAB 3: OPERATIONAL EXCELLENCE
# ============================================================================
with tab3:
    st.header("Operational Excellence")
    st.markdown("""
    Best practices from [Snowflake Well-Architected Framework - Operational Excellence](https://www.snowflake.com/en/developers/guides/well-architected-framework-operational-excellence/)
    """)
    
    # Query 1: Resource Monitors
    st.subheader("1. Resource Monitoring & Governance")
    
    query_resource_monitors = """
    SELECT 
        name,
        'level' as monitor_level,
        TO_NUMBER(credit_quota, 38, 2) as credit_quota,
        TO_NUMBER(used_credits, 38, 2) as used_credits,
        remaining_credits,
        warehouses,
        notify,
        suspend,
        suspend_immediate,
        owner,
        created
    FROM snowflake.account_usage.resource_monitors
    ORDER BY credit_quota DESC
    """
    
    try:
        df_monitors = session.sql(query_resource_monitors).to_pandas()
        
        if not df_monitors.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Monitors", len(df_monitors))
            with col2:
                account_level = len(df_monitors[df_monitors['MONITOR_LEVEL'] == 'ACCOUNT'])
                st.metric("Account-Level", account_level)
            with col3:
                total_quota = df_monitors['CREDIT_QUOTA'].sum()
                st.metric("Total Credit Quota", f"{total_quota:,.0f}")
            with col4:
                total_used = df_monitors['USED_CREDITS'].sum()
                st.metric("Total Credits Used", f"{total_used:,.0f}")
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Credit usage by monitor
                fig_quota = go.Figure()
                fig_quota.add_trace(go.Bar(
                    x=df_monitors['NAME'],
                    y=df_monitors['CREDIT_QUOTA'],
                    name='Quota',
                    marker_color='lightblue'
                ))
                fig_quota.add_trace(go.Bar(
                    x=df_monitors['NAME'],
                    y=df_monitors['USED_CREDITS'],
                    name='Used',
                    marker_color='orange'
                ))
                fig_quota.update_layout(
                    title='Resource Monitor Credit Usage',
                    xaxis_title='Monitor Name',
                    yaxis_title='Credits',
                    barmode='group'
                )
                st.plotly_chart(fig_quota, use_container_width=True)
            
            with col2:
                # Usage percentage
                df_monitors['USAGE_PCT'] = (df_monitors['USED_CREDITS'] / df_monitors['CREDIT_QUOTA'] * 100).fillna(0)
                fig_usage_pct = px.bar(
                    df_monitors,
                    x='NAME',
                    y='USAGE_PCT',
                    title='Credit Usage Percentage',
                    labels={'USAGE_PCT': 'Usage %', 'NAME': 'Monitor Name'},
                    color='USAGE_PCT',
                    color_continuous_scale=['green', 'yellow', 'red']
                )
                fig_usage_pct.add_hline(y=80, line_dash="dash", line_color="orange", annotation_text="80% Warning")
                fig_usage_pct.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="100% Quota")
                st.plotly_chart(fig_usage_pct, use_container_width=True)
            
            # Detailed table
            st.markdown("**Resource Monitor Configuration:**")
            st.dataframe(
                df_monitors,
                column_config={
                    "NAME": "Monitor Name",
                    "MONITOR_LEVEL": "Level",
                    "CREDIT_QUOTA": st.column_config.NumberColumn("Credit Quota", format="%.0f"),
                    "USED_CREDITS": st.column_config.NumberColumn("Credits Used", format="%.2f"),
                    "REMAINING_CREDITS": st.column_config.NumberColumn("Remaining Credits", format="%.2f"),
                    "WAREHOUSES": st.column_config.TextColumn("Assigned Warehouses", width="medium"),
                    "NOTIFY": st.column_config.NumberColumn("Notify At (%)", format="%d"),
                    "SUSPEND": st.column_config.NumberColumn("Suspend At (%)", format="%d"),
                    "SUSPEND_IMMEDIATE": st.column_config.NumberColumn("Suspend Immediate At (%)", format="%d"),
                    "OWNER": "Owner Role",
                    "CREATED": "Created Date"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Check for monitors approaching quota
            approaching_quota = df_monitors[df_monitors['USAGE_PCT'] > 80]
            if not approaching_quota.empty:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning(f"⚠️ **{len(approaching_quota)} resource monitor(s) have used >80% of credit quota**")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Check for monitors without suspend thresholds
            no_suspend = df_monitors[(df_monitors['SUSPEND'].isnull()) & (df_monitors['SUSPEND_IMMEDIATE'].isnull())]
            if not no_suspend.empty:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning(f"⚠️ **{len(no_suspend)} monitor(s) have no suspend thresholds**. Consider adding SUSPEND or SUSPEND_IMMEDIATE thresholds to prevent runaway costs.")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.success("✅ Resource monitors are configured to control credit usage.")
        else:
            st.markdown('<div class="danger-card">', unsafe_allow_html=True)
            st.error("⚠️ **Critical**: No resource monitors configured. Set up resource monitors to control credit usage and prevent runaway costs.")
            st.markdown('</div>', unsafe_allow_html=True)
            st.info("💡 **Recommendation**: Create at least one account-level resource monitor with SUSPEND and NOTIFY thresholds.")
            
    except Exception as e:
        st.error(f"Error fetching resource monitors: {str(e)}")
    
    st.markdown("---")
    
    # Query 2: Warehouse Auto-Suspend Configuration
    st.subheader("2. Warehouse Auto-Suspend & Auto-Resume")
    
    try:
        # Use SHOW WAREHOUSES instead of account_usage view
        df_wh_config = session.sql("SHOW WAREHOUSES").to_pandas()
        
        # SHOW WAREHOUSES returns columns with specific names - extract what we need
        # Column names in SHOW WAREHOUSES are typically quoted and case-sensitive
        # Let's work with the actual column names returned
        
        # Rename columns for consistency - handle both quoted and unquoted column names
        column_mapping = {}
        for col in df_wh_config.columns:
            col_lower = col.lower()
            if col_lower == 'name':
                column_mapping[col] = 'WAREHOUSE_NAME'
            elif col_lower == 'size':
                column_mapping[col] = 'WAREHOUSE_SIZE'
            elif col_lower == 'type':
                column_mapping[col] = 'WAREHOUSE_TYPE'
            elif col_lower == 'auto_suspend':
                column_mapping[col] = 'AUTO_SUSPEND'
            elif col_lower == 'auto_resume':
                column_mapping[col] = 'AUTO_RESUME'
            elif col_lower == 'min_cluster_count':
                column_mapping[col] = 'MIN_CLUSTER_COUNT'
            elif col_lower == 'max_cluster_count':
                column_mapping[col] = 'MAX_CLUSTER_COUNT'
            elif col_lower == 'scaling_policy':
                column_mapping[col] = 'SCALING_POLICY'
        
        df_wh_config.rename(columns=column_mapping, inplace=True)
        
        # Check for warehouses without auto-suspend (NULL or 0)
        no_auto_suspend = df_wh_config[df_wh_config['AUTO_SUSPEND'].isnull() | (df_wh_config['AUTO_SUSPEND'] == 0)]
        long_auto_suspend = df_wh_config[df_wh_config['AUTO_SUSPEND'] > 600]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Warehouses", len(df_wh_config))
        with col2:
            st.metric("No Auto-Suspend", len(no_auto_suspend))
        with col3:
            st.metric("Auto-Suspend > 10min", len(long_auto_suspend))
        
        if len(no_auto_suspend) > 0:
            st.markdown('<div class="danger-card">', unsafe_allow_html=True)
            st.error(f"⚠️ **Critical**: {len(no_auto_suspend)} warehouse(s) without auto-suspend will run continuously!")
            st.dataframe(no_auto_suspend[['WAREHOUSE_NAME', 'WAREHOUSE_SIZE', 'AUTO_SUSPEND', 'AUTO_RESUME']], hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        if len(long_auto_suspend) > 0:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.warning(f"⚠️ **Recommendation**: {len(long_auto_suspend)} warehouse(s) have auto-suspend > 10 minutes. Consider reducing to 60-300 seconds for cost optimization.")
            st.dataframe(long_auto_suspend[['WAREHOUSE_NAME', 'WAREHOUSE_SIZE', 'AUTO_SUSPEND']], hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        if len(no_auto_suspend) == 0 and len(long_auto_suspend) == 0:
            st.success("✅ All warehouses have appropriate auto-suspend configuration.")
        
        # Display full configuration
        st.markdown("**Warehouse Configuration Details:**")
        st.dataframe(
            df_wh_config,
            column_config={
                "WAREHOUSE_NAME": "Warehouse",
                "WAREHOUSE_SIZE": "Size",
                "WAREHOUSE_TYPE": "Type",
                "AUTO_SUSPEND": "Auto-Suspend (sec)",
                "AUTO_RESUME": "Auto-Resume",
                "MIN_CLUSTER_COUNT": "Min Clusters",
                "MAX_CLUSTER_COUNT": "Max Clusters",
                "SCALING_POLICY": "Scaling Policy"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Warehouse Idle Time Analysis
        st.markdown("---")
        st.markdown("**Warehouse Idle Time & Cost Analysis:**")
        
        query_idle_time = f"""
        SELECT
            warehouse_name,
            SUM(credits_used_compute) as total_compute_credits,
            SUM(credits_attributed_compute_queries) as query_credits,
            (SUM(credits_used_compute) - SUM(credits_attributed_compute_queries)) as idle_credits,
            CASE 
                WHEN SUM(credits_used_compute) > 0 
                THEN ((SUM(credits_used_compute) - SUM(credits_attributed_compute_queries)) / 
                      SUM(credits_used_compute)) * 100
                ELSE 0 
            END as idle_pct
        FROM snowflake.account_usage.warehouse_metering_history
        WHERE start_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
        GROUP BY warehouse_name
        HAVING idle_credits > 0
        ORDER BY idle_credits DESC
        """
        
        try:
            df_idle = session.sql(query_idle_time).to_pandas()
            
            if not df_idle.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_idle_credits = px.bar(
                        df_idle.head(10),
                        x='WAREHOUSE_NAME',
                        y='IDLE_CREDITS',
                        title='Top 10 Warehouses by Idle Credits',
                        labels={'IDLE_CREDITS': 'Idle Credits', 'WAREHOUSE_NAME': 'Warehouse'},
                        color='IDLE_CREDITS',
                        color_continuous_scale='Reds'
                    )
                    st.plotly_chart(fig_idle_credits, use_container_width=True)
                
                with col2:
                    fig_idle_pct = px.bar(
                        df_idle.head(10),
                        x='WAREHOUSE_NAME',
                        y='IDLE_PCT',
                        title='Top 10 Warehouses by Idle Time %',
                        labels={'IDLE_PCT': 'Idle Time %', 'WAREHOUSE_NAME': 'Warehouse'},
                        color='IDLE_PCT',
                        color_continuous_scale='Oranges'
                    )
                    st.plotly_chart(fig_idle_pct, use_container_width=True)
                
                # Summary metrics
                total_idle_credits = df_idle['IDLE_CREDITS'].sum()
                total_compute_credits = df_idle['TOTAL_COMPUTE_CREDITS'].sum()
                avg_idle_pct = df_idle['IDLE_PCT'].mean()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Idle Credits", f"{total_idle_credits:.2f}")
                with col2:
                    st.metric("Total Compute Credits", f"{total_compute_credits:.2f}")
                with col3:
                    st.metric("Avg Idle %", f"{avg_idle_pct:.1f}%")
                
                st.markdown("**Detailed Idle Time Analysis:**")
                st.dataframe(
                    df_idle,
                    column_config={
                        "WAREHOUSE_NAME": "Warehouse",
                        "TOTAL_COMPUTE_CREDITS": st.column_config.NumberColumn("Total Credits", format="%.2f"),
                        "QUERY_CREDITS": st.column_config.NumberColumn("Query Credits", format="%.2f"),
                        "IDLE_CREDITS": st.column_config.NumberColumn("Idle Credits", format="%.2f"),
                        "IDLE_PCT": st.column_config.NumberColumn("Idle %", format="%.1f")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # Check for high idle time
                high_idle = df_idle[df_idle['IDLE_PCT'] > 20]
                if not high_idle.empty:
                    st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                    st.warning(f"⚠️ **{len(high_idle)} warehouse(s) have >20% idle time**. Consider reducing auto-suspend timeout to minimize idle costs.")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.info("💡 **Tip**: Idle time occurs when warehouses are running but not executing queries. Reduce auto-suspend timeouts (60-300 seconds) to minimize idle credits.")
            else:
                st.info("No idle time detected or insufficient data for analysis.")
                
        except Exception as e:
            st.info(f"Idle time analysis unavailable: {str(e)}")
            
    except Exception as e:
        st.error(f"Error fetching warehouse configuration: {str(e)}")
    
    st.markdown("---")
    
    # Query 3: Long-Running Queries
    st.subheader("3. Long-Running Query Detection")
    
    query_long_queries = f"""
    SELECT 
        query_id,
        user_name,
        warehouse_name,
        query_type,
        execution_time / 1000 as execution_time_sec,
        total_elapsed_time / 1000 as total_elapsed_time_sec,
        bytes_scanned / POWER(1024, 3) as gb_scanned,
        start_time
    FROM snowflake.account_usage.query_history
    WHERE start_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
        AND execution_status = 'SUCCESS'
        AND execution_time > 300000  -- Greater than 5 minutes
    ORDER BY execution_time DESC
    LIMIT 50
    """
    
    try:
        df_long_queries = session.sql(query_long_queries).to_pandas()
        
        if not df_long_queries.empty:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.warning(f"⚠️ **{len(df_long_queries)} queries took longer than 5 minutes** to execute")
            st.markdown('</div>', unsafe_allow_html=True)
            
            fig_long_queries = px.histogram(
                df_long_queries,
                x='EXECUTION_TIME_SEC',
                nbins=30,
                title='Distribution of Long-Running Queries',
                labels={'EXECUTION_TIME_SEC': 'Execution Time (seconds)'}
            )
            st.plotly_chart(fig_long_queries, use_container_width=True)
            
            st.dataframe(
                df_long_queries.head(20),
                column_config={
                    "QUERY_ID": "Query ID",
                    "USER_NAME": "User",
                    "WAREHOUSE_NAME": "Warehouse",
                    "QUERY_TYPE": "Type",
                    "EXECUTION_TIME_SEC": st.column_config.NumberColumn("Execution Time (sec)", format="%.2f"),
                    "GB_SCANNED": st.column_config.NumberColumn("GB Scanned", format="%.2f"),
                    "START_TIME": "Start Time"
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.info("💡 **Tip**: Review these queries for optimization opportunities (e.g., adding filters, indexes, materialized views).")
        else:
            st.success("✅ No long-running queries detected.")
            
    except Exception as e:
        st.error(f"Error fetching long-running queries: {str(e)}")
    
    st.markdown("---")
    
    # Query 4: Query Retry Patterns
    st.subheader("4. Query Execution Patterns")
    
    query_patterns = f"""
    SELECT 
        user_name,
        query_type,
        COUNT(*) as query_count,
        AVG(execution_time) / 1000 as avg_execution_time_sec,
        COUNT(DISTINCT warehouse_name) as warehouses_used
    FROM snowflake.account_usage.query_history
    WHERE start_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
    GROUP BY user_name, query_type
    ORDER BY query_count DESC
    LIMIT 30
    """
    
    try:
        df_patterns = session.sql(query_patterns).to_pandas()
        
        if not df_patterns.empty:
            fig_users = px.bar(
                df_patterns.head(15),
                x='USER_NAME',
                y='QUERY_COUNT',
                color='QUERY_TYPE',
                title='Top Users by Query Volume',
                labels={'QUERY_COUNT': 'Number of Queries', 'USER_NAME': 'User', 'QUERY_TYPE': 'Query Type'}
            )
            st.plotly_chart(fig_users, use_container_width=True)
            
            st.dataframe(
                df_patterns.head(20),
                column_config={
                    "USER_NAME": "User",
                    "QUERY_TYPE": "Query Type",
                    "QUERY_COUNT": "Query Count",
                    "AVG_EXECUTION_TIME_SEC": st.column_config.NumberColumn("Avg Exec Time (sec)", format="%.2f"),
                    "WAREHOUSES_USED": "Warehouses Used"
                },
                hide_index=True,
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"Error fetching query patterns: {str(e)}")

# ============================================================================
# TAB 4: SECURITY & GOVERNANCE
# ============================================================================
with tab4:
    st.header("Security & Governance")
    st.markdown("""
    Best practices from [Snowflake Well-Architected Framework - Security & Governance](https://www.snowflake.com/en/developers/guides/well-architected-framework-security-and-governance/)
    """)
    
    # Query 1: MFA Adoption
    st.subheader("1. Multi-Factor Authentication (MFA)")
    
    query_mfa = """
    SELECT 
        CASE 
            WHEN ext_authn_duo = TRUE THEN 'MFA Enabled'
            ELSE 'MFA Not Enabled'
        END as mfa_status,
        COUNT(*) as user_count
    FROM snowflake.account_usage.users
    WHERE deleted_on IS NULL
        AND disabled = FALSE
    GROUP BY mfa_status
    """
    
    try:
        df_mfa = session.sql(query_mfa).to_pandas()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_mfa = px.pie(
                df_mfa,
                values='USER_COUNT',
                names='MFA_STATUS',
                title='MFA Adoption Rate',
                color='MFA_STATUS',
                color_discrete_map={'MFA Enabled': '#28a745', 'MFA Not Enabled': '#dc3545'}
            )
            st.plotly_chart(fig_mfa, use_container_width=True)
        
        with col2:
            total_users = df_mfa['USER_COUNT'].sum()
            mfa_enabled = df_mfa[df_mfa['MFA_STATUS'] == 'MFA Enabled']['USER_COUNT'].sum() if 'MFA Enabled' in df_mfa['MFA_STATUS'].values else 0
            mfa_rate = (mfa_enabled / total_users * 100) if total_users > 0 else 0
            
            st.metric("Total Active Users", total_users)
            st.metric("MFA Enabled", mfa_enabled)
            st.metric("MFA Adoption Rate", f"{mfa_rate:.1f}%")
        
        if mfa_rate < 100:
            st.markdown('<div class="danger-card">', unsafe_allow_html=True)
            st.error(f"⚠️ **Critical**: Only {mfa_rate:.1f}% of users have MFA enabled. Require MFA for all users to enhance security.")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success("✅ All active users have MFA enabled.")
            
    except Exception as e:
        st.error(f"Error fetching MFA data: {str(e)}")
    
    st.markdown("---")
    
    # Query 2: Network Policies
    st.subheader("2. Network Policy Configuration")
    
    query_network_policy = """
    SELECT 
        name as policy_name,
        allowed_ip_list,
        blocked_ip_list,
        comment
    FROM snowflake.account_usage.network_policies
    WHERE deleted IS NULL
    ORDER BY name
    """
    
    try:
        df_network_policy = session.sql(query_network_policy).to_pandas()
        
        if not df_network_policy.empty:
            st.success(f"✅ {len(df_network_policy)} network polic(ies) configured")
            
            st.dataframe(
                df_network_policy,
                column_config={
                    "POLICY_NAME": "Policy Name",
                    "ALLOWED_IP_LIST": st.column_config.TextColumn("Allowed IPs", width="large"),
                    "BLOCKED_IP_LIST": st.column_config.TextColumn("Blocked IPs", width="large"),
                    "COMMENT": "Comment"
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.warning("⚠️ **Recommendation**: No network policies configured. Implement network policies to restrict access to trusted IP ranges.")
            st.markdown('</div>', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error fetching network policies: {str(e)}")
    
    st.markdown("---")
    
    # Query 3: Privileged Role Usage
    st.subheader("3. Privileged Access Monitoring")
    
    query_privileged_roles = """
    WITH Active_Queries AS (
        SELECT
            SESSION_ID,
            USER_NAME,
            ROLE_NAME,
            start_time,
            -- Rank the queries for each session by start time (most recent first)
            ROW_NUMBER() OVER (PARTITION BY SESSION_ID ORDER BY start_time DESC) as rn
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE
            -- Filter for sessions that have had activity recently (e.g., in the last 4 hours, which is the default idle timeout)
            start_time >= DATEADD(hour, -4, CURRENT_TIMESTAMP())
            -- Ensure the query is not currently running for better performance (optional)
            AND EXECUTION_STATUS != 'RUNNING'
    )
    SELECT
        S.SESSION_ID,
        S.USER_NAME,
        AQ.ROLE_NAME AS CURRENT_ACTIVE_ROLE,
        S.CLIENT_APPLICATION_ID,
        AQ.start_time AS LAST_ACTIVITY_TIME
    FROM
        SNOWFLAKE.ACCOUNT_USAGE.SESSIONS S
    INNER JOIN
        Active_Queries AQ
        ON S.SESSION_ID = AQ.SESSION_ID
    WHERE
        -- Select only the latest query for each session
        AQ.rn = 1
        -- Filter sessions that were created recently (e.g., last 7 days)
        AND S.CREATED_ON >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    ORDER BY
        LAST_ACTIVITY_TIME DESC
    """
    
    try:
        df_priv_roles = session.sql(query_privileged_roles).to_pandas()
        
        if not df_priv_roles.empty:
            # Filter for privileged roles
            privileged_roles = ['ACCOUNTADMIN', 'SECURITYADMIN', 'SYSADMIN']
            df_privileged = df_priv_roles[df_priv_roles['CURRENT_ACTIVE_ROLE'].isin(privileged_roles)]
            
            if not df_privileged.empty:
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Active Sessions", len(df_privileged))
                with col2:
                    st.metric("Unique Users", df_privileged['USER_NAME'].nunique())
                with col3:
                    st.metric("ACCOUNTADMIN Sessions", len(df_privileged[df_privileged['CURRENT_ACTIVE_ROLE'] == 'ACCOUNTADMIN']))
                with col4:
                    st.metric("Total Active Sessions (All Roles)", len(df_priv_roles))
                
                # Chart: Sessions by Role
                role_counts = df_privileged['CURRENT_ACTIVE_ROLE'].value_counts().reset_index()
                role_counts.columns = ['ROLE', 'SESSION_COUNT']
                
                fig_priv = px.bar(
                    role_counts,
                    x='ROLE',
                    y='SESSION_COUNT',
                    title='Active Privileged Sessions by Role',
                    labels={'SESSION_COUNT': 'Active Sessions', 'ROLE': 'Privileged Role'},
                    color='ROLE',
                    color_discrete_map={
                        'ACCOUNTADMIN': '#FF4B4B',
                        'SECURITYADMIN': '#FFA500',
                        'SYSADMIN': '#FFD700'
                    }
                )
                st.plotly_chart(fig_priv, use_container_width=True)
                
                st.markdown("**Active Privileged Sessions:**")
                st.dataframe(
                    df_privileged.head(50),
                    column_config={
                        "SESSION_ID": "Session ID",
                        "USER_NAME": "User",
                        "CURRENT_ACTIVE_ROLE": "Active Role",
                        "CLIENT_APPLICATION_ID": "Client Application",
                        "LAST_ACTIVITY_TIME": st.column_config.DatetimeColumn(
                            "Last Activity",
                            format="DD/MM/YYYY HH:mm:ss"
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                st.info("💡 **Tip**: Monitor privileged role usage closely. Active sessions show users currently using privileged roles. Consider implementing role-based access with least privilege principle and session timeout policies.")
            else:
                st.info("No active privileged role sessions found in the last 4 hours.")
        else:
            st.info("No active sessions found in the selected period.")
            
    except Exception as e:
        st.error(f"Error fetching privileged role data: {str(e)}")
    
    st.markdown("---")
    
    # Query 4: Data Masking Policies
    st.subheader("4. Data Protection & Masking")
    
    query_masking = """
    SELECT 
        policy_name,
        policy_kind,
        policy_catalog,
        policy_schema
    FROM snowflake.account_usage.policy_references
    WHERE deleted IS NULL
        AND policy_kind IN ('MASKING_POLICY', 'ROW_ACCESS_POLICY')
    ORDER BY policy_kind, policy_name
    """
    
    try:
        df_masking = session.sql(query_masking).to_pandas()
        
        if not df_masking.empty:
            masking_count = len(df_masking[df_masking['POLICY_KIND'] == 'MASKING_POLICY'])
            row_access_count = len(df_masking[df_masking['POLICY_KIND'] == 'ROW_ACCESS_POLICY'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Masking Policies", masking_count)
            with col2:
                st.metric("Row Access Policies", row_access_count)
            
            st.success(f"✅ {len(df_masking)} data protection polic(ies) in place")
            
            st.dataframe(
                df_masking,
                column_config={
                    "POLICY_NAME": "Policy Name",
                    "POLICY_KIND": "Policy Type",
                    "POLICY_CATALOG": "Database",
                    "POLICY_SCHEMA": "Schema"
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.warning("⚠️ **Recommendation**: No masking or row access policies detected. Implement data masking for sensitive data (PII, PHI, financial data).")
            st.markdown('</div>', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error fetching masking policies: {str(e)}")
    
    st.markdown("---")
    
    # Query 5: Failed Login Attempts
    st.subheader("5. Failed Authentication Attempts")
    
    query_failed_logins = f"""
    SELECT 
        user_name,
        error_message,
        COUNT(*) as failed_attempts,
        MAX(event_timestamp) as last_attempt
    FROM snowflake.account_usage.login_history
    WHERE event_timestamp >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
        AND is_success = 'NO'
    GROUP BY user_name, error_message
    ORDER BY failed_attempts DESC
    LIMIT 30
    """
    
    try:
        df_failed_logins = session.sql(query_failed_logins).to_pandas()
        
        if not df_failed_logins.empty:
            total_failures = df_failed_logins['FAILED_ATTEMPTS'].sum()
            
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.warning(f"⚠️ **{total_failures:,.0f} failed login attempts** detected")
            st.markdown('</div>', unsafe_allow_html=True)
            
            fig_failed = px.bar(
                df_failed_logins.head(15),
                x='USER_NAME',
                y='FAILED_ATTEMPTS',
                title='Failed Login Attempts by User',
                labels={'FAILED_ATTEMPTS': 'Failed Attempts', 'USER_NAME': 'User'}
            )
            st.plotly_chart(fig_failed, use_container_width=True)
            
            st.dataframe(
                df_failed_logins.head(20),
                column_config={
                    "USER_NAME": "User",
                    "ERROR_MESSAGE": st.column_config.TextColumn("Error Message", width="large"),
                    "FAILED_ATTEMPTS": "Failed Attempts",
                    "LAST_ATTEMPT": "Last Attempt"
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.info("💡 **Tip**: Investigate users with multiple failed login attempts. Consider implementing account lockout policies.")
        else:
            st.success("✅ No failed login attempts in the selected period.")
            
    except Exception as e:
        st.error(f"Error fetching failed login data: {str(e)}")

# ============================================================================
# TAB 5: COST OPTIMIZATION
# ============================================================================
with tab5:
    st.header("Cost Optimization & FinOps")
    st.markdown("""
    Best practices from [Snowflake Well-Architected Framework - Cost Optimization](https://www.snowflake.com/en/developers/guides/well-architected-framework-cost-optimization-and-finops/)
    """)
    
    # Query 1: Credit Usage by Service
    st.subheader("1. Credit Consumption Overview")
    
    query_credit_usage = f"""
    SELECT 
        DATE_TRUNC('day', usage_date) as usage_date,
        service_type,
        SUM(credits_used) as total_credits
    FROM snowflake.account_usage.metering_daily_history
    WHERE usage_date >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
    GROUP BY DATE_TRUNC('day', usage_date), service_type
    ORDER BY usage_date DESC, total_credits DESC
    """
    
    try:
        df_credits = session.sql(query_credit_usage).to_pandas()
        
        # Total credits by service type
        df_credits_by_service = df_credits.groupby('SERVICE_TYPE')['TOTAL_CREDITS'].sum().reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_credits_pie = px.pie(
                df_credits_by_service,
                values='TOTAL_CREDITS',
                names='SERVICE_TYPE',
                title='Credit Distribution by Service Type',
                hole=0.4
            )
            st.plotly_chart(fig_credits_pie, use_container_width=True)
        
        with col2:
            # Credits over time
            fig_credits_trend = px.area(
                df_credits,
                x='USAGE_DATE',
                y='TOTAL_CREDITS',
                color='SERVICE_TYPE',
                title='Daily Credit Consumption Trend',
                labels={'TOTAL_CREDITS': 'Credits Used', 'USAGE_DATE': 'Date'}
            )
            st.plotly_chart(fig_credits_trend, use_container_width=True)
        
        # Metrics
        total_credits = df_credits['TOTAL_CREDITS'].sum()
        avg_daily_credits = df_credits.groupby('USAGE_DATE')['TOTAL_CREDITS'].sum().mean()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Credits Used", f"{total_credits:,.2f}")
        with col2:
            st.metric("Avg Daily Credits", f"{avg_daily_credits:,.2f}")
        with col3:
            st.metric("Estimated Monthly", f"{avg_daily_credits * 30:,.2f}")
            
    except Exception as e:
        st.error(f"Error fetching credit usage: {str(e)}")
    
    st.markdown("---")
    
    # Query 2: Warehouse Cost Analysis
    st.subheader("2. Warehouse Cost Analysis")
    
    query_wh_cost = f"""
    SELECT 
        warehouse_name,
        SUM(credits_used) as total_credits,
        SUM(credits_used_compute) as compute_credits,
        SUM(credits_used_cloud_services) as cloud_services_credits,
        AVG(CASE 
            WHEN credits_used > 0 THEN (credits_used_cloud_services / credits_used) * 100 
            ELSE 0 
        END) as cloud_services_pct
    FROM snowflake.account_usage.warehouse_metering_history
    WHERE start_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
    GROUP BY warehouse_name
    ORDER BY total_credits DESC
    LIMIT 20
    """
    
    try:
        df_wh_cost = session.sql(query_wh_cost).to_pandas()
        
        if not df_wh_cost.empty:
            fig_wh_cost = px.bar(
                df_wh_cost.head(15),
                x='WAREHOUSE_NAME',
                y='TOTAL_CREDITS',
                title='Top 15 Warehouses by Credit Consumption',
                labels={'TOTAL_CREDITS': 'Total Credits', 'WAREHOUSE_NAME': 'Warehouse'},
                color='TOTAL_CREDITS',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig_wh_cost, use_container_width=True)
            
            st.markdown("**Warehouse Cost Breakdown:**")
            st.dataframe(
                df_wh_cost,
                column_config={
                    "WAREHOUSE_NAME": "Warehouse",
                    "TOTAL_CREDITS": st.column_config.NumberColumn("Total Credits", format="%.2f"),
                    "COMPUTE_CREDITS": st.column_config.NumberColumn("Compute Credits", format="%.2f"),
                    "CLOUD_SERVICES_CREDITS": st.column_config.NumberColumn("Cloud Services Credits", format="%.2f"),
                    "CLOUD_SERVICES_PCT": st.column_config.NumberColumn("Cloud Services %", format="%.2f")
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Check for high cloud services usage
            high_cs_wh = df_wh_cost[df_wh_cost['CLOUD_SERVICES_PCT'] > 10]
            if not high_cs_wh.empty:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning(f"⚠️ **{len(high_cs_wh)} warehouse(s) with >10% cloud services credits**. You may be charged for cloud services if this exceeds the daily limit.")
                st.markdown('</div>', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error fetching warehouse cost data: {str(e)}")
    
    st.markdown("---")
    
    # Query 3: Storage Costs
    st.subheader("3. Storage Cost Analysis")
    
    query_storage = f"""
    SELECT 
        DATE_TRUNC('day', usage_date) as usage_date,
        AVG(storage_bytes + stage_bytes + failsafe_bytes) / POWER(1024, 4) as total_storage_tb,
        AVG(storage_bytes) / POWER(1024, 4) as database_storage_tb,
        AVG(stage_bytes) / POWER(1024, 4) as stage_storage_tb,
        AVG(failsafe_bytes) / POWER(1024, 4) as failsafe_storage_tb
    FROM snowflake.account_usage.storage_usage
    WHERE usage_date >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
    GROUP BY DATE_TRUNC('day', usage_date)
    ORDER BY usage_date DESC
    """
    
    try:
        df_storage = session.sql(query_storage).to_pandas()
        
        if not df_storage.empty:
            fig_storage = px.area(
                df_storage,
                x='USAGE_DATE',
                y=['DATABASE_STORAGE_TB', 'STAGE_STORAGE_TB', 'FAILSAFE_STORAGE_TB'],
                title='Storage Usage Trend (TB)',
                labels={'value': 'Storage (TB)', 'USAGE_DATE': 'Date', 'variable': 'Storage Type'}
            )
            st.plotly_chart(fig_storage, use_container_width=True)
            
            latest_storage = df_storage.iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Storage", f"{latest_storage['TOTAL_STORAGE_TB']:.2f} TB")
            with col2:
                st.metric("Database Storage", f"{latest_storage['DATABASE_STORAGE_TB']:.2f} TB")
            with col3:
                st.metric("Stage Storage", f"{latest_storage['STAGE_STORAGE_TB']:.2f} TB")
            with col4:
                st.metric("Failsafe Storage", f"{latest_storage['FAILSAFE_STORAGE_TB']:.2f} TB")
            
            # Calculate growth
            if len(df_storage) > 7:
                storage_7d_ago = df_storage.iloc[-1]['TOTAL_STORAGE_TB']
                storage_growth = ((latest_storage['TOTAL_STORAGE_TB'] - storage_7d_ago) / storage_7d_ago) * 100
                
                if storage_growth > 10:
                    st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                    st.warning(f"⚠️ **Storage growth**: {storage_growth:.1f}% increase in the last 7 days. Review data retention policies and remove unused data.")
                    st.markdown('</div>', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error fetching storage data: {str(e)}")
    
    st.markdown("---")
    
    # Query 4: Idle Warehouse Detection
    st.subheader("4. Idle Warehouse Detection")
    
    query_idle_wh = f"""
    WITH warehouse_usage AS (
        SELECT 
            warehouse_name,
            MAX(end_time) as last_used
        FROM snowflake.account_usage.query_history
        WHERE start_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
        GROUP BY warehouse_name
    )
    SELECT 
        w.warehouse_name,
        w.warehouse_size,
        wu.last_used,
        DATEDIFF(day, wu.last_used, CURRENT_TIMESTAMP()) as days_since_last_use
    FROM snowflake.account_usage.warehouses w
    LEFT JOIN warehouse_usage wu ON w.warehouse_name = wu.warehouse_name
    WHERE w.deleted IS NULL
    ORDER BY days_since_last_use DESC NULLS FIRST
    """
    
    try:
        df_idle_wh = session.sql(query_idle_wh).to_pandas()
        
        # Warehouses not used in last 7 days
        idle_wh = df_idle_wh[(df_idle_wh['DAYS_SINCE_LAST_USE'].isnull()) | (df_idle_wh['DAYS_SINCE_LAST_USE'] > 7)]
        
        if not idle_wh.empty:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.warning(f"⚠️ **{len(idle_wh)} idle warehouse(s)** detected (not used in 7+ days)")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.dataframe(
                idle_wh,
                column_config={
                    "WAREHOUSE_NAME": "Warehouse",
                    "WAREHOUSE_SIZE": "Size",
                    "LAST_USED": "Last Used",
                    "DAYS_SINCE_LAST_USE": "Days Since Last Use"
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.info("💡 **Tip**: Consider suspending or dropping unused warehouses to reduce costs.")
        else:
            st.success("✅ All warehouses have been used recently.")
            
    except Exception as e:
        st.error(f"Error fetching idle warehouse data: {str(e)}")
    
    st.markdown("---")
    
    # Query 5: Table with High Storage but Low Usage
    st.subheader("5. Storage Optimization Opportunities")
    
    query_table_storage = f"""
    WITH table_storage AS (
        SELECT 
            table_catalog,
            table_schema,
            table_name,
            active_bytes / POWER(1024, 3) as active_gb,
            time_travel_bytes / POWER(1024, 3) as time_travel_gb,
            failsafe_bytes / POWER(1024, 3) as failsafe_gb,
            (active_bytes + time_travel_bytes + failsafe_bytes) / POWER(1024, 3) as total_gb
        FROM snowflake.account_usage.table_storage_metrics
        WHERE deleted IS NULL
    ),
    table_access AS (
        SELECT 
            tables_accessed.value:objectName::STRING as table_name,
            COUNT(*) as access_count
        FROM snowflake.account_usage.access_history,
            LATERAL FLATTEN(input => base_objects_accessed) tables_accessed
        WHERE query_start_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
        GROUP BY table_name
    )
    SELECT 
        ts.table_catalog,
        ts.table_schema,
        ts.table_name,
        ts.total_gb,
        ts.active_gb,
        ts.time_travel_gb,
        ts.failsafe_gb,
        COALESCE(ta.access_count, 0) as access_count
    FROM table_storage ts
    LEFT JOIN table_access ta ON ts.table_name = ta.table_name
    WHERE ts.total_gb > 1  -- Tables larger than 1 GB
    ORDER BY ts.total_gb DESC
    LIMIT 50
    """
    
    try:
        df_table_storage = session.sql(query_table_storage).to_pandas()
        
        if not df_table_storage.empty:
            # Tables with high storage but low access
            unused_tables = df_table_storage[
                (df_table_storage['TOTAL_GB'] > 10) & 
                (df_table_storage['ACCESS_COUNT'] == 0)
            ]
            
            fig_storage_table = px.scatter(
                df_table_storage.head(30),
                x='ACCESS_COUNT',
                y='TOTAL_GB',
                size='TOTAL_GB',
                hover_data=['TABLE_CATALOG', 'TABLE_SCHEMA', 'TABLE_NAME'],
                title='Table Storage vs Access Frequency',
                labels={'TOTAL_GB': 'Storage (GB)', 'ACCESS_COUNT': 'Access Count'},
                color='TOTAL_GB',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig_storage_table, use_container_width=True)
            
            if not unused_tables.empty:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning(f"⚠️ **{len(unused_tables)} large table(s) (>10GB)** with no access in the last {days_back} days")
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.dataframe(
                    unused_tables.head(20),
                    column_config={
                        "TABLE_CATALOG": "Database",
                        "TABLE_SCHEMA": "Schema",
                        "TABLE_NAME": "Table",
                        "TOTAL_GB": st.column_config.NumberColumn("Total Storage (GB)", format="%.2f"),
                        "ACTIVE_GB": st.column_config.NumberColumn("Active (GB)", format="%.2f"),
                        "TIME_TRAVEL_GB": st.column_config.NumberColumn("Time Travel (GB)", format="%.2f"),
                        "FAILSAFE_GB": st.column_config.NumberColumn("Failsafe (GB)", format="%.2f"),
                        "ACCESS_COUNT": "Access Count"
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                st.info("💡 **Tip**: Review these tables for archival or deletion. Consider reducing data retention periods.")
            else:
                st.success("✅ All large tables are actively accessed.")
                
    except Exception as e:
        st.error(f"Error fetching table storage data: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with ❄️ Streamlit in Snowflake | Based on Snowflake Well-Architected Framework</p>
    <p><a href="https://www.snowflake.com/en/developers/guides/well-architected-framework/">Learn more about Snowflake Well-Architected Framework</a></p>
</div>
""", unsafe_allow_html=True)


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
    
    # Query 1: Query Latency SLO (P50, P99)
    st.subheader("1. Query Latency SLO Monitoring")
    
    query_latency_slo = f"""
    WITH query_metrics AS (
        SELECT 
            DATE_TRUNC('day', start_time) as query_date,
            query_type,
            execution_time / 1000 as execution_time_sec
        FROM snowflake.account_usage.query_history
        WHERE start_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
            AND execution_status = 'SUCCESS'
            AND query_type IN ('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'MERGE')
            AND user_name NOT IN ('SYSTEM', 'dataplane_service', 'dataplatform_admin')
    )
    SELECT 
        query_date,
        query_type,
        COUNT(*) as query_count,
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY execution_time_sec) as p50_latency_sec,
        PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY execution_time_sec) as p90_latency_sec,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY execution_time_sec) as p95_latency_sec,
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY execution_time_sec) as p99_latency_sec,
        AVG(execution_time_sec) as avg_latency_sec,
        MAX(execution_time_sec) as max_latency_sec
    FROM query_metrics
    GROUP BY query_date, query_type
    ORDER BY query_date DESC, query_type
    """
    
    try:
        df_latency = session.sql(query_latency_slo).to_pandas()
        
        if not df_latency.empty:
            # Overall SLO by query type
            df_slo_summary = df_latency.groupby('QUERY_TYPE').agg({
                'QUERY_COUNT': 'sum',
                'P50_LATENCY_SEC': 'mean',
                'P90_LATENCY_SEC': 'mean',
                'P95_LATENCY_SEC': 'mean',
                'P99_LATENCY_SEC': 'mean'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # P50 latency by query type
                fig_p50 = px.bar(
                    df_slo_summary,
                    x='QUERY_TYPE',
                    y='P50_LATENCY_SEC',
                    title='P50 (Median) Latency by Query Type',
                    labels={'P50_LATENCY_SEC': 'P50 Latency (sec)', 'QUERY_TYPE': 'Query Type'},
                    color='P50_LATENCY_SEC',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_p50, use_container_width=True)
            
            with col2:
                # P99 latency by query type
                fig_p99 = px.bar(
                    df_slo_summary,
                    x='QUERY_TYPE',
                    y='P99_LATENCY_SEC',
                    title='P99 Latency by Query Type',
                    labels={'P99_LATENCY_SEC': 'P99 Latency (sec)', 'QUERY_TYPE': 'Query Type'},
                    color='P99_LATENCY_SEC',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig_p99, use_container_width=True)
            
            # Latency trend over time for SELECT queries
            df_select_trend = df_latency[df_latency['QUERY_TYPE'] == 'SELECT'].sort_values('QUERY_DATE')
            
            if not df_select_trend.empty:
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=df_select_trend['QUERY_DATE'],
                    y=df_select_trend['P50_LATENCY_SEC'],
                    name='P50',
                    mode='lines+markers',
                    line=dict(color='green', width=2)
                ))
                fig_trend.add_trace(go.Scatter(
                    x=df_select_trend['QUERY_DATE'],
                    y=df_select_trend['P90_LATENCY_SEC'],
                    name='P90',
                    mode='lines+markers',
                    line=dict(color='orange', width=2)
                ))
                fig_trend.add_trace(go.Scatter(
                    x=df_select_trend['QUERY_DATE'],
                    y=df_select_trend['P99_LATENCY_SEC'],
                    name='P99',
                    mode='lines+markers',
                    line=dict(color='red', width=2)
                ))
                fig_trend.update_layout(
                    title='SELECT Query Latency Trend (P50, P90, P99)',
                    xaxis_title='Date',
                    yaxis_title='Latency (seconds)',
                    hovermode='x unified'
                )
                st.plotly_chart(fig_trend, use_container_width=True)
            
            # Summary metrics
            overall_p50 = df_latency['P50_LATENCY_SEC'].mean()
            overall_p90 = df_latency['P90_LATENCY_SEC'].mean()
            overall_p95 = df_latency['P95_LATENCY_SEC'].mean()
            overall_p99 = df_latency['P99_LATENCY_SEC'].mean()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Overall P50", f"{overall_p50:.2f}s")
            with col2:
                st.metric("Overall P90", f"{overall_p90:.2f}s")
            with col3:
                st.metric("Overall P95", f"{overall_p95:.2f}s")
            with col4:
                st.metric("Overall P99", f"{overall_p99:.2f}s")
            
            # Detailed SLO table
            st.markdown("**SLO Details by Query Type:**")
            st.dataframe(
                df_slo_summary,
                column_config={
                    "QUERY_TYPE": "Query Type",
                    "QUERY_COUNT": st.column_config.NumberColumn("Total Queries", format="%d"),
                    "P50_LATENCY_SEC": st.column_config.NumberColumn("P50 (sec)", format="%.2f"),
                    "P90_LATENCY_SEC": st.column_config.NumberColumn("P90 (sec)", format="%.2f"),
                    "P95_LATENCY_SEC": st.column_config.NumberColumn("P95 (sec)", format="%.2f"),
                    "P99_LATENCY_SEC": st.column_config.NumberColumn("P99 (sec)", format="%.2f")
                },
                hide_index=True,
                use_container_width=True
            )
            
            # SLO violations check (example thresholds)
            p99_threshold = 30  # 30 seconds for P99
            high_p99_types = df_slo_summary[df_slo_summary['P99_LATENCY_SEC'] > p99_threshold]
            
            if not high_p99_types.empty:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning(f"⚠️ **SLO Alert**: {len(high_p99_types)} query type(s) have P99 latency >{p99_threshold}s. Review performance optimization opportunities.")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.success(f"✅ All query types meet P99 latency SLO of <{p99_threshold}s")
            
            st.info("""
            💡 **Latency Percentiles**:
            - **P50 (Median)**: 50% of queries complete faster than this time
            - **P90**: 90% of queries complete faster than this time
            - **P99**: 99% of queries complete faster than this time
            - Monitor P99 to ensure the slowest 1% of queries don't impact user experience
            """)
        else:
            st.info("No latency data available for the selected period.")
            
    except Exception as e:
        st.error(f"Error fetching latency SLO data: {str(e)}")
    
    st.markdown("---")
    
    # Query 2: Warehouse Performance and Utilization
    st.subheader("2. Warehouse Utilization & Efficiency")
    
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
    st.subheader("3. Query Performance Analysis")
    
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
    st.subheader("4. Automatic Clustering Activity")
    
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
    st.subheader("5. Result Cache Efficiency")
    
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
    
    st.markdown("---")
    
    # Query 5: Warehouse Timeout Configuration
    st.subheader("6. Warehouse Timeout Configuration")
    
    try:
        # Get warehouse parameters using SHOW WAREHOUSES
        df_wh_params = session.sql("SHOW WAREHOUSES").to_pandas()
        
        # Standardize column names - handle both quoted and unquoted column names
        column_mapping = {}
        for col in df_wh_params.columns:
            col_clean = str(col).lower().strip('"').strip()
            if col_clean == 'name':
                column_mapping[col] = 'WAREHOUSE_NAME'
            elif col_clean == 'statement_timeout_in_seconds':
                column_mapping[col] = 'STATEMENT_TIMEOUT_IN_SECONDS'
            elif col_clean == 'statement_queued_timeout_in_seconds':
                column_mapping[col] = 'STATEMENT_QUEUED_TIMEOUT_IN_SECONDS'
        
        df_wh_params.rename(columns=column_mapping, inplace=True)
        
        # Try to identify columns by position if name-based mapping didn't work
        if 'WAREHOUSE_NAME' not in df_wh_params.columns:
            if len(df_wh_params.columns) > 0:
                df_wh_params['WAREHOUSE_NAME'] = df_wh_params.iloc[:, 0]
        
        # For timeout parameters, try to find them in the columns
        # SHOW WAREHOUSES may not include timeout values directly
        # We need to query each warehouse parameters individually
        warehouses = df_wh_params['WAREHOUSE_NAME'].tolist()
        
        timeout_data = []
        for wh in warehouses:
            try:
                # Get warehouse parameters
                params_df = session.sql(f"SHOW PARAMETERS FOR WAREHOUSE {wh}").to_pandas()
                
                # Find timeout parameters
                stmt_timeout = None
                queue_timeout = None
                
                for _, row in params_df.iterrows():
                    param_name = str(row.iloc[0]).strip('"').strip().upper() if len(row) > 0 else ''
                    param_value = str(row.iloc[1]).strip('"').strip() if len(row) > 1 else '0'
                    
                    if 'STATEMENT_TIMEOUT_IN_SECONDS' in param_name:
                        stmt_timeout = int(param_value) if param_value.isdigit() else 0
                    elif 'STATEMENT_QUEUED_TIMEOUT_IN_SECONDS' in param_name:
                        queue_timeout = int(param_value) if param_value.isdigit() else 0
                
                timeout_data.append({
                    'WAREHOUSE_NAME': wh,
                    'STATEMENT_TIMEOUT_IN_SECONDS': stmt_timeout,
                    'STATEMENT_QUEUED_TIMEOUT_IN_SECONDS': queue_timeout
                })
            except Exception as e:
                st.warning(f"Could not retrieve parameters for warehouse {wh}: {str(e)}")
        
        if timeout_data:
            df_params_pivot = pd.DataFrame(timeout_data)
            
            # Check for missing configurations
            no_stmt_timeout = df_params_pivot[df_params_pivot['STATEMENT_TIMEOUT_IN_SECONDS'].isnull() | 
                                              (df_params_pivot['STATEMENT_TIMEOUT_IN_SECONDS'] == 0)]
            no_queue_timeout = df_params_pivot[df_params_pivot['STATEMENT_QUEUED_TIMEOUT_IN_SECONDS'].isnull() | 
                                               (df_params_pivot['STATEMENT_QUEUED_TIMEOUT_IN_SECONDS'] == 0)]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Warehouses", len(df_params_pivot))
            with col2:
                st.metric("Missing Statement Timeout", len(no_stmt_timeout))
            with col3:
                st.metric("Missing Queue Timeout", len(no_queue_timeout))
            
            # Display warehouse timeout configuration
            st.markdown("**Timeout Configuration Details:**")
            st.dataframe(
                df_params_pivot,
                column_config={
                    "WAREHOUSE_NAME": "Warehouse",
                    "STATEMENT_TIMEOUT_IN_SECONDS": st.column_config.NumberColumn("Statement Timeout (sec)", format="%d"),
                    "STATEMENT_QUEUED_TIMEOUT_IN_SECONDS": st.column_config.NumberColumn("Queue Timeout (sec)", format="%d")
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Recommendations
            if not no_stmt_timeout.empty:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning(f"⚠️ **{len(no_stmt_timeout)} warehouse(s) without statement timeout**. Configure STATEMENT_TIMEOUT_IN_SECONDS to prevent runaway queries.")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if not no_queue_timeout.empty:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning(f"⚠️ **{len(no_queue_timeout)} warehouse(s) without queue timeout**. Configure STATEMENT_QUEUED_TIMEOUT_IN_SECONDS to prevent long queue waits.")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if no_stmt_timeout.empty and no_queue_timeout.empty:
                st.success("✅ All warehouses have timeout configurations.")
            
            st.info("💡 **Best Practice**: Set STATEMENT_TIMEOUT_IN_SECONDS (e.g., 3600) and STATEMENT_QUEUED_TIMEOUT_IN_SECONDS (e.g., 300) to prevent resource exhaustion.")
        else:
            st.info("No warehouse timeout configuration data available.")
            
    except Exception as e:
        st.error(f"Error fetching warehouse timeout configuration: {str(e)}")
    
    st.markdown("---")
    
    # Query 6: Query Spillage Detection
    st.subheader("7. Query Spillage Detection")
    
    query_spillage = f"""
    SELECT 
        DATE_TRUNC('day', start_time) as query_date,
        warehouse_name,
        COUNT(*) as total_queries,
        SUM(CASE WHEN bytes_spilled_to_local_storage > 0 THEN 1 ELSE 0 END) as queries_with_local_spill,
        SUM(CASE WHEN bytes_spilled_to_remote_storage > 0 THEN 1 ELSE 0 END) as queries_with_remote_spill,
        SUM(bytes_spilled_to_local_storage) / POWER(1024, 3) as total_local_spill_gb,
        SUM(bytes_spilled_to_remote_storage) / POWER(1024, 3) as total_remote_spill_gb,
        AVG(CASE WHEN bytes_spilled_to_local_storage > 0 
            THEN bytes_spilled_to_local_storage / POWER(1024, 3) 
            ELSE 0 END) as avg_local_spill_gb,
        AVG(CASE WHEN bytes_spilled_to_remote_storage > 0 
            THEN bytes_spilled_to_remote_storage / POWER(1024, 3) 
            ELSE 0 END) as avg_remote_spill_gb,
        (SUM(CASE WHEN bytes_spilled_to_local_storage > 0 THEN 1 ELSE 0 END)::FLOAT / COUNT(*)) * 100 as local_spill_pct,
        (SUM(CASE WHEN bytes_spilled_to_remote_storage > 0 THEN 1 ELSE 0 END)::FLOAT / COUNT(*)) * 100 as remote_spill_pct
    FROM snowflake.account_usage.query_history
    WHERE start_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
        AND warehouse_name IS NOT NULL
        AND execution_status = 'SUCCESS'
    GROUP BY DATE_TRUNC('day', start_time), warehouse_name
    HAVING queries_with_local_spill > 0 OR queries_with_remote_spill > 0
    ORDER BY total_local_spill_gb + total_remote_spill_gb DESC
    """
    
    try:
        df_spillage = session.sql(query_spillage).to_pandas()
        
        if not df_spillage.empty:
            # Aggregate by warehouse
            df_spillage_by_wh = df_spillage.groupby('WAREHOUSE_NAME').agg({
                'QUERIES_WITH_LOCAL_SPILL': 'sum',
                'QUERIES_WITH_REMOTE_SPILL': 'sum',
                'TOTAL_LOCAL_SPILL_GB': 'sum',
                'TOTAL_REMOTE_SPILL_GB': 'sum',
                'LOCAL_SPILL_PCT': 'mean',
                'REMOTE_SPILL_PCT': 'mean'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_local_spill = px.bar(
                    df_spillage_by_wh.head(10),
                    x='WAREHOUSE_NAME',
                    y='TOTAL_LOCAL_SPILL_GB',
                    title='Top 10 Warehouses by Local Disk Spillage',
                    labels={'TOTAL_LOCAL_SPILL_GB': 'Local Spill (GB)', 'WAREHOUSE_NAME': 'Warehouse'},
                    color='TOTAL_LOCAL_SPILL_GB',
                    color_continuous_scale='Oranges'
                )
                st.plotly_chart(fig_local_spill, use_container_width=True)
            
            with col2:
                fig_remote_spill = px.bar(
                    df_spillage_by_wh.head(10),
                    x='WAREHOUSE_NAME',
                    y='TOTAL_REMOTE_SPILL_GB',
                    title='Top 10 Warehouses by Remote Storage Spillage',
                    labels={'TOTAL_REMOTE_SPILL_GB': 'Remote Spill (GB)', 'WAREHOUSE_NAME': 'Warehouse'},
                    color='TOTAL_REMOTE_SPILL_GB',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig_remote_spill, use_container_width=True)
            
            # Summary metrics
            total_local_spill = df_spillage_by_wh['TOTAL_LOCAL_SPILL_GB'].sum()
            total_remote_spill = df_spillage_by_wh['TOTAL_REMOTE_SPILL_GB'].sum()
            total_queries_with_spill = df_spillage_by_wh['QUERIES_WITH_LOCAL_SPILL'].sum() + df_spillage_by_wh['QUERIES_WITH_REMOTE_SPILL'].sum()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Local Spillage", f"{total_local_spill:.2f} GB")
            with col2:
                st.metric("Total Remote Spillage", f"{total_remote_spill:.2f} GB")
            with col3:
                st.metric("Queries with Spillage", f"{total_queries_with_spill:,.0f}")
            
            st.markdown("**Spillage Details by Warehouse:**")
            st.dataframe(
                df_spillage_by_wh,
                column_config={
                    "WAREHOUSE_NAME": "Warehouse",
                    "QUERIES_WITH_LOCAL_SPILL": st.column_config.NumberColumn("Queries w/ Local Spill", format="%d"),
                    "QUERIES_WITH_REMOTE_SPILL": st.column_config.NumberColumn("Queries w/ Remote Spill", format="%d"),
                    "TOTAL_LOCAL_SPILL_GB": st.column_config.NumberColumn("Local Spill (GB)", format="%.2f"),
                    "TOTAL_REMOTE_SPILL_GB": st.column_config.NumberColumn("Remote Spill (GB)", format="%.2f"),
                    "LOCAL_SPILL_PCT": st.column_config.NumberColumn("Local Spill %", format="%.2f"),
                    "REMOTE_SPILL_PCT": st.column_config.NumberColumn("Remote Spill %", format="%.2f")
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Check for high spillage
            high_local_spill = df_spillage_by_wh[df_spillage_by_wh['LOCAL_SPILL_PCT'] > 5]
            high_remote_spill = df_spillage_by_wh[df_spillage_by_wh['REMOTE_SPILL_PCT'] > 1]
            
            if not high_local_spill.empty:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning(f"⚠️ **{len(high_local_spill)} warehouse(s) with >5% local disk spillage**. Consider increasing warehouse size to add more memory.")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if not high_remote_spill.empty:
                st.markdown('<div class="danger-card">', unsafe_allow_html=True)
                st.error(f"⚠️ **Critical: {len(high_remote_spill)} warehouse(s) with >1% remote storage spillage**. This severely impacts performance. Increase warehouse size immediately.")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.info("""
            💡 **Spillage Information**:
            - **Local Disk Spillage**: Occurs when query memory exceeds available warehouse memory. Data spills to local SSD.
            - **Remote Storage Spillage**: Occurs when local disk is full. Data spills to remote storage (S3/Azure/GCS). **Severe performance impact**.
            - **Recommendation**: If spillage occurs frequently, increase warehouse size to provide more memory.
            """)
        else:
            st.success("✅ No significant query spillage detected in the selected period.")
            
    except Exception as e:
        st.error(f"Error fetching spillage data: {str(e)}")


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
    
    # Query 3: Task Execution Reliability
    st.subheader("3. Task Execution Reliability")
    
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
        AND database_name NOT IN ('SNOWFLAKE', 'SECURITY_NETWORK_DB')
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
    
    st.markdown("---")
    
    # Query 4: Event Table Monitoring
    st.subheader("4. Event Table Monitoring")
    
    st.markdown("""
    **Event Tables** provide a centralized way to monitor and trace events across your Snowflake account, 
    including errors, warnings, and audit logs from various services like tasks, UDFs, and stored procedures.
    """)
    
    try:
        # Check for event tables
        query_event_tables = "SHOW EVENT TABLES IN ACCOUNT"
        
        df_event_tables = session.sql(query_event_tables).to_pandas()
        
        # Filter out Snowflake-owned event tables
        if not df_event_tables.empty:
            # Column names might be uppercase
            owner_col = None
            for col in df_event_tables.columns:
                if col.upper() == 'OWNER':
                    owner_col = col
                    break
            
            if owner_col:
                df_event_tables = df_event_tables[df_event_tables[owner_col] != 'SNOWFLAKE']
        
        if not df_event_tables.empty:
            st.success(f"✅ Your account has {len(df_event_tables)} event table(s) configured for centralized monitoring!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Event Tables", f"{len(df_event_tables):,.0f}")
            with col2:
                # Get objects using event tables
                df_monitored = pd.DataFrame()  # Initialize empty DataFrame
                query_objects_monitored = """
                SELECT 
                    object_type,
                    COUNT(DISTINCT object_name) as count
                FROM (
                    SELECT 'TASK' as object_type, name as object_name
                    FROM snowflake.account_usage.tasks
                    WHERE deleted IS NULL AND error_integration IS NOT NULL
                    
                    UNION ALL
                    
                    SELECT 'FUNCTION' as object_type, function_name as object_name
                    FROM snowflake.account_usage.functions
                    WHERE deleted IS NULL AND is_event_logging_enabled = 'Y'
                    
                    UNION ALL
                    
                    SELECT 'PROCEDURE' as object_type, procedure_name as object_name
                    FROM snowflake.account_usage.procedures
                    WHERE deleted IS NULL AND is_event_logging_enabled = 'Y'
                )
                GROUP BY object_type
                """
                
                try:
                    df_monitored = session.sql(query_objects_monitored).to_pandas()
                    if not df_monitored.empty:
                        total_monitored = df_monitored['COUNT'].sum()
                        st.metric("Objects Monitored", f"{total_monitored:,.0f}")
                    else:
                        st.metric("Objects Monitored", "0")
                except:
                    st.metric("Objects Monitored", "N/A")
            
            st.markdown("**Configured Event Tables:**")
            st.dataframe(
                df_event_tables,
                hide_index=True,
                use_container_width=True
            )
            
            # Show objects being monitored
            if not df_monitored.empty:
                st.markdown("**Objects with Event Logging:**")
                fig_monitored = px.bar(
                    df_monitored,
                    x='OBJECT_TYPE',
                    y='COUNT',
                    title='Objects with Event Logging Enabled',
                    labels={'COUNT': 'Count', 'OBJECT_TYPE': 'Object Type'}
                )
                st.plotly_chart(fig_monitored, use_container_width=True)
            
            st.info("""
            💡 **Benefits of Event Tables:**
            - Centralized error tracking and diagnostics
            - Enhanced observability for tasks, UDFs, and stored procedures
            - Integration with external monitoring tools
            - Long-term audit and compliance logs
            
            [Learn more about Event Tables](https://docs.snowflake.com/en/developer-guide/logging-tracing/event-table-setting-up)
            """)
        else:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.warning("⚠️ **No event tables configured**. Event tables provide centralized monitoring and error tracking for your Snowflake objects.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("""
            **Why use Event Tables?**
            
            Event tables help you:
            - 🔍 **Track errors**: Centralize error logs from tasks, UDFs, and stored procedures
            - 📊 **Monitor performance**: Analyze execution patterns and identify bottlenecks
            - 🛡️ **Ensure compliance**: Maintain audit trails for regulatory requirements
            - 🔔 **Set up alerts**: Trigger notifications based on specific events
            
            **How to create an Event Table:**
            """)
            
            st.code("""
-- Step 1: Create an event table
CREATE EVENT TABLE my_events_db.my_events_schema.my_event_table;

-- Step 2: Set it as the account-level event table
ALTER ACCOUNT SET EVENT_TABLE = my_events_db.my_events_schema.my_event_table;

-- Step 3: Enable event logging on objects (example for tasks)
CREATE TASK my_task
  WAREHOUSE = my_warehouse
  SCHEDULE = '5 MINUTE'
AS
  CALL my_procedure();

-- Event logging is automatically enabled for tasks when an account event table is set

-- Step 4: Query events
SELECT *
FROM my_events_db.my_events_schema.my_event_table
WHERE timestamp >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
ORDER BY timestamp DESC;
            """, language="sql")
            
            st.info("📚 **Learn more**: [Event Tables Documentation](https://docs.snowflake.com/en/developer-guide/logging-tracing/event-table-setting-up)")
            
    except Exception as e:
        st.warning(f"Unable to fetch event table information: {str(e)}")

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
            # Strip quotes and convert to lowercase for comparison
            col_clean = col.strip('"').lower()
            if col_clean == 'name':
                column_mapping[col] = 'WAREHOUSE_NAME'
            elif col_clean == 'size':
                column_mapping[col] = 'WAREHOUSE_SIZE'
            elif col_clean == 'type':
                column_mapping[col] = 'WAREHOUSE_TYPE'
            elif col_clean == 'auto_suspend':
                column_mapping[col] = 'AUTO_SUSPEND'
            elif col_clean == 'auto_resume':
                column_mapping[col] = 'AUTO_RESUME'
            elif col_clean == 'min_cluster_count':
                column_mapping[col] = 'MIN_CLUSTER_COUNT'
            elif col_clean == 'max_cluster_count':
                column_mapping[col] = 'MAX_CLUSTER_COUNT'
            elif col_clean == 'scaling_policy':
                column_mapping[col] = 'SCALING_POLICY'
        
        df_wh_config.rename(columns=column_mapping, inplace=True)
        
        # Ensure required columns exist (fallback if mapping didn't work)
        if 'AUTO_SUSPEND' not in df_wh_config.columns:
            # Try to find the actual column name
            for col in df_wh_config.columns:
                if 'suspend' in col.strip('"').lower():
                    df_wh_config['AUTO_SUSPEND'] = df_wh_config[col]
                    break
        
        if 'AUTO_RESUME' not in df_wh_config.columns:
            for col in df_wh_config.columns:
                if 'resume' in col.strip('"').lower():
                    df_wh_config['AUTO_RESUME'] = df_wh_config[col]
                    break
        
        # Check for warehouses without auto-suspend (NULL or 0)
        if 'AUTO_SUSPEND' in df_wh_config.columns:
            no_auto_suspend = df_wh_config[df_wh_config['AUTO_SUSPEND'].isnull() | (df_wh_config['AUTO_SUSPEND'] == 0)]
            long_auto_suspend = df_wh_config[df_wh_config['AUTO_SUSPEND'] > 600]
        else:
            no_auto_suspend = pd.DataFrame()
            long_auto_suspend = pd.DataFrame()
        
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
            display_cols = ['WAREHOUSE_NAME', 'WAREHOUSE_SIZE']
            if 'AUTO_SUSPEND' in no_auto_suspend.columns:
                display_cols.append('AUTO_SUSPEND')
            if 'AUTO_RESUME' in no_auto_suspend.columns:
                display_cols.append('AUTO_RESUME')
            st.dataframe(no_auto_suspend[display_cols], hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        if len(long_auto_suspend) > 0:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.warning(f"⚠️ **Recommendation**: {len(long_auto_suspend)} warehouse(s) have auto-suspend > 10 minutes. Consider reducing to 60-300 seconds for cost optimization.")
            display_cols = ['WAREHOUSE_NAME', 'WAREHOUSE_SIZE']
            if 'AUTO_SUSPEND' in long_auto_suspend.columns:
                display_cols.append('AUTO_SUSPEND')
            st.dataframe(long_auto_suspend[display_cols], hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        if len(no_auto_suspend) == 0 and len(long_auto_suspend) == 0:
            st.success("✅ All warehouses have appropriate auto-suspend configuration.")
        
        # Display full configuration
        st.markdown("**Warehouse Configuration Details:**")
        column_config = {}
        if 'WAREHOUSE_NAME' in df_wh_config.columns:
            column_config["WAREHOUSE_NAME"] = "Warehouse"
        if 'WAREHOUSE_SIZE' in df_wh_config.columns:
            column_config["WAREHOUSE_SIZE"] = "Size"
        if 'WAREHOUSE_TYPE' in df_wh_config.columns:
            column_config["WAREHOUSE_TYPE"] = "Type"
        if 'AUTO_SUSPEND' in df_wh_config.columns:
            column_config["AUTO_SUSPEND"] = "Auto-Suspend (sec)"
        if 'AUTO_RESUME' in df_wh_config.columns:
            column_config["AUTO_RESUME"] = "Auto-Resume"
        if 'MIN_CLUSTER_COUNT' in df_wh_config.columns:
            column_config["MIN_CLUSTER_COUNT"] = "Min Clusters"
        if 'MAX_CLUSTER_COUNT' in df_wh_config.columns:
            column_config["MAX_CLUSTER_COUNT"] = "Max Clusters"
        if 'SCALING_POLICY' in df_wh_config.columns:
            column_config["SCALING_POLICY"] = "Scaling Policy"
        
        st.dataframe(
            df_wh_config,
            column_config=column_config,
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
                
                # Hourly idle pattern analysis for top 5 warehouses
                st.markdown("---")
                st.markdown("**Hourly Idle Patterns - Last 7 Days (Top 5 Warehouses):**")
                
                # Get top 5 warehouses by idle credits
                top5_warehouses = df_idle.head(5)['WAREHOUSE_NAME'].tolist()
                
                query_hourly_idle = f"""
                WITH hourly_usage AS (
                    SELECT
                        warehouse_name,
                        HOUR(start_time) as hour_of_day,
                        SUM(credits_used_compute) as total_compute_credits,
                        SUM(credits_attributed_compute_queries) as query_credits,
                        (SUM(credits_used_compute) - SUM(credits_attributed_compute_queries)) as idle_credits
                    FROM snowflake.account_usage.warehouse_metering_history
                    WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
                        AND warehouse_name IN ('{"','".join(top5_warehouses)}')
                    GROUP BY warehouse_name, HOUR(start_time)
                )
                SELECT
                    warehouse_name,
                    hour_of_day,
                    idle_credits,
                    CASE 
                        WHEN total_compute_credits > 0 
                        THEN (idle_credits / total_compute_credits) * 100
                        ELSE 0 
                    END as idle_pct
                FROM hourly_usage
                WHERE idle_credits > 0
                ORDER BY warehouse_name, hour_of_day
                """
                
                try:
                    df_hourly_idle = session.sql(query_hourly_idle).to_pandas()
                    
                    if not df_hourly_idle.empty:
                        # Create pivot table for heatmap
                        df_pivot = df_hourly_idle.pivot(
                            index='WAREHOUSE_NAME',
                            columns='HOUR_OF_DAY',
                            values='IDLE_PCT'
                        ).fillna(0)
                        
                        # Ensure all hours 0-23 are present
                        for hour in range(24):
                            if hour not in df_pivot.columns:
                                df_pivot[hour] = 0
                        df_pivot = df_pivot.sort_index(axis=1)
                        
                        # Create heatmap
                        fig_heatmap = px.imshow(
                            df_pivot,
                            labels=dict(x="Hour of Day", y="Warehouse", color="Idle %"),
                            x=[f"{h:02d}:00" for h in range(24)],
                            y=df_pivot.index,
                            aspect="auto",
                            color_continuous_scale="Reds",
                            title="Idle Time Patterns by Hour of Day - Last 7 Days (Top 5 Warehouses)"
                        )
                        fig_heatmap.update_layout(height=400)
                        st.plotly_chart(fig_heatmap, use_container_width=True)
                        
                        # Create line chart as alternative view
                        fig_line = px.line(
                            df_hourly_idle,
                            x='HOUR_OF_DAY',
                            y='IDLE_PCT',
                            color='WAREHOUSE_NAME',
                            title='Idle Time % Throughout the Day - Last 7 Days (Top 5 Warehouses)',
                            labels={'HOUR_OF_DAY': 'Hour of Day', 'IDLE_PCT': 'Idle Time %', 'WAREHOUSE_NAME': 'Warehouse'},
                            markers=True
                        )
                        fig_line.update_xaxes(
                            tickmode='linear',
                            tick0=0,
                            dtick=2,
                            range=[0, 23]
                        )
                        st.plotly_chart(fig_line, use_container_width=True)
                        
                        st.info("💡 **Insight**: The heatmap and line chart show when warehouses are idle throughout the day. Dark red areas indicate high idle time. Consider adjusting auto-suspend timeouts or scheduling queries to avoid idle periods.")
                    else:
                        st.info("Insufficient hourly data for idle pattern analysis.")
                        
                except Exception as e:
                    st.info(f"Hourly idle pattern analysis unavailable: {str(e)}")
                
                st.info("💡 **Tip**: Idle time occurs when warehouses are running but not executing queries. Reduce auto-suspend timeouts (60-300 seconds) to minimize idle credits.")
            else:
                st.info("No idle time detected or insufficient data for analysis.")
                
        except Exception as e:
            st.info(f"Idle time analysis unavailable: {str(e)}")
            
    except Exception as e:
        st.error(f"Error fetching warehouse configuration: {str(e)}")
    
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
            SUM(TO_NUMBER(files_inserted)) as total_files_loaded,
            SUM(bytes_inserted) / POWER(1024, 3) as total_gb_loaded,
            SUM(bytes_billed) / POWER(1024, 3) as total_gb_billed,
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
                total_gb = df_pipe_usage['TOTAL_GB_LOADED'].sum()
                total_gb_billed = df_pipe_usage['TOTAL_GB_BILLED'].sum()
                total_credits = df_pipe_usage['TOTAL_CREDITS_USED'].sum()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Files Loaded", f"{total_files:,.0f}")
                with col2:
                    st.metric("Total GB Loaded", f"{total_gb:.2f}")
                with col3:
                    st.metric("Total GB Billed", f"{total_gb_billed:.2f}")
                with col4:
                    st.metric("Total Credits", f"{total_credits:.2f}")
                
                st.markdown("**Detailed Pipe Usage:**")
                st.dataframe(
                    df_pipe_usage,
                    column_config={
                        "PIPE_NAME": "Pipe Name",
                        "LOAD_EVENTS": "Load Events",
                        "TOTAL_FILES_LOADED": st.column_config.NumberColumn("Files Loaded", format="%d"),
                        "TOTAL_GB_LOADED": st.column_config.NumberColumn("GB Loaded", format="%.2f"),
                        "TOTAL_GB_BILLED": st.column_config.NumberColumn("GB Billed", format="%.2f"),
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
    
    # Query 4: Long-Running Queries
    st.subheader("4. Long-Running Query Detection")
    
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
    
    # Query 5: Query Execution Patterns
    st.subheader("5. Query Execution Patterns")
    
    query_patterns = f"""
    SELECT 
        user_name,
        query_type,
        COUNT(*) as query_count,
        AVG(execution_time) / 1000 as avg_execution_time_sec,
        COUNT(DISTINCT warehouse_name) as warehouses_used
    FROM snowflake.account_usage.query_history
    WHERE start_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
        AND user_name NOT IN ('SYSTEM', 'dataplane_service')
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
    
    st.markdown("---")
    
    # Query 6: Data Metric Functions (DMF)
    st.subheader("6. Data Metric Functions Usage")
    
    try:
        query_dmf = """
        SELECT 
            metric_database_name,
            metric_schema_name,
            metric_name,
            ref_database_name,
            ref_schema_name,
            ref_entity_name,
            schedule,
            schedule_status
        FROM snowflake.account_usage.data_metric_function_references
        WHERE schedule_status NOT LIKE 'SUSPENDED%'
        ORDER BY ref_entity_name
        """
        
        df_dmf = session.sql(query_dmf).to_pandas()
        
        if not df_dmf.empty:
            total_dmf = len(df_dmf)
            unique_tables = df_dmf[['REF_DATABASE_NAME', 'REF_SCHEMA_NAME', 'REF_ENTITY_NAME']].drop_duplicates()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Active DMF References", f"{total_dmf:,.0f}")
            with col2:
                st.metric("Tables/Views Monitored", f"{len(unique_tables):,.0f}")
            
            st.success("✅ Your organization is using Data Metric Functions for data quality monitoring!")
            
            st.dataframe(
                df_dmf,
                column_config={
                    "METRIC_DATABASE_NAME": "DMF Database",
                    "METRIC_SCHEMA_NAME": "DMF Schema",
                    "METRIC_NAME": "Metric Name",
                    "REF_DATABASE_NAME": "Monitored Database",
                    "REF_SCHEMA_NAME": "Monitored Schema",
                    "REF_ENTITY_NAME": "Monitored Object",
                    "SCHEDULE": "Schedule",
                    "SCHEDULE_STATUS": "Status"
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.info("💡 **Tip**: Data Metric Functions help monitor data quality in real-time. [Learn more](https://docs.snowflake.com/en/user-guide/data-quality-intro)")
        else:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.warning("⚠️ **No Data Metric Functions detected**. DMFs help monitor data quality and detect anomalies in your tables.")
            st.markdown('</div>', unsafe_allow_html=True)
            st.code("""
-- Example: Create a DMF to monitor null values
CREATE OR REPLACE DATA METRIC FUNCTION check_nulls_dmf(
    arg_t TABLE(arg_col NUMBER)
)
RETURNS NUMBER
AS 
$$
SELECT COUNT(*) FROM arg_t WHERE arg_col IS NULL
$$;

-- Attach to a table
ALTER TABLE my_table
    SET DATA_METRIC SCHEDULE = '1 HOUR'
    DATA METRIC FUNCTION check_nulls_dmf ON (my_column);
            """, language="sql")
            
    except Exception as e:
        st.warning(f"Unable to fetch Data Metric Functions: {str(e)}")
    
    st.markdown("---")
    
    # Query 7: Alert Usages
    st.subheader("7. Alert Configuration & History")
    
    try:
        # Get alerts using SHOW ALERTS
        query_alerts = "SHOW ALERTS"
        
        df_alerts = session.sql(query_alerts).to_pandas()
        
        if not df_alerts.empty:
            total_alerts = len(df_alerts)
            # Check for 'state' column (could be uppercase or lowercase)
            state_col = None
            for col in df_alerts.columns:
                if col.upper() == 'STATE':
                    state_col = col
                    break
            
            if state_col:
                started_alerts = len(df_alerts[df_alerts[state_col] == 'started'])
                suspended_alerts = len(df_alerts[df_alerts[state_col] == 'suspended'])
            else:
                started_alerts = 0
                suspended_alerts = 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Alerts", f"{total_alerts:,.0f}")
            with col2:
                st.metric("Active Alerts", f"{started_alerts:,.0f}", 
                         delta="✅" if started_alerts > 0 else None)
            with col3:
                st.metric("Suspended Alerts", f"{suspended_alerts:,.0f}")
            
            st.success(f"✅ Your account has {total_alerts} alert(s) configured for proactive monitoring!")
            
            # Display alerts
            st.markdown("**Configured Alerts:**")
            st.dataframe(
                df_alerts,
                hide_index=True,
                use_container_width=True
            )
            
            # Get alert history
            st.markdown("---")
            st.markdown("**Recent Alert Execution History:**")
            
            query_alert_history = f"""
            SELECT 
                alert_name,
                alert_id,
                database_name,
                schema_name,
                scheduled_time,
                completed_time,
                state,
                condition_query_text,
                action_query_text,
                error_message
            FROM snowflake.account_usage.alert_history
            WHERE scheduled_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
            ORDER BY scheduled_time DESC
            LIMIT 50
            """
            
            df_alert_history = session.sql(query_alert_history).to_pandas()
            
            if not df_alert_history.empty:
                # Count successful vs failed
                success_count = len(df_alert_history[df_alert_history['STATE'] == 'SUCCEEDED'])
                failed_count = len(df_alert_history[df_alert_history['STATE'].isin(['FAILED', 'SKIPPED'])])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Successful Executions", f"{success_count:,.0f}")
                with col2:
                    st.metric("Failed/Skipped", f"{failed_count:,.0f}", 
                             delta="⚠️" if failed_count > 0 else None)
                
                st.dataframe(
                    df_alert_history,
                    column_config={
                        "ALERT_NAME": "Alert Name",
                        "DATABASE_NAME": "Database",
                        "SCHEMA_NAME": "Schema",
                        "SCHEDULED_TIME": "Scheduled Time",
                        "COMPLETED_TIME": "Completed Time",
                        "STATE": "State",
                        "ERROR_MESSAGE": st.column_config.TextColumn("Error Message", width="medium")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                if failed_count > 0:
                    st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                    st.warning(f"⚠️ **{failed_count} alert execution(s) failed or were skipped**. Review error messages and alert conditions.")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("ℹ️ No alert execution history found in the selected period.")
            
            st.info("💡 **Tip**: Alerts help you proactively monitor data quality, pipeline health, and system performance. [Learn more](https://docs.snowflake.com/en/user-guide/alerts)")
        else:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.warning("⚠️ **No alerts configured**. Alerts help you proactively detect and respond to issues in your data pipelines.")
            st.markdown('</div>', unsafe_allow_html=True)
            st.code("""
-- Example: Create an alert for failed tasks
CREATE OR REPLACE ALERT task_failure_alert
  WAREHOUSE = my_warehouse
  SCHEDULE = '5 MINUTE'
  IF (EXISTS (
    SELECT 1
    FROM snowflake.account_usage.task_history
    WHERE state = 'FAILED'
      AND completed_time >= DATEADD(minute, -5, CURRENT_TIMESTAMP())
  ))
  THEN
    -- Define action (e.g., call stored procedure, send notification)
    CALL notify_on_task_failure();

-- Start the alert
ALTER ALERT task_failure_alert RESUME;
            """, language="sql")
            
    except Exception as e:
        st.warning(f"Unable to fetch alert data: {str(e)}")
    
    st.markdown("---")
    
    # Query 8: Account Timezone
    st.subheader("8. Account Timezone Configuration")
    
    try:
        query_timezone = """
        SELECT CURRENT_ACCOUNT() as account_name,
               CURRENT_TIMESTAMP() as current_timestamp,
               CONVERT_TIMEZONE('UTC', CURRENT_TIMESTAMP()) as utc_timestamp
        """
        
        # Get timezone parameter
        query_tz_param = "SHOW PARAMETERS LIKE 'TIMEZONE' IN ACCOUNT"
        
        df_tz_info = session.sql(query_timezone).to_pandas()
        df_tz_param = session.sql(query_tz_param).to_pandas()
        
        if not df_tz_param.empty:
            # Find the value column - could be 'value', 'VALUE', or quoted '"value"'
            value_col = None
            for col in df_tz_param.columns:
                if col.upper() == 'VALUE' or col.strip('"').upper() == 'VALUE':
                    value_col = col
                    break
            
            if value_col is None:
                raise ValueError(f"VALUE column not found. Available columns: {list(df_tz_param.columns)}")
            
            timezone = df_tz_param.iloc[0][value_col]
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Account Timezone", timezone)
            with col2:
                if not df_tz_info.empty:
                    current_ts = df_tz_info.iloc[0]['CURRENT_TIMESTAMP']
                    st.metric("Current Account Time", current_ts.strftime('%Y-%m-%d %H:%M:%S %Z') if hasattr(current_ts, 'strftime') else str(current_ts))
            
            st.info(f"""
            ℹ️ **Current Configuration**: Your account timezone is set to **{timezone}**.
            
            All timestamp operations (e.g., CURRENT_TIMESTAMP(), task schedules, query history) use this timezone.
            """)
            
            st.markdown("**How to change timezone:**")
            st.code("""
-- Change account timezone (requires ACCOUNTADMIN role)
ALTER ACCOUNT SET TIMEZONE = 'America/New_York';

-- View available timezones
SELECT * FROM TABLE(INFORMATION_SCHEMA.TIMEZONES());

-- Common timezones:
-- 'America/New_York' (EST/EDT)
-- 'America/Los_Angeles' (PST/PDT)
-- 'America/Chicago' (CST/CDT)
-- 'Europe/London' (GMT/BST)
-- 'Asia/Tokyo' (JST)
-- 'UTC' (Coordinated Universal Time)
            """, language="sql")
            
            st.warning("⚠️ **Important**: Changing the timezone affects all timestamp operations account-wide. Coordinate with your team before making changes.")
        
    except Exception as e:
        st.warning(f"Unable to fetch timezone configuration: {str(e)}")

# ============================================================================
# TAB 4: SECURITY & GOVERNANCE
# ============================================================================
with tab4:
    st.header("Security & Governance")
    st.markdown("""
    Best practices from [Snowflake Well-Architected Framework - Security & Governance](https://www.snowflake.com/en/developers/guides/well-architected-framework-security-and-governance/)
    """)
    
    # Query 1: MFA/SSO Authentication
    st.subheader("1. Multi-Factor Authentication (MFA)")
    
    # SSO Toggle
    uses_sso = st.checkbox(
        "🔐 Organization Uses SSO (Single Sign-On)",
        value=False,
        help="Enable if your organization uses SSO for authentication. This will show users created outside of SSO."
    )
    
    if uses_sso:
        # Show users NOT using SSO
        query_non_sso_users = """
        SELECT 
            name as user_name,
            login_name,
            email,
            created_on,
            last_success_login,
            disabled,
            ext_authn_duo as has_mfa,
            default_role
        FROM snowflake.account_usage.users
        WHERE deleted_on IS NULL
            AND disabled = FALSE
            AND (ext_authn_uid IS NULL OR ext_authn_uid = '')
            AND login_name NOT LIKE '%SF$SERVICE%'
        ORDER BY created_on DESC
        """
        
        try:
            df_non_sso = session.sql(query_non_sso_users).to_pandas()
            
            if not df_non_sso.empty:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning(f"⚠️ **{len(df_non_sso)} user(s) created outside SSO**. These users bypass SSO authentication and may pose a security risk.")
                st.markdown('</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Non-SSO Users", len(df_non_sso))
                with col2:
                    non_sso_with_mfa = len(df_non_sso[df_non_sso['HAS_MFA'] == True])
                    st.metric("Non-SSO Users with MFA", non_sso_with_mfa)
                
                st.markdown("**Non-SSO Users Detail:**")
                st.dataframe(
                    df_non_sso,
                    column_config={
                        "USER_NAME": "User Name",
                        "LOGIN_NAME": "Login Name",
                        "EMAIL": "Email",
                        "CREATED_ON": "Created On",
                        "LAST_SUCCESS_LOGIN": "Last Login",
                        "HAS_MFA": "MFA Enabled",
                        "DEFAULT_ROLE": "Default Role"
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                st.info("💡 **Recommendation**: For SSO-enabled organizations, disable or migrate non-SSO users to SSO authentication. Ensure all non-SSO users have MFA enabled as a minimum.")
            else:
                st.success("✅ All users are configured to use SSO authentication.")
                
        except Exception as e:
            st.error(f"Error fetching non-SSO user data: {str(e)}")
    else:
        # Show MFA adoption
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
            AND login_name NOT LIKE '%SF$SERVICE%'
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
        policy_db,
        policy_schema
    FROM snowflake.account_usage.policy_references
    WHERE policy_kind IN ('MASKING_POLICY', 'ROW_ACCESS_POLICY')
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
    
    # Query 5: Notification Contacts
    st.subheader("5. Notification Contacts Configuration")
    
    try:
        query_notification_contacts = "SHOW CONTACTS"
        
        df_contacts = session.sql(query_notification_contacts).to_pandas()
        
        if not df_contacts.empty:
            total_contacts = len(df_contacts)
            
            st.metric("Configured Contacts", f"{total_contacts:,.0f}")
            
            st.success(f"✅ Your account has {total_contacts} notification contact(s) configured!")
            
            st.dataframe(
                df_contacts,
                hide_index=True,
                use_container_width=True
            )
            
            st.info("""
            💡 **Contacts** are used to receive notifications from Snowflake about:
            - Account security updates
            - Product updates and announcements
            - Service notifications
            - Data governance alerts
            
            **How to add contacts:**
            1. Navigate to **Admin > Contacts** in Snowsight
            2. Click **+ Contact** to add a new contact
            3. Specify email address and notification types
            """)
        else:
            st.markdown('<div class="danger-card">', unsafe_allow_html=True)
            st.error("⚠️ **Critical**: No notification contacts configured. You won't receive important updates from Snowflake.")
            st.markdown('</div>', unsafe_allow_html=True)
            st.code("""
-- To create a contact (requires ACCOUNTADMIN):
CREATE CONTACT admin_contact
    TYPE = EMAIL
    EMAIL = 'admin@yourcompany.com'
    COMMENT = 'Primary admin contact for security notifications';

-- Or use Snowsight: Admin > Contacts > + Contact
            """, language="sql")
            
    except Exception as e:
        st.warning(f"Unable to fetch notification contacts: {str(e)}")
    
    st.markdown("---")
    
    # Query 6: Failed Login Attempts
    st.subheader("6. Failed Authentication Attempts")
    
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
    
    st.markdown("---")
    
    # Query 7: Data Governance Metrics
    st.subheader("7. Data Governance & Security Policies")
    
    try:
        query_governance = """
        WITH tagged_tables AS (
            SELECT COUNT(DISTINCT CONCAT(object_database, '.', object_schema, '.', object_name)) as count
            FROM snowflake.account_usage.tag_references
            WHERE object_deleted IS NULL
                AND domain = 'TABLE'
        ),
        tables_with_rap AS (
            SELECT COUNT(DISTINCT CONCAT(ref_database_name, '.', ref_schema_name, '.', ref_entity_name)) as count
            FROM snowflake.account_usage.policy_references
            WHERE policy_kind = 'ROW_ACCESS_POLICY'
                AND ref_entity_domain = 'TABLE'
                AND policy_status = 'ACTIVE'
        ),
        tagged_columns AS (
            SELECT COUNT(DISTINCT CONCAT(object_database, '.', object_schema, '.', object_name, '.', column_name)) as count
            FROM snowflake.account_usage.tag_references
            WHERE object_deleted IS NULL
                AND domain = 'COLUMN'
        ),
        columns_with_masking AS (
            SELECT COUNT(DISTINCT CONCAT(ref_database_name, '.', ref_schema_name, '.', ref_entity_name, '.', ref_column_name)) as count
            FROM snowflake.account_usage.policy_references
            WHERE policy_kind = 'MASKING_POLICY'
                AND ref_entity_domain = 'COLUMN'
                AND policy_status = 'ACTIVE'
        ),
        total_tables AS (
            SELECT COUNT(*) as count
            FROM snowflake.account_usage.tables
            WHERE deleted IS NULL
                AND table_type = 'BASE TABLE'
        ),
        total_columns AS (
            SELECT COUNT(*) as count
            FROM snowflake.account_usage.columns
            WHERE deleted IS NULL
        )
        SELECT
            tt.count as tagged_tables,
            (SELECT count FROM total_tables) as total_tables,
            rap.count as tables_with_row_access_policy,
            tc.count as tagged_columns,
            (SELECT count FROM total_columns) as total_columns,
            mp.count as columns_with_masking_policy
        FROM tagged_tables tt, tables_with_rap rap, tagged_columns tc, columns_with_masking mp
        """
        
        df_governance = session.sql(query_governance).to_pandas()
        
        if not df_governance.empty:
            row = df_governance.iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                tagged_pct = (row['TAGGED_TABLES'] / row['TOTAL_TABLES'] * 100) if row['TOTAL_TABLES'] > 0 else 0
                st.metric(
                    "Tagged Tables",
                    f"{row['TAGGED_TABLES']:,.0f}",
                    f"{tagged_pct:.1f}% of {row['TOTAL_TABLES']:,.0f}"
                )
            
            with col2:
                rap_pct = (row['TABLES_WITH_ROW_ACCESS_POLICY'] / row['TOTAL_TABLES'] * 100) if row['TOTAL_TABLES'] > 0 else 0
                st.metric(
                    "Tables with Row Access Policy",
                    f"{row['TABLES_WITH_ROW_ACCESS_POLICY']:,.0f}",
                    f"{rap_pct:.1f}% of {row['TOTAL_TABLES']:,.0f}"
                )
            
            with col3:
                tagged_col_pct = (row['TAGGED_COLUMNS'] / row['TOTAL_COLUMNS'] * 100) if row['TOTAL_COLUMNS'] > 0 else 0
                st.metric(
                    "Tagged Columns",
                    f"{row['TAGGED_COLUMNS']:,.0f}",
                    f"{tagged_col_pct:.1f}% of {row['TOTAL_COLUMNS']:,.0f}"
                )
            
            with col4:
                masked_pct = (row['COLUMNS_WITH_MASKING_POLICY'] / row['TOTAL_COLUMNS'] * 100) if row['TOTAL_COLUMNS'] > 0 else 0
                st.metric(
                    "Columns with Masking Policy",
                    f"{row['COLUMNS_WITH_MASKING_POLICY']:,.0f}",
                    f"{masked_pct:.1f}% of {row['TOTAL_COLUMNS']:,.0f}"
                )
            
            # Recommendations based on metrics
            recommendations = []
            if tagged_pct < 20:
                recommendations.append("📌 **Low table tagging**: Consider implementing a tagging strategy to classify your data assets.")
            if rap_pct < 5:
                recommendations.append("🔒 **Limited row-level security**: Review if any tables contain sensitive data that should have row access policies.")
            if masked_pct < 5:
                recommendations.append("🎭 **Limited data masking**: Review if any columns contain PII/sensitive data that should be masked.")
            
            if recommendations:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning("**Data Governance Recommendations:**")
                for rec in recommendations:
                    st.markdown(f"- {rec}")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.success("✅ Good data governance posture detected.")
            
            st.info("💡 **Learn more**: [Snowflake Data Governance](https://docs.snowflake.com/en/guides-overview-govern)")
        
    except Exception as e:
        st.warning(f"Unable to fetch data governance metrics: {str(e)}")
    
    st.markdown("---")
    
    # Query 8: Trust Center Security Violations
    st.subheader("8. Trust Center Security Violations")
    
    st.markdown("""
    **Trust Center** provides security posture monitoring and compliance insights for your Snowflake account.
    
    🔗 **[Open Trust Center in Snowsight →](https://app.snowflake.com/trust-center)**
    """)
    
    try:
        # Note: Trust Center data is not yet available via SQL in ACCOUNT_USAGE
        # This is a placeholder for when Snowflake adds this functionality
        st.info("""
        ℹ️ **How to check security violations:**
        
        1. Navigate to [Trust Center](https://app.snowflake.com/trust-center) in Snowsight
        2. Review the **Security Posture** dashboard
        3. Check for any "Open Violations" or "High Priority" items
        4. Follow remediation guidance for each violation
        
        **Common violations to watch for:**
        - Unencrypted network connections
        - Inactive users with access
        - Overly permissive roles
        - Missing MFA on privileged accounts
        - Stale access grants
        """)
        
        st.markdown('<div class="warning-card">', unsafe_allow_html=True)
        st.warning("⚠️ **Manual Review Required**: Trust Center violations are not yet queryable via SQL. Please review manually in Snowsight.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.warning(f"Unable to fetch Trust Center data: {str(e)}")

# ============================================================================
# TAB 5: COST OPTIMIZATION
# ============================================================================
with tab5:
    st.header("Cost Optimization & FinOps")
    st.markdown("""
    Best practices from [Snowflake Well-Architected Framework - Cost Optimization](https://www.snowflake.com/en/developers/guides/well-architected-framework-cost-optimization-and-finops/)
    """)
    
    # Billing Model Selector
    st.markdown("---")
    billing_model = st.radio(
        "**Select Your Billing Model:**",
        options=["On-Demand", "Reserved Capacity (Contract)"],
        horizontal=True,
        help="Select 'Reserved Capacity' if you have a Snowflake contract with upfront capacity commitment. Select 'On-Demand' for pay-as-you-go billing."
    )
    use_demo_data = False  # Demo data removed
    
    # Show billing reconciliation for Reserved Capacity customers
    if billing_model == "Reserved Capacity (Contract)":
        st.markdown("---")
        st.subheader("📊 Contract & Billing Reconciliation")
        st.info("💡 **Note**: These views use Organization Usage schema. Ensure you have ORGADMIN or ACCOUNTADMIN role with appropriate permissions.")
        
        # Reference: https://docs.snowflake.com/en/user-guide/billing-reconcile
        
        # Get current contract information
        st.markdown("**Current Contract Status:**")
        
        try:
            if use_demo_data:
                # Generate sample data for demonstration
                import datetime
                df_balance = pd.DataFrame({
                    'DATE': [datetime.date.today() - datetime.timedelta(days=1)],
                    'CONTRACT_NUMBER': ['SF-12345-2024'],
                    'ORGANIZATION_NAME': ['ACME Corporation'],
                    'CURRENCY': ['USD'],
                    'CAPACITY_BALANCE': [750000.00],
                    'FREE_USAGE_BALANCE': [25000.00],
                    'ROLLOVER_BALANCE': [50000.00],
                    'REMAINING_BALANCE': [825000.00]
                })
                st.info("📊 **Demo Mode**: Showing sample data. This represents a $1M contract with $825K remaining.")
            else:
                # Query for remaining balance
                query_remaining_balance = """
                SELECT 
                    date,
                    contract_number,
                    organization_name,
                    currency,
                    capacity_balance,
                    free_usage_balance,
                    rollover_balance,
                    (capacity_balance + free_usage_balance + rollover_balance) AS remaining_balance
                FROM snowflake.organization_usage.remaining_balance_daily
                WHERE date = CURRENT_DATE() - 1
                ORDER BY contract_number
                """
                
                df_balance = session.sql(query_remaining_balance).to_pandas()
            
            if not df_balance.empty:
                # Display metrics for each contract
                for idx, row in df_balance.iterrows():
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Contract", row['CONTRACT_NUMBER'])
                    with col2:
                        st.metric("Remaining Balance", f"{row['CURRENCY']} {row['REMAINING_BALANCE']:,.2f}")
                    with col3:
                        st.metric("Capacity Balance", f"{row['CURRENCY']} {row['CAPACITY_BALANCE']:,.2f}")
                    with col4:
                        st.metric("Free Usage Balance", f"{row['CURRENCY']} {row['FREE_USAGE_BALANCE']:,.2f}")
                
                st.dataframe(
                    df_balance,
                    column_config={
                        "DATE": "Date",
                        "CONTRACT_NUMBER": "Contract Number",
                        "ORGANIZATION_NAME": "Organization",
                        "CURRENCY": "Currency",
                        "CAPACITY_BALANCE": st.column_config.NumberColumn("Capacity Balance", format="%.2f"),
                        "FREE_USAGE_BALANCE": st.column_config.NumberColumn("Free Usage", format="%.2f"),
                        "ROLLOVER_BALANCE": st.column_config.NumberColumn("Rollover", format="%.2f"),
                        "REMAINING_BALANCE": st.column_config.NumberColumn("Total Remaining", format="%.2f")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.warning("⚠️ No contract balance data found. You may need ORGADMIN privileges or your organization may not have a contract.")
                
        except Exception as e:
            st.warning(f"⚠️ Unable to access organization usage data: {str(e)}\n\nThis typically means you need ORGADMIN or ACCOUNTADMIN role with organization access.")
        
        st.markdown("---")
        st.markdown("**Monthly Usage by Contract:**")
        
        try:
            if use_demo_data:
                # Generate sample monthly usage data
                import datetime
                today = datetime.date.today()
                months = []
                for i in range(3):
                    month_date = today - datetime.timedelta(days=30 * (i+1))
                    month_start = month_date.replace(day=1)
                    months.append(month_start)
                
                # Create sample data for multiple accounts
                data = []
                accounts = ['ABC123-US-EAST-1', 'DEF456-US-WEST-2', 'GHI789-EU-CENTRAL-1']
                base_usage = [45000, 32000, 18000]  # Different usage per account
                
                for month_idx, month in enumerate(months):
                    for acc_idx, account in enumerate(accounts):
                        # Add some variation month to month
                        variation = 1 + (0.1 * (month_idx - 1))  # -10% to +10%
                        consumed = base_usage[acc_idx] * variation
                        credits = consumed / 3  # Rough conversion
                        
                        data.append({
                            'CONTRACT_NUMBER': 'SF-12345-2024',
                            'USAGE_MONTH': pd.Timestamp(month),
                            'ACCOUNT_NAME': account,
                            'TOTAL_CONSUMED': consumed,
                            'TOTAL_CREDITS': credits
                        })
                
                df_monthly = pd.DataFrame(data)
                st.info("📊 **Demo Mode**: Showing sample 3-month usage across 3 accounts.")
            else:
                # Query for monthly usage by contract
                query_monthly_usage = f"""
                SELECT 
                    contract_number,
                    DATE_TRUNC('month', usage_date) AS usage_month,
                    CONCAT(account_locator, '-', region) AS account_name,
                    SUM(usage_in_currency) AS total_consumed,
                    SUM(usage) AS total_credits
                FROM snowflake.organization_usage.usage_in_currency_daily
                WHERE TRUE
                    AND usage_date >= DATEADD(month, -3, CURRENT_DATE())
                    AND LOWER(balance_source) != 'overage'
                GROUP BY 1, 2, 3
                ORDER BY 1, 2 DESC, 4 DESC
                LIMIT 100
                """
                
                df_monthly = session.sql(query_monthly_usage).to_pandas()
            
            if not df_monthly.empty:
                # Chart: Monthly consumption trend
                df_monthly_summary = df_monthly.groupby('USAGE_MONTH')['TOTAL_CONSUMED'].sum().reset_index()
                fig_monthly_trend = px.line(
                    df_monthly_summary,
                    x='USAGE_MONTH',
                    y='TOTAL_CONSUMED',
                    title='Monthly Consumption Trend (Last 3 Months)',
                    labels={'TOTAL_CONSUMED': 'Currency Consumed', 'USAGE_MONTH': 'Month'},
                    markers=True
                )
                st.plotly_chart(fig_monthly_trend, use_container_width=True)
                
                # Detailed table
                st.dataframe(
                    df_monthly.head(50),
                    column_config={
                        "CONTRACT_NUMBER": "Contract",
                        "USAGE_MONTH": "Month",
                        "ACCOUNT_NAME": "Account",
                        "TOTAL_CONSUMED": st.column_config.NumberColumn("Currency Consumed", format="%.2f"),
                        "TOTAL_CREDITS": st.column_config.NumberColumn("Credits Used", format="%.2f")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No monthly usage data available.")
                
        except Exception as e:
            st.warning(f"Unable to access monthly usage data: {str(e)}")
        
        st.markdown("---")
        st.markdown("**Usage by Category:**")
        
        try:
            if use_demo_data:
                # Generate sample usage by category data
                import datetime
                today = datetime.date.today()
                current_month = today.replace(day=1)
                
                # Realistic usage categories with sample data
                categories = [
                    ('WAREHOUSE_METERING', 'ABC123-US-EAST-1', 12500, 35000),
                    ('WAREHOUSE_METERING', 'DEF456-US-WEST-2', 8200, 25000),
                    ('WAREHOUSE_METERING', 'GHI789-EU-CENTRAL-1', 5300, 16000),
                    ('AUTOMATIC_CLUSTERING', 'ABC123-US-EAST-1', 450, 3500),
                    ('AUTOMATIC_CLUSTERING', 'DEF456-US-WEST-2', 280, 2100),
                    ('MATERIALIZED_VIEW_MAINTENANCE', 'ABC123-US-EAST-1', 320, 2800),
                    ('SNOWPIPE', 'ABC123-US-EAST-1', 180, 1800),
                    ('SNOWPIPE', 'DEF456-US-WEST-2', 95, 950),
                    ('REPLICATION', 'ABC123-US-EAST-1', 85, 850),
                    ('QUERY_ACCELERATION', 'DEF456-US-WEST-2', 45, 450),
                    ('SEARCH_OPTIMIZATION', 'ABC123-US-EAST-1', 35, 350),
                    ('CLOUD_SERVICES', 'ABC123-US-EAST-1', 125, 0),  # Often zero cost
                    ('CLOUD_SERVICES', 'DEF456-US-WEST-2', 82, 0),
                    ('DATA_TRANSFER', 'GHI789-EU-CENTRAL-1', 28, 280)
                ]
                
                data = []
                for category, account, units, cost in categories:
                    data.append({
                        'CONTRACT_NUMBER': 'SF-12345-2024',
                        'USAGE_MONTH': pd.Timestamp(current_month),
                        'ACCOUNT_NAME': account,
                        'USAGE_CATEGORY': category,
                        'UNITS_CONSUMED': units,
                        'TOTAL_USAGE': cost
                    })
                
                df_usage_type = pd.DataFrame(data)
                st.info("📊 **Demo Mode**: Showing sample usage breakdown by Snowflake service category.")
            else:
                # Query for usage by type
                query_usage_by_type = f"""
                SELECT 
                    contract_number,
                    DATE_TRUNC('month', usage_date) AS usage_month,
                    CONCAT(account_locator, '-', region) AS account_name,
                    usage_type AS usage_category,
                    SUM(usage) AS units_consumed,
                    SUM(usage_in_currency) AS total_usage
                FROM snowflake.organization_usage.usage_in_currency_daily
                WHERE TRUE
                    AND usage_date >= DATEADD(month, -1, CURRENT_DATE())
                    AND LOWER(balance_source) != 'overage'
                GROUP BY 1, 2, 3, 4
                ORDER BY 6 DESC
                LIMIT 50
                """
                
                df_usage_type = session.sql(query_usage_by_type).to_pandas()
            
            if not df_usage_type.empty:
                # Chart: Top usage categories
                df_category_summary = df_usage_type.groupby('USAGE_CATEGORY')['TOTAL_USAGE'].sum().reset_index().sort_values('TOTAL_USAGE', ascending=False).head(10)
                fig_categories = px.bar(
                    df_category_summary,
                    x='USAGE_CATEGORY',
                    y='TOTAL_USAGE',
                    title='Top 10 Usage Categories (Last Month)',
                    labels={'TOTAL_USAGE': 'Currency Spent', 'USAGE_CATEGORY': 'Category'},
                    color='TOTAL_USAGE',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_categories, use_container_width=True)
                
                # Detailed table
                st.dataframe(
                    df_usage_type,
                    column_config={
                        "CONTRACT_NUMBER": "Contract",
                        "USAGE_MONTH": "Month",
                        "ACCOUNT_NAME": "Account",
                        "USAGE_CATEGORY": "Category",
                        "UNITS_CONSUMED": st.column_config.NumberColumn("Units", format="%.2f"),
                        "TOTAL_USAGE": st.column_config.NumberColumn("Currency Spent", format="%.2f")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                st.info("💡 **Tip**: Use this breakdown to identify which Snowflake features are consuming the most from your contract. Focus optimization efforts on high-cost categories.")
            else:
                st.info("No usage category data available.")
                
        except Exception as e:
            st.warning(f"Unable to access usage category data: {str(e)}")
        
        st.markdown("---")
        st.info("""
        📚 **Documentation Reference**: 
        [Snowflake Billing Reconciliation Guide](https://docs.snowflake.com/en/user-guide/billing-reconcile)
        
        These queries help you reconcile your usage statement with Organization Usage data.
        """)
    
    st.markdown("---")
    
    # Query 1: Credit Usage by Service
    section_prefix = "2." if billing_model == "Reserved Capacity (Contract)" else "1."
    st.subheader(f"{section_prefix} Credit Consumption Overview")
    
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
    section_num = 3 if billing_model == "Reserved Capacity (Contract)" else 2
    st.subheader(f"{section_num}. Warehouse Cost Analysis")
    
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
    section_num = 4 if billing_model == "Reserved Capacity (Contract)" else 3
    st.subheader(f"{section_num}. Storage Cost Analysis")
    
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
    section_num = 5 if billing_model == "Reserved Capacity (Contract)" else 4
    st.subheader(f"{section_num}. Idle Warehouse Detection")
    
    try:
        # Get warehouse list using SHOW WAREHOUSES
        df_warehouses = session.sql("SHOW WAREHOUSES").to_pandas()
        
        # Rename columns for consistency - handle both quoted and unquoted column names
        column_mapping = {}
        for col in df_warehouses.columns:
            col_clean = str(col).lower().strip('"').strip()
            if col_clean == 'name':
                column_mapping[col] = 'WAREHOUSE_NAME'
            elif col_clean == 'size':
                column_mapping[col] = 'WAREHOUSE_SIZE'
            elif col_clean == 'state':
                column_mapping[col] = 'STATE'
        
        # If no mappings found, print debug info
        if not column_mapping:
            st.warning(f"Debug: Available columns: {list(df_warehouses.columns)}")
        
        df_warehouses.rename(columns=column_mapping, inplace=True)
        
        # Verify we have the required columns, if not try to find them with different approach
        if 'WAREHOUSE_NAME' not in df_warehouses.columns or 'WAREHOUSE_SIZE' not in df_warehouses.columns:
            # Try alternative column selection based on position (standard SHOW WAREHOUSES output)
            # Column 0 is usually 'name', Column 5 is usually 'size'
            try:
                if len(df_warehouses.columns) >= 6:
                    df_warehouses['WAREHOUSE_NAME'] = df_warehouses.iloc[:, 0]
                    df_warehouses['WAREHOUSE_SIZE'] = df_warehouses.iloc[:, 5]
                else:
                    st.error(f"Unable to parse warehouse information. Columns found: {list(df_warehouses.columns)}")
                    st.stop()
            except Exception as e:
                st.error(f"Unable to parse warehouse information: {str(e)}")
                st.stop()
        
        # Get warehouse usage from query history
        query_usage = f"""
        SELECT 
            warehouse_name,
            MAX(end_time) as last_used
        FROM snowflake.account_usage.query_history
        WHERE start_time >= DATEADD(day, -{days_back}, CURRENT_TIMESTAMP())
        GROUP BY warehouse_name
        """
        
        df_usage = session.sql(query_usage).to_pandas()
        
        # Merge warehouses with usage data
        df_idle_wh = df_warehouses[['WAREHOUSE_NAME', 'WAREHOUSE_SIZE']].merge(
            df_usage,
            left_on='WAREHOUSE_NAME',
            right_on='WAREHOUSE_NAME',
            how='left'
        )
        
        # Calculate days since last use
        current_time = pd.Timestamp.now(tz='UTC')
        df_idle_wh['DAYS_SINCE_LAST_USE'] = df_idle_wh['LAST_USED'].apply(
            lambda x: (current_time - pd.to_datetime(x, utc=True)).days if pd.notna(x) else None
        )
        
        # Sort by days since last use (nulls first)
        df_idle_wh = df_idle_wh.sort_values('DAYS_SINCE_LAST_USE', ascending=False, na_position='first')
        
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
    section_num = 6 if billing_model == "Reserved Capacity (Contract)" else 5
    st.subheader(f"{section_num}. Storage Optimization Opportunities")
    
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
    
    st.markdown("---")
    
    # Query 6: Tables Storage Usage with Time Travel
    section_num = 7 if billing_model == "Reserved Capacity (Contract)" else 6
    st.subheader(f"{section_num}. Tables Storage Usage with Time Travel")
    
    query_time_travel_storage = """
    SELECT 
        table_catalog as database_name,
        table_schema as schema_name,
        table_name,
        active_bytes / POWER(1024, 3) as active_storage_gb,
        time_travel_bytes / POWER(1024, 3) as time_travel_storage_gb,
        failsafe_bytes / POWER(1024, 3) as failsafe_storage_gb,
        (active_bytes + time_travel_bytes + failsafe_bytes) / POWER(1024, 3) as total_storage_gb,
        CASE 
            WHEN active_bytes > 0 THEN (time_travel_bytes / active_bytes) * 100
            ELSE 0
        END as time_travel_percentage,
        CASE 
            WHEN active_bytes > 0 THEN (failsafe_bytes / active_bytes) * 100
            ELSE 0
        END as failsafe_percentage,
        deleted
    FROM snowflake.account_usage.table_storage_metrics
    WHERE deleted IS NULL
        AND (active_bytes + time_travel_bytes + failsafe_bytes) > 0
    ORDER BY time_travel_storage_gb DESC
    LIMIT 100
    """
    
    try:
        df_time_travel = session.sql(query_time_travel_storage).to_pandas()
        
        if not df_time_travel.empty:
            # Summary metrics
            total_active = df_time_travel['ACTIVE_STORAGE_GB'].sum()
            total_time_travel = df_time_travel['TIME_TRAVEL_STORAGE_GB'].sum()
            total_failsafe = df_time_travel['FAILSAFE_STORAGE_GB'].sum()
            total_storage = df_time_travel['TOTAL_STORAGE_GB'].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Active Storage", f"{total_active:.2f} GB")
            with col2:
                st.metric("Time Travel Storage", f"{total_time_travel:.2f} GB")
            with col3:
                st.metric("Failsafe Storage", f"{total_failsafe:.2f} GB")
            with col4:
                time_travel_pct = (total_time_travel / total_active * 100) if total_active > 0 else 0
                st.metric("Time Travel Overhead", f"{time_travel_pct:.1f}%")
            
            # Visualization: Storage breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                # Top tables by time travel storage
                fig_tt = px.bar(
                    df_time_travel.head(15),
                    x='TABLE_NAME',
                    y='TIME_TRAVEL_STORAGE_GB',
                    title='Top 15 Tables by Time Travel Storage',
                    labels={'TIME_TRAVEL_STORAGE_GB': 'Time Travel Storage (GB)', 'TABLE_NAME': 'Table'},
                    color='TIME_TRAVEL_STORAGE_GB',
                    color_continuous_scale='Oranges'
                )
                fig_tt.update_xaxis(tickangle=-45)
                st.plotly_chart(fig_tt, use_container_width=True)
            
            with col2:
                # Storage composition pie chart
                storage_breakdown = pd.DataFrame({
                    'Type': ['Active', 'Time Travel', 'Failsafe'],
                    'Storage_GB': [total_active, total_time_travel, total_failsafe]
                })
                fig_pie = px.pie(
                    storage_breakdown,
                    values='Storage_GB',
                    names='Type',
                    title='Storage Composition',
                    color_discrete_sequence=['#29b5e8', '#ff7f0e', '#d62728']
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Tables with high time travel overhead
            high_tt_overhead = df_time_travel[df_time_travel['TIME_TRAVEL_PERCENTAGE'] > 100]
            
            if not high_tt_overhead.empty:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.warning(f"⚠️ **{len(high_tt_overhead)} table(s) with Time Travel storage >100% of active data**")
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("**Tables with High Time Travel Overhead:**")
                st.dataframe(
                    high_tt_overhead.head(20),
                    column_config={
                        "DATABASE_NAME": "Database",
                        "SCHEMA_NAME": "Schema",
                        "TABLE_NAME": "Table",
                        "ACTIVE_STORAGE_GB": st.column_config.NumberColumn("Active (GB)", format="%.2f"),
                        "TIME_TRAVEL_STORAGE_GB": st.column_config.NumberColumn("Time Travel (GB)", format="%.2f"),
                        "FAILSAFE_STORAGE_GB": st.column_config.NumberColumn("Failsafe (GB)", format="%.2f"),
                        "TOTAL_STORAGE_GB": st.column_config.NumberColumn("Total (GB)", format="%.2f"),
                        "TIME_TRAVEL_PERCENTAGE": st.column_config.NumberColumn("Time Travel %", format="%.1f"),
                        "FAILSAFE_PERCENTAGE": st.column_config.NumberColumn("Failsafe %", format="%.1f")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            
            st.info("""
            💡 **Time Travel & Failsafe Information**:
            - **Time Travel**: Allows querying historical data (default 1 day, configurable up to 90 days for Enterprise Edition)
            - **Failsafe**: 7-day period after Time Travel for disaster recovery (Snowflake-managed)
            - **Cost Impact**: Both Time Travel and Failsafe storage incur storage costs
            - **Optimization**: Consider reducing DATA_RETENTION_TIME_IN_DAYS for tables with high overhead
            - Use `ALTER TABLE <table_name> SET DATA_RETENTION_TIME_IN_DAYS = 1;` to reduce retention
            """)
        else:
            st.info("No time travel storage data available.")
            
    except Exception as e:
        st.error(f"Error fetching time travel storage data: {str(e)}")
    
    st.markdown("---")
    
    # Query 7: Use of Iceberg Tables (Gen2)
    section_num = 8 if billing_model == "Reserved Capacity (Contract)" else 7
    st.subheader(f"{section_num}. Iceberg Tables (Gen2) Usage")
    
    query_iceberg_tables = """
    SELECT 
        table_catalog as database_name,
        table_schema as schema_name,
        table_name,
        table_type,
        is_iceberg,
        created,
        last_altered,
        row_count,
        bytes / POWER(1024, 3) as storage_gb,
        comment
    FROM snowflake.account_usage.tables
    WHERE deleted IS NULL
        AND is_iceberg = 'YES'
    ORDER BY last_altered DESC
    """
    
    try:
        df_iceberg = session.sql(query_iceberg_tables).to_pandas()
        
        # Also get total table count for comparison
        query_total_tables = """
        SELECT 
            COUNT(*) as total_tables,
            SUM(CASE WHEN is_iceberg = 'YES' THEN 1 ELSE 0 END) as iceberg_tables,
            SUM(bytes) / POWER(1024, 3) as total_storage_gb,
            SUM(CASE WHEN is_iceberg = 'YES' THEN bytes ELSE 0 END) / POWER(1024, 3) as iceberg_storage_gb
        FROM snowflake.account_usage.tables
        WHERE deleted IS NULL
        """
        
        df_summary = session.sql(query_total_tables).to_pandas()
        
        if not df_summary.empty:
            total_tables = df_summary['TOTAL_TABLES'].iloc[0]
            iceberg_tables = df_summary['ICEBERG_TABLES'].iloc[0]
            total_storage = df_summary['TOTAL_STORAGE_GB'].iloc[0]
            iceberg_storage = df_summary['ICEBERG_STORAGE_GB'].iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Tables", f"{total_tables:,}")
            with col2:
                st.metric("Iceberg Tables", f"{iceberg_tables:,}")
            with col3:
                iceberg_pct = (iceberg_tables / total_tables * 100) if total_tables > 0 else 0
                st.metric("Iceberg Adoption", f"{iceberg_pct:.1f}%")
            with col4:
                st.metric("Iceberg Storage", f"{iceberg_storage:.2f} GB")
            
            if not df_iceberg.empty:
                # Iceberg tables by database
                iceberg_by_db = df_iceberg.groupby('DATABASE_NAME').agg({
                    'TABLE_NAME': 'count',
                    'STORAGE_GB': 'sum'
                }).reset_index()
                iceberg_by_db.columns = ['DATABASE_NAME', 'TABLE_COUNT', 'TOTAL_STORAGE_GB']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_db = px.bar(
                        iceberg_by_db,
                        x='DATABASE_NAME',
                        y='TABLE_COUNT',
                        title='Iceberg Tables by Database',
                        labels={'TABLE_COUNT': 'Number of Tables', 'DATABASE_NAME': 'Database'},
                        color='TABLE_COUNT',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig_db, use_container_width=True)
                
                with col2:
                    fig_storage = px.bar(
                        iceberg_by_db,
                        x='DATABASE_NAME',
                        y='TOTAL_STORAGE_GB',
                        title='Iceberg Storage by Database',
                        labels={'TOTAL_STORAGE_GB': 'Storage (GB)', 'DATABASE_NAME': 'Database'},
                        color='TOTAL_STORAGE_GB',
                        color_continuous_scale='Greens'
                    )
                    st.plotly_chart(fig_storage, use_container_width=True)
                
                # Detailed table list
                st.markdown("**Iceberg Tables Details:**")
                st.dataframe(
                    df_iceberg,
                    column_config={
                        "DATABASE_NAME": "Database",
                        "SCHEMA_NAME": "Schema",
                        "TABLE_NAME": "Table",
                        "TABLE_TYPE": "Type",
                        "IS_ICEBERG": "Iceberg",
                        "CREATED": st.column_config.DatetimeColumn("Created", format="YYYY-MM-DD HH:mm"),
                        "LAST_ALTERED": st.column_config.DatetimeColumn("Last Altered", format="YYYY-MM-DD HH:mm"),
                        "ROW_COUNT": st.column_config.NumberColumn("Rows", format="%d"),
                        "STORAGE_GB": st.column_config.NumberColumn("Storage (GB)", format="%.2f"),
                        "COMMENT": "Comment"
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                st.success(f"✅ Found {len(df_iceberg)} Iceberg table(s) in your account")
                
                st.info("""
                💡 **Iceberg Tables (Gen2) Benefits**:
                - **Better Performance**: Optimized for large-scale analytics with improved query performance
                - **Open Format**: Apache Iceberg is an open table format, enabling interoperability with other platforms
                - **ACID Transactions**: Full transactional support with schema evolution
                - **Time Travel**: Enhanced time travel capabilities with snapshot isolation
                - **Partitioning**: Automatic partition pruning and hidden partitioning
                - **Metadata Management**: Efficient metadata operations for large tables
                
                **When to Use Iceberg Tables**:
                - Large tables (>1TB) with frequent updates
                - Tables requiring complex partitioning strategies
                - Multi-cloud or hybrid cloud architectures
                - Need for interoperability with external compute engines (Spark, Flink, etc.)
                """)
            else:
                st.info("""
                ℹ️ **No Iceberg tables found in your account.**
                
                Consider using Iceberg tables for:
                - Large analytical tables (>1TB)
                - Tables with frequent updates and deletes
                - Cross-platform data sharing requirements
                
                To create an Iceberg table:
                ```sql
                CREATE ICEBERG TABLE my_table (
                    id INT,
                    name STRING,
                    created_date DATE
                )
                CATALOG = 'SNOWFLAKE'
                EXTERNAL_VOLUME = 'my_external_volume'
                BASE_LOCATION = 'my_iceberg_table';
                ```
                """)
        else:
            st.info("Unable to fetch table statistics.")
            
    except Exception as e:
        st.error(f"Error fetching Iceberg table data: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with ❄️ Streamlit in Snowflake | Based on Snowflake Well-Architected Framework</p>
    <p><a href="https://www.snowflake.com/en/developers/guides/well-architected-framework/">Learn more about Snowflake Well-Architected Framework</a></p>
</div>
""", unsafe_allow_html=True)


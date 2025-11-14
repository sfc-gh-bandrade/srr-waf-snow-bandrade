# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Streamlit Application                        │
│                        (app.py)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│  │ Performance│  │ Reliability│  │  Security  │  ...          │
│  │    Tab     │  │    Tab     │  │    Tab     │              │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘              │
│        │                │                │                      │
│        └────────────────┴────────────────┘                      │
│                         │                                       │
│                         ▼                                       │
│              ┌──────────────────────┐                          │
│              │  Query Executor      │                          │
│              │  (Snowpark Session)  │                          │
│              └──────────┬───────────┘                          │
└─────────────────────────┼───────────────────────────────────────┘
                          │
                          │ SQL Queries
                          ▼
        ┌─────────────────────────────────────┐
        │      Snowflake Account              │
        ├─────────────────────────────────────┤
        │                                     │
        │  ┌─────────────────────────────┐  │
        │  │  ACCOUNT_USAGE Schema       │  │
        │  ├─────────────────────────────┤  │
        │  │ • QUERY_HISTORY             │  │
        │  │ • WAREHOUSE_METERING        │  │
        │  │ • STORAGE_USAGE             │  │
        │  │ • DATABASES                 │  │
        │  │ • WAREHOUSES                │  │
        │  │ • USERS                     │  │
        │  │ • LOGIN_HISTORY             │  │
        │  │ • SESSIONS                  │  │
        │  │ • RESOURCE_MONITORS         │  │
        │  │ • PIPES                     │  │
        │  │ • TASKS                     │  │
        │  │ • POLICY_REFERENCES         │  │
        │  │ • ACCESS_HISTORY            │  │
        │  │ • TABLE_STORAGE_METRICS     │  │
        │  │ • ... and more              │  │
        │  └─────────────────────────────┘  │
        │                                     │
        └─────────────────────────────────────┘
```

## Component Architecture

### 1. User Interface Layer

```
┌──────────────────────────────────────────────────────────┐
│                    Streamlit UI                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐                                       │
│  │   Sidebar    │  • Date Range Selector (7-90 days)   │
│  │              │  • Configuration Options              │
│  │              │  • About Information                  │
│  └──────────────┘                                       │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │            Tab Navigation                        │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ 🚀 Performance | 🛡️ Reliability | ⚙️ Ops | ...   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Visualization Components                 │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ • Plotly Charts (Bar, Line, Pie, Scatter)       │  │
│  │ • Data Tables (with column config)              │  │
│  │ • Metric Cards (st.metric)                      │  │
│  │ • Alert Boxes (Success, Warning, Error)         │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 2. Data Processing Layer

```
┌──────────────────────────────────────────────────────────┐
│                Data Processing Pipeline                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  User Input (Date Range) ──┐                            │
│                             │                            │
│                             ▼                            │
│                    ┌─────────────────┐                  │
│                    │ Query Builder   │                  │
│                    │ • Dynamic dates │                  │
│                    │ • Parameterized │                  │
│                    └────────┬────────┘                  │
│                             │                            │
│                             ▼                            │
│                    ┌─────────────────┐                  │
│                    │ Snowpark SQL    │                  │
│                    │ Execution       │                  │
│                    └────────┬────────┘                  │
│                             │                            │
│                             ▼                            │
│                    ┌─────────────────┐                  │
│                    │ Pandas DataFrame│                  │
│                    │ Conversion      │                  │
│                    └────────┬────────┘                  │
│                             │                            │
│                             ▼                            │
│                    ┌─────────────────┐                  │
│                    │ Data Transform  │                  │
│                    │ & Aggregation   │                  │
│                    └────────┬────────┘                  │
│                             │                            │
│                             ▼                            │
│                    ┌─────────────────┐                  │
│                    │ Threshold Check │                  │
│                    │ & Alerting      │                  │
│                    └────────┬────────┘                  │
│                             │                            │
│                             ▼                            │
│                        Visualization                     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 3. Query Architecture by Pillar

#### Performance Pillar Queries

```
┌─────────────────────────────────────────────────┐
│         Performance Analysis Queries            │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. Warehouse Utilization                       │
│    └─> QUERY_HISTORY                           │
│        • Total queries per warehouse           │
│        • Avg execution time                    │
│        • Queue time percentage                 │
│                                                 │
│ 2. Query Performance                           │
│    └─> QUERY_HISTORY                           │
│        • Execution time trends                 │
│        • Partition scan efficiency             │
│        • Slow query detection                  │
│                                                 │
│ 3. Clustering Analysis                         │
│    └─> AUTOMATIC_CLUSTERING_HISTORY            │
│        • Clustering depth                      │
│        • Overlaps                              │
│                                                 │
│ 4. Cache Hit Rate                              │
│    └─> QUERY_HISTORY                           │
│        • Result cache utilization              │
│        • Cache hit trends                      │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### Reliability Pillar Queries

```
┌─────────────────────────────────────────────────┐
│         Reliability Analysis Queries            │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. Replication Status                          │
│    └─> DATABASES                               │
│        • Replication enabled/disabled          │
│        • Replication schedules                 │
│                                                 │
│ 2. Query Failures                              │
│    └─> QUERY_HISTORY                           │
│        • Failed query counts                   │
│        • Error messages                        │
│        • Failure trends                        │
│                                                 │
│ 3. Pipeline Reliability                        │
│    └─> PIPES                                   │
│        • Error counts                          │
│        • Last error messages                   │
│                                                 │
│ 4. Task Reliability                            │
│    └─> TASKS                                   │
│        • Error integration status              │
│        • Task states                           │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### Operational Excellence Queries

```
┌─────────────────────────────────────────────────┐
│    Operational Excellence Analysis Queries      │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. Resource Monitors                           │
│    └─> RESOURCE_MONITORS                       │
│        • Monitor configurations                │
│        • Credit quotas                         │
│        • Alert thresholds                      │
│                                                 │
│ 2. Warehouse Config                            │
│    └─> WAREHOUSES                              │
│        • Auto-suspend settings                 │
│        • Auto-resume settings                  │
│        • Multi-cluster config                  │
│                                                 │
│ 3. Long-Running Queries                        │
│    └─> QUERY_HISTORY                           │
│        • Queries > 5 minutes                   │
│        • Execution time distribution           │
│                                                 │
│ 4. Query Patterns                              │
│    └─> QUERY_HISTORY                           │
│        • User activity                         │
│        • Query types                           │
│        • Warehouse usage                       │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### Security & Governance Queries

```
┌─────────────────────────────────────────────────┐
│    Security & Governance Analysis Queries       │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. MFA Adoption                                │
│    └─> USERS                                   │
│        • MFA enabled users                     │
│        • Adoption rate                         │
│                                                 │
│ 2. Network Policies                            │
│    └─> NETWORK_POLICIES                        │
│        • Policy configurations                 │
│        • Allowed/blocked IPs                   │
│                                                 │
│ 3. Privileged Access                           │
│    └─> SESSIONS                                │
│        • ACCOUNTADMIN usage                    │
│        • SECURITYADMIN usage                   │
│        • Session counts                        │
│                                                 │
│ 4. Data Masking                                │
│    └─> POLICY_REFERENCES                       │
│        • Masking policies                      │
│        • Row access policies                   │
│                                                 │
│ 5. Failed Logins                               │
│    └─> LOGIN_HISTORY                           │
│        • Failed attempts                       │
│        • Error patterns                        │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### Cost Optimization Queries

```
┌─────────────────────────────────────────────────┐
│      Cost Optimization Analysis Queries         │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. Credit Usage                                │
│    └─> METERING_DAILY_HISTORY                  │
│        • Service type breakdown                │
│        • Daily trends                          │
│                                                 │
│ 2. Warehouse Costs                             │
│    └─> WAREHOUSE_METERING_HISTORY              │
│        • Compute credits                       │
│        • Cloud services credits                │
│        • Cost by warehouse                     │
│                                                 │
│ 3. Storage Costs                               │
│    └─> STORAGE_USAGE                           │
│        • Database storage                      │
│        • Stage storage                         │
│        • Failsafe storage                      │
│        • Growth trends                         │
│                                                 │
│ 4. Idle Warehouses                             │
│    └─> WAREHOUSES + QUERY_HISTORY              │
│        • Last usage timestamp                  │
│        • Idle duration                         │
│                                                 │
│ 5. Storage Optimization                        │
│    └─> TABLE_STORAGE_METRICS + ACCESS_HISTORY  │
│        • Large unused tables                   │
│        • Storage breakdown                     │
│        • Access frequency                      │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Data Flow

```
┌──────────┐     ┌───────────┐     ┌──────────┐     ┌──────────┐
│          │     │           │     │          │     │          │
│  User    │────▶│ Streamlit │────▶│ Snowpark │────▶│ Snowflake│
│  Browser │     │    UI     │     │  Session │     │ Account  │
│          │     │           │     │          │     │          │
└──────────┘     └───────────┘     └──────────┘     └──────────┘
     ▲                                                    │
     │                                                    │
     │           ┌───────────┐     ┌──────────┐         │
     │           │           │     │          │         │
     └───────────│  Plotly   │◀────│  Pandas  │◀────────┘
                 │  Charts   │     │DataFrame │
                 │           │     │          │
                 └───────────┘     └──────────┘
```

### Detailed Flow

1. **User Interaction**
   - User selects date range via sidebar
   - User navigates to a specific pillar tab

2. **Query Generation**
   - Application generates SQL query with date parameters
   - Query targets specific ACCOUNT_USAGE views

3. **Query Execution**
   - Snowpark session executes SQL
   - Results returned to Snowpark

4. **Data Transformation**
   - Snowpark converts to Pandas DataFrame
   - Data aggregation and calculations performed
   - Thresholds checked for alerting

5. **Visualization**
   - Plotly creates interactive charts
   - Streamlit renders tables
   - Alert boxes displayed based on thresholds

6. **User Feedback**
   - Visual charts displayed
   - Recommendations shown
   - Data tables available for export

## Deployment Architectures

### Architecture 1: Snowflake Streamlit (Recommended)

```
┌─────────────────────────────────────────────────────┐
│              Snowflake Account                      │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │      Streamlit in Snowflake                │   │
│  │                                            │   │
│  │  • Native integration                      │   │
│  │  • No external hosting                     │   │
│  │  • Built-in authentication                 │   │
│  │  • Direct ACCOUNT_USAGE access             │   │
│  │                                            │   │
│  └────────────────┬───────────────────────────┘   │
│                   │                                │
│                   ▼                                │
│  ┌────────────────────────────────────────────┐   │
│  │       Compute Warehouse                    │   │
│  │       (streamlit_wh - XSMALL)              │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
         ▲
         │ HTTPS
         │
    ┌────┴────┐
    │  Users  │
    │ Browser │
    └─────────┘
```

**Pros**:
- No infrastructure management
- Native Snowflake authentication
- Direct access to ACCOUNT_USAGE
- Secure by default
- No external dependencies

**Cons**:
- Requires Streamlit feature (may need upgrade)
- Limited customization of hosting

### Architecture 2: Local Development

```
┌──────────────────────┐         ┌─────────────────────┐
│   Developer Machine  │         │  Snowflake Account  │
│                      │         │                     │
│  ┌────────────────┐ │         │  ┌──────────────┐  │
│  │   Streamlit    │ │ HTTPS   │  │  ACCOUNT     │  │
│  │   App (Local)  │─┼─────────┼─▶│  USAGE       │  │
│  │                │ │ Auth    │  │              │  │
│  └────────────────┘ │         │  └──────────────┘  │
│         ▲            │         │                     │
│         │            │         └─────────────────────┘
│    ┌────┴────┐      │
│    │localhost│      │
│    │  :8501  │      │
│    └─────────┘      │
│                      │
└──────────────────────┘
```

**Pros**:
- Fast development iteration
- Full control over environment
- Easier debugging

**Cons**:
- Requires local setup
- Credential management needed
- Not suitable for production

## Security Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Security Layers                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. Authentication                                  │
│     ├─> Snowflake user authentication              │
│     ├─> MFA enforcement                            │
│     └─> SSO integration                            │
│                                                     │
│  2. Authorization                                   │
│     ├─> Role-based access (RBAC)                   │
│     ├─> ACCOUNT_USAGE privileges                   │
│     └─> Warehouse usage grants                     │
│                                                     │
│  3. Network Security                                │
│     ├─> Network policies                           │
│     ├─> IP whitelisting                            │
│     └─> Private Link (optional)                    │
│                                                     │
│  4. Data Access                                     │
│     ├─> Read-only queries                          │
│     ├─> No data modification                       │
│     └─> ACCOUNT_USAGE views only                   │
│                                                     │
│  5. Application Security                            │
│     ├─> No credential storage                      │
│     ├─> Session-based auth                         │
│     └─> Input sanitization (Snowpark)              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Performance Considerations

### Caching Strategy

```
┌─────────────────────────────────────────────┐
│           Caching Layers                    │
├─────────────────────────────────────────────┤
│                                             │
│  1. Streamlit Session Cache                │
│     └─> @st.cache_resource                 │
│         • Snowflake connection             │
│         • Persists across reruns           │
│                                             │
│  2. Snowflake Query Result Cache           │
│     └─> 24-hour automatic caching          │
│         • Identical queries reuse results  │
│         • No compute cost                  │
│                                             │
│  3. ACCOUNT_USAGE View Latency             │
│     └─> 45 min - 3 hours delay             │
│         • Inherent in system design        │
│         • Data consistency guaranteed      │
│                                             │
└─────────────────────────────────────────────┘
```

### Query Optimization

- Use date filters to limit data scanned
- Aggregate before returning to Streamlit
- Limit result sets (TOP N queries)
- Use appropriate indexes on ACCOUNT_USAGE views (automatic)

## Scalability

The application scales naturally with Snowflake:

- **Warehouse Sizing**: Adjust query warehouse based on data volume
- **Concurrent Users**: Snowflake handles multiple simultaneous connections
- **Data Growth**: ACCOUNT_USAGE views handle any account size
- **Query Performance**: Elastic compute scales with workload

## Monitoring & Observability

```
┌─────────────────────────────────────────────┐
│        Application Monitoring               │
├─────────────────────────────────────────────┤
│                                             │
│  1. Query Performance                      │
│     └─> QUERY_HISTORY tracks app queries  │
│                                             │
│  2. Warehouse Usage                        │
│     └─> Monitor streamlit_wh credits      │
│                                             │
│  3. Error Tracking                         │
│     └─> Streamlit error logs              │
│                                             │
│  4. User Access                            │
│     └─> SESSION_HISTORY                   │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Frontend** | Streamlit | ≥1.28.0 |
| **Visualization** | Plotly | ≥5.17.0 |
| **Data Processing** | Pandas | ≥2.0.0 |
| **Database Connector** | Snowflake Snowpark | ≥1.11.1 |
| **Database** | Snowflake | Any edition |
| **Language** | Python | ≥3.8 |

---

## Design Principles

1. **Simplicity**: Single-file application for easy deployment
2. **Security**: Read-only queries, no data modification
3. **Performance**: Efficient queries with date filtering
4. **Usability**: Clear visualizations and actionable recommendations
5. **Maintainability**: Well-documented code and modular structure
6. **Scalability**: Leverages Snowflake's elastic compute
7. **Reliability**: Error handling for graceful degradation

---

**Last Updated**: November 12, 2025


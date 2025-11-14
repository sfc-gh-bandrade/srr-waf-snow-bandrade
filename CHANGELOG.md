# Changelog

All notable changes to the Snowflake Well-Architected Framework Review application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-12

### Added

#### Core Application
- Initial release of Snowflake Well-Architected Framework Review Streamlit application
- Multi-tab interface covering all 5 pillars of the Well-Architected Framework
- Custom CSS styling with color-coded alert cards
- Configurable analysis period (7-90 days)
- Interactive visualizations using Plotly

#### Performance Pillar
- Warehouse utilization and efficiency analysis
- Query performance trends and metrics
- Table clustering health monitoring
- Result cache hit rate tracking
- Automated recommendations for queue times and partitioning

#### Reliability Pillar
- Database replication status monitoring
- Query failure and error analysis with trend visualization
- Snowpipe reliability tracking
- Task error notification configuration review
- Failure pattern detection

#### Operational Excellence Pillar
- Resource monitor configuration review
- Warehouse auto-suspend/auto-resume analysis
- Long-running query detection (>5 minutes)
- Query execution pattern analysis by user
- Warehouse configuration best practices validation

#### Security & Governance Pillar
- Multi-factor authentication (MFA) adoption tracking
- Network policy configuration review
- Privileged role usage monitoring (ACCOUNTADMIN, SECURITYADMIN, SYSADMIN)
- Data masking and row access policy coverage
- Failed login attempt tracking and analysis

#### Cost Optimization Pillar
- Credit consumption overview by service type
- Warehouse cost analysis and breakdown
- Storage cost trends (database, stage, failsafe)
- Idle warehouse detection (>7 days unused)
- Storage optimization opportunities (unused large tables)

#### Documentation
- Comprehensive README with installation and usage instructions
- Quick Start Guide for rapid deployment
- Detailed metrics reference documentation
- SQL deployment script with role-based access
- Git ignore file for security
- Secrets template for local development
- Requirements file with pinned dependencies

### Features

- **Real-time Analysis**: Queries live data from ACCOUNT_USAGE views
- **Visual Dashboard**: Interactive charts, graphs, and tables
- **Actionable Alerts**: Color-coded warnings (success, warning, critical)
- **Flexible Time Range**: Analyze 7-90 days of historical data
- **Export Ready**: Tables can be copied for reporting
- **Mobile Responsive**: Works on various screen sizes
- **Zero Setup** (Snowflake): Deploy directly in Snowflake Streamlit
- **Local Development**: Support for local testing with secrets management

### Best Practices Alignment

All metrics and recommendations aligned with official Snowflake documentation:
- [Performance Framework](https://www.snowflake.com/en/developers/guides/well-architected-framework-performance/)
- [Reliability Framework](https://www.snowflake.com/en/developers/guides/well-architected-framework-reliability/)
- [Operational Excellence Framework](https://www.snowflake.com/en/developers/guides/well-architected-framework-operational-excellence/)
- [Security & Governance Framework](https://www.snowflake.com/en/developers/guides/well-architected-framework-security-and-governance/)
- [Cost Optimization Framework](https://www.snowflake.com/en/developers/guides/well-architected-framework-cost-optimization-and-finops/)

### Technical Details

- **Language**: Python 3.8+
- **Framework**: Streamlit
- **Database**: Snowflake
- **Visualization**: Plotly Express
- **Data Processing**: Pandas
- **Snowflake SDK**: snowflake-snowpark-python

### Known Limitations

- ACCOUNT_USAGE views have 45 minutes to 3 hours latency
- Some queries may timeout on very large accounts (>1 million daily queries)
- Requires IMPORTED PRIVILEGES on SNOWFLAKE database
- Network policies may not be available in all Snowflake editions
- Some features require specific Snowflake edition (Enterprise, Business Critical)

---

## [Unreleased]

### Planned Features for Future Releases

- Export to PDF report functionality
- Email/Slack integration for alerts
- Historical trend comparison (compare current vs. previous period)
- Custom threshold configuration
- Support for INFORMATION_SCHEMA views for real-time data
- Multi-account comparison (for organizations with multiple accounts)
- Integration with Snowflake Horizon for governance
- Automated remediation suggestions with SQL scripts
- Cost forecasting based on usage trends
- Performance baselines and anomaly detection

---

## Version History

| Version | Release Date | Key Features |
|---------|--------------|--------------|
| 1.0.0 | 2025-11-12 | Initial release with all 5 pillars |

---

## Upgrade Guide

### From Development to Production

1. **Review Permissions**: Ensure the production role has access to ACCOUNT_USAGE
2. **Configure Resource Monitors**: Set up warehouse resource monitors
3. **Test Data Access**: Verify all queries return data in production environment
4. **Set Up Alerts**: Configure external monitoring for the Streamlit app availability
5. **Document Findings**: Create a baseline report for comparison

### Future Upgrades

When upgrading to newer versions:
1. Backup your current `app.py` file
2. Review the CHANGELOG for breaking changes
3. Test in development environment first
4. Update `requirements.txt` if dependencies changed
5. Redeploy to production

---

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Update documentation
5. Submit a pull request

---

## Support

For issues, questions, or feature requests:
- Open an issue in the repository
- Contact your Snowflake Solution Engineer
- Refer to [Snowflake Documentation](https://docs.snowflake.com/)

---

## License

This project is licensed under the MIT License.

---

**Maintained by**: Snowflake Solution Engineering Team
**Last Updated**: November 12, 2025


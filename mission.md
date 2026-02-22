# SanctionDefenderV2 Mission

**Objective:** Maintain, improve, and extend the SanctionDefenderV2 system for robust sanction screening and analysis.

## Description
SanctionDefenderV2 is a comprehensive system designed to:
1.  **Import & Process**: Ingest sanction data from various sources (Excel, XML, API) including OFAC, EU, UK, and UN lists.
2.  **Analyze**: Perform advanced matching and screening against entities to identify potential sanctions risks.
3.  **Manage Data**: Store and manage sanction data efficiently using PostgreSQL (Neon) and local databases.
4.  **API Integration**: Provide API endpoints for real-time screening and checks.
5.  **Reporting**: Generate detailed reports and logs of screening activities.

## Core Responsibilities
-   Ensure data import pipelines are reliable and handle schema updates gracefully.
-   Optimize search and matching algorithms for accuracy and performance.
-   Maintain API endpoints and ensure high availability.
-   Monitor system health and audit logs.

## Success Criteria
-   All import scripts run without errors.
-   Matching logic correctly identifies sanctioned entities with minimal false positives.
-   API response times are within acceptable limits.
-   Documentation is kept up-to-date with code changes.

## Current Focus
-   Integration of Agentic workflows (Antigravity template).
-   Ongoing maintenance and bug fixes.

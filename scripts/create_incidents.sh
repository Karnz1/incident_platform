#!/bin/bash

#!/bin/bash

# A single unified list containing all incidents: Title | Description
INCIDENTS=(
    # --- CRITICAL ---
    "Database Cluster Crash|The primary database cluster went down at midnight."
    "Core Infrastructure Failure|We received an alert that the entire system down."
    "Gateway Disconnection|The main API service down signal was triggered."
    "Web UI Inaccessible|The front-end portal is completely not working."
    "DNS Resolution Failure|The server IP address is currently unavailable."
    "Data Center Incident|A power loss caused a major site outage."
    "Cloud Provider Drop|The team is responding to a massive production outage."
    "IAM Lockout|Administrators cannot access the management console."
    "Storage Volume Corruption|The hard drive crash caused irreversible data loss."
    "Unauthorized Infrastructure Access|Firewall logs confirm a malicious security breach."
    "Stripe Integration Failure|The checkout gateway reports a total payment failure."
    "Global Access Disruption|This disruption is actively blocking all users."
    "Total Authentication Block|The login form is broken so no one can authenticate."

    # --- HIGH ---
    "Query Performance Drops|The search index response time is extremely slow."
    "Dashboard Lag|Loading metrics on the main screen is very slow today."
    "Network Latency Issues|The overall asset pipeline has heavily degraded."
    "Single Request Drops|The third-party webhook threw an unexpected timeout."
    "Batch Processing Delays|The backend logs show repeated connection timeouts."
    "Build Pipeline Interruption|The latest deployment to production failed completely."
    "Kafka Stream Dropping|The real-time analytics sync is actively failing."
    "VPC Configuration Flaw|Engineers are investigating a major issue with routing."
    "High-Volume Support Spikes|Customer support is getting tickets from many users."
    "Flaky Internal Tools|The internal monitoring tool connectivity is intermittent."
    "Enterprise Account SLA Threat|This bug is affecting a critical customer account."
    "Git Repository Lockout|The engineering deployment pipeline is totally blocked."

    # --- MEDIUM ---
    "API Syntax Exception|The logging service caught a runtime unhandled error."
    "UI Rendering Flaw|The layout engine contains a CSS rendering bug."
    "Reporting Discrepancy|Finance flagged a minor accounting calculation issue."
    "Database Lock Warning|The deadlocks indicate a performance problem."
    "Metadata Mismatch|The exported CSV file contains incorrect timestamp values."
    "Bad Label String|The pricing page displays the wrong tax rate."
    "Wizard Form Stoppage|Applicants cannot complete the multi-step form."
    "Worker Queue Dropping|The email service suffered a partial failure."
    "Localized Latency Spikes|The regional delay is only impacting some users."

    # --- LOW ---
    "Community Forum Inquiry|A community member submitted a syntax question."
    "Access Provisioning Request|An intern filed a standard sandbox access request."
    "Documentation Shortcoming|We need a clear guide on how to rotate secrets."
    "Non-Breaking Warning|The console log shows a minor deprecation notice."
    "Dark Mode Alignment|The settings panel has a slight cosmetic misalignment."
    "Documentation Review|The readme file has a small spelling typo."
    "Log Retention Tweak|Moving logs to cold storage is a great improvement."
    "CLI Tool Suggestion|The analytics team opened a new feature request."
)


for incident in "${INCIDENTS[@]}"; do
    title="${incident%%|*}"
    description="${incident##*|}"

    curl -X POST localhost:8000/incidents -H "Content-Type: application/json" -d "{\"title\": \"$title\", \"description\": \"$description\"}" || echo "Error creating incident"
done 


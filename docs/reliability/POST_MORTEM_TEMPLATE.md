# Incident Post-Mortem: [Incident Title]

**Date:** YYYY-MM-DD  
**Status:** [Draft/Final]  
**Incident ID:** [e.g., INC-123]  
**Authors:** [SRE-1, etc.]

## Summary
A brief (2-3 sentence) overview of what happened, the impact on users, and how long it lasted.

## Impact
- **Duration:** [Start Time] to [End Time] ([Total Duration])
- **Services Affected:** [e.g., Task Execution API, Web Frontend]
- **User Experience:** [e.g., 5% of users experienced 500 errors when retrying tasks]

## Timeline (all times in UTC)
- **HH:MM** - Incident start.
- **HH:MM** - Monitoring alert [Alert Name] triggered.
- **HH:MM** - On-call engineer acknowledged incident.
- **HH:MM** - Root cause identified as [Cause].
- **HH:MM** - Remediation [Action] applied.
- **HH:MM** - Incident resolved; monitoring confirmed recovery.

## Root Cause Analysis (RCA)
Detailed explanation of why the incident occurred. Use the "5 Whys" method if applicable.

## Resolution and Recovery
Description of the immediate actions taken to resolve the incident and any steps taken to restore full service.

## Lessons Learned
- What went well? (e.g., Monitoring detected it in 1 minute).
- What went poorly? (e.g., Lack of documentation for [Component] delayed recovery).
- Where did we get lucky?

## Corrective Actions / Next Steps
| Action Item | Owner | Status | Due Date |
| :--- | :--- | :--- | :--- |
| [e.g., Add circuit breaker to DB connection] | SWE-1 | To Do | YYYY-MM-DD |
| [e.g., Update dashboard with queue depth alert] | SRE-1 | Done | YYYY-MM-DD |

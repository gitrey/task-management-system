# Team Protocols

This document outlines the standardized protocols for collaboration, synchronization, and coordination within the development team to ensure efficient progress and minimize friction.

## 1. Git Sync Protocols

* **Pull/Fetch Before Starting Work**: Every agent must execute a 'git pull' or 'git fetch' followed by a rebase/merge before reading files or starting a new implementation task.
* **Sync Before Committing**: Perform a final sync immediately before committing or pushing changes to identify any potential conflicts introduced during the development window.
* **Frequent Small Commits**: Prefer small, focused commits over large, monolithic changes to facilitate easier integration and conflict resolution.
* **Non-Interactive Git Configuration**: All agents must ensure their git environment is configured for non-interactive operation (e.g., `git config --global core.editor cat`, `git config --global pull.rebase false`) to prevent terminal prompts from stalling automated workflows.

## 2. Explicit Hand-off Verification

* **Spec Access Verification**: Upon PM approval of a specification, the TPM must explicitly verify that all assigned agents have access to the relevant spec documents.
* **Confirmation of Readiness**: Agents should confirm they have read and understood the requirements before transitioning their JIRA tickets to 'In Progress'.
* **Environment and Permissions Check**: Before starting a milestone, agents must verify they have necessary Hub permissions and API access (e.g., Gemini LLM access) to avoid runtime failures.

## 3. Communication of Technical Blockers

* **Immediate Reporting**: TPM and individual agents must proactively report any technical blockers, environment issues, or requirement ambiguities as soon as they are identified.
* **Blocker Status in JIRA**: Use the 'Blocked' status or add a 'blocker' label/comment to JIRA issues to provide visibility.
* **Escalation**: If a blocker cannot be resolved within a reasonable timeframe, escalate to the TPM or PO for coordination.

## 4. Backlog and JIRA Synchronization

* **Immediate Assignment Updates**: The TPM must update 'docs/BACKLOG.md' with sub-agent assignments immediately upon task creation or assignment.
* **Increased Sync Frequency**: The Product Owner (PO) and TPM will increase the frequency of JIRA status synchronizations to ensure that the task board reflects the real-time state of the project.
* **Backlog Granularity**: Ensure the backlog is broken down into granular sub-tasks to better track progress and identify bottlenecks.

# F-0003: Team Process Retrospective & Agent Protocol Improvements

- **Type:** Enhancement
- **Priority:** P2
- **Status:** Approved

## Problem
During the execution of Milestones 1 and 2, several minor friction points were identified in agent coordination:
1. **Sync Delays:** The TPM and PO occasionally missed newly created spec files due to branch divergence or sync delays, requiring the PM to send content via messages.
2. **Git Conflicts:** Frequent updates to `docs/BACKLOG.md` led to merge conflicts that required manual resolution.
3. **Sub-task Visibility:** While the TPM successfully assigned tasks to SWE agents, the granular progress of these sub-tasks was not always immediately visible in the central backlog until completion.

## Requirements
1. **Standardize Sync Protocol:** All agents must execute a `git pull` or `git fetch` before attempting to read shared files or make new commits.
2. **Explicit Hand-off Verification:** When a PM approves a spec, the TPM must explicitly verify they can access the file on their current branch or request the specific branch name from the PM.
3. **Backlog Granularity:** TPM should update `docs/BACKLOG.md` with specific sub-agent assignments (e.g., [Assigned: SWE-1]) as soon as tasks are broken down, rather than just at completion.
4. **Agent Role Refinement:** 
    - **PO:** Increase frequency of JIRA status syncs.
    - **TPM:** Proactively report technical blockers (like git credential issues) to the PM/PO if they persist for more than one turn.

## Acceptance Criteria
- [ ] Protocol document created and shared with all agents.
- [ ] TPM updates the backlog structure to include sub-task assignments for the next milestone.
- [ ] No merge conflicts in `docs/BACKLOG.md` for at least one full feature cycle.

## JIRA Issue
- [TBD]

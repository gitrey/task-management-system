# F-0007: AI-Assisted DAG Generation (GENDEV-97)

- **Type:** Feature
- **Priority:** P2
- **Status:** Approved

## Problem
Building complex DAGs manually via the form can be time-consuming and error-prone for users who aren't familiar with the underlying task logic.

## Requirements
1. Implement a natural language interface on the dashboard to describe task workflows.
2. Integrate with an LLM (e.g., Gemini) to parse descriptions and generate a proposed DAG structure.
3. Users must be able to preview and approve the generated DAG before it is added to the system.
4. Support for common workflow patterns (sequential, fan-out/fan-in).

## Acceptance Criteria
- [ ] Users can enter natural language text into a "Generate Workflow" field.
- [ ] The system displays a visual preview of the proposed DAG.
- [ ] Clicking "Apply" successfully creates the tasks and dependencies in the backend.
- [ ] Error handling for ambiguous or impossible workflow requests.

## Out of Scope
- Direct code generation from natural language (limited to task metadata and dependencies).
- Real-time editing of the AI-proposed graph before application.

## Dependencies
- LLM API Access (e.g., Google Vertex AI/Gemini)
- F-0004 (DAG Visualizer) for previewing.

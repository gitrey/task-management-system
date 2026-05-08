# F-0004: Interactive DAG Graph Visualizer (GENDEV-94)

- **Type:** Feature
- **Priority:** P1
- **Status:** Approved

## Problem
There is no visual way to understand the dependencies between tasks or their current execution state.

## Requirements
1. Implement a lightweight visual graph representing the DAG of tasks and their dependencies.
2. Use a library like Vis.js, Cytoscape.js, or SVG-based custom rendering.
3. Color-code task nodes in real-time based on `TaskStatus`:
    - **Green:** Completed
    - **Vibrant Blue:** Running
    - **Vivid Amber:** Retrying (with retry count badge)
    - **Curated Red:** Failed (click to view error stack)
    - **Muted Gray:** Pending / Cancelled

## Acceptance Criteria
- [ ] DAG graph renders correctly in the browser.
- [ ] Nodes are connected by arrows indicating dependencies.
- [ ] Node colors update automatically when task status changes in the backend.
- [ ] Hovering or clicking a node shows basic task details.

## Out of Scope
- Manual editing of graph (drag and drop to change dependencies).
- Zoom/Pan if the graph is small (below 10 nodes).

## Dependencies
- Frontend graph library (e.g., Cytoscape.js)
- WebSocket or polling mechanism for real-time updates.

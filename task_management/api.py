import datetime
from typing import Any, Dict, List

from .manager import TaskManager


def export_task_hierarchy(manager: TaskManager) -> Dict[str, Any]:
    """Exports the task graph as a visual-ready hierarchy."""
    with manager.lock:
        sanitized_tasks = {}
        for task_id, task in manager.tasks.items():
            sanitized_tasks[task_id] = {
                "task_id": task.task_id,
                "status": task.status.value,
                "progress_pct": task.progress_pct,
                "dependencies": list(task.dependencies),
                "priority": task.priority,
                "children": []
            }
            
        roots = []
        for task_id, task in manager.tasks.items():
            if task.parent_id:
                if task.parent_id in sanitized_tasks:
                    sanitized_tasks[task.parent_id]["children"].append(sanitized_tasks[task_id])
            else:
                roots.append(sanitized_tasks[task_id])
                
        def sort_hierarchy(task_nodes: List[Dict[str, Any]]):
            task_nodes.sort(key=lambda t: (t["priority"], t["task_id"]))
            for node in task_nodes:
                sort_hierarchy(node["children"])
                
        sort_hierarchy(roots)
        
        return {
            "status": "success",
            "data": {
                "hierarchy": roots
            },
            "metadata": {
                "total_tasks": len(manager.tasks),
                "exported_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
        }

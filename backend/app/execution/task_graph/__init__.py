from typing import List, Dict, Any, Set, Optional

class TaskNode:
    """Represents a single node within the Execution DAG."""
    def __init__(self, step_id: str, name: str, action_type: str, agent_target: str, params: Dict[str, Any], depends_on: Optional[List[str]] = None, max_retries: int = 2):
        self.step_id = step_id
        self.name = name
        self.action_type = action_type # e.g. "write_file", "search_rag", "run_command"
        self.agent_target = agent_target # e.g. "coding", "research", "ceo"
        self.params = params
        self.depends_on = depends_on or [] # List of step_ids this node depends on
        self.status = "pending" # pending, running, completed, failed, suspended, skipped
        self.result = None
        self.retry_count = 0
        self.max_retries = max_retries
        self.conditional_branch: Optional[Dict[str, Any]] = None # {"condition": "lambda/expr", "then_steps": [...]}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "name": self.name,
            "action_type": self.action_type,
            "agent_target": self.agent_target,
            "params": self.params,
            "depends_on": self.depends_on,
            "status": self.status,
            "result": self.result,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "conditional_branch": self.conditional_branch
        }

class TaskGraph:
    """Directed Acyclic Graph (DAG) state manager for user intent execution tracks."""
    def __init__(self):
        self.nodes: Dict[str, TaskNode] = {}

    def add_node(self, node: TaskNode) -> None:
        self.nodes[node.step_id] = node

    def add_step(self, step_id: str, name: str, action_type: str, agent_target: str, params: Dict[str, Any], depends_on: Optional[List[str]] = None, max_retries: int = 2) -> TaskNode:
        node = TaskNode(step_id, name, action_type, agent_target, params, depends_on, max_retries)
        self.add_node(node)
        return node

    def get_node(self, step_id: str) -> Optional[TaskNode]:
        return self.nodes.get(step_id)

    def validate_dag(self) -> bool:
        """Performs Depth-First Search topology validation to verify there are no dependency cycles."""
        visited: Dict[str, int] = {} # 0=unvisited, 1=visiting, 2=fully_visited
        for node_id in self.nodes:
            visited[node_id] = 0

        def dfs(node_id: str) -> bool:
            if visited.get(node_id) == 1:
                return False # Cycle detected!
            if visited.get(node_id) == 2:
                return True

            visited[node_id] = 1
            node = self.nodes.get(node_id)
            if node:
                for dep in node.depends_on:
                    if dep in self.nodes: # ignore external dependencies missing in plan
                        if not dfs(dep):
                            return False
            visited[node_id] = 2
            return True

        for node_id in self.nodes:
            if visited[node_id] == 0:
                if not dfs(node_id):
                    return False
        return True

    def get_ready_steps(self) -> List[TaskNode]:
        """Gathers list of steps whose dependencies are fully completed and is in 'pending' status."""
        ready = []
        for node in self.nodes.values():
            if node.status == "pending":
                dependencies_satisfied = True
                for dep_id in node.depends_on:
                    dep_node = self.nodes.get(dep_id)
                    if dep_node and dep_node.status != "completed":
                        dependencies_satisfied = False
                        break
                if dependencies_satisfied:
                    ready.append(node)
        return ready

    def is_completed(self) -> bool:
        """Determines if all nodes in the DAG have finished executing successfully."""
        return all(node.status in ["completed", "skipped"] for node in self.nodes.values())

    def has_failures(self) -> bool:
        """Determines if any of the nodes locked out on terminal failed states."""
        return any(node.status == "failed" for node in self.nodes.values())

    def reset_failed_nodes(self) -> None:
        """Resets failed statuses back to pending to enable re-runs or retries."""
        for node in self.nodes.values():
            if node.status == "failed":
                node.status = "pending"

    def serialize(self) -> List[Dict[str, Any]]:
        return [node.to_dict() for node in self.nodes.values()]

    @classmethod
    def deserialize(cls, steps_list: List[Dict[str, Any]]) -> "TaskGraph":
        graph = cls()
        for s in steps_list:
            node = TaskNode(
                step_id=s["step_id"],
                name=s["name"],
                action_type=s["action_type"],
                agent_target=s["agent_target"],
                params=s["params"],
                depends_on=s.get("depends_on", []),
                max_retries=s.get("max_retries", 2)
            )
            node.status = s.get("status", "pending")
            node.result = s.get("result")
            node.retry_count = s.get("retry_count", 0)
            node.conditional_branch = s.get("conditional_branch")
            graph.add_node(node)
        return graph

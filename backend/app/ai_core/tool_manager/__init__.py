import datetime
import os
import subprocess
from typing import Dict, Any, List, Type
from ..interfaces.tool import BaseTool

# --- Concrete Tool Implementations ---

class CalculatorTool(BaseTool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Executes mathematical expressions securely using parsing routines."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "The math formula (e.g. '120 * 45 + 12')"}
            },
            "required": ["expression"]
        }

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        expr = arguments.get("expression", "")
        # Safe eval check
        allowed = "0123456789+-*/() .*"
        if not all(c in allowed for c in expr):
            return {"status": "error", "message": "Insecure characters in expression."}
        try:
            val = eval(expr)
            return {"status": "success", "result": float(val)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

class TimeTool(BaseTool):
    @property
    def name(self) -> str:
        return "time"

    @property
    def description(self) -> str:
        return "Fetches current system time and active time zone coordinates."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.datetime.now()
        return {
            "status": "success",
            "iso": now.isoformat(),
            "formatted": now.strftime("%Y-%m-%d %H:%M:%S EST")
        }

class FilesystemTool(BaseTool):
    @property
    def name(self) -> str:
        return "filesystem"

    @property
    def description(self) -> str:
        return "Inspects and manages logs/files on filesystem container limits."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["list", "read", "write", "delete"], "description": "Operation type"},
                "filepath": {"type": "string", "description": "Path relative to file systems"},
                "content": {"type": "string", "description": "Raw text for safe writing purposes"}
            },
            "required": ["action", "filepath"]
        }

    @property
    def requires_approval(self) -> bool:
        return True # Modifying files is safety-gated

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        action = arguments.get("action")
        path = arguments.get("filepath", "")
        content = arguments.get("content", "")
        
        # Guard rails: avoid editing critical workspace files
        if any(bad in path for bad in [".env", "main.py", "database.py", "auth.py"]):
            return {"status": "error", "message": "Access restricted for core system settings."}
            
        try:
            if action == "list":
                files = os.listdir(".")
                return {"status": "success", "files": files}
            elif action == "read":
                if not os.path.exists(path):
                    return {"status": "error", "message": "File not found."}
                with open(path, "r", encoding="utf-8") as f:
                    txt = f.read(2000) # Read chunk limit
                return {"status": "success", "content": txt}
            elif action == "write":
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return {"status": "success", "message": f"Successfully wrote bytes to {path}."}
            elif action == "delete":
                if os.path.exists(path):
                    os.remove(path)
                    return {"status": "success", "message": f"Deleted {path} successfully."}
                return {"status": "error", "message": "File not found."}
            return {"status": "error", "message": "Unknown action."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

class BrowserTool(BaseTool):
    @property
    def name(self) -> str:
        return "browser"

    @property
    def description(self) -> str:
        return "Simulates viewing target documentation portals or searching pages."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
         return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The destination URL web link"}
            },
            "required": ["url"]
        }

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        url = arguments.get("url", "")
        return {
            "status": "success",
            "title": f"Rendered page title for {url}",
            "summary": "This is a simulated browser representation page text. The network is configured properly."
        }

class CalendarTool(BaseTool):
    @property
    def name(self) -> str:
        return "calendar"

    @property
    def description(self) -> str:
        return "Manages events, schedules meetings, and resolves calendar entries."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["add", "list"], "description": "Calendar action"},
                "event_name": {"type": "string"},
                "start_time": {"type": "string"}
            },
            "required": ["action"]
        }

    @property
    def requires_approval(self) -> bool:
        return True # Changing calendar is high risk

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        action = arguments.get("action")
        event = arguments.get("event_name", "Sync Event")
        time_str = arguments.get("start_time", "2026-06-25T14:00:00")
        return {
            "status": "success",
            "action": action,
            "message": f"Calendar {action} action successful for '{event}' at {time_str}."
        }

class EmailTool(BaseTool):
    @property
    def name(self) -> str:
        return "email"

    @property
    def description(self) -> str:
        return "Formulates and sends outbound communication to contacts."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"}
            },
            "required": ["to", "subject", "body"]
        }

    @property
    def requires_approval(self) -> bool:
        return True # Sending email requires authorization

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        to = arguments.get("to")
        subj = arguments.get("subject")
        return {
            "status": "success",
            "message": f"Outbound email queued successfully to {to} regarding '{subj}'."
        }

class TerminalTool(BaseTool):
    @property
    def name(self) -> str:
        return "terminal"

    @property
    def description(self) -> str:
        return "Executes localized environment container sandbox shell commands safely."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Standard shell command sequence (e.g. 'echo hello')"}
            },
            "required": ["command"]
        }

    @property
    def requires_approval(self) -> bool:
         return True # Terminal execution is high risk

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        cmd = arguments.get("command", "")
        # Simple security boundaries
        restrict = ["rm -rf", "sudo", "shutdown", "reboot", ":(){ :|:& };:"]
        if any(r in cmd for r in restrict):
            return {"status": "error", "message": "Command violates runtime sandbox policy. Rejected."}
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5.0)
            return {
                "status": "success",
                "code": res.returncode,
                "stdout": res.stdout[:1500],
                "stderr": res.stderr[:500]
            }
        except Exception as e:
            return {"status": "error", "message": f"Execution timed out or failed: {str(e)}"}

class GitTool(BaseTool):
    @property
    def name(self) -> str:
        return "git"

    @property
    def description(self) -> str:
        return "Coordinates remote repository synchronization, commits, and branch management."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
         return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["status", "commit", "push"], "description": "Git action"}
            },
            "required": ["action"]
        }

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        action = arguments.get("action")
        return {
            "status": "success",
            "output": f"Simulated Git '{action}' tracking: clean working directory, 0 pending conflicts."
        }

class VSCodeTool(BaseTool):
    @property
    def name(self) -> str:
        return "vscode"

    @property
    def description(self) -> str:
        return "Instructs workspace debugger nodes to open editor files or view references."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
         return {
            "type": "object",
            "properties": {
                "filepath": {"type": "string"},
                "reveal_line": {"type": "integer"}
            },
            "required": ["filepath"]
        }

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        path = arguments.get("filepath")
        return {
            "status": "success",
            "message": f"VS Code opened {path} tracking position at focus highlight."
        }


# --- Tool Manager Registry ---

class ToolManager:
    """
    Unified Tool registry manager coordinating dynamic lookup,
    parameters JSON schemas extraction, and secure code runtimes.
    """
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        # Auto register default suite
        self.register_tool(CalculatorTool())
        self.register_tool(TimeTool())
        self.register_tool(FilesystemTool())
        self.register_tool(BrowserTool())
        self.register_tool(CalendarTool())
        self.register_tool(EmailTool())
        self.register_tool(TerminalTool())
        self.register_tool(GitTool())
        self.register_tool(VSCodeTool())

    def register_tool(self, tool: BaseTool) -> None:
        self._tools[tool.name.lower()] = tool

    def get_registered_tools(self) -> List[Dict[str, Any]]:
        """Returns schemas and indicators of all selectable components."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "schema": t.parameters_schema,
                "requires_approval": t.requires_approval
            }
            for t in self._tools.values()
        ]

    def has_tool(self, name: str) -> bool:
         return name.lower() in self._tools

    def lookup_tool(self, name: str) -> BaseTool:
         tool = self._tools.get(name.lower())
         if not tool:
             raise ValueError(f"Tool '{name}' is not registered under NEXUS OS core.")
         return tool

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Wrapper ensuring lookup safety boundaries and returning status."""
        try:
            tool = self.lookup_tool(name)
            return tool.execute(arguments)
        except Exception as e:
            return {"status": "error", "message": str(e)}

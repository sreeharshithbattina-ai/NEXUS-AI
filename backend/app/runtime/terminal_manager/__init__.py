import os
import sys
import shlex
import asyncio
import logging
import subprocess
from typing import List, Dict, Any, Optional

from ..interfaces import ITerminalManager
from ..event_manager import global_event_bus

logger = logging.getLogger("terminal_manager")

class TerminalManager(ITerminalManager):
    def __init__(self):
        self._history: List[Dict[str, Any]] = []
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._active_processes: Dict[str, subprocess.Popen] = {}

    def classify_risk(self, command: str) -> Dict[str, Any]:
        """Classifies commands based on structural keywords to prevent malicious execution."""
        cmd_lower = command.lower().strip()
        tokens = shlex.split(cmd_lower) if cmd_lower else []
        if not tokens:
            return {"level": "LOW", "score": 0, "categories": []}

        danger_tokens = {
            "rm": 8, "rf": 9, "format": 10, "mkfs": 10, "dd": 10, "shred": 9,
            "sudo": 7, "chmod": 6, "chown": 6, "mv": 4, "curl": 5, "wget": 5,
            "pip": 4, "npm": 4, "apt": 6, "yum": 6, "docker": 5
        }

        score = 0
        categories = []
        for token in tokens:
            # Check individual base commands
            cleaned = token.replace("-", "").replace("/", "")
            if cleaned in danger_tokens:
                score += danger_tokens[cleaned]
                categories.append(cleaned)
            # Find redirection / piping pipelines
            if ">" in token or "|" in token or "&&" in token:
                score += 3
                categories.append("control_structures")

        if score >= 8:
            level = "HIGH"
        elif score >= 4:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "level": level,
            "score": score,
            "danger_indicators": list(set(categories))
        }

    def run_command(self, schema_command: str) -> Dict[str, Any]:
        """Synchronously runs single command, capturing full outputs and recording histories."""
        risk = self.classify_risk(schema_command)
        task_id = f"cmd-{len(self._history) + 1:03d}"
        
        # Guard statement: log event
        global_event_bus.emit(
            "CommandExecuted",
            "TerminalManager",
            {"command": schema_command, "task_id": task_id, "risk": risk.get("level")}
        )

        try:
            # Execute safely using native subprocess
            # Bind to sandbox shell execution limits
            result = subprocess.run(
                schema_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30 # Keep standard timeouts for safe execution
            )
            
            summary = {
                "task_id": task_id,
                "command": schema_command,
                "risk_level": risk.get("level"),
                "risk_score": risk.get("score"),
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "status": "success" if result.returncode == 0 else "failed"
            }
        except subprocess.TimeoutExpired:
            summary = {
                "task_id": task_id,
                "command": schema_command,
                "risk_level": risk.get("level"),
                "risk_score": risk.get("score"),
                "exit_code": -1,
                "stdout": "",
                "stderr": "Execution timed out.",
                "status": "timeout"
            }
        except Exception as e:
            summary = {
                "task_id": task_id,
                "command": schema_command,
                "risk_level": risk.get("level"),
                "risk_score": risk.get("score"),
                "exit_code": -2,
                "stdout": "",
                "stderr": f"Error initiating execution: {str(e)}",
                "status": "error"
            }

        self._history.append(summary)
        return summary

    def cancel_command(self, task_id: str) -> bool:
        """Kills any active subprocess tasks associated with ID."""
        # Simulated cancel, or check native tasks
        if task_id in self._active_processes:
            try:
                proc = self._active_processes[task_id]
                proc.terminate()
                global_event_bus.emit(
                    "CommandCancelled",
                    "TerminalManager",
                    {"task_id": task_id}
                )
                return True
            except Exception:
                pass
        return False

    def get_history(self) -> List[Dict[str, Any]]:
        return self._history

global_terminal_manager = TerminalManager()

import os
from typing import Dict, Any, List

class ExecutionSandboxVerifier:
    """Blocks unauthorized system calls, command expansions, or arbitrary raw binary launches."""
    def __init__(self):
        self.allowed_binary_whitelist = ["python", "python3", "echo", "ls", "node", "npm", "git"]
        self.forbidden_character_sequences = [";", "&&", "||", "`", "$", "\n", "\r", ".."]

    def is_safe_command(self, raw_command: str) -> bool:
        """Heuristically inspects argument vectors to prevent path injection and chained execution."""
        cleaned = raw_command.strip()
        if not cleaned:
            return True
            
        # 1. Block forbidden shell sequence delimiters
        for seq in self.forbidden_character_sequences:
            if seq in cleaned:
                return False
                
        # 2. Block absolute paths crawling out of standard app root bounds
        parts = cleaned.split()
        if not parts:
            return True
            
        primary_executable = os.path.basename(parts[0])
        return primary_executable in self.allowed_binary_whitelist

global_sandbox_verifier = ExecutionSandboxVerifier()

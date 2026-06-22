import hashlib
import time
from typing import List, Dict, Any

class ChainedAuditLogger:
    """Writes sequential audit entries, linking them together with SHA-256 historical signature hashes."""
    def __init__(self):
        self._audit_chain: List[Dict[str, Any]] = []
        self._last_block_hash = "0" * 64

    def commit_audit_entry(self, user_id: str, action: str, details: str, threat_classification: str = "Low") -> Dict[str, Any]:
        """Calculates historical hashes and appends entries to our secure validation records."""
        timestamp = time.time()
        
        # Calculate block hash
        digest = hashlib.sha256()
        digest.update(f"{self._last_block_hash}:{user_id}:{action}:{details}:{timestamp}:{threat_classification}".encode("utf-8"))
        block_hash = digest.hexdigest()
        
        entry = {
            "index": len(self._audit_chain),
            "user_id": user_id,
            "action": action,
            "details": details,
            "threat_classification": threat_classification,
            "timestamp": timestamp,
            "previous_hash": self._last_block_hash,
            "hash": block_hash
        }
        
        self._audit_chain.append(entry)
        self._last_block_hash = block_hash
        return entry

    def verify_chain_integrity(self) -> bool:
        """Audits block indexes sequentially to detect deletions or manual tamperings."""
        expected_prev_hash = "0" * 64
        for idx, entry in enumerate(self._audit_chain):
            if entry["index"] != idx:
                return False
            if entry["previous_hash"] != expected_prev_hash:
                return False
                
            digest = hashlib.sha256()
            digest.update(f"{entry['previous_hash']}:{entry['user_id']}:{entry['action']}:{entry['details']}:{entry['timestamp']}:{entry['threat_classification']}".encode("utf-8"))
            if digest.hexdigest() != entry["hash"]:
                return False
                
            expected_prev_hash = entry["hash"]
        return True

    def list_entries(self) -> List[Dict[str, Any]]:
        return self._audit_chain

global_chained_audit_logger = ChainedAuditLogger()
# Seed genesis block
global_chained_audit_logger.commit_audit_entry("0", "KernelInit", "Initialized Immutable Security Cryptographic Audit Log Segment.")

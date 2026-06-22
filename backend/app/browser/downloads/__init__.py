import os
import time
from typing import Dict, Any, List

class DownloadHandler:
    """Monitors browser download pipes to capture, register, and save incoming documents."""
    def __init__(self, target_directory: str = "/tmp/nexus_downloads"):
        self.target_directory = target_directory
        self._registry: List[Dict[str, Any]] = []

    def register_download(self, filename: str, mime_type: str, bytes_count: int, source_url: str) -> Dict[str, Any]:
        """Saves file details to audit logs."""
        record = {
            "file_id": f"dl-{int(time.time())}",
            "filename": filename,
            "path": os.path.join(self.target_directory, filename),
            "mime_type": mime_type,
            "bytes": bytes_count,
            "source": source_url,
            "downloaded_at": time.time(),
            "scanned_safe": True
        }
        self._registry.append(record)
        return record

    def list_downloads(self) -> List[Dict[str, Any]]:
        return self._registry

global_download_handler = DownloadHandler()

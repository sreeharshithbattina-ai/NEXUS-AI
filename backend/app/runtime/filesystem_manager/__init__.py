import os
import shutil
import logging
from typing import List, Dict, Any, Optional
from ..interfaces import IFilesystemManager
from ..event_manager import global_event_bus

logger = logging.getLogger("filesystem_manager")

class FilesystemManager(IFilesystemManager):
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = os.path.abspath(workspace_root)
        self.recycle_bin_dir = os.path.join(self.workspace_root, ".nexus_recycle_bin")
        os.makedirs(self.recycle_bin_dir, exist_ok=True)
        # Dictionary pattern matching file tag indexes: {absolute_path: [tags]}
        self._tags: Dict[str, List[str]] = {}

    def _resolve_path(self, target_path: str) -> str:
        # Prevent path traversal outside system limits if requested, or return fully-qualified paths
        if os.path.isabs(target_path):
            return target_path
        return os.path.abspath(os.path.join(self.workspace_root, target_path))

    def create_folder(self, path: str) -> Dict[str, Any]:
        full_path = self._resolve_path(path)
        os.makedirs(full_path, exist_ok=True)
        global_event_bus.emit(
            "FileModified",
            "FilesystemManager",
            {"operation": "create_folder", "path": full_path}
        )
        return {"status": "success", "path": full_path, "type": "directory"}

    def delete_item(self, path: str, force: bool = False) -> Dict[str, Any]:
        """Implements safe deleted file operations; never hard-purges unless forced."""
        full_path = self._resolve_path(path)
        if not os.path.exists(full_path):
            return {"status": "error", "message": f"Path '{path}' does not exist."}

        # Recycle bin routing
        name = os.path.basename(full_path)
        recycle_path = os.path.join(self.recycle_bin_dir, f"{name}_{int(os.path.getmtime(full_path))}")
        
        # If force flag is enabled or confirmed, we can perform standard erase
        if force:
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)
            global_event_bus.emit(
                "FileModified",
                "FilesystemManager",
                {"operation": "permanent_delete", "path": full_path}
            )
            return {"status": "success", "message": f"Permanently destroyed '{name}'."}
        else:
            # Safe moving to Recycle Bin
            shutil.move(full_path, recycle_path)
            global_event_bus.emit(
                "FileModified",
                "FilesystemManager",
                {"operation": "recycle_delete", "path": full_path, "recycle_path": recycle_path}
            )
            return {
                "status": "recycled",
                "message": f"Moved '{name}' safely to the Recycle Bin. Confirmation required for permanent removal.",
                "original_path": full_path,
                "recycle_path": recycle_path
            }

    def rename_item(self, src: str, dst: str) -> Dict[str, Any]:
        src_path = self._resolve_path(src)
        dst_path = self._resolve_path(dst)
        if not os.path.exists(src_path):
            return {"status": "error", "message": f"Source '{src}' does not exist."}
        
        os.rename(src_path, dst_path)
        global_event_bus.emit(
            "FileModified",
            "FilesystemManager",
            {"operation": "rename", "src": src_path, "dst": dst_path}
        )
        return {"status": "success", "src": src_path, "dst": dst_path}

    def copy_item(self, src: str, dst: str) -> Dict[str, Any]:
        src_path = self._resolve_path(src)
        dst_path = self._resolve_path(dst)
        if not os.path.exists(src_path):
            return {"status": "error", "message": f"Source '{src}' does not exist."}
            
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, dst_path)
            
        global_event_bus.emit(
            "FileModified",
            "FilesystemManager",
            {"operation": "copy", "src": src_path, "dst": dst_path}
        )
        return {"status": "success", "src": src_path, "dst": dst_path}

    def move_item(self, src: str, dst: str) -> Dict[str, Any]:
        src_path = self._resolve_path(src)
        dst_path = self._resolve_path(dst)
        if not os.path.exists(src_path):
            return {"status": "error", "message": f"Source '{src}' does not exist."}
            
        shutil.move(src_path, dst_path)
        global_event_bus.emit(
            "FileModified",
            "FilesystemManager",
            {"operation": "move", "src": src_path, "dst": dst_path}
        )
        return {"status": "success", "src": src_path, "dst": dst_path}

    def read_file(self, path: str) -> str:
        full_path = self._resolve_path(path)
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def write_file(self, path: str, content: str) -> Dict[str, Any]:
        full_path = self._resolve_path(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        global_event_bus.emit(
            "FileModified",
            "FilesystemManager",
            {"operation": "write_file", "path": full_path, "size": len(content)}
        )
        return {"status": "success", "path": full_path, "bytes": len(content)}

    def search_files(self, pattern: str, root_dir: str = ".") -> List[Dict[str, Any]]:
        full_root = self._resolve_path(root_dir)
        results = []
        for dirpath, _, filenames in os.walk(full_root):
            for f in filenames:
                if pattern.lower() in f.lower():
                    abs_path = os.path.join(dirpath, f)
                    results.append({
                        "filename": f,
                        "path": abs_path,
                        "size": os.path.getsize(abs_path),
                        "tags": self._tags.get(abs_path, [])
                    })
        return results

    def tag_file(self, path: str, tag: str) -> Dict[str, Any]:
        full_path = self._resolve_path(path)
        if not os.path.exists(full_path):
            return {"status": "error", "message": "File does not exist to assign tags."}
        if full_path not in self._tags:
            self._tags[full_path] = []
        if tag not in self._tags[full_path]:
            self._tags[full_path].append(tag)
        return {"status": "success", "path": full_path, "tags": self._tags[full_path]}

    def untag_file(self, path: str, tag: str) -> Dict[str, Any]:
        full_path = self._resolve_path(path)
        if full_path in self._tags and tag in self._tags[full_path]:
            self._tags[full_path].remove(tag)
        return {"status": "success", "path": full_path, "tags": self._tags.get(full_path, [])}

    def list_recycle_bin(self) -> List[Dict[str, Any]]:
        results = []
        for f in os.listdir(self.recycle_bin_dir):
            p = os.path.join(self.recycle_bin_dir, f)
            results.append({
                "deleted_name": f,
                "path": p,
                "size_bytes": os.path.getsize(p)
            })
        return results

    def empty_recycle_bin(self) -> Dict[str, Any]:
        count = 0
        for f in os.listdir(self.recycle_bin_dir):
            p = os.path.join(self.recycle_bin_dir, f)
            if os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
            count += 1
        return {"status": "success", "purged_items_count": count}

global_filesystem_manager = FilesystemManager()

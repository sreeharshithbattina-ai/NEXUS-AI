from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class IApplicationManager(ABC):
    @abstractmethod
    def open_app(self, app_name_or_path: str) -> Dict[str, Any]: pass
    @abstractmethod
    def close_app(self, identifier: str) -> Dict[str, Any]: pass
    @abstractmethod
    def focus_app(self, identifier: str) -> Dict[str, Any]: pass
    @abstractmethod
    def list_running_apps(self) -> List[Dict[str, Any]]: pass
    @abstractmethod
    def get_active_window(self) -> Dict[str, Any]: pass

class IFilesystemManager(ABC):
    @abstractmethod
    def create_folder(self, path: str) -> Dict[str, Any]: pass
    @abstractmethod
    def delete_item(self, path: str, force: bool = False) -> Dict[str, Any]: pass
    @abstractmethod
    def rename_item(self, src: str, dst: str) -> Dict[str, Any]: pass
    @abstractmethod
    def copy_item(self, src: str, dst: str) -> Dict[str, Any]: pass
    @abstractmethod
    def move_item(self, src: str, dst: str) -> Dict[str, Any]: pass
    @abstractmethod
    def read_file(self, path: str) -> str: pass
    @abstractmethod
    def write_file(self, path: str, content: str) -> Dict[str, Any]: pass
    @abstractmethod
    def search_files(self, pattern: str, root_dir: str) -> List[Dict[str, Any]]: pass

class ITerminalManager(ABC):
    @abstractmethod
    def run_command(self, schema_command: str) -> Dict[str, Any]: pass
    @abstractmethod
    def cancel_command(self, task_id: str) -> bool: pass
    @abstractmethod
    def get_history(self) -> List[Dict[str, Any]]: pass

class IProcessManager(ABC):
    @abstractmethod
    def get_system_metrics(self) -> Dict[str, Any]: pass
    @abstractmethod
    def list_processes(self) -> List[Dict[str, Any]]: pass

class IClipboardManager(ABC):
    @abstractmethod
    def read(self) -> str: pass
    @abstractmethod
    def write(self, data: str) -> bool: pass
    @abstractmethod
    def get_history(self) -> List[str]: pass

class IScreenshotManager(ABC):
    @abstractmethod
    def capture_fullscreen(self) -> str: pass
    @abstractmethod
    def capture_region(self, x: int, y: int, w: int, h: int) -> str: pass

class INotificationManager(ABC):
    @abstractmethod
    def notify(self, title: str, body: str, actions: Optional[List[str]] = None) -> str: pass
    @abstractmethod
    def solicit_approval(self, prompt: str, timeout_sec: int = 30) -> bool: pass

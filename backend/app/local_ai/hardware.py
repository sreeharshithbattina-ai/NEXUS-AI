import os
import platform
import subprocess
from typing import Dict, Any

class HardwareDetector:
    """Discovers acceleration coprocessors and sets batch allocations for local model runs."""
    def __init__(self):
        self.device = "cpu"
        self.gpu_vram_gb = 0.0
        self.cpu_cores = os.cpu_count() or 4
        self.detect_hardware()

    def detect_hardware(self) -> str:
        """Checks CUDA registers, Apple Silicon MPS tags, or falls back to system CPUs."""
        # 1. Check env override
        override = os.environ.get("NEXUS_ACCELERATOR")
        if override:
            self.device = override.lower()
            return self.device

        # 2. Check system platform
        sys_platform = platform.system().lower()
        
        # Check CUDA (NVIDIA)
        try:
            # We can mock/check nvidia-smi as standard subprocess lookup
            if platform.system() != "Windows":
                res = subprocess.run(["which", "nvidia-smi"], capture_output=True, text=True)
                if res.returncode == 0:
                    self.device = "cuda"
                    self.gpu_vram_gb = 8.0 # fallback representation
                    return "cuda"
        except Exception:
            pass

        # Check MPS (Apple Silicon)
        if sys_platform == "darwin":
            if platform.processor() == "arm":
                self.device = "mps"
                self.gpu_vram_gb = 16.0 # unified memory block representation
                return "mps"

        self.device = "cpu"
        return "cpu"

    def get_hardware_status(self) -> Dict[str, Any]:
        return {
            "device": self.device,
            "architecture": platform.machine(),
            "cpu_cores": self.cpu_cores,
            "gpu_vram_gb": self.gpu_vram_gb,
            "cpu_fallback_active": self.device == "cpu"
        }

global_hardware_detector = HardwareDetector()

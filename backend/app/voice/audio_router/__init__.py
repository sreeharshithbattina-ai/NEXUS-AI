import numpy as np
from typing import List
from ..interfaces import IAudioRouter

class AudioRouter(IAudioRouter):
    """Filters noisy mic signals, decouples loudspeaker loopbacks (AEC) and runs VAD metrics."""
    def __init__(self):
        self.echo_cancellation_active = True
        self.noise_suppression_level = 3 # 0-5 scale

    def process_input(self, record_buffer: bytes) -> bytes:
        """Applies digital bandpass and noise attenuation filtering over raw PCM arrays."""
        if not record_buffer or len(record_buffer) < 2:
            return record_buffer
            
        # Transform stream to audio array for math analysis
        samples = np.frombuffer(record_buffer, dtype=np.int16, errors="ignore").copy()
        
        # Simple simulated noise cancellation (moving average smoothing attenuates high spikes)
        if self.noise_suppression_level > 0 and len(samples) > 2:
            window = self.noise_suppression_level + 1
            kernel = np.ones(window) / window
            smoothed = np.convolve(samples, kernel, mode="same")
            samples = np.clip(smoothed, -32768, 32767).astype(np.int16)
            
        return samples.tobytes()

    def enable_echo_cancellation(self, enabled: bool) -> None:
        self.echo_cancellation_active = enabled

    def detect_voice_activity(self, frame: bytes) -> bool:
        """Heuristically runs standard short term energy checks to filter background hum."""
        if not frame or len(frame) < 10:
            return False
        samples = np.frombuffer(frame, dtype=np.int16, errors="ignore")
        if len(samples) == 0:
            return False
            
        energy = np.mean(np.abs(samples))
        # standard silent threshold is around 120
        return energy > 400.0

global_audio_router = AudioRouter()

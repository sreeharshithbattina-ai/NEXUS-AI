import math
import struct
from typing import List, Dict, Any
from ..interfaces import ITextToSpeech

class TextToSpeech(ITextToSpeech):
    """Bridges digital string responses into synthetic wav streams with custom speeds/voice modulation."""
    def __init__(self):
        self._voice_packs = [
            {"id": "zephyr", "name": "Zephyr (Male Warm)", "downloaded": True, "size_mb": 42.4},
            {"id": "aurora", "name": "Aurora (Female Crisp)", "downloaded": True, "size_mb": 31.8},
            {"id": "echo", "name": "Echo (Neutral Mono)", "downloaded": False, "size_mb": 50.1},
            {"id": "borealis", "name": "Borealis (Deep Robotic)", "downloaded": False, "size_mb": 48.0}
        ]

    def list_voice_packs(self) -> List[Dict[str, Any]]:
        return self._voice_packs

    def download_voice_pack(self, voice_id: str) -> bool:
        for vp in self._voice_packs:
            if vp["id"] == voice_id:
                vp["downloaded"] = True
                return True
        return False

    def synthesize(self, text: str, voice_pack: str = "zephyr", speed: float = 1.0, pitch: float = 1.0) -> bytes:
        """Saves textual expressions into synthesised WAVE streams, dynamically pitch-modulating frequencies."""
        # Simple procedural wave generator (pure sine synthesis) simulating voice output
        sample_rate = 16000
        duration = min(3.0, max(0.5, len(text) * 0.05 / speed))
        num_samples = int(sample_rate * duration)
        
        # Audio parameter verification
        freq = 220.0 * pitch # base pitch shift
        if voice_pack == "aurora":
            freq = 380.0 * pitch
        elif voice_pack == "borealis":
            freq = 90.0 * pitch

        # Generate WAVE bytes block
        audio_buffer = bytearray()
        for i in range(num_samples):
            # Generate sine-wave oscillation
            t = float(i) / sample_rate
            val = math.sin(2.0 * math.pi * freq * t)
            # Apply volume envelope
            envelope = math.sin(math.pi * t / duration)
            sample = int(val * envelope * 32767)
            audio_buffer.extend(struct.pack("<h", sample))

        # Write clean WAV headers
        bytes_per_sample = 2
        num_channels = 1
        byte_rate = sample_rate * num_channels * bytes_per_sample
        data_chunk_size = len(audio_buffer)
        riff_chunk_size = 36 + data_chunk_size
        
        wav_header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF", riff_chunk_size, b"WAVE",
            b"fmt ", 16, 1, num_channels, sample_rate, byte_rate,
            num_channels * bytes_per_sample, bytes_per_sample * 8,
            b"data", data_chunk_size
        )
        
        return bytes(wav_header + audio_buffer)

global_tts_engine = TextToSpeech()

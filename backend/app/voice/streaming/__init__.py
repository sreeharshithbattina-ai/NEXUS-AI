import asyncio
from typing import AsyncGenerator

class SoundStreamer:
    """Manages continuous micro-chunk stream distributions for network endpoints or media players."""
    def __init__(self):
        self.is_active = False

    async def stream_audio_out(self, audio_data: bytes, chunk_size: int = 4096) -> AsyncGenerator[bytes, None]:
        """Slices output WAV bytes into dynamic payloads for real-time WebSocket broadcasting."""
        self.is_active = True
        offset = 0
        while self.is_active and offset < len(audio_data):
            slice_bytes = audio_data[offset : offset + chunk_size]
            offset += chunk_size
            yield slice_bytes
            await asyncio.sleep(0.02) # throttle to mimic standard speech play rate
        self.is_active = False

global_sound_streamer = SoundStreamer()

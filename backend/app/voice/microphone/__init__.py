import collections
from typing import Optional

class MicroBuffer:
    """Manages high efficiency sliding frames buffer for physical microphone interfaces."""
    def __init__(self, capacity: int = 100):
        self._queue = collections.deque(maxlen=capacity)
        self.muted = False

    def push(self, frame: bytes) -> None:
        if not self.muted:
            self._queue.append(frame)

    def pop_all(self) -> bytes:
        combined = b""
        while self._queue:
            combined += self._queue.popleft()
        return combined

    def clear(self) -> None:
        self._queue.clear()

global_micro_buffer = MicroBuffer()

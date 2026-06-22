from typing import List

class InterruptionDetector:
    """Listens recursively for priority command cancels ('stop', 'shh') to mute TTS output instantly."""
    def __init__(self):
        self._keywords = ["stop", "cancel", "hold on", "shh", "quiet", "shut up", "nexus stop"]

    def check_text(self, text: str) -> bool:
        """Flags true if text inputs match early muting triggers."""
        cleaned = text.lower().strip()
        return any(kw in cleaned for kw in self._keywords)

    def check_acoustic_interruption(self, rms_db: float, threshold_db: float = 85.0) -> bool:
        """Bypasses full transcript synthesis if user emits a high impact sound burst (e.g. cough or shout)."""
        return rms_db > threshold_db

global_interruption_detector = InterruptionDetector()

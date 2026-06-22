import time
from typing import Dict, Any, List

class ConversationalLoopManager:
    """Powers ambient Hands-Free conversational states, tracking timeouts and silence boundaries."""
    def __init__(self):
        self.always_listening = False
        self.is_speaking = False
        self.last_speech_time = time.time()
        self.silence_tolerance_sec = 2.5 # auto replies if user ceases speaking longer than 2.5sec

    def update_activity(self, voice_active: bool) -> str:
        """Determines pipeline feedback cues (e.g. 'start_transcribing', 'keep_listening', 'trigger_tts')."""
        current_time = time.time()
        
        if voice_active:
            self.last_speech_time = current_time
            if not self.is_speaking:
                self.is_speaking = True
                return "user_started_speaking"
            return "user_speaking"
        
        # User not speaking
        if self.is_speaking:
            # Check length of silence
            if current_time - self.last_speech_time > self.silence_tolerance_sec:
                self.is_speaking = False
                return "user_finished_speaking"
            return "awaiting_silence_boundary"
            
        return "idle"

global_conversational_loop_manager = ConversationalLoopManager()

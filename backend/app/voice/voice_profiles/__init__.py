from typing import Dict, Any, List, Optional

class VoiceProfile:
    """Configures explicit vocal acoustic settings for personalized assistant interactions."""
    def __init__(self, profile_id: str, name: str, base_pitch: float, base_speed: float, noise_filter_enabled: bool):
        self.profile_id = profile_id
        self.name = name
        self.base_pitch = base_pitch
        self.base_speed = base_speed
        self.noise_filter_enabled = noise_filter_enabled

class VoiceProfileManager:
    """Stores and synchronizes active user vocal settings."""
    def __init__(self):
        self._profiles = {
            "default": VoiceProfile("default", "Standard Executive", 1.0, 1.0, True),
            "whisperer": VoiceProfile("whisperer", "Soothing Therapist", 0.85, 0.9, True),
            "lecturer": VoiceProfile("lecturer", "Accelerated Presenter", 1.2, 1.25, False),
            "cosmic": VoiceProfile("cosmic", "Space Ambient Sound", 0.65, 0.85, True)
        }
        self.active_profile_id = "default"

    def list_profiles(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": p.profile_id,
                "name": p.name,
                "base_pitch": p.base_pitch,
                "base_speed": p.base_speed,
                "noise_filter_enabled": p.noise_filter_enabled,
                "is_active": p.profile_id == self.active_profile_id
            } for p in self._profiles.values()
        ]

    def set_active_profile(self, profile_id: str) -> bool:
        if profile_id in self._profiles:
            self.active_profile_id = profile_id
            return True
        return False

    def get_current(self) -> VoiceProfile:
        return self._profiles[self.active_profile_id]

global_voice_profile_manager = VoiceProfileManager()

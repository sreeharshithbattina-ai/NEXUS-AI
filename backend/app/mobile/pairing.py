import secrets
import time
from typing import Dict, Any

class MobileDevicePairingManager:
    """Manages trust handshakes, QR authentication frames, and secure API key provisioning."""
    def __init__(self):
        self._pending_challenges: Dict[str, Dict[str, Any]] = {}
        self._paired_devices: Dict[str, Dict[str, Any]] = {}

    def generate_pairing_challenge(self, user_id: str) -> Dict[str, Any]:
        """Creates a short-lived Numeric Code and QR content payload."""
        code = f"{secrets.randbelow(900000) + 100000}" # 6-digit PIN
        secret_salt = secrets.token_hex(16)
        
        self._pending_challenges[user_id] = {
            "pairing_code": code,
            "secret_salt": secret_salt,
            "expires_at": time.time() + 300.0 # 5 minutes
        }
        return {
            "pairing_code": code,
            "qr_payload": f"NEXUS_OS_PAIR:{user_id}:{code}:{secret_salt}",
            "expires_in_sec": 300
        }

    def verify_pairing_pin(self, user_id: str, candidate_pin: str, device_name: str) -> Dict[str, Any]:
        """Validates incoming client PIN challenges and generates secure tokens."""
        challenge = self._pending_challenges.get(user_id)
        if not challenge:
            return {"success": False, "reason": "No pending pairing challenge exists for this token."}
            
        if time.time() > challenge["expires_at"]:
            del self._pending_challenges[user_id]
            return {"success": False, "reason": "Pairing challenge has expired."}
            
        if challenge["pairing_code"] != candidate_pin:
            return {"success": False, "reason": "Verification PIN mismatch."}
            
        # Success! Provision API token
        device_token = f"nxtk_{secrets.token_hex(24)}"
        dev_id = f"mbl-{secrets.token_hex(4)}"
        
        paired_record = {
            "device_id": dev_id,
            "device_name": device_name,
            "token_hash": dev_id, # simulated
            "paired_at": time.time(),
            "owner_user_id": user_id
        }
        
        self._paired_devices[device_token] = paired_record
        del self._pending_challenges[user_id]
        
        return {
            "success": True,
            "device_id": dev_id,
            "api_token": device_token,
            "message": "Mobile device pairing authentication successful."
        }

global_mobile_pairing_manager = MobileDevicePairingManager()

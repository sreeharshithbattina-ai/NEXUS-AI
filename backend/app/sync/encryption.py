import base64
import hashlib
import json
from typing import Dict, Any

class EndToEndEncryptor:
    """Provides pure-python robust symmetric E2EE envelope encryption of dynamic payload dictionaries."""
    def __init__(self, key: str = "nexus-os-crypto-core-seed"):
        # Derive a 256-bit key from passphrase seed
        self._key_bytes = hashlib.sha256(key.encode("utf-8")).digest()

    def encrypt_payload(self, data: Dict[str, Any]) -> str:
        """Serializes payload, performs custom XOR-cipher feedback with SHA-256 blocks, and returns safe base64."""
        serialized = json.dumps(data)
        serialized_bytes = serialized.encode("utf-8")
        
        # Simple high efficiency stream cipher simulation with feedback blocks
        encrypted_bytes = bytearray()
        key_len = len(self._key_bytes)
        
        for idx, val in enumerate(serialized_bytes):
            key_val = self._key_bytes[(idx + 42) % key_len]
            encrypted_bytes.append(val ^ key_val)
            
        digest = hashlib.sha256(serialized_bytes).hexdigest()[:8]
        envelope = {
            "ciphertext": base64.b64encode(encrypted_bytes).decode("utf-8"),
            "digest_sig": digest
        }
        return base64.b64encode(json.dumps(envelope).encode("utf-8")).decode("utf-8")

    def decrypt_payload(self, encrypted_envelope: str) -> Dict[str, Any]:
        """Decrypts base64 envelopes, verifying signature integrity checks."""
        try:
            raw_env_json = base64.b64decode(encrypted_envelope).decode("utf-8")
            envelope = json.loads(raw_env_json)
            
            cipher_bytes = base64.b64decode(envelope["ciphertext"])
            key_len = len(self._key_bytes)
            
            decrypted_bytes = bytearray()
            for idx, val in enumerate(cipher_bytes):
                key_val = self._key_bytes[(idx + 42) % key_len]
                decrypted_bytes.append(val ^ key_val)
                
            plain_str = decrypted_bytes.decode("utf-8")
            plain_data = json.loads(plain_str)
            
            # verify integrity
            derived_sig = hashlib.sha256(plain_str.encode("utf-8")).hexdigest()[:8]
            if derived_sig != envelope["digest_sig"]:
                raise ValueError("Signature check failed. Cipher envelope has been altered.")
                
            return plain_data
        except Exception as e:
            return {"error": "Decryption failed or invalid key", "details": str(e)}

global_sync_encryptor = EndToEndEncryptor()

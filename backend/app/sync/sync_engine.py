import time
from typing import Dict, Any, List

from .encryption import global_sync_encryptor
from .conflict_resolver import global_conflict_resolver
from ..database import SessionLocal
from ..models import UserProfile, MemoryItem

class CentralDeviceSyncEngine:
    """Manages secure transport sync streams, decrypting peer records and merging platform states."""
    def __init__(self):
        self.registered_devices = [
            {"device_id": "dev-main-vault", "device_type": "Main Desktop Runtime", "trusted": True},
            {"device_id": "dev-mobile-companion", "device_type": "iOS / Android Client", "trusted": True}
        ]

    def register_new_trust_device(self, device_id: str, device_type: str) -> None:
        if not any(d["device_id"] == device_id for d in self.registered_devices):
            self.registered_devices.append({
                "device_id": device_id,
                "device_type": device_type,
                "trusted": True
            })

    def process_incoming_sync(self, user_id: str, encrypted_envelope: str) -> Dict[str, Any]:
        """Decrypts sync messages, runs conflict resolvers and updates database states."""
        payload = global_sync_encryptor.decrypt_payload(encrypted_envelope)
        if "error" in payload:
            return {"success": False, "reason": "Decryption check failed", "details": payload}

        payload_type = payload.get("sync_type") # e.g. "preferences", "memories", "workflows"
        remote_data = payload.get("data", {})
        
        db = SessionLocal()
        synced_count = 0
        status_info = "Success"

        try:
            if payload_type == "preferences":
                # Resolve assistant controls
                profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
                if profile:
                    local_p = {
                        "assistant_personality": profile.assistant_personality,
                        "assistant_voicepack": profile.assistant_voicepack,
                        "speaking_speed": profile.speaking_speed,
                        "timestamp": time.time() - 100.0 # simulated local older stamp
                    }
                    resolved = global_conflict_resolver.reconcile_items(local_p, remote_data)
                    
                    profile.assistant_personality = resolved.get("assistant_personality", profile.assistant_personality)
                    profile.assistant_voicepack = resolved.get("assistant_voicepack", profile.assistant_voicepack)
                    profile.speaking_speed = resolved.get("speaking_speed", profile.speaking_speed)
                    db.commit()
                    synced_count = 1
                    
            elif payload_type == "memories":
                # Resolve saved semantic memories
                for mem in remote_data:
                    mem_id = mem.get("id")
                    if mem_id:
                        existing = db.query(MemoryItem).filter(MemoryItem.id == mem_id).first()
                        if existing:
                            local_m = {
                                "id": existing.id,
                                "content": existing.content,
                                "category": existing.category,
                                "tags": existing.tags,
                                "timestamp": time.time() - 200.0
                            }
                            resolved = global_conflict_resolver.reconcile_items(local_m, mem)
                            existing.content = resolved.get("content", existing.content)
                        else:
                            # Add new
                            new_item = MemoryItem(
                                id=mem_id,
                                user_id=user_id,
                                content=mem.get("content"),
                                category=mem.get("category", "Preference"),
                                tags=mem.get("tags", []),
                                confidence=mem.get("confidence", 0.9)
                            )
                            db.add(new_item)
                        synced_count += 1
                db.commit()

        except Exception as e:
            db.rollback()
            status_info = f"Database rollback: {str(e)}"
            return {"success": False, "reason": status_info}
        finally:
            db.close()

        # Compile fresh snapshot
        return {
            "success": True,
            "synced_records_count": synced_count,
            "status": status_info,
            "timestamp": time.time(),
            "devices": self.registered_devices
        }

global_central_sync_engine = CentralDeviceSyncEngine()

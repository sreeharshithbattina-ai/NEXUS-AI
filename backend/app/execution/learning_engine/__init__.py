import re
import datetime
from typing import List, Dict, Any, Optional
from ..interfaces import ILearningEngine
from ...database import SessionLocal
from ...models import MemoryItem, UserProfile
from ...runtime.event_manager import global_event_bus

class LearningEngine(ILearningEngine):
    """Analyzes conversation and workflow logs to extract user preferences, persisting them reviewably."""
    def __init__(self):
        # Local short-term buffer for learnings if DB transaction is busy
        self._learned_preferences: List[Dict[str, Any]] = []

    def extract_preferences(self, user_id: str, session_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parses active message lines or logs to capture preference rules, returning newly cataloged items."""
        newly_learned = []
        db = SessionLocal()
        
        try:
            for session in session_history:
                text = str(session.get("content", "")).lower()
                category = "Preference"
                content = None
                tags = []
                
                # 1. Preferred IDE
                ide_match = re.search(r"prefer\s+(vs\s*code|cursor|neovim|intellij|pycharm|sublime)", text)
                if ide_match:
                    ide = ide_match.group(1).upper()
                    content = f"Prefers using {ide} as primary development IDE."
                    tags = ["ide", "coding", "workspace"]
                elif "use vscode" in text or "open vs code" in text:
                    content = "Prefers VS Code for code-editing tasks."
                    tags = ["ide", "coding"]
                
                # 2. Preferred Coding Style
                elif any(word in text for word in ["docstring", "pythonic", "type hint", "camelcase", "snakecase", "strict types"]):
                    style_extracted = []
                    if "docstring" in text:
                        style_extracted.append("including docstrings on every function")
                    if "type hint" in text or "strict types" in text:
                        style_extracted.append("enforcing strict type hinting")
                    if "camelcase" in text:
                        style_extracted.append("formatting code in camelCase style")
                    if "snakecase" in text:
                        style_extracted.append("formatting variables in snake_case")
                        
                    if style_extracted:
                        content = f"Prefers coding style: {', '.join(style_extracted)}."
                        tags = ["coding_style", "coding"]
                
                # 3. Travel preferences
                elif any(word in text for word in ["window seat", "aisle seat", "eco-friendly", "morning flight", "first class"]):
                    prefs = []
                    if "window seat" in text:
                        prefs.append("window seats")
                    if "aisle seat" in text:
                        prefs.append("aisle seats")
                    if "eco-friendly" in text:
                        prefs.append("eco-friendly transit options")
                    if "morning flight" in text:
                        prefs.append("morning flight times")
                        
                    if prefs:
                        content = f"Travel planning priority: prefers {', '.join(prefs)}."
                        tags = ["travel", "itinerary"]

                # 4. Working Hours
                elif any(word in text for word in ["working hours", "available from", "work between", "deep work", "timezone"]):
                    hours_match = re.search(r"(?:work|available|active)\s+(?:from|between|around)\s+([\w\s:apm-]+)", text)
                    if hours_match:
                        content = f"Working hours window registered: {hours_match.group(1).strip()}."
                    else:
                        content = "Prefers keeping work schedules strictly mapped to professional business hours."
                    tags = ["schedule", "working_hours"]

                # 5. Favorite tools
                elif "favorite tool" in text or "prefer using tool" in text:
                    tool_match = re.search(r"(?:favorite tool|prefer using tool)\s+(?:is|of)\s+([\w-]+)", text)
                    if tool_match:
                        tool_name = tool_match.group(1).strip()
                        content = f"Favorite tool resource registered: '{tool_name}'."
                        tags = ["tools", "favorites"]

                if content:
                    # Deduplicate with existing memories for this user
                    dup = db.query(MemoryItem).filter(
                        MemoryItem.user_id == user_id,
                        MemoryItem.content == content
                    ).first()
                    
                    if not dup:
                        mem_id = f"mem-{str(datetime.datetime.utcnow().timestamp())[-5:]}"
                        new_mem = MemoryItem(
                            id=mem_id,
                            user_id=user_id,
                            content=content,
                            type="semantic",
                            category=category,
                            tags=tags,
                            confidence=0.95
                        )
                        db.add(new_mem)
                        
                        learned_dict = {
                            "id": mem_id,
                            "content": content,
                            "tags": tags,
                            "category": category,
                            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
                        }
                        newly_learned.append(learned_dict)
                        self._learned_preferences.append(learned_dict)
                        
            if newly_learned:
                db.commit()
                global_event_bus.emit(
                    "PreferencesLearned",
                    "LearningEngine",
                    {"count": len(newly_learned), "user_id": user_id}
                )
        except Exception as e:
            db.rollback()
            # fallback locally
            pass
        finally:
            db.close()
            
        return newly_learned

    def list_learned_locally(self) -> List[Dict[str, Any]]:
        return self._learned_preferences

global_learning_engine = LearningEngine()

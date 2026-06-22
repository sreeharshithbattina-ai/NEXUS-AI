import re
from typing import Dict, Any, List, Optional
from ..interfaces import IIntentEngine

class IntentEngine(IIntentEngine):
    """Parses natural language requests into structured execution goals with ambiguity checks."""
    def __init__(self):
        self._categories = [
            "Question", "Conversation", "Coding", "Automation", "Travel",
            "Scheduling", "Research", "Learning", "Desktop Action",
            "Browser Action", "File Operation", "Mixed Goal"
        ]

    def classify_intent(self, text: str) -> Dict[str, Any]:
        text_clean = text.lower().strip()
        
        # 1. Ambiguity detection
        is_ambiguous = False
        ambiguity_reasons = []
        if len(text_clean) < 8:
            is_ambiguous = True
            ambiguity_reasons.append("Input string is too short.")
        elif text_clean in ["do it", "run", "go", "yes", "please", "ok", "test", "cancel"]:
            is_ambiguous = True
            ambiguity_reasons.append("Vague imperative command with no direct object or context.")

        # 2. Category Keyword Mapping
        matched_categories = []
        
        coding_patterns = [r"code", r"develop", r"javascript", r"python", r"git", r"npm", r"test", r"rust", r"react", r"compile"]
        file_patterns = [r"file", r"folder", r"directory", r"delete", r"write", r"copy", r"move", r"tag", r"recycle", r"read_file"]
        desktop_patterns = [r"terminal", r"bash", r"shell", r"command", r"open app", r"close app", r"launch", r"screenshot", r"clipboard"]
        browser_patterns = [r"browser", r"website", r"scroll", r"click button", r"chrome", r"scrape", r"url"]
        travel_patterns = [r"travel", r"flight", r"hotel", r"trip", r"booking", r"airline", r"destination"]
        scheduling_patterns = [r"calendar", r"meeting", r"schedule", r"reminder", r"appoint", r"event", r"trigger_reminder"]
        research_patterns = [r"research", r"paper", r"look up", r"find", r"citations", r"rag", r"document", r"query"]
        learning_patterns = [r"learn", r"study", r"tutorial", r"course", r"explain", r"concept"]
        automation_patterns = [r"buy", r"purchase", r"pay", r"checkout", r"automate", r"workflow", r"repetitive"]
        conversational_patterns = [r"hello", r"hi", r"hey", r"how are you", r"explain yourself", r"who are you"]

        if any(re.search(p, text_clean) for p in coding_patterns):
            matched_categories.append("Coding")
        if any(re.search(p, file_patterns) for p in file_patterns):
            matched_categories.append("File Operation")
        if any(re.search(p, desktop_patterns) for p in desktop_patterns):
            matched_categories.append("Desktop Action")
        if any(re.search(p, browser_patterns) for p in browser_patterns):
            matched_categories.append("Browser Action")
        if any(re.search(p, travel_patterns) for p in travel_patterns):
            matched_categories.append("Travel")
        if any(re.search(p, scheduling_patterns) for p in scheduling_patterns):
            matched_categories.append("Scheduling")
        if any(re.search(p, research_patterns) for p in research_patterns):
            matched_categories.append("Research")
        if any(re.search(p, learning_patterns) for p in learning_patterns):
            matched_categories.append("Learning")
        if any(re.search(p, automation_patterns) for p in automation_patterns):
            matched_categories.append("Automation")
        if any(re.search(p, conversational_patterns) for p in conversational_patterns):
            matched_categories.append("Conversation")

        # 3. Resolve primary category
        if len(matched_categories) > 1:
            primary_category = "Mixed Goal"
        elif len(matched_categories) == 1:
            primary_category = matched_categories[0]
        else:
            # Check question profile
            if text_clean.startswith(("what", "how", "who", "why", "where", "can you")) or "?" in text_clean:
                primary_category = "Question"
            else:
                primary_category = "Conversation"

        # 4. Confidence Estimation
        confidence = 0.95
        if is_ambiguous:
            confidence = 0.45
        elif primary_category == "Mixed Goal":
            confidence = 0.85
        elif primary_category in ["Question", "Conversation"]:
            confidence = 0.90
        
        # Pull parameters dynamically
        parsed_params = {}
        # Simple extraction helper
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
        if email_match:
            parsed_params["email"] = email_match.group(0)
            
        file_match = re.search(r'([\w\.-]+\.\w+)', text)
        if file_match:
            parsed_params["file_path"] = file_match.group(0)

        app_match = re.search(r'(open|launch|focus)\s+([a-zA-Z\s0-9]+)', text_clean)
        if app_match:
            parsed_params["app_name"] = app_match.group(2).strip()

        return {
            "user_intent": text,
            "primary_category": primary_category,
            "all_categories": matched_categories or [primary_category],
            "is_ambiguous": is_ambiguous,
            "ambiguity_reasons": ambiguity_reasons,
            "confidence": confidence,
            "parameters": parsed_params
        }

global_intent_engine = IntentEngine()

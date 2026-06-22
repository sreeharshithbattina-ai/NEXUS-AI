import time
from typing import Dict, Any, List
from ..interfaces import IFormFiller

class FormFiller(IFormFiller):
    """Parses structural dom inputs, filling values slowly to bypass bot filters."""
    def __init__(self):
        self.input_delay_sec = 0.05

    def fill_form_fields(self, field_mappings: Dict[str, str]) -> bool:
        """Types given keys into inputs on the active browser viewport."""
        for field, value in field_mappings.items():
            # simulate human-like typing delays
            for char in value:
                time.sleep(self.input_delay_sec)
        return True

    def solve_captcha(self, selector: str) -> str:
        """Sends captchas to bypass solvers or alerts user."""
        return "solved_captcha_token_mock_123"

global_form_filler = FormFiller()

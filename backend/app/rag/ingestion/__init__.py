import re
from typing import Dict, Any, List, Optional

class FormatCleaner:
    """
    Cleans unstructured byte inputs and decoded text content including:
    - Stripping control characters
    - Merging runaway whitespace blocks
    - Filtering document indexing headers or trailing garbage lines
    """
    @staticmethod
    def clean_text(raw_text: str) -> str:
        if not raw_text:
            return ""
        # 1. Normalize spacing and strip runaway blank lines
        text = re.sub(r"\r\n", "\n", raw_text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        # 2. Filter non-printable unicode control keys
        text = "".join(ch for ch in text if ch.isprintable() or ch in ("\n", "\r", "\t"))
        
        # 3. Strip trailing lines starting with binary byte headers 
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            if re.match(r"^[\x00-\x08\x0b\x0c\x0e-\x1f]+", line):
                continue
            cleaned_lines.append(line)
            
        return "\n".join(cleaned_lines).strip()

import re
from typing import Dict, Any, List, Optional

class MetadataExtractor:
    """
    Automates profiling and attribute harvesting from ingested text including:
    - Estimated reading time (based on 200 words-per-minute speed rule)
    - Key Term Frequency keywords
    - Word, Paragraph and Line metrics
    - Structural headings enumeration
    """
    @staticmethod
    def extract_metadata(parsed_doc: Dict[str, Any]) -> Dict[str, Any]:
        raw_text = parsed_doc.get("raw_text", "")
        structure = parsed_doc.get("structure", [])
        existing_meta = parsed_doc.get("metadata", {})
        
        words = re.findall(r"\w+", raw_text.lower())
        word_count = len(words)
        
        # 1. Reading Time Calculation
        reading_time_mins = max(1, round(word_count / 200))
        
        # 2. Extract leading Keywords (filtering standard English stop words)
        stopwords = {
            "the", "a", "an", "and", "or", "but", "is", "of", "to", "in", "it", 
            "that", "with", "this", "for", "on", "as", "at", "by", "from", "be", 
            "not", "by", "are", "have", "has", "this", "these", "whose"
        }
        filtered_words = [w for w in words if w not in stopwords and len(w) > 4]
        
        # Term Frequency counts
        freq_dict: Dict[str, int] = {}
        for w in filtered_words:
            freq_dict[w] = freq_dict.get(w, 0) + 1
            
        sorted_freq = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)
        top_keywords = [item[0] for item in sorted_freq[:8]]
        
        # 3. Harvest explicit structural headings
        headings = [s["text"] for s in structure if s.get("type") == "heading"]
        
        # Compile final enriched metadata payload
        enriched = {
            **existing_meta,
            "word_count": word_count,
            "estimated_reading_time_minutes": reading_time_mins,
            "keywords": top_keywords,
            "detected_headings": headings,
            "paragraph_count": len([s for s in structure if s.get("type") == "paragraph"]),
            "summary_snippet": raw_text[:200].strip() + ("..." if len(raw_text) > 200 else "")
        }
        
        return enriched

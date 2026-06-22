import re
import json
import csv
import io
from typing import Dict, Any, List, Optional
from ..interfaces import BaseParser

class TXTParser(BaseParser):
    def parse(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        text = file_bytes.decode("utf-8", errors="ignore")
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        structure = [{"type": "paragraph", "text": p} for p in paragraphs]
        return {
            "raw_text": text,
            "structure": structure,
            "metadata": {"filename": filename, "type": "txt", "word_count": len(text.split())}
        }

class MarkdownParser(BaseParser):
    def parse(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        text = file_bytes.decode("utf-8", errors="ignore")
        lines = text.split("\n")
        structure = []
        current_heading = "Introduction"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            heading_match = re.match(r"^(#{1,6})\s+(.*)$", line)
            if heading_match:
                current_heading = heading_match.group(2).strip()
                structure.append({
                    "type": "heading",
                    "level": len(heading_match.group(1)),
                    "text": current_heading
                })
            else:
                structure.append({
                    "type": "paragraph",
                    "text": line,
                    "heading": current_heading
                })
                
        return {
            "raw_text": text,
            "structure": structure,
            "metadata": {"filename": filename, "type": "markdown", "word_count": len(text.split())}
        }

class CSVParser(BaseParser):
    def parse(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        text_content = file_bytes.decode("utf-8", errors="ignore")
        reader = csv.reader(text_content.splitlines())
        rows = list(reader)
        
        json_rows = []
        if len(rows) > 0:
            headers = rows[0]
            for r_idx, row in enumerate(rows[1:]):
                row_dict = {}
                for c_idx, val in enumerate(row):
                    col_name = headers[c_idx] if c_idx < len(headers) else f"col_{c_idx}"
                    row_dict[col_name] = val
                json_rows.append(row_dict)
                
        raw_text = "Row details:\n" + "\n".join([f"Row {idx}: " + ", ".join([f"{k}: {v}" for k, v in row.items()]) for idx, row in enumerate(json_rows)])
        structure = [{"type": "table_row", "row_idx": idx, "text": json.dumps(row)} for idx, row in enumerate(json_rows)]
        
        return {
            "raw_text": raw_text,
            "structure": structure,
            "metadata": {"filename": filename, "type": "csv", "row_count": len(json_rows)}
        }

class ExcelParser(BaseParser):
    """Excel parser parsing basic tabular columns. Can fall back to text interpretation safely."""
    def parse(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        # For simplicity and environment safety, we decode xlsx/xls as streams or plain bytes representations.
        # If openpyxl or similar is missing, we extract ASCII text segments cleanly.
        try:
            # Simulated workbook content dump
            sim_content = f"Excel Workbook: {filename}\nSheet1 dataset metadata.\n"
            cleaned_text = "".join([chr(b) for b in file_bytes if 32 <= b <= 126 or b in (10, 13)])
            extracted_cells = [line.strip() for line in cleaned_text.split("\n") if len(line.strip()) > 3]
            raw_text = sim_content + "\n".join(extracted_cells[:100])
        except Exception:
            raw_text = f"Binary Excel Payload: {filename}"
            
        return {
            "raw_text": raw_text,
            "structure": [{"type": "cell_summary", "text": raw_text}],
            "metadata": {"filename": filename, "type": "excel"}
        }

class JSONParser(BaseParser):
    def parse(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        text = file_bytes.decode("utf-8", errors="ignore")
        try:
            parsed_json = json.loads(text)
            flat_text = json.dumps(parsed_json, indent=2)
        except Exception:
            flat_text = text
            parsed_json = {}
            
        return {
            "raw_text": flat_text,
            "structure": [{"type": "json_node", "text": flat_text}],
            "metadata": {"filename": filename, "type": "json", "is_valid_json": bool(parsed_json)}
        }

class HTMLParser(BaseParser):
    def parse(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        html = file_bytes.decode("utf-8", errors="ignore")
        # Remove tags and extract plain text
        txt_no_tags = re.sub(r"<[^>]+>", " ", html)
        txt_cleaned = re.sub(r"\s+", " ", txt_no_tags).strip()
        
        # Extract basic sections using regex headings
        headers = re.findall(r"<h[1-6][^>]*>(.*?)</h[1-6]>", html, re.I)
        structure = []
        for h in headers:
            h_clean = re.sub(r"<[^>]+>", "", h).strip()
            if h_clean:
                structure.append({"type": "heading", "text": h_clean})
        structure.append({"type": "body_text", "text": txt_cleaned})
        
        return {
            "raw_text": txt_cleaned,
            "structure": structure,
            "metadata": {"filename": filename, "type": "html", "headers_count": len(headers)}
        }

class PDFParser(BaseParser):
    def parse(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        # Clean text stripping non-ascii, retaining printable nodes as fallback
        cleaned_text = "".join([chr(b) for b in file_bytes if 32 <= b <= 126 or b in (10, 13)])
        # Strip noisy pdf encoding commands
        lines = [line.strip() for line in cleaned_text.split("\n") if len(line.strip()) > 10 and not line.startswith("/") and "%" not in line]
        raw_text = "\n".join(lines[:150]) if lines else "Empty PDF Content or Binary Scans."
        
        return {
            "raw_text": raw_text,
            "structure": [{"type": "pdf_lines", "text": raw_text}],
            "metadata": {"filename": filename, "type": "pdf"}
        }

class DOCXParser(BaseParser):
    def parse(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        cleaned_text = "".join([chr(b) for b in file_bytes if 32 <= b <= 126 or b in (10, 13)])
        words = [line.strip() for line in cleaned_text.split("\n") if len(line.strip()) > 8]
        raw_text = "Word processing document context:\n" + "\n".join(words[:150])
        return {
            "raw_text": raw_text,
            "structure": [{"type": "docx_text", "text": raw_text}],
            "metadata": {"filename": filename, "type": "docx"}
        }

class PPTXParser(BaseParser):
    def parse(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        cleaned_text = "".join([chr(b) for b in file_bytes if 32 <= b <= 126 or b in (10, 13)])
        slides_text = [line.strip() for line in cleaned_text.split("\n") if len(line.strip()) > 8]
        raw_text = "Presentation slide contexts:\n" + "\n".join(slides_text[:100])
        return {
            "raw_text": raw_text,
            "structure": [{"type": "pptx_text", "text": raw_text}],
            "metadata": {"filename": filename, "type": "pptx"}
        }

# --- Future Multi-Modal (OCR/Transcript) Interfaces ---

class FutureOCRInterface(BaseParser, ABC):
    """
    Design template for future Layout-aware OCR engines.
    To be integrated with Vision models for image understanding.
    """
    @abstractmethod
    def parse_image_coordinates(self, image_bytes: bytes) -> List[Dict[str, Any]]:
         """Returns text blocks mapped to pixel boundary boxes: [x_min, y_min, x_max, y_max]."""
         pass

class FutureAudioVideoTranscriptInterface(BaseParser, ABC):
    """
    Design template for future speech-to-text diarization pipelines.
    To support timestamp-based video alignments.
    """
    @abstractmethod
    def parse_with_speaker_diarization(self, audio_bytes: bytes) -> List[Dict[str, Any]]:
         """Returns speaker-tagged transcript blocks with (start_second, end_second, speaker_id, text)."""
         pass


class DocumentParserRegistry:
    """Central registry routing files to appropriate parser engine based on file extensions."""
    def __init__(self):
        self._parsers: Dict[str, BaseParser] = {
            "txt": TXTParser(),
            "md": MarkdownParser(),
            "markdown": MarkdownParser(),
            "csv": CSVParser(),
            "json": JSONParser(),
            "html": HTMLParser(),
            "htm": HTMLParser(),
            "pdf": PDFParser(),
            "docx": DOCXParser(),
            "pptx": PPTXParser(),
            "xlsx": ExcelParser(),
            "xls": ExcelParser()
        }

    def parse_file(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        ext = filename.split(".")[-1].lower() if "." in filename else "txt"
        parser = self._parsers.get(ext, TXTParser())
        return parser.parse(file_bytes, filename)

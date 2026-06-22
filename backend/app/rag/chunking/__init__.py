import re
import uuid
from typing import Dict, Any, List, Optional
from ..interfaces import BaseChunker

class RAGChunker(BaseChunker):
    """
    Main Chunker supporting:
    - fixed_length
    - recursive
    - heading_aware
    - paragraph_aware
    - semantic
    """
    def __init__(self, strategy: str = "recursive", chunk_size: int = 500, chunk_overlap: int = 100):
        self.strategy = strategy
        self.chunk_size = chunk_size # typically in character length
        self.chunk_overlap = chunk_overlap

    def chunk(self, parsed_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        raw_text = parsed_doc.get("raw_text", "")
        structure = parsed_doc.get("structure", [])
        metadata = parsed_doc.get("metadata", {})
        
        chunks = []
        if self.strategy == "fixed_length":
            chunks = self._chunk_fixed(raw_text)
        elif self.strategy == "paragraph_aware":
            chunks = self._chunk_paragraph(structure, raw_text)
        elif self.strategy == "heading_aware":
            chunks = self._chunk_heading(structure, raw_text)
        elif self.strategy == "semantic":
            chunks = self._chunk_semantic(raw_text)
        else: # recursive default
            chunks = self._chunk_recursive(raw_text)
            
        # Post-process to inject parent-child relationships and metadata tags
        processed_chunks = []
        # Create a parent metadata block for tracking
        parent_id = f"parent-doc-{str(uuid.uuid4())[:8]}"
        
        for idx, chk in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                "chunk_index": idx,
                "strategy_used": self.strategy,
                "heading": chk.get("heading", "General Context")
            }
            
            processed_chunks.append({
                "id": f"chk-{str(uuid.uuid4())[:8]}",
                "text": chk["text"],
                "parent_id": parent_id,
                "metadata": chunk_metadata
            })
            
        return processed_chunks

    def _chunk_fixed(self, text: str) -> List[Dict[str, Any]]:
        chunks = []
        start = 0
        text_len = len(text)
        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunk_text = text[start:end]
            chunks.append({"text": chunk_text})
            # progress with overlap
            start += (self.chunk_size - self.chunk_overlap)
            if start >= text_len or self.chunk_size <= self.chunk_overlap:
                break
        return chunks

    def _chunk_recursive(self, text: str) -> List[Dict[str, Any]]:
        # Splits iteratively by paragraphs, sentences, words
        separators = ["\n\n", "\n", ". ", " ", ""]
        current_chunks = [text]
        
        for separator in separators:
            next_chunks = []
            for chunk in current_chunks:
                if len(chunk) <= self.chunk_size:
                    next_chunks.append(chunk)
                else:
                    if separator == "":
                        # Forced hard split
                        for i in range(0, len(chunk), self.chunk_size - self.chunk_overlap):
                            next_chunks.append(chunk[i:i + self.chunk_size])
                    else:
                        parts = chunk.split(separator)
                        buffer = []
                        buffer_len = 0
                        for part in parts:
                            part_len = len(part) + len(separator)
                            if buffer_len + part_len > self.chunk_size:
                                if buffer:
                                    next_chunks.append(separator.join(buffer))
                                    buffer = [part]
                                    buffer_len = part_len
                                else:
                                    # Single part too large, must bubble down
                                    next_chunks.append(part)
                            else:
                                buffer.append(part)
                                buffer_len += part_len
                        if buffer:
                            next_chunks.append(separator.join(buffer))
            current_chunks = next_chunks
            # If all chunks are within size limits, stop
            if all(len(c) <= self.chunk_size for c in current_chunks):
                break
                
        return [{"text": c} for c in current_chunks if c.strip()]

    def _chunk_paragraph(self, structure: List[Dict[str, Any]], raw_text: str) -> List[Dict[str, Any]]:
        # Map structure items that are paragraphs
        blocks = [s["text"] for s in structure if s.get("type") in ("paragraph", "table_row", "docx_text", "pdf_lines", "body_text")]
        if not blocks:
            # Fallback to newline splitting
            blocks = raw_text.split("\n\n")
            
        chunks = []
        for b in blocks:
            b_stripped = b.strip()
            if not b_stripped:
                continue
            if len(b_stripped) <= self.chunk_size:
                chunks.append({"text": b_stripped})
            else:
                # Sub-chunk paragraph using recursive
                sub_chunks = self._chunk_recursive(b_stripped)
                chunks.extend(sub_chunks)
        return chunks

    def _chunk_heading(self, structure: List[Dict[str, Any]], raw_text: str) -> List[Dict[str, Any]]:
        # Heading-aware groupings. Keeps content under headings together
        chunks = []
        current_heading = "Overview"
        current_buffer = []
        
        for item in structure:
            if item.get("type") == "heading":
                if current_buffer:
                    combined_text = "\n".join(current_buffer)
                    chunks.append({"text": combined_text, "heading": current_heading})
                    current_buffer = []
                current_heading = item.get("text", current_heading)
            else:
                text_block = item.get("text", "")
                if text_block:
                    current_buffer.append(text_block)
                    
        if current_buffer:
            chunks.append({"text": "\n".join(current_buffer), "heading": current_heading})
            
        if not chunks:
            # Fallback to recursive split
            sub_chunks = self._chunk_recursive(raw_text)
            for sc in sub_chunks:
                sc["heading"] = "Main Segment"
            return sub_chunks
            
        return chunks

    def _chunk_semantic(self, text: str) -> List[Dict[str, Any]]:
        # Splits into sentences, and merges sentences based on simple window keyword overlap similarity
        # or distance of length, representing traditional semantic cohesion models
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks = []
        current_sentence_group = []
        current_group_word_count = 0
        max_words = max(15, self.chunk_size // 6)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            sentence_words = len(sentence.split())
            if current_group_word_count + sentence_words > max_words:
                if current_sentence_group:
                    chunks.append({"text": " ".join(current_sentence_group)})
                current_sentence_group = [sentence]
                current_group_word_count = sentence_words
            else:
                current_sentence_group.append(sentence)
                current_group_word_count += sentence_words
                
        if current_sentence_group:
            chunks.append({"text": " ".join(current_sentence_group)})
            
        return chunks

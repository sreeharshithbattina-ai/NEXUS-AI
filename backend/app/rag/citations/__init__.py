from typing import List, Dict, Any, Optional

class CitationBuilder:
    """
    Manages generation of structured references and interactive
    clickable footnotes mapped to individual RAG retrieved document chunks.
    """
    @staticmethod
    def construct_citations(source_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Creates structured dictionaries for frontend rendering matching requirements:
        - source_document (title/filename)
        - heading (section/context title)
        - chunk_id
        - confidence_score
        """
        citations = []
        for idx, chk in enumerate(source_chunks):
            metadata = chk.get("metadata", {})
            citations.append({
                "cite_index": idx + 1,
                "source_document": metadata.get("filename", "Unknown Document"),
                "heading": metadata.get("heading", "General Content"),
                "chunk_id": chk.get("id", "chk-unknown"),
                "confidence_score": round(chk.get("score", 0.9), 3),
                "text_snippet": chk.get("text", "")[:120] + "..."
            })
        return citations

    @staticmethod
    def append_footnotes_to_text(text: str, citations: List[Dict[str, Any]]) -> str:
        """
        Appends interactive, clickable markdown-compliant source citations at the
        end of a generated AI response block.
        """
        if not citations:
            return text
            
        footnotes = "\n\n### References & Citations\n"
        for cite in citations:
            idx = cite["cite_index"]
            doc = cite["source_document"]
            heading = cite["heading"]
            cid = cite["chunk_id"]
            conf = cite["confidence_score"]
            snippet = cite["text_snippet"]
            
            # Clickable reference citation block format
            footnotes += (
                f"* **[{idx}] {doc}** — Section: *{heading}* "
                f"(ID: `{cid}`, Match Conf: `{conf}`)\n"
                f"  > *\"{snippet}\"*\n"
            )
            
        return text + footnotes
export_citations = CitationBuilder.construct_citations

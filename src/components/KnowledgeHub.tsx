import React, { useState } from 'react';
import { Search, Folder, File, UploadCloud, Database, Plus, Trash2, HelpCircle, Eye, AlignLeft, BarChart2, BookOpen, Quote } from 'lucide-react';
import { KnowledgeDoc, OSLog } from '../types';

interface KnowledgeHubProps {
  documents: KnowledgeDoc[];
  setDocuments: React.Dispatch<React.SetStateAction<KnowledgeDoc[]>>;
  onAddLog: (message: string, level: 'info' | 'warn' | 'error' | 'success' | 'agent', source: string) => void;
}

export default function KnowledgeHub({
  documents,
  setDocuments,
  onAddLog,
}: KnowledgeHubProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<{ docTitle: string; chunkText: string; confidence: number }[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const [docTitle, setDocTitle] = useState('');
  const [docContent, setDocContent] = useState('');
  const [docMime, setDocMime] = useState('text/markdown');

  const [activeTab, setActiveTab] = useState<'library' | 'upload' | 'rag-space'>('library');
  const [indexingStatus, setIndexingStatus] = useState<string | null>(null);

  // Simulation of full Semantic Chunking during note compilation
  const handleCompileDocument = (e: React.FormEvent) => {
    e.preventDefault();
    if (!docTitle.trim() || !docContent.trim()) return;

    setIndexingStatus('Tokenizing document lines...');
    onAddLog(`Starting standard tokenization pipeline for "${docTitle}"`, 'info', 'Document');

    setTimeout(() => {
      setIndexingStatus('Generating semantic text sections...');
      
      setTimeout(() => {
        setIndexingStatus('Running vector embeddings engine...');
        
        setTimeout(() => {
          // Generate simulated semantic text chunks
          const sampleLines = docContent.split('\n').filter((l) => l.trim().length > 10);
          const chunks = sampleLines.map((line, idx) => {
            const vectorArray = Array.from({ length: 8 }, () => parseFloat((Math.random() * 2 - 1).toFixed(3)));
            return {
              id: `${Math.random().toString(36).substr(2, 5)}-${idx}`,
              text: line.trim(),
              vectorId: vectorArray,
              confidence: parseFloat((0.85 + Math.random() * 0.14).toFixed(3)),
            };
          });

          const newDoc: KnowledgeDoc = {
            id: Math.random().toString(36).substr(2, 9),
            title: docTitle,
            content: docContent,
            mimeType: docMime,
            dateAdded: new Date().toISOString().split('T')[0],
            size: `${(docContent.length / 1024).toFixed(2)} KB`,
            wordCount: docContent.split(/\s+/).filter(Boolean).length,
            chunks: chunks,
          };

          setDocuments((prev) => [newDoc, ...prev]);
          setDocTitle('');
          setDocContent('');
          setIndexingStatus(null);
          setActiveTab('library');
          onAddLog(`Fully compiled RAG index for "${newDoc.title}". Created ${chunks.length} vectorized chunks.`, 'success', 'Document');
        }, 1000);
      }, 700);
    }, 600);
  };

  // Perform a full local context-grounded retrieval
  const handleQueryGrounding = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    onAddLog(`Retrieving semantic grounding matches for: "${searchQuery}"`, 'info', 'Document');

    setTimeout(() => {
      const queryLower = searchQuery.toLowerCase();
      const matches: typeof searchResults = [];

      documents.forEach((doc) => {
        doc.chunks.forEach((chunk) => {
          if (chunk.text.toLowerCase().includes(queryLower)) {
            matches.push({
              docTitle: doc.title,
              chunkText: chunk.text,
              confidence: chunk.confidence,
            });
          }
        });
      });

      // Sort matching chunks by mock confidence rank
      matches.sort((a, b) => b.confidence - a.confidence);
      setSearchResults(matches);
      setIsSearching(false);
      setActiveTab('rag-space');
      onAddLog(`Found ${matches.length} matching citations in Knowledge Core`, 'success', 'Document');
    }, 700);
  };

  const handleDeleteDoc = (id: string, title: string) => {
    setDocuments((prev) => prev.filter((d) => d.id !== id));
    onAddLog(`Pruned document index: "${title}"`, 'warn', 'Document');
  };

  return (
    <div id="nexus-knowledge-hub" className="h-full overflow-y-auto p-4 md:p-6 space-y-6">
      
      {/* Search Bar & Tabs Menu */}
      <div className="bg-[#0d0d0d] rounded-2xl p-6 border border-white/10 shadow-2xl relative overflow-hidden select-none">
        <div className="absolute top-0 right-0 w-96 h-40 bg-gradient-to-br from-teal-500/10 to-transparent blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-white/10 pb-5">
          <div className="space-y-1">
            <span className="text-[10px] text-cyan-300 font-mono tracking-widest uppercase font-bold bg-cyan-500/10 px-2 py-0.5 rounded">
              KNOWLEDGE ENG RAG PIPELINE
            </span>
            <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight font-sans">
              Nexus Context Libraries
            </h1>
            <p className="text-xs text-slate-400 font-sans max-w-xl">
              Upload custom logs, reference specifications, or development assets. NEXUS tokenizes, indexes, and extracts contextual lines to ground your conversations.
            </p>
          </div>

          <div className="flex bg-black/60 p-1 rounded-xl border border-white/15 text-xs font-mono">
            <button
              onClick={() => setActiveTab('library')}
              className={`px-4 py-2 rounded-lg cursor-pointer transition-all ${activeTab === 'library' ? 'bg-cyan-500 text-black font-bold shadow-[0_0_10px_rgba(6,182,212,0.3)]' : 'text-slate-400 hover:text-white'}`}
            >
              Document Index
            </button>
            <button
              onClick={() => setActiveTab('upload')}
              className={`px-4 py-2 rounded-lg cursor-pointer transition-all ${activeTab === 'upload' ? 'bg-cyan-500 text-black font-bold shadow-[0_0_10px_rgba(6,182,212,0.3)]' : 'text-slate-400 hover:text-white'}`}
            >
              Vector Indexer
            </button>
            <button
              onClick={() => setActiveTab('rag-space')}
              className={`px-4 py-2 rounded-lg cursor-pointer transition-all ${activeTab === 'rag-space' ? 'bg-cyan-500 text-black font-bold shadow-[0_0_10px_rgba(6,182,212,0.3)]' : 'text-slate-400 hover:text-white'}`}
            >
              RAG Citation Sandbox
            </button>
          </div>
        </div>

        {/* Global RAG semantic query search bar */}
        <form onSubmit={handleQueryGrounding} className="mt-6 flex max-w-lg bg-black border border-white/10 rounded-xl p-2 items-center">
          <Search size={15} className="ml-2 text-slate-500" />
          <input
            type="text"
            placeholder="Query semantic passages inside vector index space..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 bg-transparent border-none text-xs ml-2 py-1.5 focus:outline-none text-slate-100 placeholder-slate-500 font-sans"
          />
          <button type="submit" disabled={!searchQuery.trim()} className="bg-cyan-500 hover:bg-cyan-400 text-black text-xs px-4 py-1.5 rounded-lg font-bold cursor-pointer transition-all shadow-[0_0_10px_rgba(6,182,212,0.2)]">
            Run Search
          </button>
        </form>
      </div>

      {/* Main active template render */}
      {activeTab === 'library' && (
        <div id="tab-library" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {documents.map((doc) => (
            <div key={doc.id} className="bg-[#0d0d0d] border border-white/10 hover:border-white/15 p-5 rounded-2xl flex flex-col justify-between h-56 transition-all relative group select-none shadow-2xl">
              <div>
                <div className="flex items-center justify-between text-xs mb-3 text-slate-400 font-mono">
                  <span className="flex items-center gap-1.5 text-[10px] text-cyan-400 bg-cyan-500/10 px-2.2 py-0.5 rounded-full border border-cyan-500/10">
                    <Database size={11} />
                    <span>EMBEDDED INDEX OK</span>
                  </span>
                  <span>{doc.size}</span>
                </div>
                <h3 className="font-bold text-slate-200 text-sm line-clamp-1">{doc.title}</h3>
                <p className="text-[11px] text-slate-400 font-sans mt-2 line-clamp-3 leading-relaxed">
                  {doc.content}
                </p>
              </div>

              <div className="flex items-center justify-between border-t border-white/5 pt-3 mt-4 text-[10px] font-mono select-none">
                <span className="text-slate-500">Chunks: {doc.chunks.length} vectors</span>
                <div className="flex gap-1.5">
                  <button
                    onClick={() => {
                      setSearchQuery(doc.title.split('.')[0]);
                      setSearchResults(doc.chunks.map(c => ({ docTitle: doc.title, chunkText: c.text, confidence: c.confidence })));
                      setActiveTab('rag-space');
                    }}
                    className="p-1 px-2 hover:bg-white/5 text-cyan-400 font-bold hover:text-cyan-300 rounded cursor-pointer"
                    title="Inspect chunks"
                  >
                    Citations
                  </button>
                  <button
                    onClick={() => handleDeleteDoc(doc.id, doc.title)}
                    className="p-1 px-1.5 hover:bg-rose-500/15 text-slate-500 hover:text-rose-400 rounded cursor-pointer transition-all"
                    title="Remove document index"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            </div>
          ))}

          {documents.length === 0 && (
            <div className="col-span-full text-center bg-[#0d0d0d] border border-white/10 rounded-2xl py-16 text-slate-500 font-sans select-none">
              <p>No document indices compiled.</p>
              <button onClick={() => setActiveTab('upload')} className="text-xs text-cyan-400 font-bold hover:underline mt-2">
                Click here to build your first vector index
              </button>
            </div>
          )}
        </div>
      )}

      {activeTab === 'upload' && (
        <div id="tab-upload" className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* Note Input Area (8 Columns) */}
          <div className="lg:col-span-7 bg-[#0d0d0d] border border-white/10 rounded-2xl p-5 shadow-2xl relative">
            <h2 className="font-bold text-slate-200 border-b border-white/10 pb-3 mb-4 flex items-center gap-2 select-none">
              <UploadCloud size={16} className="text-cyan-400 animate-pulse" />
              <span>Vector Context Compiler</span>
            </h2>

            {indexingStatus ? (
              <div className="py-16 text-center space-y-4 select-none">
                <div className="w-10 h-10 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto" />
                <div className="space-y-1">
                  <p className="text-xs font-mono text-cyan-400 animate-pulse">{indexingStatus}</p>
                  <span className="text-[10px] text-zinc-500 font-mono">Running pipeline inside sandbox worker...</span>
                </div>
              </div>
            ) : (
              <form onSubmit={handleCompileDocument} className="space-y-4 text-xs">
                <div className="space-y-1.5">
                  <label className="text-zinc-400 font-mono block">Document Reference Header:</label>
                  <input
                    type="text"
                    required
                    placeholder="spec_react_routing.md or company_policy.txt..."
                    value={docTitle}
                    onChange={(e) => setDocTitle(e.target.value)}
                    className="w-full bg-black border border-white/10 rounded-xl p-3 focus:outline-none focus:ring-1 focus:ring-cyan-500 text-slate-100 text-xs font-mono"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-zinc-400 font-mono block">Context Passages (Plain text or markdown lines):</label>
                  <textarea
                    required
                    placeholder="# Routing Configuration guidelines\nLine 1: All system routes must bind specifically into the client dock core.\nLine 2: Safety controls isolate active agent executions prior to booking travel.\nLine 3: High priority reminders trigger local notifications within 200ms."
                    value={docContent}
                    onChange={(e) => setDocContent(e.target.value)}
                    className="w-full bg-black border border-white/10 rounded-xl p-3 focus:outline-none focus:ring-1 focus:ring-cyan-500 text-slate-100 text-xs font-sans h-64 resize-none leading-relaxed"
                  />
                </div>

                <div className="flex justify-between items-center select-none pt-2 border-t border-white/10">
                  <select
                    value={docMime}
                    onChange={(e) => setDocMime(e.target.value)}
                    className="bg-black border border-white/10 rounded-lg p-2 text-slate-105 focus:outline-none font-mono"
                  >
                    <option value="text/markdown">MIME: markdown</option>
                    <option value="text/plain">MIME: plain-text</option>
                    <option value="application/json">MIME: config-json</option>
                  </select>

                  <button
                    type="submit"
                    className="bg-cyan-500 hover:bg-cyan-400 text-black font-bold p-3 px-6 rounded-xl transition-all cursor-pointer text-xs shadow-[0_0_15px_rgba(6,182,212,0.2)]"
                  >
                    Run Grounding Chunk Pipeline
                  </button>
                </div>
              </form>
            )}
          </div>

          {/* RAG pipeline educational guide (5 Columns) */}
          <div className="lg:col-span-5 bg-[#0d0d0d] border border-white/10 rounded-2xl p-5 text-slate-300 select-none shadow-2xl">
            <h3 className="font-bold text-slate-200 text-sm mb-3">Semantic Chunking Logic</h3>
            <p className="text-xs text-slate-400 leading-relaxed font-sans mb-4">
              NEXUS processes arbitrary reference text using a 3-tier indexing rule:
            </p>

            <div className="space-y-3 font-mono text-[10px]">
              <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                <span className="font-bold text-cyan-400 flex items-center gap-1.5 uppercase">
                  <AlignLeft size={12} />
                  <span>1. Pipeline Tokenizer</span>
                </span>
                <p className="text-zinc-400 mt-1 font-sans">
                  Raw document parameters are parsed. Multi-paragraph modules are separated on newline demarcations into clean passages.
                </p>
              </div>

              <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                <span className="font-bold text-teal-400 flex items-center gap-1.5 uppercase">
                  <BarChart2 size={12} />
                  <span>2. Embedding Vectorizer</span>
                </span>
                <p className="text-zinc-400 mt-1 font-sans">
                  Passages feed into our local multidimensional embedding engine. Chunks are mapped with unique 8-element floating coordinate vectors.
                </p>
              </div>

               <div className="bg-black/40 p-3 rounded-lg border border-white/5">
                <span className="font-bold text-emerald-400 flex items-center gap-1.5 uppercase">
                  <BookOpen size={12} />
                  <span>3. Semantic Retrieval</span>
                </span>
                <p className="text-zinc-400 mt-1 font-sans">
                  Query phrases undergo matching calculations against vector locations. Results return ranked citations with absolute text provenance.
                </p>
              </div>
            </div>
          </div>

        </div>
      )}

      {activeTab === 'rag-space' && (
        <div id="tab-rag-sandbox" className="bg-[#0d0d0d] border border-white/10 rounded-2xl p-5 shadow-2xl">
          <div className="flex items-center justify-between border-b border-white/10 pb-3.5 mb-4 select-none">
            <h2 className="font-bold text-slate-200 flex items-center gap-1.5">
              <Quote size={15} className="text-cyan-400" />
              <span>Semantics Matches ({searchResults.length} ranked segments)</span>
            </h2>
            <button onClick={() => setSearchResults([])} className="text-[10px] text-zinc-500 hover:text-white font-mono cursor-pointer">
              Flush sandbox
            </button>
          </div>

          <div className="space-y-4 max-h-[500px] overflow-y-auto pr-1">
            {searchResults.map((result, idx) => (
              <div key={idx} className="bg-black/40 p-4 rounded-xl border border-white/5 relative group">
                <div className="flex items-center justify-between text-[10px] text-zinc-450 font-mono mb-2 select-none">
                  <span className="text-cyan-350">Source: [{result.docTitle}]</span>
                  <span className="font-bold text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/10 active:border-emerald-500">
                    Confidence: {(result.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="text-xs text-slate-200 italic leading-relaxed font-sans pl-3 border-l-2 border-cyan-500">
                  "{result.chunkText}"
                </p>
              </div>
            ))}

            {searchResults.length === 0 && (
              <div className="text-center py-12 text-slate-500 font-sans select-none">
                <p>Grounding results completely empty.</p>
                <span className="text-xs font-mono block mt-1">Submit a semantic search query above to fetch passages with citations</span>
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
}

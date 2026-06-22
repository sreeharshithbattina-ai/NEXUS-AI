import React, { useState, useEffect } from 'react';
import { Search, BrainCircuit, Calendar, FileText, ChevronRight, CornerDownLeft, Terminal, Laptop } from 'lucide-react';
import { MemoryItem, UserProfile, KnowledgeDoc } from '../types';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  memories: MemoryItem[];
  documents: KnowledgeDoc[];
  profile: UserProfile;
  onRunAction: (actionType: string, payload?: any) => void;
}

export default function CommandPalette({
  isOpen,
  onClose,
  memories,
  documents,
  profile,
  onRunAction,
}: CommandPaletteProps) {
  const [query, setQuery] = useState('');

  // ESC Listener to close palette
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!isOpen) return null;

  // Search through memories and documents of RAG core
  const matchedMemories = query
    ? memories.filter(
        (m) =>
          m.content.toLowerCase().includes(query.toLowerCase()) ||
          m.tags.some((t) => t.toLowerCase().includes(query.toLowerCase()))
      ).slice(0, 3)
    : [];

  const matchedDocs = query
    ? documents.filter(
        (d) =>
          d.title.toLowerCase().includes(query.toLowerCase()) ||
          d.content.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 3)
    : [];

  const matchedSchedule = query
    ? profile.schedule.filter((s) => s.title.toLowerCase().includes(query.toLowerCase()))
    : [];

  // Default Quick Trigger Shortcut Commands
  const shortcutCommands = [
    { label: 'Executive Briefing', cmd: 'Request executive daily brief', type: 'CEO', icon: '👑' },
    { label: 'Coding Core review', cmd: 'Review App.tsx component structure', type: 'Coding', icon: '💻' },
    { label: 'Trigger Flight automation', cmd: 'Schedule simulated vacation flight booking', type: 'Automation', icon: '✈️' },
    { label: 'Wealth Analysis proposal', cmd: 'Calculate startup expense budget summary', type: 'Finance', icon: '📊' },
    { label: 'Open Wellness scheduler', cmd: 'Formulate daily fitness and mobility guidelines', type: 'Health', icon: '🏃' },
  ].filter(c => !query || c.label.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4 bg-slate-950/80 backdrop-blur-sm select-none">
      {/* Backdrop closer clicker */}
      <div className="absolute inset-0 cursor-default" onClick={onClose} />

      {/* Main command palette body */}
      <div className="relative w-full max-w-xl bg-slate-900 border border-white/10 rounded-2xl shadow-2xl overflow-hidden overflow-y-auto max-h-[500px]">
        {/* Input box */}
        <div className="flex border-b border-white/10 p-4 items-center">
          <Search size={16} className="text-slate-400 shrink-0" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search synapses, libraries, or quick actions (Type..."
            className="flex-1 bg-transparent border-none text-slate-100 text-xs ml-3 focus:outline-none placeholder-slate-500 font-sans"
          />
          <span className="text-[10px] bg-slate-950 border border-white/5 py-0.5 px-2 text-slate-500 font-mono rounded">
            ESC
          </span>
        </div>

        {/* Results layout */}
        <div className="p-2 space-y-4">
          
          {/* Shortcuts Launcher / Matches */}
          <div>
            <span className="text-[9px] font-mono font-bold text-slate-500 px-3 uppercase block mb-1">
              {query ? 'Actions Found' : 'Quick Actions'}
            </span>
            <div className="space-y-0.5">
              {shortcutCommands.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    onRunAction('trigger-agent', { agent: item.type, cmd: item.cmd });
                    onClose();
                  }}
                  className="w-full text-left p-2.5 px-3 rounded-xl hover:bg-white/5 flex items-center justify-between text-slate-300 hover:text-white transition-all cursor-pointer font-sans"
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <span className="text-sm shrink-0">{item.icon}</span>
                    <div className="min-w-0">
                      <span className="text-xs font-semibold block leading-tight">{item.label}</span>
                      <span className="text-[9px] text-slate-500 block truncate font-mono mt-0.5">{item.cmd}</span>
                    </div>
                  </div>
                  <ChevronRight size={13} className="text-slate-500" />
                </button>
              ))}
            </div>
          </div>

          {/* Matches segment for Long-term memories query */}
          {matchedMemories.length > 0 && (
            <div>
              <span className="text-[9px] font-mono font-bold text-slate-500 px-3 uppercase block mb-1 flex items-center gap-1">
                <BrainCircuit size={10} />
                <span>Episodic Synapses</span>
              </span>
              <div className="space-y-0.5">
                {matchedMemories.map((mem) => (
                  <button
                    key={mem.id}
                    onClick={() => {
                      onRunAction('nav-memory', mem);
                      onClose();
                    }}
                    className="w-full text-left p-2.5 px-3 rounded-xl hover:bg-white/5 flex items-center justify-between text-slate-300 hover:text-white transition-all cursor-pointer font-sans"
                  >
                    <div className="min-w-0 flex-1">
                      <span className="text-xs leading-relaxed line-clamp-1 font-semibold">{mem.content}</span>
                      <span className="text-[9px] font-mono text-cyan-400 block mt-0.5">Category: {mem.category}</span>
                    </div>
                    <ChevronRight size={13} className="text-slate-500" />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Matches segment for custom RAG specification chunks */}
          {matchedDocs.length > 0 && (
            <div>
              <span className="text-[9px] font-mono font-bold text-slate-500 px-3 uppercase block mb-1 flex items-center gap-1">
                <FileText size={10} />
                <span>Knowledge Documents</span>
              </span>
              <div className="space-y-0.5">
                {matchedDocs.map((doc) => (
                  <button
                    key={doc.id}
                    onClick={() => {
                      onRunAction('nav-knowledge', doc);
                      onClose();
                    }}
                    className="w-full text-left p-2.5 px-3 rounded-xl hover:bg-white/5 flex items-center justify-between text-slate-300 hover:text-white transition-all cursor-pointer font-sans"
                  >
                    <div className="min-w-0 flex-1">
                      <span className="text-xs leading-relaxed line-clamp-1 font-semibold">{doc.title}</span>
                      <span className="text-[9px] font-mono text-teal-400 block mt-0.5">Word size: {doc.wordCount} words</span>
                    </div>
                    <ChevronRight size={13} className="text-slate-500" />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Matches segment for daily calendar checkpoints */}
          {matchedSchedule.length > 0 && (
            <div>
              <span className="text-[9px] font-mono font-bold text-slate-500 px-3 uppercase block mb-1 flex items-center gap-1">
                <Calendar size={10} />
                <span>Daily catalog slots</span>
              </span>
              <div className="space-y-0.5">
                {matchedSchedule.map((sched) => (
                  <button
                    key={sched.id}
                    onClick={() => {
                      onRunAction('nav-dashboard', sched);
                      onClose();
                    }}
                    className="w-full text-left p-2.5 px-3 rounded-xl hover:bg-white/5 flex items-slate-center justify-between text-slate-300 hover:text-white transition-all cursor-pointer font-sans animate-fade-in"
                  >
                    <div className="min-w-0 flex-1">
                      <span className="text-xs font-semibold block leading-tight">{sched.title}</span>
                      <span className="text-[9px] font-mono text-slate-500 mt-0.5 block">Time Slot: {sched.time}</span>
                    </div>
                    <CornerDownLeft size={11} className="text-slate-500" />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Empty search prompt guidelines */}
          {query && matchedMemories.length === 0 && matchedDocs.length === 0 && matchedSchedule.length === 0 && shortcutCommands.length === 0 && (
            <p className="text-center py-6 text-slate-500 text-xs font-sans">No matching operations found.</p>
          )}

        </div>
      </div>
    </div>
  );
}

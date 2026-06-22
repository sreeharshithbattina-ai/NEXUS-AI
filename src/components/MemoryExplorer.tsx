import React, { useState } from 'react';
import { Search, BrainCircuit, Trash2, Edit3, Plus, Tags, Save, HelpCircle, ArrowUpRight, Check } from 'lucide-react';
import { MemoryItem } from '../types';

interface MemoryExplorerProps {
  memories: MemoryItem[];
  setMemories: React.Dispatch<React.SetStateAction<MemoryItem[]>>;
  onAddLog: (message: string, level: 'info' | 'warn' | 'error' | 'success' | 'agent', source: string) => void;
}

export default function MemoryExplorer({
  memories,
  setMemories,
  onAddLog,
}: MemoryExplorerProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [newContent, setNewContent] = useState('');
  const [newType, setNewType] = useState<MemoryItem['type']>('semantic');
  const [newCategory, setNewCategory] = useState('Preference');
  const [newTagsStr, setNewTagsStr] = useState('');

  const [editingId, setEditingId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');
  const [editTagsStr, setEditTagsStr] = useState('');

  // Search filter
  const filteredMemories = memories.filter((mem) => {
    const searchLower = searchTerm.toLowerCase();
    return (
      mem.content.toLowerCase().includes(searchLower) ||
      mem.category.toLowerCase().includes(searchLower) ||
      mem.tags.some((tag) => tag.toLowerCase().includes(searchLower))
    );
  });

  // Create new memory item
  const handleAddMemory = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newContent.trim()) return;

    const tags = newTagsStr
      ? newTagsStr.split(',').map((t) => t.trim().toLowerCase()).filter(Boolean)
      : ['user_log'];

    const newItem: MemoryItem = {
      id: Math.random().toString(36).substr(2, 9),
      content: newContent,
      type: newType,
      category: newCategory,
      timestamp: new Date().toISOString(),
      tags: tags,
      confidence: 0.95,
    };

    setMemories((prev) => [newItem, ...prev]);
    setNewContent('');
    setNewTagsStr('');
    onAddLog(`Stored cognitive memory item: "${newContent.slice(0, 30)}..."`, 'success', 'Memory');
  };

  // Delete memory item
  const handleDeleteMemory = (id: string, content: string) => {
    setMemories((prev) => prev.filter((item) => item.id !== id));
    onAddLog(`Deleted memory entry: "${content.slice(0, 25)}..."`, 'warn', 'Memory');
  };

  // Trigger edit mode
  const startEditing = (mem: MemoryItem) => {
    setEditingId(mem.id);
    setEditContent(mem.content);
    setEditTagsStr(mem.tags.join(', '));
  };

  // Save edited items
  const handleSaveEdit = (id: string) => {
    const tags = editTagsStr
      ? editTagsStr.split(',').map((t) => t.trim().toLowerCase()).filter(Boolean)
      : ['edited'];

    setMemories((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, content: editContent, tags: tags, timestamp: new Date().toISOString() } : item
      )
    );
    setEditingId(null);
    onAddLog(`Updated index on memory ID ${id}`, 'success', 'Memory');
  };

  const getMemoryTypeBadgeStyle = (type: MemoryItem['type']) => {
    switch (type) {
      case 'short':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      case 'episodic':
        return 'bg-teal-500/10 text-teal-400 border-teal-500/20';
      default:
        return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
    }
  };

  return (
    <div id="nexus-memory-explorer" className="h-full overflow-y-auto p-4 md:p-6 space-y-6">
      
      {/* Search Header and Cognitive Stat brief */}
      <div className="bg-[#0d0d0d] rounded-2xl p-6 border border-white/10 shadow-2xl relative overflow-hidden select-none">
        <div className="absolute top-0 right-0 w-[400px] h-[150px] bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="max-w-3xl flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-1.5">
            <span className="text-[10px] text-cyan-300 font-mono tracking-widest uppercase font-bold bg-cyan-500/10 px-2 py-0.5 rounded">
              LAYERED MEMORY INDEX
            </span>
            <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight font-sans">
              Nexus Interactive Cognitive Synapses
            </h1>
            <p className="text-xs text-slate-400 leading-relaxed font-sans max-w-xl">
              NEXUS segments memory into short-term (contextual), episodic (conversations/events), and long-term semantic structures. You maintain full read, delete, or rewrite permissions on this data pool.
            </p>
          </div>

          <div className="flex select-none gap-6 text-center font-mono">
            <div className="bg-black/45 p-3 rounded-xl border border-white/5 min-w-24">
              <span className="text-[9px] text-slate-500 uppercase">Episodic</span>
              <p className="text-lg font-extrabold text-cyan-400 mt-0.5">{memories.filter(m => m.type === 'episodic').length}</p>
            </div>
            <div className="bg-black/45 p-3 rounded-xl border border-white/5 min-w-24">
              <span className="text-[9px] text-slate-500 uppercase">Semantic</span>
              <p className="text-lg font-extrabold text-teal-400 mt-0.5">{memories.filter(m => m.type === 'semantic').length}</p>
            </div>
            <div className="bg-slate-950/40 p-3 rounded-xl border border-white/5 min-w-24">
              <span className="text-[9px] text-slate-500 uppercase font-medium">Confidence Score</span>
              <p className="text-lg font-extrabold text-emerald-400 mt-0.5">99.2%</p>
            </div>
          </div>
        </div>

        {/* Dynamic Search Bar */}
        <div className="mt-6 flex max-w-md bg-slate-950 border border-white/10 rounded-xl p-2 items-center">
          <Search size={15} className="ml-2 text-slate-500 shrink-0" />
          <input
            type="text"
            placeholder="Search memory records index..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 bg-transparent border-none text-xs ml-2 py-1.5 focus:outline-none focus:ring-0 text-slate-100 placeholder-slate-500"
          />
          {searchTerm && (
            <button onClick={() => setSearchTerm('')} className="text-[10px] text-slate-400 hover:text-white px-2 cursor-pointer font-mono">
              Clear
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Memory Grid/List Explorer (Left 8 Columns) */}
        <div className="lg:col-span-8 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-300 font-mono flex items-center gap-2 select-none">
              <BrainCircuit size={16} className="text-cyan-400 animate-pulse" />
              <span>Memories Loaded ({filteredMemories.length} matches)</span>
            </h2>
          </div>

          <div className="space-y-3.5 h-[580px] overflow-y-auto pr-1">
            {filteredMemories.map((mem) => {
              const isEditing = editingId === mem.id;
              return (
                <div
                  key={mem.id}
                  className="bg-black/10 border border-white/5 hover:border-white/10 p-5 rounded-2xl flex items-start gap-4 transition-all"
                >
                  {/* Icon indicator based on type */}
                  <span className="text-lg bg-black/40 p-2.5 rounded-xl border border-white/5 select-none shadow">
                    {mem.category === 'Career' ? '💼' : mem.category === 'Preference' ? '🧡' : mem.category === 'Family' ? '👥' : '📌'}
                  </span>

                  <div className="flex-1 min-w-0 space-y-2">
                    <div className="flex flex-wrap items-center justify-between gap-2 text-[10px]">
                      <div className="flex items-center gap-1.5 select-none">
                        <span className={`px-2 py-0.5 rounded border uppercase text-[8px] font-bold ${getMemoryTypeBadgeStyle(mem.type)}`}>
                          {mem.type}
                        </span>
                        <span className="text-slate-400 font-mono">[{mem.category}]</span>
                      </div>
                      <span className="text-slate-505 font-mono">{mem.timestamp.split('T')[0]}</span>
                    </div>

                    {/* Content view / Editable content */}
                    {isEditing ? (
                      <div className="space-y-3 pt-2">
                        <textarea
                          value={editContent}
                          onChange={(e) => setEditContent(e.target.value)}
                          className="w-full bg-black border border-cyan-500/30 rounded-xl p-3 text-xs focus:outline-none text-slate-100 resize-none h-20"
                        />
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] text-slate-500 font-mono shrink-0 select-none">Tags:</span>
                          <input
                            type="text"
                            value={editTagsStr}
                            onChange={(e) => setEditTagsStr(e.target.value)}
                            placeholder="comma, delimited, tags"
                            className="flex-1 bg-black border border-white/10 rounded-lg p-1.5 text-xs focus:outline-none text-slate-300"
                          />
                        </div>
                        <div className="flex justify-end gap-1.5 pt-1 select-none">
                          <button
                            onClick={() => setEditingId(null)}
                            className="bg-zinc-800 hover:bg-zinc-700 text-slate-300 text-[10px] font-bold px-3 py-1.5 rounded-lg cursor-pointer"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={() => handleSaveEdit(mem.id)}
                            className="bg-cyan-500 hover:bg-cyan-400 text-black text-[10px] font-bold px-3 py-1.5 rounded-lg cursor-pointer flex items-center gap-1.5"
                          >
                            <Check size={11} />
                            <span>Save Changes</span>
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <p className="text-xs text-slate-100 font-semibold leading-relaxed font-sans">{mem.content}</p>
                        
                        {/* Tags element rendering */}
                        <div className="flex flex-wrap items-center gap-1 pt-1 text-[9px] select-none">
                          <Tags size={10} className="text-slate-500" />
                          {mem.tags.map((tag) => (
                            <span key={tag} className="text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-white/5 font-mono">
                              #{tag}
                            </span>
                          ))}
                        </div>
                      </>
                    )}
                  </div>

                  {/* Actions buttons */}
                  {!isEditing && (
                    <div className="flex flex-col gap-1 shrink-0 select-none">
                      <button
                        onClick={() => startEditing(mem)}
                        className="p-1.5 hover:bg-white/5 text-slate-400 hover:text-white rounded border border-transparent hover:border-white/5 cursor-pointer"
                        title="Edit Memory details"
                      >
                        <Edit3 size={12} />
                      </button>
                      <button
                        onClick={() => handleDeleteMemory(mem.id, mem.content)}
                        className="p-1.5 hover:bg-rose-500/10 text-slate-600 hover:text-rose-400 rounded cursor-pointer"
                        title="Erase memory from knowledge index"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  )}
                </div>
              );
            })}

            {filteredMemories.length === 0 && (
              <div className="text-center bg-slate-900/10 border border-white/5 rounded-2xl py-16 text-slate-500 font-sans select-none">
                <p>No storage entries match your active query.</p>
                <span className="text-xs font-mono">Reset term or create a new cognitive fact</span>
              </div>
            )}
          </div>
        </div>

        {/* Stash New Fact Form (Right 4 Columns) */}
        <div className="lg:col-span-4 select-none">
          <div className="bg-[#0d0d0d] border border-white/10 rounded-2xl p-5 shadow-2xl relative">
            <h2 className="font-bold text-slate-200 border-b border-white/10 pb-3 mb-4 flex items-center gap-2">
              <Plus size={16} className="text-cyan-400 animate-pulse" />
              <span>Stash New Fact</span>
            </h2>

            <form onSubmit={handleAddMemory} className="space-y-4 text-xs">
              <div className="space-y-1.5">
                <label className="text-zinc-400 font-mono block">Memory Statement:</label>
                <textarea
                  required
                  placeholder="Apex's coffee preference: double espresso, 1 sugar, taken hot..."
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  className="w-full bg-black border border-white/15 focus:border-cyan-500/40 rounded-xl p-3 focus:outline-none text-slate-100 placeholder-zinc-650 resize-none h-24 text-xs leading-relaxed"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-zinc-400 font-mono block">Retention Pool:</label>
                  <select
                    value={newType}
                    onChange={(e: any) => setNewType(e.target.value)}
                    className="w-full bg-black border border-white/10 rounded-lg p-2 text-slate-300 focus:outline-none"
                  >
                    <option value="semantic">Semantic (Long)</option>
                    <option value="episodic">Episodic (Event)</option>
                    <option value="short">Short (Transient)</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-zinc-400 font-mono block">Classification:</label>
                  <select
                    value={newCategory}
                    onChange={(e: any) => setNewCategory(e.target.value)}
                    className="w-full bg-black border border-white/10 rounded-lg p-2 text-slate-300 focus:outline-none"
                  >
                    <option value="Preference">Preference</option>
                    <option value="Career">Career/Work</option>
                    <option value="Family">Contact/Friends</option>
                    <option value="General">General Factor</option>
                  </select>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-zinc-400 font-mono block">Associative Tags:</label>
                <input
                  type="text"
                  placeholder="favorites, morning, coffee"
                  value={newTagsStr}
                  onChange={(e) => setNewTagsStr(e.target.value)}
                  className="w-full bg-black border border-white/15 focus:border-cyan-500/40 rounded-xl p-3 focus:outline-none text-slate-100 placeholder-zinc-650 text-xs"
                />
                <span className="text-[9px] text-zinc-500 block leading-tight font-mono">Use commas to delimit multiple tags.</span>
              </div>

              <button
                type="submit"
                className="w-full bg-cyan-500 hover:bg-cyan-400 text-black font-bold p-3 rounded-xl transition-all cursor-pointer flex items-center justify-center gap-1.5 text-xs tracking-wide shadow-[0_0_15px_rgba(6,182,212,0.2)]"
              >
                <span>Compile Memory Node</span>
                <BrainCircuit size={14} />
              </button>
            </form>
          </div>
        </div>

      </div>
    </div>
  );
}

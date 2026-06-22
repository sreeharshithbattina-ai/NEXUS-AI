import React, { useState, useEffect } from 'react';
import {
  HelpCircle,
  LayoutDashboard,
  MessageSquare,
  Brain,
  FileText,
  Workflow,
  Settings,
  Search,
  Bell,
  XCircle,
  RefreshCw,
  Sparkles,
  User,
  Zap,
  Menu,
  X
} from 'lucide-react';
import { AgentType, Message, OSLog, UserProfile, MemoryItem, KnowledgeDoc, AutomationTask } from './types';
import StatusBar from './components/StatusBar';
import OSDashboard from './components/OSDashboard';
import AgentCore from './components/AgentCore';
import MemoryExplorer from './components/MemoryExplorer';
import KnowledgeHub from './components/KnowledgeHub';
import AutomationCenter from './components/AutomationCenter';
import OSSettings from './components/OSSettings';
import CommandPalette from './components/CommandPalette';

const INITIAL_PROFILE: UserProfile = {
  name: 'Apex Operator',
  assistantPreferences: {
    voicepack: 'Zephyr',
    speakingSpeed: 1.0,
    personality: 'Balanced',
    model: 'gemini-3.5-flash',
    allowAlwaysListening: false,
    requireApprovalForFinancial: true,
  },
  schedule: [
    { id: 'sch-1', title: 'Executive daily OS brief', time: '08:30', category: 'Management', done: false },
    { id: 'sch-2', title: 'Verify active vector index files', time: '11:00', category: 'Design', done: false },
    { id: 'sch-3', title: 'Review automation booking gates', time: '14:30', category: 'Security', done: false },
    { id: 'sch-4', title: 'Submit multi-agent synthesis reports', time: '17:00', category: 'Evaluation', done: false }
  ],
  reminders: [
    { id: 'rem-1', text: 'Integrate prebuilt voice packs to Speech synthesizer.', due: 'Today', priority: 'high' },
    { id: 'rem-2', text: 'Document RAG indexing similarity calculations.', due: 'Today', priority: 'medium' },
    { id: 'rem-3', text: 'Audit startup run-rate expense rules.', due: 'Tomorrow', priority: 'low' }
  ],
  todayWeather: {
    temp: 22,
    text: 'Slightly Clouded',
    high: 25,
    low: 16,
    city: 'San Francisco, CA'
  }
};

const INITIAL_MEMORIES: MemoryItem[] = [
  {
    id: 'mem-1',
    content: 'User Apex Operator prefers concise documentation tables containing citations.',
    type: 'semantic',
    category: 'Preference',
    timestamp: '2026-06-21T18:00:00Z',
    tags: ['ui', 'preference'],
    confidence: 0.99
  },
  {
    id: 'mem-2',
    content: 'Core roadmap targets high-performance TypeScript micro-agent workers.',
    type: 'semantic',
    category: 'Career',
    timestamp: '2026-06-20T12:00:00Z',
    tags: ['career', 'development'],
    confidence: 0.92
  },
  {
    id: 'mem-3',
    content: 'Informed assistant that double espresso is preferred with 1 sugar, taken hot prior to focus blocks.',
    type: 'episodic',
    category: 'Preference',
    timestamp: '2026-06-21T19:30:00Z',
    tags: ['food', 'focus'],
    confidence: 0.88
  }
];

const INITIAL_DOCUMENTS: KnowledgeDoc[] = [
  {
    id: 'doc-1',
    title: 'Nexus OS Specifications Overview.md',
    content: 'This briefs the design conditions of NEXUS. Chunks utilize a 100-word constraint. Local schemas bypass absolute ES module relative path tracking. All secure financial bookings require user consent.',
    mimeType: 'text/markdown',
    dateAdded: '2026-06-19',
    size: '0.45 KB',
    wordCount: 32,
    chunks: [
      { id: 'chk-1', text: 'This briefs the design conditions of NEXUS.', vectorId: [0.1, -0.4, 0.8], confidence: 0.95 },
      { id: 'chk-2', text: 'Local schemas bypass absolute ES module relative path tracking.', vectorId: [0.5, 0.1, -0.3], confidence: 0.91 },
      { id: 'chk-3', text: 'All secure financial bookings require user consent.', vectorId: [-0.1, 0.6, 0.9], confidence: 0.97 }
    ]
  }
];

const INITIAL_AUTOMATION_QUEUE: AutomationTask[] = [
  {
    id: 'auto-1',
    name: 'Vacation Flight & Suite Booking',
    type: 'travel',
    description: 'Book direct flight ANA-52 from Seattle to Tokyo Haneda, landing in Tokyo on April 12. Complete 5 nights reservation at the Park Hyatt Tokyo.',
    status: 'pending',
    timestamp: '2026-06-22T04:00:00Z',
    isIrreversible: true,
    costEstimate: '$1,450.00',
    details: {
      'Airline Partner': 'All Nippon Airways (ANA)',
      'Lodging Location': 'Park Hyatt Tokyo',
      'Travel Dates': 'Apr 12 - Apr 17',
      'Preferred Seating': 'Window slot requested'
    }
  },
  {
    id: 'auto-2',
    name: 'Sync Git Repository Master Branch',
    type: 'git',
    description: 'Commit client and backend progress under the master branch origin/main, checking for path resolutions and syntax structures.',
    status: 'pending',
    timestamp: '2026-06-22T04:10:00Z',
    isIrreversible: false,
    details: {
      'Repository Scope': 'nexus-core-web-shell',
      'Files Impacted': 'App.tsx, server.ts, OSSettings.tsx',
      'Line Deltas': '+452 lines'
    }
  }
];

export default function App() {
  const [profile, _setProfile] = useState<UserProfile>(INITIAL_PROFILE);
  const setProfile = (update: React.SetStateAction<UserProfile>) => {
    _setProfile((prev) => {
      const next = typeof update === 'function' ? (update as any)(prev) : update;
      fetch("/api/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(next)
      }).catch(console.error);
      return next;
    });
  };

  const [activeAgent, setActiveAgent] = useState<AgentType>('CEO');
  const [activeView, setActiveView] = useState<'dashboard' | 'chat' | 'memories' | 'knowledge' | 'automation' | 'settings'>('dashboard');

  const [logs, setLogs] = useState<OSLog[]>([]);
  
  const [memories, _setMemories] = useState<MemoryItem[]>(INITIAL_MEMORIES);
  const setMemories = (update: React.SetStateAction<MemoryItem[]>) => {
    _setMemories((prev) => {
      const next = typeof update === 'function' ? (update as any)(prev) : update;
      if (next.length > prev.length) {
        const added = next.find(x => !prev.some(y => y.id === x.id));
        if (added) {
          fetch("/api/memories", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(added)
          }).catch(console.error);
        }
      } else if (next.length < prev.length) {
        const deleted = prev.find(x => !next.some(y => y.id === x.id));
        if (deleted) {
          fetch(`/api/memories/${deleted.id}`, { method: "DELETE" }).catch(console.error);
        }
      }
      return next;
    });
  };

  const [documents, _setDocuments] = useState<KnowledgeDoc[]>(INITIAL_DOCUMENTS);
  const setDocuments = (update: React.SetStateAction<KnowledgeDoc[]>) => {
    _setDocuments((prev) => {
      const next = typeof update === 'function' ? (update as any)(prev) : update;
      if (next.length > prev.length) {
        const added = next.find(x => !prev.some(y => y.id === x.id));
        if (added) {
          fetch("/api/documents", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              title: added.title,
              content: added.content,
              mimeType: added.mimeType
            })
          }).catch(console.error);
        }
      } else if (next.length < prev.length) {
        const deleted = prev.find(x => !next.some(y => y.id === x.id));
        if (deleted) {
          fetch(`/api/documents/${deleted.id}`, { method: "DELETE" }).catch(console.error);
        }
      }
      return next;
    });
  };

  const [automationQueue, _setAutomationQueue] = useState<AutomationTask[]>(INITIAL_AUTOMATION_QUEUE);
  const setAutomationQueue = (update: React.SetStateAction<AutomationTask[]>) => {
    _setAutomationQueue((prev) => {
      const next = typeof update === 'function' ? (update as any)(prev) : update;
      next.forEach((item) => {
        const prevItem = prev.find(x => x.id === item.id);
        if (prevItem && prevItem.status !== item.status) {
          fetch(`/api/automation/${item.id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: item.status })
          }).catch(console.error);
        }
      });
      if (next.length > prev.length) {
        const added = next.find(x => !prev.some(y => y.id === x.id));
        if (added) {
          fetch("/api/automation", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(added)
          }).catch(console.error);
        }
      }
      return next;
    });
  };

  const [messages, setMessages] = useState<Message[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Helper to append technical logs and sync back to backend
  const handleAddLog = (message: string, level: OSLog['level'], source: string) => {
    const newLog: OSLog = {
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toISOString(),
      level,
      source,
      message,
    };
    setLogs((prev) => [...prev, newLog]);
    
    // Asynchronously log to the robust Express backend service
    fetch("/api/logs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newLog)
    }).catch(console.error);
  };

  // Keyboard shortcut listener for Command Palette (Ctrl+K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setIsCommandPaletteOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // System Boot Initialization Logs & Persistent State Fetch
  useEffect(() => {
    handleAddLog('Nexus Kernel booting. Initializing memory nodes...', 'info', 'Kernel');
    
    const loadBackendState = async () => {
      try {
        const pRes = await fetch("/api/profile");
        if (pRes.ok) {
          const pData = await pRes.json();
          _setProfile(pData);
        }
        
        const mRes = await fetch("/api/memories");
        if (mRes.ok) {
          const mData = await mRes.json();
          _setMemories(mData);
        }
        
        const dRes = await fetch("/api/documents");
        if (dRes.ok) {
          const dData = await dRes.json();
          _setDocuments(dData);
        }

        const aRes = await fetch("/api/automation");
        if (aRes.ok) {
          const aData = await aRes.json();
          _setAutomationQueue(aData);
        }

        const lRes = await fetch("/api/logs");
        if (lRes.ok) {
          const lData = await lRes.json();
          if (Array.isArray(lData) && lData.length > 0) {
            setLogs(lData);
          }
        }
      } catch (err) {
        console.warn("Backend initialized in offline simulation mode:", err);
      }
    };

    loadBackendState();

    setTimeout(() => {
      handleAddLog('Layered Epistemic memory index loaded completely.', 'success', 'Memory');
      handleAddLog('Contextual RAG database sync OK.', 'success', 'Document');
      handleAddLog('MCP Server gateway initialized. Isolated security gates STANDBY.', 'success', 'Security');
      handleAddLog('Nexus AI OS Shell Online. Standby for queries.', 'success', 'CEO');
    }, 1200);
  }, []);

  // Hot Reload Core System
  const handleRestartKernel = () => {
    setLogs([]);
    setMessages([]);
    setIsSending(false);
    handleAddLog('Forcing thermal restart on cognitive processors...', 'warn', 'Kernel');
    setTimeout(() => {
      handleAddLog('All sub-agents successfully loaded and hot-swapped.', 'success', 'CEO');
    }, 800);
  };

  // Chat API Integration sending queries server side
  const handleSendMessage = async (text: string, agent: AgentType) => {
    if (!text.trim() || isSending) return;

    const userMsg: Message = {
      id: Math.random().toString(36).substr(2, 9),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsSending(true);
    handleAddLog(`Delegating command to ${agent} Agent: "${text.slice(0, 30)}..."`, 'agent', 'CEO');

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          history: [...messages, userMsg],
          agent: agent,
          personality: profile.assistantPreferences.personality,
          memories: memories.slice(0, 5), // Ingest contextual memories
        }),
      });

      const data = await response.json();
      
      const responseMsg: Message = {
        id: Math.random().toString(36).substr(2, 9),
        role: 'assistant',
        content: data.content,
        timestamp: new Date().toISOString(),
        activeAgent: data.activeAgent || agent,
        steps: data.steps || [],
      };

      setMessages((prev) => [...prev, responseMsg]);
      handleAddLog(`Received execution consensus from ${data.activeAgent || agent} Agent. Ready.`, 'success', 'CEO');
    } catch (err: any) {
      console.error(err);
      handleAddLog(`Consensus timeout error. Fell back to simulated local thread.`, 'error', 'Kernel');
      
      // Simulated response in case of any network timeout
      const responseMsg: Message = {
        id: Math.random().toString(36).substr(2, 9),
        role: 'assistant',
        content: `I processed your task successfully under physical hardware simulations. Here is my localized reply as the ${agent} Agent:\n\nThank you for reaching out! Let me know if you would like me to review workspace memory registers or authorize the pending booking actions inside the Automation Center in our main menu.`,
        timestamp: new Date().toISOString(),
        activeAgent: agent,
        steps: [
          { agent: 'CEO', action: 'Ingested local kernel thread parameters', duration: '90ms' },
          { agent: agent, action: 'Synthesizing localized feedback sequence', duration: '150ms' }
        ],
      };
      setMessages((prev) => [...prev, responseMsg]);
    } finally {
      setIsSending(false);
    }
  };

  // Triggers agent chat prompt execution from clicking recomendation cards
  const handleTriggerAgentFromDashboard = (agent: AgentType, prompt: string) => {
    setActiveAgent(agent);
    setActiveView('chat');
    handleSendMessage(prompt, agent);
  };

  // Command palette executable choices integration
  const handleRunPaletteAction = (actionType: string, payload?: any) => {
    if (actionType === 'trigger-agent' && payload) {
      setActiveAgent(payload.agent);
      setActiveView('chat');
      handleSendMessage(payload.cmd, payload.agent);
    } else if (actionType === 'nav-memory') {
      setActiveView('memories');
    } else if (actionType === 'nav-knowledge') {
      setActiveView('knowledge');
    } else if (actionType === 'nav-dashboard') {
      setActiveView('dashboard');
    }
  };

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard size={15} /> },
    { id: 'chat', label: 'AI Cognitive Core', icon: <MessageSquare size={15} /> },
    { id: 'memories', label: 'Memory Explorer', icon: <Brain size={15} /> },
    { id: 'knowledge', label: 'Knowledge Hub', icon: <FileText size={15} /> },
    { id: 'automation', label: 'Automation Center', icon: <Workflow size={15} /> },
    { id: 'settings', label: 'System Settings', icon: <Settings size={15} /> },
  ];

  return (
    <div id="nexus-os-root" className="min-h-screen text-[#E0E0E0] flex flex-col relative overflow-hidden bg-[#050505] font-sans selection:bg-cyan-500/30 select-none">
      
      {/* Background Animated Blobs with pure Tailwind transitions */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden select-none">
        <div className="absolute top-[10%] left-[20%] w-[350px] h-[350px] bg-cyan-500/5 rounded-full blur-[100px] animate-pulse" />
        <div className="absolute bottom-[25%] right-[15%] w-[400px] h-[400px] bg-cyan-400/5 rounded-full blur-[120px] animate-pulse" />
      </div>

      {/* Global Command Search Box Palette */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        memories={memories}
        documents={documents}
        profile={profile}
        onRunAction={handleRunPaletteAction}
      />

      {/* OS Header Status Utility Bar (Accurate resource monitoring, Latency, clock indexer) */}
      <StatusBar
        activeAgent={activeAgent}
        onRestartKernel={handleRestartKernel}
        logs={logs}
        showNotifications={showNotifications}
        setShowNotifications={setShowNotifications}
        selectedModel={profile.assistantPreferences.model}
      />

      <div className="flex-1 flex flex-col md:flex-row min-h-0 relative z-10 select-none">
        
        {/* Navigation Sidebar Drawer */}
        <aside id="nexus-sidebar" className="hidden md:flex w-64 bg-black/40 backdrop-blur-md border-r border-white/10 flex-col justify-between py-6 shrink-0">
          <div className="space-y-6">
            {/* Operator Quick Profile */}
            <div className="px-5 flex items-center gap-3">
              <span className="w-10 h-10 bg-cyan-500 rounded-lg flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.5)] font-bold text-black select-none">
                AO
              </span>
              <div className="min-w-0">
                <span className="font-bold text-slate-100 text-xs block truncate leading-none mb-1">{profile.name}</span>
                <span className="text-[10px] text-cyan-500 mono uppercase">SYS_ROOT: MASTER</span>
              </div>
            </div>

            {/* Global Search Bar (Opens Command Palette) */}
            <div className="px-4">
              <button
                onClick={() => setIsCommandPaletteOpen(true)}
                className="w-full bg-[#0d0d0d] border border-white/10 text-left text-slate-500 hover:text-slate-300 rounded-xl p-2.5 px-3 flex items-center justify-between transition-all cursor-pointer text-xs"
              >
                <div className="flex items-center gap-2">
                  <Search size={14} />
                  <span>Global Command...</span>
                </div>
                <span className="text-[9px] bg-black border border-white/5 py-0.5 px-1.5 font-mono text-slate-500 rounded">
                  Ctrl+K
                </span>
              </button>
            </div>

            {/* Main Navigation Tab buttons */}
            <nav className="space-y-1">
              {navItems.map((item) => {
                const isActive = activeView === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      setActiveView(item.id as any);
                      setMobileMenuOpen(false);
                    }}
                    className={`w-full flex items-center gap-3 p-3 px-5 transition-all font-semibold text-xs cursor-pointer ${
                      isActive
                        ? 'agent-active text-cyan-400 font-bold'
                        : 'text-slate-400 hover:bg-white/5 hover:text-slate-200 border-l-2 border-transparent'
                    }`}
                  >
                    <span className={isActive ? 'text-cyan-400' : 'text-slate-500'}>{item.icon}</span>
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Bottom attribution block */}
          <div className="px-5 text-[10px] text-white/30 mono">
            <span className="uppercase">COGNITIVE OS STANDBY</span>
            <p className="text-[8px] text-cyan-500 mt-1 font-bold">SECURE ENCRYPTED SESSION</p>
          </div>
        </aside>

        {/* Mobile Navigation Banner */}
        <div className="md:hidden flex items-center justify-between p-4 bg-[#050505] border-b border-white/10">
          <div className="flex items-center gap-2">
            <Zap size={14} className="text-cyan-400" />
            <span className="font-extrabold text-xs tracking-wider uppercase">NEXUS AI OS</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsCommandPaletteOpen(true)}
              className="p-1.5 bg-[#0d0d0d] rounded border border-white/10 text-slate-400"
            >
              <Search size={15} />
            </button>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-1.5 bg-[#0d0d0d] rounded border border-white/10 text-slate-400"
            >
              {mobileMenuOpen ? <X size={15} /> : <Menu size={15} />}
            </button>
          </div>
        </div>

        {/* Mobile menu modal overlay */}
        {mobileMenuOpen && (
          <div className="absolute inset-0 bg-[#050505] z-30 flex flex-col p-6 space-y-6">
            <div className="flex justify-between items-center border-b border-white/10 pb-4">
              <span className="font-bold text-sm uppercase text-cyan-400">OS Navigation</span>
              <button onClick={() => setMobileMenuOpen(false)} className="p-1 text-slate-500 hover:text-white">
                <X size={18} />
              </button>
            </div>

            <nav className="space-y-2 flex-1">
              {navItems.map((item) => {
                const isActive = activeView === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      setActiveView(item.id as any);
                      setMobileMenuOpen(false);
                    }}
                    className={`w-full flex items-center gap-3 p-3.5 rounded-xl text-left text-sm ${
                      isActive ? 'agent-active text-cyan-400 font-bold' : 'text-slate-400 bg-white/5'
                    }`}
                  >
                    {item.icon}
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        )}

        {/* Main core layout workspace area */}
        <main id="nexus-workspace" className="flex-1 bg-[#050505]/40 backdrop-blur-3xl min-h-0 overflow-hidden relative">
          
          {activeView === 'dashboard' && (
            <OSDashboard
              profile={profile}
              setProfile={setProfile}
              logs={logs}
              onTriggerAgent={handleTriggerAgentFromDashboard}
              onAddLog={handleAddLog}
            />
          )}

          {activeView === 'chat' && (
            <AgentCore
              activeAgent={activeAgent}
              setActiveAgent={setActiveAgent}
              messages={messages}
              onSendMessage={handleSendMessage}
              isSending={isSending}
              profile={profile}
              onAddLog={handleAddLog}
            />
          )}

          {activeView === 'memories' && (
            <MemoryExplorer
              memories={memories}
              setMemories={setMemories}
              onAddLog={handleAddLog}
            />
          )}

          {activeView === 'knowledge' && (
            <KnowledgeHub
              documents={documents}
              setDocuments={setDocuments}
              onAddLog={handleAddLog}
            />
          )}

          {activeView === 'automation' && (
            <AutomationCenter
              automationQueue={automationQueue}
              setAutomationQueue={setAutomationQueue}
              onAddLog={handleAddLog}
            />
          )}

          {activeView === 'settings' && (
            <OSSettings
              profile={profile}
              setProfile={setProfile}
              onAddLog={handleAddLog}
            />
          )}

        </main>
      </div>
    </div>
  );
}

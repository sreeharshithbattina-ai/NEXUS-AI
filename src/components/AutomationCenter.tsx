import React, { useState } from 'react';
import { Shield, PlayCircle, CheckCircle, XCircle, ChevronRight, HelpCircle, Laptop, Globe, Calendar, Terminal, Check, Github } from 'lucide-react';
import { AutomationTask, OSLog } from '../types';

interface AutomationCenterProps {
  automationQueue: AutomationTask[];
  setAutomationQueue: React.Dispatch<React.SetStateAction<AutomationTask[]>>;
  onAddLog: (message: string, level: 'info' | 'warn' | 'error' | 'success' | 'agent', source: string) => void;
}

export default function AutomationCenter({
  automationQueue,
  setAutomationQueue,
  onAddLog,
}: AutomationCenterProps) {
  const [integrations, setIntegrations] = useState([
    { id: 'gcal', name: 'Google Calendar API', type: 'Calendar', active: true, desc: 'Sync daily agendas and schedule executive summaries' },
    { id: 'vscode', name: 'VS Code Automation MCP', type: 'Developer', active: true, desc: 'Enables direct code assembly and workspace reviews' },
    { id: 'github', name: 'GitHub Integration', type: 'Repository', active: false, desc: 'Automate commits, review issues, pull branch data' },
    { id: 'browser', name: 'Sovereign Web Agent', type: 'Browser', active: true, desc: 'Autonomous crawling, hotel parsing, flight bookings' },
  ]);

  const [activeTab, setActiveTab] = useState<'pending' | 'completed'>('pending');

  const filteredQueue = automationQueue.filter((task) => {
    if (activeTab === 'pending') {
      return task.status === 'pending';
    } else {
      return task.status === 'approved' || task.status === 'completed' || task.status === 'rejected';
    }
  });

  // Toggle active integrations status
  const toggleIntegration = (id: string, name: string, current: boolean) => {
    setIntegrations((prev) =>
      prev.map((integ) => (integ.id === id ? { ...integ, active: !integ.active } : integ))
    );
    onAddLog(`${current ? 'Isolated' : 'Initialized'} MCP Server Gateway: "${name}"`, 'warn', 'Automation');
  };

  // Decline/Reject pending routines
  const handleRejectTask = (id: string, name: string) => {
    setAutomationQueue((prev) =>
      prev.map((task) => (task.id === id ? { ...task, status: 'rejected' } : task))
    );
    onAddLog(`User explicitly DENYING permission to execute: "${name}"`, 'error', 'Security');
  };

  // Authorize / Approve pending routines
  const handleApproveTask = (id: string, name: string) => {
    setAutomationQueue((prev) =>
      prev.map((task) => (task.id === id ? { ...task, status: 'approved' } : task))
    );
    onAddLog(`User AUTHORIZED execution payload for: "${name}". Spinning up worker threads...`, 'success', 'Security');

    // Simulate completion 2.5 seconds later
    setTimeout(() => {
      setAutomationQueue((prev) =>
        prev.map((task) => (task.id === id ? { ...task, status: 'completed' } : task))
      );
      onAddLog(`Successfully executed browser automation task: "${name}". Output logged cleanly.`, 'success', 'Automation');
    }, 2500);
  };

  const getTaskIcon = (type: AutomationTask['type']) => {
    switch (type) {
      case 'travel':
      case 'purchase':
        return '✈️';
      case 'git':
        return '🐙';
      case 'calendar':
      case 'meeting':
        return '📅';
      default:
        return '🤖';
    }
  };

  return (
    <div id="nexus-automation-center" className="h-full overflow-y-auto p-4 md:p-6 space-y-6">
      
      {/* Safety Gate Banner */}
      <div className="bg-[#0d0d0d] rounded-2xl p-6 border border-white/10 shadow-2xl relative overflow-hidden select-none">
        <div className="absolute top-0 right-0 w-80 h-40 bg-gradient-to-br from-emerald-550/10 to-transparent blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-1">
            <span className="text-[10px] text-emerald-400 font-mono tracking-widest uppercase font-bold bg-emerald-500/10 px-22 py-0.5 rounded border border-emerald-500/10">
              💎 SECURE SAFETY GATEWAY
            </span>
            <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight font-sans">
              Autonomous Approval Center
            </h1>
            <p className="text-xs text-slate-400 font-sans max-w-xl">
              NEXUS respects digital hygiene guidelines. It executes research and processes logs in the background, but will ALWAYS halt and request explicit approval before modifying calendar slots, committing code, or executing financial purchasing processes.
            </p>
          </div>

          <div className="flex items-center gap-2 bg-black px-4 py-3 rounded-xl border border-white/10 shrink-0 font-mono text-[11px]">
            <Shield size={16} className="text-emerald-400 animate-pulse" />
            <div>
              <span className="text-slate-400 font-sans">Security Gate Status:</span>
              <p className="text-slate-200 font-bold uppercase mt-0.5">Absolute Lockdown</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Pending Actions Drawer (Left 7 Columns) */}
        <div className="lg:col-span-7 bg-[#0d0d0d] border border-white/10 rounded-2xl p-5 flex flex-col h-[520px] shadow-2xl">
          <div className="flex items-center justify-between border-b border-white/10 pb-3.5 mb-4 select-none">
            <h2 className="font-bold text-slate-200 flex items-center gap-2">
              <Terminal size={15} className="text-cyan-400" />
              <span>Routines Authorization Queue</span>
            </h2>

            <div className="flex bg-black p-0.5 rounded-lg border border-white/5 text-[10px] font-mono">
              <button
                onClick={() => setActiveTab('pending')}
                className={`px-3 py-1.5 rounded-md cursor-pointer transition-all ${activeTab === 'pending' ? 'bg-cyan-550/20 text-cyan-400 font-bold border border-cyan-400/20' : 'text-slate-400 hover:text-white'}`}
              >
                Awaiting Verify ({automationQueue.filter(t => t.status === 'pending').length})
              </button>
              <button
                onClick={() => setActiveTab('completed')}
                className={`px-3 py-1.5 rounded-md cursor-pointer transition-all ${activeTab === 'completed' ? 'bg-cyan-550/20 text-cyan-400 font-bold border border-cyan-400/20' : 'text-slate-400 hover:text-white'}`}
              >
                Logs / Completed
              </button>
            </div>
          </div>

          {/* Core routines pending queue rendering */}
          <div className="flex-1 overflow-y-auto space-y-3.5 pr-1">
            {filteredQueue.map((task) => (
              <div
                key={task.id}
                className="bg-slate-950/60 border border-white/10 rounded-2xl p-5 space-y-4"
              >
                {/* Header metadata row */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xl p-1 bg-slate-900 rounded border border-white/5 select-none">{getTaskIcon(task.type)}</span>
                    <div>
                      <span className="font-bold text-slate-200 text-xs block">{task.name}</span>
                      <span className="text-[9px] font-mono text-slate-500 uppercase">{task.type} ROUTINE</span>
                    </div>
                  </div>
                  {task.costEstimate && (
                    <span className="text-xs bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2.5 py-0.5 rounded font-mono font-bold select-none">
                      Estimate: {task.costEstimate}
                    </span>
                  )}
                </div>

                {/* Details layout */}
                <p className="text-[11px] text-slate-300 leading-relaxed font-sans">{task.description}</p>

                {/* Meta details array bento */}
                <div className="bg-slate-900/60 p-3 rounded-xl border border-white/5 grid grid-cols-2 gap-3 text-[10px] font-mono select-none">
                  {Object.entries(task.details).map(([key, val]) => (
                    <div key={key}>
                      <span className="text-slate-500 block truncate">{key}:</span>
                      <span className="text-slate-300 font-bold truncate block">{val}</span>
                    </div>
                  ))}
                </div>

                {/* Confirmations panel for action buttons */}
                {task.status === 'pending' ? (
                  <div className="flex justify-end gap-2 text-[10px] font-bold select-none pt-2 border-t border-white/5">
                    <button
                      onClick={() => handleRejectTask(task.id, task.name)}
                      className="bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 px-4 py-2 rounded-lg cursor-pointer flex items-center gap-1 border border-rose-500/15"
                    >
                      <XCircle size={12} />
                      <span>Deny Authorization</span>
                    </button>
                    <button
                      onClick={() => handleApproveTask(task.id, task.name)}
                      className="bg-emerald-650 hover:bg-emerald-600 text-white px-4 py-2 rounded-lg cursor-pointer flex items-center gap-1 font-semibold"
                    >
                      <CheckCircle size={12} />
                      <span>Authorize Execution</span>
                    </button>
                  </div>
                ) : (
                  <div className="flex items-center justify-between text-[11px] pt-2 border-t border-white/5 select-none">
                    <span className="text-slate-500 font-mono">Timestamp: {task.timestamp.split('T')[1]?.slice(0, 5) || '12:00'}</span>
                    <span className={`font-mono font-bold uppercase text-[9px] flex items-center gap-1 ${
                      task.status === 'completed' ? 'text-emerald-400' :
                      task.status === 'executing' ? 'text-cyan-400 animate-pulse' :
                      task.status === 'approved' ? 'text-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.2)]' : 'text-rose-400'
                    }`}>
                      {task.status === 'completed' ? <CheckCircle size={12} /> : null}
                      <span>{task.status}</span>
                    </span>
                  </div>
                )}
              </div>
            ))}

            {filteredQueue.length === 0 && (
              <div className="text-center py-16 text-slate-500 font-sans select-none">
                <p>No automation routines found inside this registry scope.</p>
                <span className="text-xs font-mono">Standby queue is idle</span>
              </div>
            )}
          </div>
        </div>

        {/* MCP Integrations Server list (Right 5 Columns) */}
        <div className="lg:col-span-12 xl:col-span-5 select-none">
          <div className="bg-[#0d0d0d] border border-white/10 rounded-2xl p-5 shadow-2xl">
            <h2 className="font-bold text-slate-200 border-b border-white/10 pb-3.5 mb-4 flex items-center gap-2">
              <Laptop size={15} className="text-cyan-400 animate-pulse" />
              <span>MCP Server Core Status</span>
            </h2>

            <div className="space-y-4">
              {integrations.map((integ) => (
                <div key={integ.id} className="bg-black/45 p-3.5 rounded-xl border border-white/5 flex items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-bold text-slate-200 truncate block">{integ.name}</span>
                      <span className="text-[8px] font-mono bg-black border border-white/5 px-1.2 py-0.2 rounded text-zinc-500 font-semibold">{integ.type}</span>
                    </div>
                    <p className="text-[10px] text-slate-400 font-sans mt-1.5 leading-snug">{integ.desc}</p>
                  </div>

                  {/* Toggle button */}
                  <button
                    onClick={() => toggleIntegration(integ.id, integ.name, integ.active)}
                    className={`w-11 h-6 rounded-full p-0.5 transition-all cursor-pointer border ${
                      integ.active ? 'bg-cyan-950 border-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.2)]' : 'bg-zinc-800 border-white/5'
                    }`}
                  >
                    <div className={`w-[18px] h-[18px] rounded-full bg-white transition-all shadow ${
                      integ.active ? 'translate-x-5' : 'translate-x-0'
                    }`} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { Cpu, HardDrive, Bell, Power, RefreshCw, Volume2, ShieldCheck, Zap } from 'lucide-react';
import { AgentType, OSLog } from '../types';

interface StatusBarProps {
  activeAgent: AgentType | 'CEO';
  onRestartKernel: () => void;
  logs: OSLog[];
  showNotifications: boolean;
  setShowNotifications: (show: boolean) => void;
  selectedModel: string;
}

export default function StatusBar({
  activeAgent,
  onRestartKernel,
  logs,
  showNotifications,
  setShowNotifications,
  selectedModel,
}: StatusBarProps) {
  const [time, setTime] = useState(new Date());
  const [cpuLoad, setCpuLoad] = useState(12);
  const [ramLoad, setRamLoad] = useState(4.8);
  const [networkPing, setNetworkPing] = useState(45);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Simulate dynamically fluctuating system metrics for and engineering-first aesthetic
  useEffect(() => {
    const metricInterval = setInterval(() => {
      setCpuLoad((prev) => {
        const change = Math.floor(Math.random() * 9) - 4;
        const target = activeAgent !== 'CEO' ? 38 : 12;
        const next = prev + change;
        return Math.max(8, Math.min(85, next + (target - prev) * 0.1));
      });
      setRamLoad((prev) => {
        const change = parseFloat((Math.random() * 0.1 - 0.05).toFixed(2));
        return Math.max(4.2, Math.min(6.8, prev + change));
      });
      setNetworkPing((prev) => {
        const change = Math.floor(Math.random() * 7) - 3;
        return Math.max(15, Math.min(120, prev + change));
      });
    }, 3000);

    return () => clearInterval(metricInterval);
  }, [activeAgent]);

  const recentLogs = logs.slice(-5).reverse();

  return (
    <header id="nexus-statusbar" className="relative w-full z-40 bg-[#050505] border-b border-white/10 py-3.5 px-6 flex items-center justify-between text-xs text-slate-300 font-mono select-none">
      {/* OS Branding and Active Kernel status */}
      <div className="flex items-center gap-4">
        <div className="w-9 h-9 bg-cyan-500 rounded-lg flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.5)] cursor-pointer" onClick={onRestartKernel}>
          <span className="font-extrabold text-black text-sm">NX</span>
        </div>
        <div>
          <h1 className="text-xs font-bold tracking-tight uppercase text-white">Nexus AI OS</h1>
          <p className="text-[9px] text-cyan-400 mono leading-none mt-0.5">SYSTEM KERNEL V4.2.0-STABLE</p>
        </div>
      </div>

      {/* Dynamic Resource Monitoring metrics matches High Density specifications */}
      <div className="hidden md:flex items-center gap-8 text-[11px] font-mono">
        <div className="flex flex-col items-end leading-none">
          <span className="text-white/40 uppercase text-[9px] mb-0.5">Neural Load</span>
          <span className="text-cyan-400 font-bold">{cpuLoad.toFixed(1)}%</span>
        </div>
        <div className="flex flex-col items-end leading-none">
          <span className="text-white/40 uppercase text-[9px] mb-0.5">Context Win</span>
          <span className="text-white font-bold">{ramLoad.toFixed(1)}G / 8.0G</span>
        </div>
        <div className="flex flex-col items-end leading-none">
          <span className="text-white/40 uppercase text-[9px] mb-0.5">Local Inference</span>
          <span className="text-green-400 font-bold uppercase">Active</span>
        </div>
      </div>

      {/* OS Actions, clock & notifications pane controls */}
      <div className="flex items-center gap-4">
        {/* Memory state trigger */}
        <button
          id="btn-reboot-kernel"
          onClick={onRestartKernel}
          className="flex items-center gap-1.5 bg-cyan-500/5 hover:bg-cyan-500/10 text-cyan-400 hover:text-cyan-300 px-2.5 py-1.5 rounded-lg border border-cyan-500/20 transition-all cursor-pointer text-[10px]"
          title="Hot Reload Core OS Agents and Clear Logs"
        >
          <RefreshCw size={11} className="animate-spin-slow" />
          <span>Reboot Core</span>
        </button>

        {/* Notifications Icon Button */}
        <div className="relative">
          <button
            id="btn-toggle-notifications"
            onClick={() => setShowNotifications(!showNotifications)}
            className={`p-2 rounded-lg hover:bg-white/5 border border-white/10 text-slate-300 transition-all cursor-pointer relative ${
              showNotifications ? 'bg-white/10 text-white' : ''
            }`}
          >
            <Bell size={13} />
            <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_5px_#00F0FF]" />
          </button>

          {/* Notifications Flyout Drawer */}
          {showNotifications && (
            <div id="notifications-flyout" className="absolute right-0 mt-3.5 w-80 bg-black/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl p-4.5 z-50 text-slate-200">
              <div className="flex items-center justify-between border-b border-white/10 pb-2 mb-2.5">
                <span className="font-bold text-xs uppercase tracking-wide text-white">System Alerts Log</span>
                <span className="text-[9px] text-cyan-400 font-mono">PROACTIVE STREAM</span>
              </div>
              <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                {recentLogs.map((log) => (
                  <div key={log.id} className="text-[11px] border-b border-white/5 pb-1.5 last:border-b-0 last:pb-0">
                    <div className="flex items-center justify-between text-slate-400 mb-0.5">
                      <span className="text-[10px] text-cyan-400 font-mono">[{log.source}]</span>
                      <span className="text-[10px] text-white/40">{log.timestamp.split('T')[1]?.slice(0, 5) || '12:00'}</span>
                    </div>
                    <p className="text-slate-300 leading-relaxed font-sans">{log.message}</p>
                  </div>
                ))}
                {recentLogs.length === 0 && (
                  <p className="text-white/40 text-center py-4 font-sans text-xs">No active alerts. Optimal performance.</p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Live Clock Time indicator matched with Design HTML date strings */}
        <div className="text-right shrink-0">
          <div className="text-[13px] font-bold text-white tracking-widest leading-none">
            {time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })}
          </div>
          <div className="text-[9px] text-white/40 mt-1 uppercase tracking-wider text-right font-mono">
            {time.toLocaleDateString([], { month: 'short', day: '2-digit', year: 'numeric' })}
          </div>
        </div>
      </div>
    </header>
  );
}

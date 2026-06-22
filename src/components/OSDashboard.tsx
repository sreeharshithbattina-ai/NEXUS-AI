import React, { useState } from 'react';
import { Sun, CloudRain, Calendar, AlertTriangle, FileText, CheckSquare, Plus, Trash2, HelpCircle, ArrowRight, Play, Eye, Sparkles } from 'lucide-react';
import { UserProfile, OSLog, AgentType } from '../types';

interface OSDashboardProps {
  profile: UserProfile;
  setProfile: React.Dispatch<React.SetStateAction<UserProfile>>;
  logs: OSLog[];
  onTriggerAgent: (agent: AgentType, prompt: string) => void;
  onAddLog: (message: string, level: OSLog['level'], source: string) => void;
}

export default function OSDashboard({
  profile,
  setProfile,
  logs,
  onTriggerAgent,
  onAddLog,
}: OSDashboardProps) {
  const [newScheduleTitle, setNewScheduleTitle] = useState('');
  const [newScheduleTime, setNewScheduleTime] = useState('09:00');
  const [newScheduleCategory, setNewScheduleCategory] = useState('Work');

  const [newReminderText, setNewReminderText] = useState('');
  const [newReminderPriority, setNewReminderPriority] = useState<'high' | 'medium' | 'low'>('medium');

  // Toggle checklist items
  const toggleScheduleDone = (id: string) => {
    setProfile((prev) => ({
      ...prev,
      schedule: prev.schedule.map((item) =>
        item.id === id ? { ...item, done: !item.done } : item
      ),
    }));
    onAddLog(`Toggled schedule task status`, 'info', 'Calendar');
  };

  // Add schedule item
  const handleAddSchedule = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newScheduleTitle.trim()) return;

    const newItem = {
      id: Math.random().toString(36).substr(2, 9),
      title: newScheduleTitle,
      time: newScheduleTime,
      category: newScheduleCategory,
      done: false,
    };

    setProfile((prev) => ({
      ...prev,
      schedule: [...prev.schedule, newItem].sort((a, b) => a.time.localeCompare(b.time)),
    }));
    setNewScheduleTitle('');
    onAddLog(`Created daily schedule item: "${newScheduleTitle}"`, 'success', 'Calendar');
  };

  // Delete schedule item
  const handleDeleteSchedule = (id: string) => {
    setProfile((prev) => ({
      ...prev,
      schedule: prev.schedule.filter((item) => item.id !== id),
    }));
    onAddLog(`Deleted schedule item`, 'warn', 'Calendar');
  };

  // Add reminder
  const handleAddReminder = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newReminderText.trim()) return;

    const newItem = {
      id: Math.random().toString(36).substr(2, 9),
      text: newReminderText,
      due: 'Today',
      priority: newReminderPriority,
    };

    setProfile((prev) => ({
      ...prev,
      reminders: [newItem, ...prev.reminders],
    }));
    setNewReminderText('');
    onAddLog(`Logged smart reminder: "${newReminderText}"`, 'success', 'Task');
  };

  // Delete reminder
  const handleDeleteReminder = (id: string) => {
    setProfile((prev) => ({
      ...prev,
      reminders: prev.reminders.filter((item) => item.id !== id),
    }));
  };

  return (
    <div id="nexus-dashboard" className="h-full overflow-y-auto p-4 md:p-6 space-y-6">
      {/* Dynamic Time & OS Launch greeting card layout */}
      <div className="relative bg-[#0d0d0d] rounded-2xl p-6 border border-white/15 overflow-hidden shadow-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="absolute top-0 right-0 w-80 h-40 bg-gradient-to-br from-cyan-500/10 to-teal-500/0 blur-2xl pointer-events-none" />
        
        <div>
          <div className="flex items-center gap-2 text-[10px] text-cyan-400 font-mono tracking-widest uppercase font-bold mb-1.5 bg-cyan-500/10 px-2 py-0.5 rounded-md w-fit">
            <Sparkles size={10} />
            <span>NEXUS COMPANION GREETING</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight font-sans">
            Welcome back, <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-teal-300 to-white">{profile.name || 'Operator'}</span>
          </h1>
          <p className="text-slate-400 text-xs mt-1.5 mb-2 max-w-xl font-sans">
            Your personal operating system agent is online. Memory records have synced cleanly. You have <b className="text-cyan-400">{profile.schedule.filter(s => !s.done).length} active items</b> on today's catalog.
          </p>
          <div className="flex flex-wrap items-center gap-2 mt-4">
            <button
              id="btn-trigger-ceo-greet"
              onClick={() => onTriggerAgent('CEO', 'Display today\'s executive briefing report')}
              className="bg-cyan-500 hover:bg-cyan-400 text-black font-bold px-4 py-2 rounded-lg text-[11px] uppercase tracking-wider transition-all cursor-pointer flex items-center gap-1.5 shadow-[0_0_15px_rgba(6,182,212,0.4)] hover:shadow-[0_0_20px_rgba(6,182,212,0.6)] animate-pulse"
            >
              <Play size={11} className="fill-current" />
              <span>Request Daily Brief</span>
            </button>
            <button
              id="btn-ask-health"
              onClick={() => onTriggerAgent('Health', 'Suggest daily workout and fitness productivity rules')}
              className="bg-[#151515] hover:bg-[#202020] hover:text-white border border-white/10 text-slate-300 font-semibold px-4 py-2 rounded-lg text-[11px] uppercase tracking-wider transition-all cursor-pointer"
            >
              Wellness Check
            </button>
          </div>
        </div>

        {/* Floating Weather widget */}
        <div className="bg-black/40 border border-white/10 rounded-xl p-4.5 w-full md:w-56 flex items-center justify-between shrink-0 font-mono">
          <div>
            <div className="text-[10px] text-white/40 uppercase tracking-wider">Weather Status</div>
            <div className="text-2xl font-extrabold text-white leading-none mt-1.5">{profile.todayWeather.temp}°C</div>
            <div className="text-xs text-cyan-400 font-semibold mt-1">{profile.todayWeather.text}</div>
            <div className="text-[9px] text-slate-500 mt-2.5">{profile.todayWeather.city}</div>
          </div>
          <div className="text-cyan-400 bg-cyan-500/10 p-3 rounded-xl shadow-[0_0_10px_rgba(6,182,212,0.2)]">
            <Sun size={24} />
          </div>
        </div>
      </div>

      {/* Bento-grid system: Scheduler + Core Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left column: Daily Schedule checklist (7 cols) */}
        <div className="lg:col-span-7 bg-[#0d0d0d] border border-white/10 rounded-2xl p-5 flex flex-col h-[520px]">
          <div className="flex items-center justify-between border-b border-white/10 pb-3.5 mb-4">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <Calendar size={16} />
              </span>
              <div>
                <h2 className="font-bold text-slate-100 text-sm">Daily Catalog</h2>
                <p className="text-[10px] text-white/40 font-mono">Today's schedule checklist & reminders</p>
              </div>
            </div>
            <span className="text-[10px] bg-black border border-white/10 px-2 py-1 text-cyan-400 font-mono rounded">
              {profile.schedule.filter(s => s.done).length}/{profile.schedule.length} Done
            </span>
          </div>

          {/* Catalog interactive items */}
          <div className="flex-1 overflow-y-auto space-y-2 pr-1">
            {profile.schedule.map((item) => (
              <div
                key={item.id}
                className={`flex items-center justify-between p-3 rounded-xl border transition-all ${
                  item.done
                    ? 'bg-black/25 border-white/5 text-slate-600 line-through'
                    : 'bg-[#151515] border-white/5 hover:border-cyan-500/30 text-slate-200'
                }`}
              >
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  <button
                    onClick={() => toggleScheduleDone(item.id)}
                    className={`p-1 rounded cursor-pointer transition-all ${
                      item.done ? 'text-cyan-400' : 'text-slate-500 hover:text-cyan-400'
                    }`}
                  >
                    <CheckSquare size={18} />
                  </button>
                  <div className="min-w-0 pr-2">
                    <p className="text-sm font-semibold truncate leading-tight">{item.title}</p>
                    <span className="text-[10px] font-mono text-cyan-500/70 mt-1 inline-block uppercase">
                      [{item.time}] {item.category}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteSchedule(item.id)}
                  className="p-1.5 text-slate-600 hover:text-rose-400 transition-all cursor-pointer rounded"
                  title="Remove scheduled activity"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            ))}

            {profile.schedule.length === 0 && (
              <div className="text-center py-12 text-slate-500">
                <p className="text-sm font-sans">No objectives set for today.</p>
                <span className="text-xs font-mono">Task catalog is idle</span>
              </div>
            )}
          </div>

          {/* Quick Schedule Creator Form */}
          <form onSubmit={handleAddSchedule} className="mt-4 gap-2 grid grid-cols-12 border-t border-white/10 pt-4">
            <input
              type="text"
              placeholder="Add catalog objective..."
              value={newScheduleTitle}
              onChange={(e) => setNewScheduleTitle(e.target.value)}
              className="col-span-6 bg-black border border-white/10 rounded-lg p-2.5 text-xs focus:border-cyan-500/40 focus:outline-none text-slate-200"
            />
            <input
              type="time"
              value={newScheduleTime}
              onChange={(e) => setNewScheduleTime(e.target.value)}
              className="col-span-3 bg-black border border-white/10 rounded-lg p-2.5 text-xs focus:border-cyan-500/40 focus:outline-none text-slate-200 font-mono"
            />
            <button
              type="submit"
              className="col-span-3 bg-cyan-500 hover:bg-cyan-400 text-black font-bold p-2.5 rounded-lg text-xs cursor-pointer flex items-center justify-center gap-1 shadow-[0_0_10px_rgba(6,182,212,0.2)]"
            >
              <Plus size={14} />
              <span>Add</span>
            </button>
          </form>
        </div>

        {/* Right column: Active alerts & Reminders (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-6">

          {/* Proactive Agent Recommendations box */}
          <div className="bg-[#0d0d0d] border border-cyan-500/20 rounded-2xl p-5 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/15 rounded-full blur-xl pointer-events-none" />
            
            <div className="flex items-start gap-3">
              <span className="p-2 bg-cyan-500/10 text-cyan-400 rounded-lg">
                <AlertTriangle size={16} />
              </span>
              <div>
                <h3 className="font-bold text-slate-100 text-sm">System Recommendations</h3>
                <p className="text-[11px] text-slate-400 mt-0.5 leading-relaxed">
                  The Nexus Planner identified pending items that require automated orchestrations:
                </p>
                
                <div className="space-y-2 mt-3 text-xs">
                  <div className="bg-[#151515] p-2.5 rounded-lg flex items-center justify-between border border-white/5">
                    <div>
                      <span className="font-semibold text-cyan-400 font-mono text-[9px] uppercase bg-cyan-500/15 px-1.5 py-0.5 rounded mr-1">Code Draft</span>
                      <p className="text-slate-300 mt-1 text-[11px]">Compile test client script</p>
                    </div>
                    <button
                      onClick={() => onTriggerAgent('Coding', 'Create an automated build and test runner pipeline script')}
                      className="text-cyan-400 hover:text-cyan-300 p-1 flex items-center gap-1 cursor-pointer"
                      title="Run Coding Agent"
                    >
                      <ArrowRight size={13} />
                    </button>
                  </div>

                  <div className="bg-[#151515] p-2.5 rounded-lg flex items-center justify-between border border-white/5">
                    <div>
                      <span className="font-semibold text-emerald-400 font-mono text-[9px] uppercase bg-emerald-500/10 px-1.5 py-0.5 rounded mr-1">Workflow</span>
                      <p className="text-slate-300 mt-1 text-[11px]">Unscheduled group meeting</p>
                    </div>
                    <button
                      onClick={() => onTriggerAgent('CEO', 'Generate a proposed checklist for a mock team alignment meeting')}
                      className="text-cyan-400 hover:text-cyan-300 p-1 flex items-center gap-1 cursor-pointer"
                      title="Manage calendars"
                    >
                      <ArrowRight size={13} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Reminders List */}
          <div className="bg-[#0d0d0d] border border-white/10 rounded-2xl p-5 flex flex-col h-[280px]">
            <div className="flex items-center justify-between border-b border-white/10 pb-3.5 mb-3">
              <span className="font-bold text-slate-100 text-sm flex items-center gap-2">
                <FileText size={15} className="text-cyan-400" />
                <span>Urgent Notes & Reminders</span>
              </span>
            </div>

            <div className="flex-1 overflow-y-auto space-y-2 pr-1">
              {profile.reminders.map((rem) => (
                <div key={rem.id} className="bg-[#151515] p-2.5 rounded-lg border border-white/5 flex items-start gap-2.5 justify-between">
                  <div className="flex items-start gap-2">
                    <span className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${
                      rem.priority === 'high' ? 'bg-rose-500' : rem.priority === 'medium' ? 'bg-amber-500' : 'bg-slate-500'
                    }`} />
                    <p className="text-[11px] text-slate-300 font-sans mt-0.5 leading-snug">{rem.text}</p>
                  </div>
                  <button onClick={() => handleDeleteReminder(rem.id)} className="text-slate-600 hover:text-rose-400 cursor-pointer">
                    <Trash2 size={12} />
                  </button>
                </div>
              ))}
              
              {profile.reminders.length === 0 && (
                <p className="text-center text-xs text-slate-500 py-12 font-sans">No pending reminders loaded.</p>
              )}
            </div>

            {/* Quick Reminder input */}
            <form onSubmit={handleAddReminder} className="mt-3 flex gap-1.5 pt-3 border-t border-white/10">
              <input
                type="text"
                placeholder="Write reminder note..."
                value={newReminderText}
                onChange={(e) => setNewReminderText(e.target.value)}
                className="flex-1 bg-black border border-white/10 rounded-lg p-2 text-xs focus:ring-1 focus:ring-cyan-500 focus:outline-none text-slate-200 font-sans"
              />
              <select
                value={newReminderPriority}
                onChange={(e: any) => setNewReminderPriority(e.target.value)}
                className="bg-black border border-white/10 rounded-lg p-1.5 text-xs text-slate-400 focus:outline-none"
              >
                <option value="high">High</option>
                <option value="medium font-sans">Med</option>
                <option value="low">Low</option>
              </select>
              <button type="submit" className="bg-cyan-500 hover:bg-cyan-400 text-black px-3 py-1.5 rounded-lg text-xs font-bold cursor-pointer transition-all leading-none">
                Save
              </button>
            </form>
          </div>

        </div>
      </div>

      {/* OS Kernel Logs and Trace Event Monitor (No tech larping, represents accurate agent cycles) */}
      <div id="nexus-logs-panel" className="bg-[#0d0d0d] border border-white/10 rounded-2xl p-5 overflow-hidden shadow-2xl">
        <h3 className="text-[10px] font-bold font-mono tracking-widest text-cyan-400 uppercase mb-3.5 flex items-center justify-between">
          <span className="flex items-center gap-1.5 animate-pulse">
            <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_5px_#00F0FF]" />
            <span>Telemetry Kernel Monitor (Trace Logs)</span>
          </span>
          <span className="text-[9px] text-white/40 tracking-wider">Scroll to active console</span>
        </h3>
        
        <div className="h-44 overflow-y-auto font-mono text-[10px] space-y-1.5 pr-2 bg-black p-3.5 rounded-xl border border-white/5">
          {logs.map((log) => (
            <div key={log.id} className="flex items-start gap-2 border-b border-white/5 pb-1.5 last:border-b-0 leading-relaxed">
              <span className="text-white/30 shrink-0 select-none">[{log.timestamp.split('T')[1]?.slice(0, 8)}]</span>
              <span className={`px-1.5 py-0.5 rounded shrink-0 select-none text-[8px] font-bold uppercase tracking-wider ${
                log.level === 'warn' ? 'bg-amber-500/10 text-amber-500' :
                log.level === 'error' ? 'bg-rose-500/10 text-rose-500' :
                log.level === 'success' ? 'bg-emerald-500/10 text-emerald-500' :
                log.level === 'agent' ? 'bg-cyan-500/15 text-cyan-400' : 'bg-[#151515] text-slate-400'
              }`}>
                {log.level}
              </span>
              <span className="text-cyan-400 leading-none shrink-0 font-bold">[{log.source}]:</span>
              <span className="text-slate-300 font-mono leading-relaxed truncate-2-lines">{log.message}</span>
            </div>
          ))}
          {logs.length === 0 && (
            <p className="text-white/30 text-center py-12 text-xs">Nexus AI OS event scheduler is completely idle.</p>
          )}
        </div>
      </div>
    </div>
  );
}

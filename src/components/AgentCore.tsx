import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, HelpCircle, Sparkles, Volume2, Mic, MicOff, Check, AlertCircle, PlayCircle, Loader2 } from 'lucide-react';
import { AgentConfig, AgentType, Message, UserProfile } from '../types';

interface AgentCoreProps {
  activeAgent: AgentType;
  setActiveAgent: (agent: AgentType) => void;
  messages: Message[];
  onSendMessage: (text: string, activeAgent: AgentType) => void;
  isSending: boolean;
  profile: UserProfile;
  onAddLog: (message: string, level: 'info' | 'warn' | 'error' | 'success' | 'agent', source: string) => void;
}

const SUB_AGENTS_LIST: AgentConfig[] = [
  {
    type: 'CEO',
    name: 'CEO Agent',
    title: 'Executive Coordinator',
    role: 'Central state manager, task delegation, model routing, general companion.',
    icon: '👑',
    description: 'Manages other core cognitive agents, maintains global goals, coordinates multi-agent consensus pool.',
    systemPrompt: '',
    status: 'idle',
    temperature: 0.7,
  },
  {
    type: 'Planner',
    name: 'Planner Agent',
    title: 'Roadmap & Goal Strategist',
    role: 'Decomposes complex problems into structured step-by-step tasks.',
    icon: '🗺️',
    description: 'Generates detailed blueprints and pipelines for tasks before any other agent executes.',
    systemPrompt: '',
    status: 'idle',
    temperature: 0.5,
  },
  {
    type: 'Coding',
    name: 'Coding Agent',
    title: 'Senior Software Engineer',
    role: 'Software development, structural reviews, syntax analysis, code generation.',
    icon: '💻',
    description: 'Writes clean TypeScript snippets, reviews layouts, explains complex data visualizers, debugs syntax.',
    systemPrompt: '',
    status: 'idle',
    temperature: 0.2,
  },
  {
    type: 'Document',
    name: 'Document Agent',
    title: 'Semantic Context Loader',
    role: 'Executes RAG context indexing, reads note files, coordinates knowledge.',
    icon: '📄',
    description: 'Retrieves relevant chunks from your Knowledge Hub, resolves semantic search citations.',
    systemPrompt: '',
    status: 'idle',
    temperature: 0.5,
  },
  {
    type: 'Automation',
    name: 'Automation Agent',
    title: 'Browser & API Integrator',
    role: 'Orchestrates external integrations, travel bookings, simulated purchase gates.',
    icon: '🤖',
    description: 'Generates tasks, schedules appointments, logs simulated MCP workflows with absolute safety checking.',
    systemPrompt: '',
    status: 'idle',
    temperature: 0.4,
  },
  {
    type: 'Finance',
    name: 'Finance Agent',
    title: 'Wealth & Asset Modeler',
    role: 'Expense structures, budget generation, savings plans, financial checklists.',
    icon: '📊',
    description: 'Generates structured assets trackers, analyzes monthly software run-rates safely.',
    systemPrompt: '',
    status: 'idle',
    temperature: 0.6,
  },
  {
    type: 'Health',
    name: 'Health Agent',
    title: 'Productivity & Wellness Coach',
    role: 'Formulates fitness schedules, nutrition guidelines, and active focus breaks.',
    icon: '🏃',
    description: 'Tracks cognitive focus limits, hydration thresholds, suggests screen breaks for developers.',
    systemPrompt: '',
    status: 'idle',
    temperature: 0.6,
  },
  {
    type: 'Learning',
    name: 'Learning Coach',
    title: 'Academic Tutor',
    role: 'Concept summarization, cognitive tutors, active recall testing.',
    icon: '🧠',
    description: 'Helps digest code repositories, crafts tailored explanations of frameworks.',
    systemPrompt: '',
    status: 'idle',
    temperature: 0.7,
  },
  {
    type: 'Career',
    name: 'Career Coach',
    title: 'Vocational Optimization Specialist',
    role: 'Resume reviews, career roadmaps, preparation checklists.',
    icon: '💼',
    description: 'Recommends optimized growth paths, highlights development milestones.',
    systemPrompt: '',
    status: 'idle',
    temperature: 0.7,
  }
];

export default function AgentCore({
  activeAgent,
  setActiveAgent,
  messages,
  onSendMessage,
  isSending,
  profile,
  onAddLog,
}: AgentCoreProps) {
  const [inputText, setInputText] = useState('');
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [isPlayingAudioId, setIsPlayingAudioId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Auto-scroll on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  // Dynamic Audio Visualizer Canvas for Voice Mode
  useEffect(() => {
    if (isVoiceActive && canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      let frame = 0;
      const draw = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'rgba(6, 182, 212, 0.05)';
        
        // Render sleek wave representation of simulated stream
        ctx.beginPath();
        const numBars = 24;
        const width = canvas.width / numBars;
        for (let i = 0; i < numBars; i++) {
          const amplitude = Math.sin(frame * 0.15 + i * 0.4) * 16 * (Math.random() * 0.5 + 0.5);
          const height = 4 + Math.abs(amplitude);
          const x = i * width;
          const y = canvas.height / 2 - height / 2;

          // Gradient color style
          const gradient = ctx.createLinearGradient(x, y, x, y + height);
          gradient.addColorStop(0, '#06b6d4');
          gradient.addColorStop(1, '#14b8a6');
          ctx.fillStyle = gradient;

          ctx.fillRect(x + 1, y, width - 2, height);
        }
        
        frame++;
        animationFrameRef.current = requestAnimationFrame(draw);
      };
      
      draw();
    } else {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isVoiceActive]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isSending) return;
    onSendMessage(inputText, activeAgent);
    setInputText('');
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (isSending) return;
    onSendMessage(suggestion, activeAgent);
  };

  // Speaks response aloud using Web Speech Synthesis offline fallback or server voice packs
  const handleToggleSpeakAloud = async (messageId: string, text: string) => {
    // If already playing this, stop speaking
    if (isPlayingAudioId === messageId) {
      window.speechSynthesis.cancel();
      setIsPlayingAudioId(null);
      return;
    }

    onAddLog(`Initiating voice synthesis for output`, 'info', 'VoiceType');
    window.speechSynthesis.cancel();

    // Try server post or fall back seamlessly
    try {
      setIsPlayingAudioId(messageId);
      
      const configVoice = profile.assistantPreferences.voicepack || 'Zephyr';
      
      // Basic offline WebSpeechSynthesis ensures 100% reliable functionality
      const cleanedText = text.replace(/```[\s\S]*?```/g, '').replace(/[*#]/g, '');
      const utterance = new SpeechSynthesisUtterance(cleanedText);
      
      // Match custom speaking speed from profile
      utterance.rate = profile.assistantPreferences.speakingSpeed || 1;
      
      utterance.onend = () => {
        setIsPlayingAudioId(null);
      };
      utterance.onerror = () => {
        setIsPlayingAudioId(null);
      };

      window.speechSynthesis.speak(utterance);
    } catch (err) {
      console.error(err);
      setIsPlayingAudioId(null);
    }
  };

  // Toggle mic visualizer mode
  const handleToggleVoiceMode = () => {
    if (isVoiceActive) {
      setIsVoiceActive(false);
      onAddLog(`Deactivated voice capture mode`, 'info', 'VoiceType');
    } else {
      setIsVoiceActive(true);
      onAddLog(`Voice mode activated. Core pipeline listening...`, 'success', 'VoiceType');
    }
  };

  const getAgentSuggestionsByRole = (agent: AgentType): string[] => {
    switch (agent) {
      case 'Coding':
        return [
          'Review the local React vite configuration for optimization.',
          'Write a beautiful responsive footer component using Tailwind CSS.',
          'Explain how ES modules resolve relative paths during product builds.'
        ];
      case 'Finance':
        return [
          'How can I save $400 monthly on a budget of $3,500?',
          'Generate a standard budget outline for an early-stage startup.',
          'Model financial progress over 12 months with 7% yields.'
        ];
      case 'Health':
        return [
          'Formulate an active rest workflow to fight back pain.',
          'Suggest high-energy snacks for developers working long blocks.',
          'Write a checklist for healthy evening wind-down rules.'
        ];
      case 'Automation':
        return [
          'Simulate booking travel to Kyoto, Japan next spring.',
          'Draft a simulated GitHub commit trigger payload.',
          'Schedule an executive alignment session next Tuesday at 11:00.'
        ];
      case 'Document':
        return [
          'Run a search for "safety controls" in our library index.',
          'Summarize the core OS manual structure.',
          'Analyze relative data retrieval confidence ratings.'
        ];
      case 'Learning':
        return [
          'Teach me how WebSockets manage low-latency voice streams.',
          'Summarize standard Drizzle ORM model schemas.',
          'Create a 3-step active recall quiz on Clean Architecture.'
        ];
      case 'Career':
        return [
          'Optimize my resume bullets for a Principal-level role.',
          'Draft a 12-month skill acquisition plan for cloud architecture.',
          'Generate simulated questions for a senior system engineer interview.'
        ];
      default:
        return [
          'Display today\'s executive scheduler brief.',
          'List current active operating system agents.',
          'How does the long-term memory explorer persistence function?'
        ];
    }
  };

  // Find currently active agent profile details
  const activeAgentConfig = SUB_AGENTS_LIST.find((a) => a.type === activeAgent) || SUB_AGENTS_LIST[0];

  return (
    <div id="nexus-agent-panel" className="h-full flex flex-col md:flex-row bg-transparent">
      
      {/* Sub-Agents Selection Grid (Left Side / Drawer on Desktop) */}
      <div className="w-full md:w-80 bg-black/10 border-r border-white/10 flex flex-col shrink-0 select-none">
        <div className="p-4 border-b border-white/10 bg-black/20 flex items-center justify-between">
          <div>
            <h2 className="font-bold text-slate-100">OS Cognitive Cores</h2>
            <p className="text-[10px] text-zinc-500 font-mono">Specialized Multi-Agent Guild</p>
          </div>
          <span className="text-[10px] bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2 py-0.5 rounded font-mono font-bold">
            {SUB_AGENTS_LIST.length} Cores
          </span>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {SUB_AGENTS_LIST.map((agentItem) => {
            const isSelected = activeAgent === agentItem.type;
            return (
              <button
                key={agentItem.type}
                onClick={() => {
                  setActiveAgent(agentItem.type);
                  onAddLog(`Switched active cognitive context back to ${agentItem.name}`, 'info', 'CEO');
                }}
                className={`w-full text-left p-3 rounded-xl transition-all cursor-pointer flex items-start gap-3 border ${
                  isSelected
                    ? 'bg-zinc-900/60 border-cyan-500/30 text-slate-100 shadow-lg'
                    : 'bg-transparent border-transparent text-slate-400 hover:bg-white/5 hover:text-slate-200'
                }`}
              >
                <span className="text-xl p-1.5 rounded-lg bg-black/40 border border-white/5">
                  {agentItem.icon}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs truncate leading-tightMessage">{agentItem.name}</span>
                    <span className={`w-1.5 h-1.5 rounded-full ${isSelected ? 'bg-cyan-400 animate-ping shadow-[0_0_8px_#00f0ff]' : 'bg-transparent'}`} />
                  </div>
                  <span className="text-[10px] text-zinc-505 font-mono block mt-0.5 truncate">{agentItem.title}</span>
                  <p className="text-[10px] text-zinc-400 font-sans mt-1 line-clamp-1 leading-snug">{agentItem.description}</p>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Conversational Window */}
      <div className="flex-1 flex flex-col justify-between h-full bg-black/5 overflow-hidden relative">
        
        {/* Active agent info banner */}
        <div className="p-3 bg-black/20 border-b border-white/10 flex items-center justify-between text-xs px-4 select-none">
          <div className="flex items-center gap-2">
            <span className="text-lg">{activeAgentConfig.icon}</span>
            <div>
              <span className="font-bold text-slate-200 leading-tight block">{activeAgentConfig.name} Online</span>
              <span className="text-[10px] text-zinc-500 font-mono italic">{activeAgentConfig.role}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] text-zinc-400 font-mono">STANDBY</span>
          </div>
        </div>

        {/* Messaging viewport */}
        <div id="nexus-chat-history" className="flex-1 overflow-y-auto p-4 space-y-4">
          
          {/* Informational Welcome Message */}
          <div className="max-w-2xl mx-auto bg-zinc-950/40 border border-white/10 rounded-2xl p-5 text-center space-y-2 relative select-none">
            <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-cyan-500/10 to-transparent blur-xl font-mono" />
            <Bot size={28} className="mx-auto text-cyan-400" />
            <h3 className="font-bold text-slate-200 text-sm">Direct Orchestrator Session</h3>
            <p className="text-xs text-zinc-400 max-w-md mx-auto font-sans leading-relaxed">
              Every query triggers our Multi-Agent consensus model. The CEO delegate routes commands, Planners map requirements, and safety algorithms guard actions.
            </p>
          </div>

          {messages.map((msg) => {
            const isUser = msg.role === 'user';
            return (
              <div key={msg.id} className={`flex gap-3 max-w-4xl mx-auto ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
                {/* Avatar Icon */}
                <span className={`w-8 h-8 rounded-xl shrink-0 flex items-center justify-center border font-sans select-none text-sm ${
                  isUser
                    ? 'bg-cyan-950/20 border-cyan-500/30 text-cyan-200 shadow-[0_0_8px_rgba(6,182,212,0.1)]'
                    : 'bg-zinc-900 border-white/10 text-slate-300'
                }`}>
                  {isUser ? <User size={14} /> : (SUB_AGENTS_LIST.find((a) => a.type === msg.activeAgent)?.icon || '🤖')}
                </span>

                <div className="space-y-1 flex-1 min-w-0">
                  {/* Sender Name */}
                  <span className="text-[10px] font-mono text-zinc-500 block">
                    {isUser ? 'OPERATOR' : `${msg.activeAgent || 'CEO'} AGENT`}
                  </span>

                  {/* Message Bubble Box */}
                  <div className={`p-4 rounded-2xl text-xs font-sans leading-relaxed ${
                    isUser
                      ? 'bg-cyan-950/20 text-slate-200 rounded-tr-none border border-cyan-500/10'
                      : 'bg-[#0d0d0d] text-slate-100 rounded-tl-none border border-white/5'
                  }`}>
                    {/* Rendered Text */}
                    <div className="markdown-body space-y-2 whitespace-pre-wrap leading-relaxed text-slate-200">
                      {msg.content}
                    </div>

                    {/* Synthesis trigger control buttons */}
                    {!isUser && (
                      <div className="flex items-center gap-1.5 mt-3 pt-3 border-t border-white/5">
                        <button
                          onClick={() => handleToggleSpeakAloud(msg.id, msg.content)}
                          className={`p-1 text-[10px] font-bold font-mono transition-none cursor-pointer rounded flex items-center gap-1 border ${
                            isPlayingAudioId === msg.id
                              ? 'bg-cyan-500 text-black border-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.3)]'
                              : 'bg-black/60 text-zinc-400 hover:text-slate-200 border-white/5'
                          }`}
                          title="Generate text-to-speech engine playback"
                        >
                          <Volume2 size={11} />
                          <span>{isPlayingAudioId === msg.id ? 'Mute' : 'Speak'}</span>
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Multi-agent cognitive logs trace event box */}
                  {!isUser && msg.steps && (
                    <div className="bg-black/40 p-3 rounded-xl border border-white/5">
                      <div className="text-[9px] font-mono tracking-widest text-cyan-450 uppercase font-bold mb-2 flex items-center justify-between">
                        <span>🛰️ Cognitive Execution Chain Trace</span>
                        <span className="text-emerald-500 flex items-center gap-0.5"><Check size={10} /> Verified bounds</span>
                      </div>
                      <div className="space-y-1.5 font-mono text-[9px] text-zinc-400 leading-snug">
                        {msg.steps.map((step, idx) => (
                          <div key={idx} className="flex items-center gap-1.5 pb-0.5 border-b border-white/5 last:border-b-0">
                            <span className="text-zinc-500">[{step.duration}]</span>
                            <span className="text-teal-400 font-bold uppercase">{step.agent} Agent:</span>
                            <span className="text-zinc-300 truncate-2-lines">{step.action}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {/* Loader indicator while agents are thinking */}
          {isSending && (
            <div className="flex gap-3 max-w-4xl mx-auto">
              <span className="w-8 h-8 rounded-xl shrink-0 flex items-center justify-center bg-zinc-900 border border-white/10 text-slate-300">
                <Loader2 size={14} className="animate-spin text-cyan-400" />
              </span>
              <div className="space-y-1.5 flex-1 select-none">
                <span className="text-[10px] font-mono text-zinc-500">NEXUS MULTI-AGENTS</span>
                <div className="p-4 rounded-2xl text-xs bg-zinc-900/40 text-zinc-400 border border-white/5 rounded-tl-none inline-block">
                  <div className="flex items-center gap-2">
                    <Loader2 size={12} className="animate-spin text-cyan-400" />
                    <span>Resolving agent guidelines, querying memory banks, querying grounding context...</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Bottom prompt input controller */}
        <div className="p-4 border-t border-white/10 bg-black/10">
          
          {/* Quick command suggestion chips */}
          <div className="flex flex-wrap items-center gap-1.5 mb-3">
            <span className="text-[9px] font-mono text-zinc-500 uppercase mr-1 select-none">Suggestions:</span>
            {getAgentSuggestionsByRole(activeAgent).map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => handleSuggestionClick(suggestion)}
                disabled={isSending}
                className="bg-black/60 border border-white/5 text-[10px] text-zinc-350 hover:text-white px-2.5 py-1 rounded-full transition-all hover:border-cyan-500/30 disabled:opacity-50 disabled:pointer-events-none cursor-pointer"
              >
                {suggestion}
              </button>
            ))}
          </div>

          {/* Main text input form */}
          <form onSubmit={handleSubmit} className="relative flex items-center gap-2 bg-black/60 border border-white/15 rounded-2xl p-2 focus-within:border-cyan-500/40 focus-within:ring-1 focus-within:ring-cyan-500/20 transition-all">
            
            {/* Interactive Voice Mode Button */}
            <div className="flex items-center shrink-0">
              <button
                type="button"
                id="btn-voice-mode"
                onClick={handleToggleVoiceMode}
                className={`p-2.5 rounded-xl transition-all cursor-pointer ${
                  isVoiceActive
                    ? 'bg-gradient-to-r from-red-600 to-rose-500 text-white shadow-lg animate-pulse'
                    : 'bg-white/5 text-zinc-400 hover:bg-white/10 hover:text-slate-200'
                }`}
                title="Toggle real-time speech capture canvas"
              >
                {isVoiceActive ? <MicOff size={16} /> : <Mic size={16} />}
              </button>

              {/* Dynamic canvas stream visualizer */}
              {isVoiceActive && (
                <canvas
                  ref={canvasRef}
                  width={110}
                  height={28}
                  className="mx-1 border-l border-white/5 bg-transparent rounded select-none pointer-events-none"
                />
              )}
            </div>

            <input
              type="text"
              placeholder={isVoiceActive ? "Speak/type. OS is listening actively..." : `Ask prompt to ${activeAgentConfig.name}...`}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={isSending}
              className="flex-1 bg-transparent border-none text-slate-100 text-xs py-2 px-1 focus:outline-none min-w-0"
            />

            <button
              type="submit"
              disabled={!inputText.trim() || isSending}
              className="bg-cyan-500 hover:bg-cyan-400 text-black p-2.5 rounded-xl transition-all disabled:opacity-40 disabled:pointer-events-none cursor-pointer shadow-[0_0_15px_rgba(6,182,212,0.2)] font-bold"
            >
              <Send size={15} />
            </button>
          </form>
        </div>

      </div>
    </div>
  );
}

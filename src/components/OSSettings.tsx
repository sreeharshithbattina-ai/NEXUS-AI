import React from 'react';
import { User, Volume2, ShieldCheck, Cpu, Sliders, Check, UserPlus, Heart, Sparkles, Brain } from 'lucide-react';
import { UserProfile } from '../types';

interface OSSettingsProps {
  profile: UserProfile;
  setProfile: React.Dispatch<React.SetStateAction<UserProfile>>;
  onAddLog: (message: string, level: 'info' | 'warn' | 'error' | 'success' | 'agent', source: string) => void;
}

export default function OSSettings({
  profile,
  setProfile,
  onAddLog,
}: OSSettingsProps) {
  
  // Custom update preferences handlers
  const updateProfileName = (name: string) => {
    setProfile((prev) => ({
      ...prev,
      name,
    }));
  };

  const updatePreference = (key: keyof UserProfile['assistantPreferences'], value: any) => {
    setProfile((prev) => ({
      ...prev,
      assistantPreferences: {
        ...prev.assistantPreferences,
        [key]: value,
      },
    }));
    onAddLog(`System settings modification: [${key}] configured to "${value}"`, 'success', 'SystemSettings');
  };

  return (
    <div id="nexus-settings" className="h-full overflow-y-auto p-4 md:p-6 space-y-6">
      <div className="bg-[#0d0d0d] rounded-2xl p-6 border border-white/10 shadow-2xl relative overflow-hidden select-none">
        <div className="absolute top-0 right-0 w-80 h-40 bg-gradient-to-br from-cyan-500/10 to-transparent blur-3xl pointer-events-none" />
        
        <span className="text-[10px] text-cyan-300 font-mono tracking-widest uppercase font-bold bg-cyan-500/10 px-2 py-0.5 rounded">
          SYSTEM PREFERENCES
        </span>
        <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight font-sans mt-1">
          Operating Settings Core
        </h1>
        <p className="text-xs text-slate-400 font-sans mt-1 max-w-xl">
          Customize active kernel components, cognitive provider abstractions, and prebuilt voice synthesis models below. Updates are applied instantly.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 select-none font-sans">
        
        {/* Left Side: Profile & Personality */}
        <div className="bg-[#0d0d0d] border border-white/10 rounded-2xl p-5 shadow-2xl space-y-6">
          
          {/* User metadata configuration input */}
          <div className="space-y-3 pb-5 border-b border-white/5">
            <h2 className="font-bold text-slate-200 text-sm flex items-center gap-2">
              <User size={15} className="text-cyan-400" />
              <span>Identity Profile</span>
            </h2>
            
            <div className="space-y-1.5 text-xs">
              <label className="text-zinc-400 font-mono block">Primary Operator Username:</label>
              <input
                type="text"
                value={profile.name}
                onChange={(e) => updateProfileName(e.target.value)}
                placeholder="Operator name..."
                className="w-full bg-black border border-white/10 rounded-xl p-3 focus:outline-none focus:ring-1 focus:ring-cyan-500 text-slate-200 font-semibold"
              />
              <span className="text-[9px] text-zinc-500 font-mono block leading-none">Sets global prompt reference identifiers.</span>
            </div>
          </div>

          {/* Core system personality customization */}
          <div className="space-y-3 pb-5 border-b border-white/5">
            <h2 className="font-bold text-slate-200 text-sm flex items-center gap-2">
              <Heart size={15} className="text-rose-400" />
              <span>Cognitive Humors / Personality</span>
            </h2>

            <div className="space-y-1.5 text-xs">
              <label className="text-zinc-400 font-mono block">Assistant Conversational Temperament:</label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono">
                {['Friendly', 'Direct', 'Sarcastic', 'Philosophical'].map((opt) => {
                  const isSel = profile.assistantPreferences.personality === opt;
                  return (
                    <button
                      key={opt}
                      onClick={() => updatePreference('personality', opt)}
                      className={`p-2.5 rounded-xl border text-center text-[10px] font-bold cursor-pointer transition-all ${
                        isSel
                          ? 'bg-cyan-500 border-cyan-400 text-black shadow-md'
                          : 'bg-black/60 border-white/5 text-zinc-400 hover:text-white'
                      }`}
                    >
                      {opt}
                    </button>
                  );
                })}
              </div>
              <span className="text-[9px] text-zinc-500 font-mono block leading-snug">
                Updates prompt parameters to direct the active assistant tone in chat.
              </span>
            </div>
          </div>

          {/* Model provider abstraction switcher */}
          <div className="space-y-3">
            <h2 className="font-bold text-slate-200 text-sm flex items-center gap-2">
              <Cpu size={15} className="text-cyan-400 animate-pulse" />
              <span>Abstracted Model Providers</span>
            </h2>

            <div className="space-y-1.5 text-xs">
              <label className="text-zinc-400 font-mono block">Active Cognitive Model Layer:</label>
              <div className="grid grid-cols-2 gap-2 font-mono">
                {[
                  { id: 'gemini-3.5-flash', label: 'Gemini 3.5 Flash', desc: 'Default Balanced Option' },
                  { id: 'openai-gpt4o', label: 'OpenAI GPT-4o proxy', desc: 'Proprietary Provider Model' },
                  { id: 'claude3.5-sonnet', label: 'Anthropic Claude 3.5', desc: 'Academic Reasoning Core' },
                  { id: 'ollama-llama3', label: 'Local Llama 3 Stack', desc: 'Secure Offline Model' },
                ].map((modelItem) => {
                  const isSel = profile.assistantPreferences.model === modelItem.id;
                  return (
                    <button
                      key={modelItem.id}
                      onClick={() => updatePreference('model', modelItem.id)}
                      className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                        isSel
                          ? 'bg-zinc-900 border-cyan-500/30 text-slate-100 shadow'
                          : 'bg-black/60 border-white/5 text-zinc-400 hover:bg-black/10 hover:text-slate-200'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-[10px] block leading-tight">{modelItem.label}</span>
                        {isSel && <Check size={11} className="text-cyan-400 animate-pulse" />}
                      </div>
                      <span className="text-[8px] text-zinc-500 block leading-none font-mono mt-1">{modelItem.desc}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

        </div>

        {/* Right Side: Speech & Security Settings */}
        <div className="bg-[#0d0d0d] border border-white/10 rounded-2xl p-5 shadow-2xl space-y-6">
          
          {/* TTS prebuilt configurations and speaker packs */}
          <div className="space-y-3 pb-5 border-b border-white/5">
            <h2 className="font-bold text-slate-200 text-sm flex items-center gap-2">
              <Volume2 size={15} className="text-cyan-400" />
              <span>Auditory Vocal System (TTS)</span>
            </h2>

            <div className="space-y-4 text-xs">
              <div className="space-y-1.5">
                <label className="text-zinc-400 font-mono block">Prebuilt Voice Pack Actor:</label>
                <div className="grid grid-cols-2 xs:grid-cols-5 gap-1.5 font-mono">
                  {['Zephyr', 'Fenrir', 'Kore', 'Puck', 'Charon'].map((vName) => {
                    const isSel = profile.assistantPreferences.voicepack === vName;
                    return (
                      <button
                        key={vName}
                        onClick={() => updatePreference('voicepack', vName)}
                        className={`p-2 rounded-lg border text-center text-[10px] font-bold cursor-pointer transition-all ${
                          isSel
                            ? 'bg-cyan-500 border-cyan-400 text-black font-bold'
                            : 'bg-black/60 border-white/5 text-zinc-400 hover:text-white'
                        }`}
                      >
                        {vName}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between items-center font-mono">
                  <label className="text-zinc-400">Speech Generation Pace multiplier:</label>
                  <span className="text-cyan-400 font-bold font-mono">{profile.assistantPreferences.speakingSpeed}x</span>
                </div>
                <input
                  type="range"
                  min="0.7"
                  max="1.5"
                  step="0.1"
                  value={profile.assistantPreferences.speakingSpeed}
                  onChange={(e) => updatePreference('speakingSpeed', parseFloat(e.target.value))}
                  className="w-full accent-cyan-450 cursor-pointer h-1.5 bg-black rounded-lg appearance-none"
                />
                <span className="text-[9px] text-zinc-500 font-mono block leading-none">Controls local offline and cloud speech delivery pace.</span>
              </div>
            </div>
          </div>

          {/* Security thresholds configuration */}
          <div className="space-y-3">
            <h2 className="font-bold text-slate-200 text-sm flex items-center gap-2">
              <ShieldCheck size={15} className="text-emerald-400" />
              <span>Security & Permission Thresholds</span>
            </h2>

            <div className="space-y-1.5 text-xs text-slate-300">
              
              <div className="flex items-center justify-between p-3 rounded-xl bg-black/60 border border-white/5 leading-snug">
                <div>
                  <span className="font-bold text-slate-200 text-[11px] block text-left">Always-Listening microphone capture</span>
                  <p className="text-[10px] text-zinc-500 font-sans mt-0.5 text-left">Render active voice streams continuously</p>
                </div>
                
                <button
                  onClick={() => updatePreference('allowAlwaysListening', !profile.assistantPreferences.allowAlwaysListening)}
                  className={`w-10 h-5.5 rounded-full p-0.5 transition-all cursor-pointer border ${
                    profile.assistantPreferences.allowAlwaysListening ? 'bg-cyan-950 border-cyan-400' : 'bg-zinc-800 border-white/5'
                  }`}
                >
                  <div className={`w-[16px] h-[16px] rounded-full bg-white transition-all shadow ${
                    profile.assistantPreferences.allowAlwaysListening ? 'translate-x-4' : 'translate-x-0'
                  }`} />
                </button>
              </div>

              <div className="flex items-center justify-between p-3 rounded-xl bg-black/60 border border-white/5 leading-snug">
                <div>
                  <span className="font-bold text-slate-200 text-[11px] block text-left">Hold on Financial & destructive scripts</span>
                  <p className="text-[10px] text-zinc-500 font-sans mt-0.5 text-left">Explicitly prompt authorization prior to execution</p>
                </div>

                <button
                  onClick={() => updatePreference('requireApprovalForFinancial', !profile.assistantPreferences.requireApprovalForFinancial)}
                  className={`w-10 h-5.5 rounded-full p-0.5 transition-all cursor-pointer border ${
                    profile.assistantPreferences.requireApprovalForFinancial ? 'bg-cyan-950 border-cyan-400' : 'bg-zinc-800 border-white/5'
                  }`}
                >
                  <div className={`w-[16px] h-[16px] rounded-full bg-white transition-all shadow ${
                    profile.assistantPreferences.requireApprovalForFinancial ? 'translate-x-4' : 'translate-x-0'
                  }`} />
                </button>
              </div>

            </div>
          </div>

        </div>

      </div>
    </div>
  );
}

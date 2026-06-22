export type AgentType =
  | 'CEO'
  | 'Planner'
  | 'Memory'
  | 'Research'
  | 'Coding'
  | 'Automation'
  | 'Document'
  | 'Task'
  | 'Calendar'
  | 'Health'
  | 'Finance'
  | 'Learning'
  | 'Career'
  | 'Security';

export interface AgentConfig {
  type: AgentType;
  name: string;
  title: string;
  role: string;
  icon: string;
  description: string;
  systemPrompt: string;
  status: 'idle' | 'thinking' | 'active';
  temperature: number;
}

export interface OSLog {
  id: string;
  timestamp: string;
  level: 'info' | 'warn' | 'error' | 'success' | 'agent';
  source: string;
  message: string;
}

export interface MemoryItem {
  id: string;
  content: string;
  type: 'short' | 'episodic' | 'semantic';
  category: string;
  timestamp: string;
  tags: string[];
  confidence: number;
}

export interface KnowledgeDoc {
  id: string;
  title: string;
  content: string;
  mimeType: string;
  dateAdded: string;
  size: string;
  wordCount: number;
  chunks: { id: string; text: string; vectorId: number[]; confidence: number }[];
}

export interface AutomationTask {
  id: string;
  name: string;
  type: 'travel' | 'email' | 'git' | 'calendar' | 'purchase' | 'meeting';
  description: string;
  status: 'pending' | 'approved' | 'executing' | 'completed' | 'rejected';
  timestamp: string;
  isIrreversible: boolean;
  costEstimate?: string;
  details: Record<string, string>;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  voiceAudioUrl?: string; // base64 encoded speech from API
  activeAgent?: AgentType;
  steps?: { agent: AgentType; action: string; duration: string; output?: string }[];
}

export interface UserProfile {
  name: string;
  assistantPreferences: {
    voicepack: string;
    speakingSpeed: number;
    personality: string;
    model: string;
    allowAlwaysListening: boolean;
    requireApprovalForFinancial: boolean;
  };
  schedule: { id: string; title: string; time: string; category: string; done: boolean }[];
  reminders: { id: string; text: string; due: string; priority: 'high' | 'medium' | 'low' }[];
  todayWeather: {
    temp: number;
    text: string;
    high: number;
    low: number;
    city: string;
  };
}

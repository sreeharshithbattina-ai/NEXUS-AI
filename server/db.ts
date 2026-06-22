import fs from "fs";
import path from "path";
import { UserProfile, MemoryItem, KnowledgeDoc, AutomationTask, Message, OSLog } from "../src/types";

const DB_FILE = path.join(process.cwd(), "db.json");

interface DBStructure {
  profile: UserProfile;
  memories: MemoryItem[];
  documents: KnowledgeDoc[];
  automationQueue: AutomationTask[];
  messages: Message[];
  logs: OSLog[];
}

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

class FileDatabase {
  private schema: DBStructure;

  constructor() {
    this.schema = {
      profile: INITIAL_PROFILE,
      memories: INITIAL_MEMORIES,
      documents: INITIAL_DOCUMENTS,
      automationQueue: INITIAL_AUTOMATION_QUEUE,
      messages: [],
      logs: []
    };
    this.init();
  }

  private init() {
    try {
      if (fs.existsSync(DB_FILE)) {
        const raw = fs.readFileSync(DB_FILE, "utf-8");
        this.schema = JSON.parse(raw);
        console.log("Persistent File DB loaded successfully:", DB_FILE);
      } else {
        this.save();
        console.log("Initialized persistent File DB:", DB_FILE);
      }
    } catch (err) {
      console.error("Failed to load or initialize database:", err);
    }
  }

  private save() {
    try {
      fs.writeFileSync(DB_FILE, JSON.stringify(this.schema, null, 2), "utf-8");
    } catch (err) {
      console.error("Failed to persist database changes:", err);
    }
  }

  public getProfile(): UserProfile {
    return this.schema.profile;
  }

  public updateProfile(p: Partial<UserProfile>): UserProfile {
    this.schema.profile = { ...this.schema.profile, ...p };
    this.save();
    return this.schema.profile;
  }

  public getMemories(): MemoryItem[] {
    return this.schema.memories;
  }

  public addMemory(m: MemoryItem): MemoryItem {
    this.schema.memories.push(m);
    this.save();
    return m;
  }

  public deleteMemory(id: string): boolean {
    const len = this.schema.memories.length;
    this.schema.memories = this.schema.memories.filter(x => x.id !== id);
    this.save();
    return this.schema.memories.length < len;
  }

  public getDocuments(): KnowledgeDoc[] {
    return this.schema.documents;
  }

  public addDocument(d: KnowledgeDoc): KnowledgeDoc {
    this.schema.documents.push(d);
    this.save();
    return d;
  }

  public deleteDocument(id: string): boolean {
    const len = this.schema.documents.length;
    this.schema.documents = this.schema.documents.filter(x => x.id !== id);
    this.save();
    return this.schema.documents.length < len;
  }

  public getTasks(): AutomationTask[] {
    return this.schema.automationQueue;
  }

  public addTask(t: AutomationTask): AutomationTask {
    this.schema.automationQueue.push(t);
    this.save();
    return t;
  }

  public updateTaskStatus(id: string, s: AutomationTask["status"]): AutomationTask | null {
    const task = this.schema.automationQueue.find(x => x.id === id);
    if (task) {
      task.status = s;
      this.save();
      return task;
    }
    return null;
  }

  public getLogs(): OSLog[] {
    return this.schema.logs;
  }

  public addLog(l: OSLog): OSLog {
    this.schema.logs.push(l);
    this.save();
    return l;
  }

  public getMessages(): Message[] {
    return this.schema.messages;
  }

  public saveMessage(m: Message): Message {
    this.schema.messages.push(m);
    this.save();
    return m;
  }

  public clearAll() {
    this.schema.messages = [];
    this.schema.logs = [];
    this.save();
  }
}

export const dbInstance = new FileDatabase();

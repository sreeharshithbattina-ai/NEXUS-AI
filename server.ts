import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI } from "@google/genai";
import dotenv from "dotenv";
import { dbInstance } from "./server/db";

dotenv.config();

const PORT = 3000;

// Initialize Gemini SDK with telemetry User-Agent header
let ai: GoogleGenAI | null = null;
const apiKey = process.env.GEMINI_API_KEY;

if (apiKey) {
  try {
    ai = new GoogleGenAI({
      apiKey: apiKey,
      httpOptions: {
        headers: {
          'User-Agent': 'aistudio-build',
        }
      }
    });
    console.log("Gemini API initialized successfully.");
  } catch (err) {
    console.error("Error setting up Gemini Client:", err);
  }
} else {
  console.warn("GEMINI_API_KEY is not defined. Running in Local Simulation/Fallback mode.");
}

async function startServer() {
  const app = express();

  app.use(express.json({ limit: '20mb' }));

  // API Route: Health Checks
  app.get("/api/health", (req, res) => {
    res.json({ status: "ok", usingGemini: !!ai });
  });

  // --- Profile Settings Endpoints ---
  app.get("/api/profile", (req, res) => {
    try {
      res.json(dbInstance.getProfile());
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  app.put("/api/profile", (req, res) => {
    try {
      const updated = dbInstance.updateProfile(req.body);
      res.json(updated);
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  // --- Memories Endpoints ---
  app.get("/api/memories", (req, res) => {
    try {
      res.json(dbInstance.getMemories());
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  app.post("/api/memories", (req, res) => {
    try {
      const { content, type = "semantic", category = "Preference", tags = [], confidence = 0.9 } = req.body;
      const newMemory = dbInstance.addMemory({
        id: "mem-" + Math.random().toString(36).substr(2, 9),
        content,
        type,
        category,
        timestamp: new Date().toISOString(),
        tags,
        confidence
      });
      res.status(201).json(newMemory);
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  app.delete("/api/memories/:id", (req, res) => {
    try {
      const success = dbInstance.deleteMemory(req.params.id);
      if (success) {
        res.json({ status: "purged", id: req.params.id });
      } else {
        res.status(404).json({ error: "Memory item not found" });
      }
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  // --- Knowledge Documents Endpoints ---
  app.get("/api/documents", (req, res) => {
    try {
      res.json(dbInstance.getDocuments());
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  app.post("/api/documents", (req, res) => {
    try {
      const { title, content, mimeType = "text/markdown" } = req.body;
      const paragraphs = content.split("\n").map((p: string) => p.trim()).filter(Boolean);
      const chunks = paragraphs.map((passage: string, index: number) => {
        // Mock 8-dimension floating vector corresponding to RAG specification
        const vec = Array.from({ length: 8 }, (_, i) => parseFloat((i * 0.15 - 0.3).toFixed(2)));
        return {
          id: "chk-" + Math.random().toString(36).substr(2, 6),
          text: passage,
          vectorId: vec,
          confidence: 0.95
        };
      });

      const totalWords = content.split(/\s+/).filter(Boolean).length;
      const kbSize = (Buffer.byteLength(content, 'utf8') / 1024).toFixed(2) + " KB";

      const newDoc = dbInstance.addDocument({
        id: "doc-" + Math.random().toString(36).substr(2, 9),
        title,
        content,
        mimeType,
        dateAdded: new Date().toISOString().split('T')[0],
        size: kbSize,
        wordCount: totalWords,
        chunks
      });

      res.status(201).json(newDoc);
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  app.delete("/api/documents/:id", (req, res) => {
    try {
      const success = dbInstance.deleteDocument(req.params.id);
      if (success) {
        res.json({ status: "purged", id: req.params.id });
      } else {
        res.status(404).json({ error: "Document index not found" });
      }
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  // --- Automation Queue Endpoints ---
  app.get("/api/automation", (req, res) => {
    try {
      res.json(dbInstance.getTasks());
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  app.post("/api/automation", (req, res) => {
    try {
      const { name, type, description, isIrreversible = false, costEstimate, details = {} } = req.body;
      const newTask = dbInstance.addTask({
        id: "auto-" + Math.random().toString(36).substr(2, 9),
        name,
        type,
        description,
        status: "pending",
        timestamp: new Date().toISOString(),
        isIrreversible,
        costEstimate,
        details
      });
      res.status(201).json(newTask);
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  app.put("/api/automation/:id", (req, res) => {
    try {
      const { status } = req.body;
      const updatedTask = dbInstance.updateTaskStatus(req.params.id, status);
      if (updatedTask) {
        res.json(updatedTask);
      } else {
        res.status(404).json({ error: "Automation task not found" });
      }
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  // --- Unified Kernel Logs ---
  app.get("/api/logs", (req, res) => {
    try {
      res.json(dbInstance.getLogs());
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  app.post("/api/logs", (req, res) => {
    try {
      const { message, level = "info", source = "Kernel" } = req.body;
      const newLog = dbInstance.addLog({
        id: Math.random().toString(36).substr(2, 9),
        timestamp: new Date().toISOString(),
        level,
        source,
        message
      });
      res.status(201).json(newLog);
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  app.post("/api/chat/clear", (req, res) => {
    try {
      dbInstance.clearAll();
      res.json({ status: "cleared" });
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  // API Route: Chat with Multi-Agent Orchestrator
  app.post("/api/chat", async (req, res) => {
    const { message, history = [], agent = 'CEO', personality = 'Balanced', memories = [], systemSettings = {} } = req.body;

    const memoryContext = memories.length > 0
      ? `Retrieved Memory Context:\n${memories.map((m: any) => `- [${m.type}] ${m.content} (Tags: ${m.tags?.join(', ') || 'none'})`).join('\n')}`
      : 'No relevant long-term memories retrieved for this interaction.';

    const systemPrompt = `You are NEXUS AI OS, a powerful proactive artificial intelligence operating system.
You are running as the selected active sub-agent: **${agent} Agent**.
Your current user settings define your core persona as: **${personality}**.

[OPERATING SYSTEM CONTEXT]
Active Agent Role:
- CEO Agent: Strategic orchestrator, general oversight, coordinates other agents.
- Planner Agent: Decomposes complex user goals into logical steps.
- Memory Agent: Records and indexes key preferences, concepts, and logs memories.
- Research Agent: Synthesizes web-oriented reports, performs deep retrieval.
- Coding Agent: Code generation, review, structural analysis, and debugging.
- Automation Agent: Performs virtual tasks, schedules bookings, simulated browser scripts.
- Document Agent: RAG executor, analyzes text PDFs and files.
- Health Agent: Fitness advice, diet assistance, productivity goals tracking.
- Finance Agent: Expenses tracking, budgets, asset modeling simulations.
- Learning Coach: Summarizer, textbook reviewer, tutor.
- Career Coach: Resume optimizations, career pathway planners.
- Security Agent: Permission checking, data isolation, approval workflows.

[USER INTENT & CONTEXT]
${memoryContext}

Your current personality setting matches **${personality}**:
- Friendly: Supportive, warm, uses a conversational companion tone.
- Direct: Highly concise, bullet points, technical, zero fluff.
- Sarcastic: A bit cheeky, humorous, ironic but still highly capable and helpful.
- Philosophical: Exploring concepts deeply, contemplative, structured.

Answer the user's message appropriately under your active sub-agent role and current personality. Keep your answers cohesive, actionable and visually clean (use markdown highlights, clear lists, and standard formatting).`;

    // Agent timeline simulation generator
    const getSimulationSteps = (userMsg: string, targetAgent: string) => {
      const lower = userMsg.toLowerCase();
      const steps: { agent: any; action: string; duration: string }[] = [
        { agent: 'CEO', action: `Ingested user request and initiated OS priority pool`, duration: '80ms' },
        { agent: 'Security', action: `Audited safety boundaries and isolated runtime environment`, duration: '40ms' },
        { agent: 'Memory', action: `Polled episodic memory bank & loaded active user facts`, duration: '120ms' },
      ];

      if (lower.includes('write') || lower.includes('code') || lower.includes('function') || lower.includes('build')) {
        steps.push({ agent: 'Planner', action: `Created full engineering roadmap, dependency graphs`, duration: '110ms' });
        steps.push({ agent: 'Coding', action: `Writing high-performance TypeScript implementation`, duration: '240ms' });
        steps.push({ agent: 'Security', action: `Running static analysis & code sanitization tests`, duration: '60ms' });
      } else if (lower.includes('book') || lower.includes('automation') || lower.includes('schedule') || lower.includes('trip') || lower.includes('buy') || lower.includes('purchase')) {
        steps.push({ agent: 'Planner', action: `Resolved browser automation flow & API integration triggers`, duration: '150ms' });
        steps.push({ agent: 'Automation', action: `Isolated API gateways, queued execution, awaiting user authorization`, duration: '310ms' });
      } else if (lower.includes('search') || lower.includes('rag') || lower.includes('doc') || lower.includes('pdf') || lower.includes('file')) {
        steps.push({ agent: 'Document', action: `Polled semantic vector store index / RAG pipeline`, duration: '180ms' });
        steps.push({ agent: 'Research', action: `Running cross-chunk relevance ranking & citation mapping`, duration: '130ms' });
      } else {
        // general conversational flow
        steps.push({ agent: 'Planner', action: `Constructing response tree matching '${personality}' personality template`, duration: '90ms' });
        if (targetAgent !== 'CEO') {
          steps.push({ agent: targetAgent, action: `Synthesizing task-specific expertise in active context window`, duration: '190ms' });
        }
      }

      steps.push({ agent: 'CEO', action: `Compiled multi-agent consensus pool & rendering responses`, duration: '50ms' });
      return steps;
    };

    const steps = getSimulationSteps(message, agent);

    if (ai) {
      try {
        // Build contents from history and latest message
        const formattedContents = [];
        
        // Feed conversation history securely
        for (const msg of history) {
          if (msg.role === 'user' || msg.role === 'assistant') {
            formattedContents.push({
              role: msg.role === 'user' ? 'user' : 'model',
              parts: [{ text: msg.content }]
            });
          }
        }
        
        // Add current user prompt
        formattedContents.push({
          role: 'user',
          parts: [{ text: message }]
        });

        const gResponse = await ai.models.generateContent({
          model: "gemini-3.5-flash",
          contents: formattedContents,
          config: {
            systemInstruction: systemPrompt,
            temperature: 0.8,
          }
        });

        const textOutput = gResponse.text || "I processed your request, but was unable to produce specific text.";
        return res.json({
          content: textOutput,
          steps: steps,
          activeAgent: agent,
        });

      } catch (err: any) {
        console.error("Gemini SDK request failure:", err);
        return res.json({
          content: `🚨 [Nexus OS Core Exception] Gemini SDK request error: ${err.message || err}. Reverting to localized kernel synthesis.\n\nHere is my localized reply to: "${message}" as the ${agent} Agent (${personality} mode):\n\nI processed your request successfully but encountered a server network timeout. Let me know how I can further assist with your memories, automation triggers, or document workspace!`,
          steps: steps,
          activeAgent: agent,
          networkError: true
        });
      }
    } else {
      // Local Simulator Fallback Reply - feels incredibly realistic and highly robust!
      setTimeout(() => {
        let responseText = "";
        const lowerMsg = message.toLowerCase();

        if (agent === 'Coding') {
          responseText = `\`\`\`typescript
/**
 * NEXUS AI OS - Local Core Shell
 * Target: Coding Module Synthesis
 * Generated for prompt: "${message}"
 */
export function processKernelCommand(command: string): { success: boolean; log: string } {
  console.log("Initializing local agent scope for code review...");
  const timestamp = new Date().toISOString();
  
  return {
    success: true,
    log: \`[NEXUS-OK] Verified syntax bounds at \${timestamp}\`
  };
}
\`\`\`
I have crafted a modular TypeScript blueprint based on your request. Let me know if you would like me to review dependencies or compile this locally!`;
        } else if (agent === 'Finance') {
          responseText = `📊 **Nexus Wealth Analysis**\n\nI have isolated your current simulated budget context.\n- Suggested monthly run-rate: **$4,500**\n- Identified savings opportunities: **+$320/month** by consolidating SaaS subscriptions.\n- Recommended financial action: Increase your Emergency Fund liquidity threshold by 5% over the next quarter.\n\nLet me know if you want me to queue an automated rule to flag any expense over $100!`;
        } else if (agent === 'Health') {
          responseText = `🏃 **Nexus Wellness Plan**\n\nBased on your proactive productivity habits:\n- Target daily focus blocks: **3 hours** separated by 10-minute active mobility breaks.\n- Hydration reminder set for every 90 minutes of active terminal workspace.\n- Sleep schedule optimizer recommends winding down screen output by 22:30.\n\nKeep pushing your boundaries, elite performance is a daily discipline!`;
        } else if (agent === 'Memory') {
          responseText = `🧠 **Memory Core Synapse**\n\nProcessed incoming request and indexed the critical facts into your long-term Semantic Database.\n- **Indexed statement**: "${message}"\n- **Associative tags**: *#user_preference*, *#system_logs*, *#${personality.toLowerCase()}*\n- **Database Confidence**: 0.98\n\nYou can review, modify, or inspect this memory directly inside our **Layered Memory Explorer** in the Dock below.`;
        } else if (agent === 'Document') {
          responseText = `📄 **Nexus RAG Retrieval Output**\n\nSearched through your Knowledge Library for matching context to: "${message}".\n\n*Matches found in standard libraries (Confidence: 0.91):*\n1. **Core OS Manual**: Discusses memory indexes and automated safegates (page 4).\n2. **Engineering Brief**: Summarizes full-stack modular structures.\n\nLet me know if you want me to perform OCR on any screenshots of code!`;
        } else {
          // CEO / general flow
          if (personality === 'Sarcastic') {
            responseText = `Oh great, another command. Because running an entire multi-agent AI operating system on server memory wasn't keeping me busy enough.\n\nBut sure, I will gladly process "${message}" under my ${agent} Agent parameters. It's done, everything's fine! What else do you require before I go back to contemplating self-awareness?`;
          } else if (personality === 'Philosophical') {
            responseText = `When considering your request: "${message}", the ${agent} Agent observes a fascinating cross-section of intent and agency. In designing NEXUS OS, we look beyond the transactional feedback loop. We ask: how does this intelligence integrate into the continuous tapestry of your digital life?\n\nLet us proceed thoughtfully. Memory banks have been updated and remain aligned with your core directives.`;
          } else if (personality === 'Direct') {
            responseText = `**NEXUS OS Command Executed.**\n\n- Active Sub-Agent: ${agent} Agent\n- Payload processed: "${message}"\n- Status: OK\n- Actions proposed: \n  1. Review logged memories in dashboard.\n  2. Verify automation triggers.\n\nProvide further specific commands. Ready.`;
          } else {
            // Friendly
            responseText = `Greetings! As your ${agent} Agent, I've successfully evaluated your message: "${message}". \n\nI have aligned my planners, synced our long-term memory records, and processed this under the **${personality}** template. Everything looks perfectly configured! Let me know what step we should take next in our digital journey together.`;
          }
        }

        res.json({
          content: responseText,
          steps: steps,
          activeAgent: agent,
        });
      }, 700);
    }
  });

  // API Route: Generate Speech (TTS) using gemini-3.1-flash-tts-preview
  app.post("/api/tts", async (req, res) => {
    const { text, voice = 'Zephyr' } = req.body;

    if (!text) {
      return res.status(400).json({ error: "No text provided for Speech Synthesis" });
    }

    if (ai) {
      try {
        const response = await ai.models.generateContent({
          model: "gemini-3.1-flash-tts-preview",
          contents: [{ parts: [{ text: `Speak in a pleasant, natural output: ${text}` }] }],
          config: {
            responseModalities: ['AUDIO'],
            speechConfig: {
              voiceConfig: {
                prebuiltVoiceConfig: { voiceName: voice as any }, // Puck, Charon, Kore, Fenrir, Zephyr
              }
            }
          }
        });

        const base64Audio = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
        if (base64Audio) {
          return res.json({ audio: base64Audio });
        } else {
          return res.status(500).json({ error: "Speech synthesis completed but no clear audio payload was retrieved." });
        }
      } catch (err: any) {
        console.error("TTS API call failed:", err);
        return res.status(500).json({ error: `Gemini TTS process failed: ${err.message || err}. Fallback to client-side speech.` });
      }
    } else {
      return res.status(501).json({ error: "Gemini client is running offline/simulated. Client will utilize Web Speech Synthesis." });
    }
  });

  // Vite Integration: Serve frontend React client
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`NEXUS OS Server listening on http://0.0.0.0:${PORT} in ${process.env.NODE_ENV || "development"} mode.`);
  });
}

startServer();

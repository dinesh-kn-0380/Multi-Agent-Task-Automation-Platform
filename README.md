# 🤖 Multi-Agent Task Automation Platform

> **Built on top of [chatbot-ui](https://github.com/dinesh-kn-0380/chatbot-ui)**  
> Aligned with **SDG 9 — Industry, Innovation, and Infrastructure**

A production-grade AI system that transforms a single-agent chatbot into an intelligent **multi-agent orchestration platform** using a Planner → Executor → Final Agent pipeline.

---

## 🏗 Architecture

```
User Input
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│              Multi-Agent Workflow (Orchestrator)         │
│                                                         │
│  ① Planner Agent                                        │
│     └─ Understands goal → Decomposes into ordered tasks │
│                                                         │
│  ② Executor Agents (parallel where possible)            │
│     ├─ Task 1 → Output 1                               │
│     ├─ Task 2 → Output 2                               │
│     └─ Task N → Output N                               │
│                                                         │
│  ③ Final Response Agent                                │
│     └─ Aggregates → Structured Response               │
└─────────────────────────────────────────────────────────┘
    │
    ▼
Structured Output:
  • Goal Understanding
  • Task Breakdown
  • Agent Execution Results
  • Final Answer (Markdown)
```

---

## 📁 Project Structure

```
Multi-Agent-Task-Automation-Platform/
│
├── chatbot-ui-base/              ← Cloned from dinesh-kn-0380/chatbot-ui
│   └── app/api/multi-agent/      ← NEW: Next.js proxy route
│
├── backend/
│   ├── agents/
│   │   ├── planner_agent.py      ← Goal decomposition
│   │   ├── executor_agent.py     ← Parallel task execution
│   │   └── final_agent.py        ← Response aggregation + refinement
│   ├── workflows/
│   │   └── orchestrator.py       ← Graph-based pipeline coordination
│   ├── memory/
│   │   └── conversation_memory.py← Session memory (sliding window)
│   ├── api/
│   │   └── server.py             ← Flask REST + SSE API
│   └── requirements.txt
│
├── frontend/
│   ├── components/multi-agent/
│   │   ├── AgentProgressPanel.tsx ← Real-time phase indicator
│   │   ├── StructuredResponseCard.tsx ← Rich structured output
│   │   └── MultiAgentChatInput.tsx   ← SSE-streaming input
│   ├── styles/
│   │   └── multi-agent.css       ← Dark glassmorphism UI
│   └── types/
│       └── multi-agent-api.ts    ← TypeScript API client
│
├── docker/
│   └── start.sh                  ← Container startup script
├── Dockerfile                    ← Multi-stage build
├── docker-compose.yml            ← Service orchestration
└── .env.example                  ← Environment template
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- Node.js 20+
- OpenAI API Key
- (Optional) Supabase project for chatbot persistence

### 2. Environment Setup

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY and Supabase credentials
```

### 3. Run Backend (Flask)

```bash
cd backend
pip install -r requirements.txt
python -m backend.api.server
# Runs on http://localhost:5000
```

### 4. Run Frontend (Next.js)

```bash
cd chatbot-ui-base
npm install
npm run dev
# Runs on http://localhost:3000
```

### 5. Docker (All-in-one)

```bash
docker-compose up --build
# Backend: http://localhost:5000
# Frontend: http://localhost:3000
```

---

## 🔌 API Reference

### `POST /api/chat`
Run the full multi-agent pipeline.

**Request:**
```json
{
  "message": "Create a 4-week marketing plan for a SaaS product",
  "session_id": "optional-uuid",
  "stream": false
}
```

**Response:**
```json
{
  "run_id": "...",
  "goal_understanding": "...",
  "task_breakdown": [
    { "id": "task_1", "title": "...", "status": "completed" }
  ],
  "agent_results": [
    { "task_id": "task_1", "output": "...", "confidence": 0.92 }
  ],
  "final_answer": "## Marketing Plan\n...",
  "timing": { "planning": 1.2, "execution": 4.5, "total": 6.8 }
}
```

Set `"stream": true` for Server-Sent Events.

### `GET /api/health`
Service health check.

### `POST /api/session/clear`
Clear conversation memory for a session.

---

## 🧠 Agent Design Details

### Planner Agent
- Receives raw user goal + conversation context
- Returns structured JSON task graph with dependency tracking
- Temperature: 0.3 (deterministic planning)
- Max tasks: 8

### Executor Agent
- Executes tasks in dependency order
- Parallel execution for independent tasks (`asyncio.gather`)
- Chain-of-thought reasoning captured per task
- Returns confidence score + caveats

### Final Response Agent
- Aggregates all execution results
- Iterative refinement loop (up to 2 passes)
- Outputs fully structured Markdown-formatted final answer
- Detects incomplete responses and re-runs if needed

---

## 🎨 Frontend Integration

Import the multi-agent components into your chatbot UI:

```tsx
// In your chat page
import { MultiAgentChatInput } from "@/components/multi-agent/MultiAgentChatInput"
import { StructuredResponseCard } from "@/components/multi-agent/StructuredResponseCard"
import "@/styles/multi-agent.css"

// Render the agent input
<MultiAgentChatInput
  sessionId={sessionId}
  onResponse={(response) => setResponses(prev => [...prev, response])}
/>

// Render structured responses
{responses.map(r => (
  <StructuredResponseCard key={r.run_id} response={r} />
))}
```

---

## 📊 Output Format

Every multi-agent response contains:

| Section | Description |
|---|---|
| **Goal Understanding** | Restated user intent with nuance |
| **Task Breakdown** | Ordered tasks with completion status |
| **Agent Execution Results** | Per-task outputs with confidence scores |
| **Final Answer** | Comprehensive Markdown-formatted response |

---

## 🌍 SDG 9 Alignment

This platform directly supports **SDG 9 (Industry, Innovation, and Infrastructure)** by:

- Enabling **intelligent automation** for complex multi-step tasks
- Providing **modular, scalable architecture** for production AI systems
- Supporting **innovation** through multi-agent collaboration
- Making advanced AI orchestration **accessible** through an open-source foundation

---

## 🔧 Configuration

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required. OpenAI API key |
| `PLANNER_MODEL` | `gpt-4o-mini` | Model for the Planner Agent |
| `EXECUTOR_MODEL` | `gpt-4o-mini` | Model for Executor Agents |
| `FINAL_MODEL` | `gpt-4o-mini` | Model for the Final Agent |
| `PORT` | `5000` | Flask backend port |
| `FLASK_DEBUG` | `false` | Enable Flask debug mode |
| `NEXT_PUBLIC_BACKEND_URL` | `http://localhost:5000` | Backend URL for frontend |

---

## 📄 License

Inherits the license from the original [chatbot-ui](https://github.com/mckaywrigley/chatbot-ui) project.

# 🚀 AI Business Idea Validator

> **An enterprise-grade AI Business Intelligence Platform** that validates startup ideas through a multi-agent pipeline powered by GPT-4o, Retrieval-Augmented Generation (RAG), and explainable scoring.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-orange.svg)](https://openai.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://docker.com)

---

## 📌 Problem Statement

Entrepreneurs waste months and significant capital building startups that fail due to poor initial validation. **AI Business Idea Validator** solves this by instantly analyzing a business idea across 5 critical dimensions — market demand, financial feasibility, risk landscape, competitive positioning, and growth scalability — using an autonomous multi-agent AI pipeline grounded in proven business frameworks.

---

## 🎯 Target Users & Pain Points

| User | Pain Point |
|:---|:---|
| **Early-stage founders** | No structured way to stress-test ideas before investing time |
| **University students** | Lack access to mentors or consultants for idea feedback |
| **Startup incubators** | Manual screening of hundreds of pitches is slow and inconsistent |
| **Angel investors** | Need fast, objective first-pass analysis before deeper due diligence |

---

## 🤖 AI Capability Used

This application uses **multi-agent text generation** (not just a simple chatbot or CRUD wrapper):
- 5 independent analytical AI agents, each specialized in one business domain
- 2 generative agents (SWOT + Business Model Canvas)
- 1 final recommendation agent that synthesizes all results
- RAG grounding: every analysis is anchored in retrieved business framework knowledge
- Explainable confidence scores with natural language reasoning

---

## 🏆 Competitor Reference Apps

| Competitor | Strength | Our Differentiator |
|:---|:---|:---|
| [IdeaBuddy](https://ideabuddy.com) | Guided idea planning templates | We use AI agents, not static templates |
| [Validator AI](https://validatorai.com) | Single-prompt AI feedback | We run 8 sequential specialized agents |
| [ChatGPT](https://chat.openai.com) | General-purpose AI analysis | We have domain-specific RAG grounding + scoring |
| [Bizplan](https://bizplan.com) | Business plan builder | We focus on validation, not writing |
| [Lean Canvas](https://leanstack.com) | Structured lean canvas tool | We automate the canvas generation via BMC agent |

---

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User (Browser)                          │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
┌────────────────────────▼────────────────────────────────────┐
│              React Frontend (Port 3000)                     │
│   IdeaForm → AnalysisResults → Dashboard → Reports         │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────┐
│           FastAPI Backend (Port 8000)                       │
│   /api/v1/analysis  /api/v1/dashboard  /api/v1/auth        │
│   Input Validation → Security → AnalysisOrchestrator       │
└──────┬──────────────────────────────────────────┬───────────┘
       │                                          │
┌──────▼──────────────────────┐    ┌─────────────▼────────────┐
│   8-Agent Pipeline          │    │   RAG Vector Store       │
│  ┌─────────────────────┐    │    │   (SQLite + OpenAI       │
│  │ 1. Market Agent     │    │    │    text-embedding-3-small)│
│  │ 2. Financial Agent  │    │    │                          │
│  │ 3. Risk Agent       │◄───┼────│  Frameworks:             │
│  │ 4. Competition Agent│    │    │  • SWOT Analysis         │
│  │ 5. Growth Agent     │    │    │  • Lean Startup          │
│  │ 6. SWOT Generator   │    │    │  • Business Model Canvas │
│  │ 7. BMC Generator    │    │    │  • Porter's Five Forces  │
│  │ 8. Recommend. Agent │    │    │  • Market Research       │
│  └─────────────────────┘    │    │  • Financial Validation  │
└──────────────────┬──────────┘    │  • Competitive Analysis  │
                   │               │  • Startup Failures      │
┌──────────────────▼──────────┐    └──────────────────────────┘
│   SQLite / PostgreSQL DB    │
│   Users, Ideas, Results     │
└─────────────────────────────┘
```

---

## 🧠 LLM & Model Selection

### Model Comparison

| Model | Context Window | Cost (1K tokens) | Strengths | Weaknesses |
|:---|:---|:---|:---|:---|
| **GPT-4o** ✅ Selected | 128K | ~$0.005 input | Best reasoning, JSON reliability, fast | Costs more than GPT-3.5 |
| GPT-3.5-Turbo | 16K | ~$0.0005 input | Very cheap, fast | Unreliable JSON output, weaker reasoning |
| Claude 3 Sonnet | 200K | ~$0.003 input | Long context, nuanced writing | Slower, no structured output guarantee |
| Gemini 1.5 Pro | 1M tokens | ~$0.0035 input | Massive context window | Less predictable JSON formatting |
| Llama 3 (local) | 8K | Free (compute) | No API cost | Requires GPU, lower reasoning quality |

### Final Choice: GPT-4o

**Justification:**
1. **Structured JSON reliability** — Our 8 agents all output strict JSON schemas. GPT-4o is the most reliable at following complex JSON output instructions without hallucinating extra fields.
2. **Reasoning depth** — Business analysis requires chain-of-thought reasoning across financial, market, and risk dimensions. GPT-4o outperforms GPT-3.5 significantly on multi-step domain reasoning.
3. **Context window** — 128K tokens comfortably handles all 8 framework documents retrieved via RAG plus the idea context in a single call.
4. **OpenAI API ecosystem** — Same API also powers `text-embedding-3-small` for our RAG vector store, simplifying integration to a single API key.

### Embedding Model: `text-embedding-3-small`
Used for RAG document indexing and similarity search. 1536-dimensional vectors at minimal cost (~$0.00002/1K tokens).

---

## 🔬 Prompt Engineering

### Techniques Implemented

| Technique | Where Used | Example |
|:---|:---|:---|
| **Zero-shot prompting** | All 8 agent prompts | Direct instruction with no examples |
| **Few-shot prompting** | Market & Risk agents | 2 example inputs/outputs embedded in prompt |
| **Chain-of-Thought (CoT)** | Market & Risk agents | "Think step by step before scoring" instruction |
| **System prompt design** | All agents | Role, tone, format constraint, output schema |
| **Structured output prompting** | All 8 prompts | Explicit JSON schema with typed fields |
| **Role prompting** | All agents | "You are an expert Market Intelligence Agent…" |
| **Negative prompting** | All prompts | "Do NOT include markdown code blocks or backticks" |
| **Prompt chaining** | Orchestrator | Agent outputs feed into Recommendation Agent |

### Prompt Management
- All prompts stored as plain `.txt` files in [`backend/app/prompts/`](backend/app/prompts/)
- Variables templated using Python f-string `{idea_context}` and `{retrieved_context}` placeholders
- Prompt files are versioned in Git alongside code

### Prompt Files
```
backend/app/prompts/
├── market_analysis.txt       # Market Intelligence Agent
├── financial_analysis.txt    # Financial Feasibility Agent
├── risk_analysis.txt         # Risk Assessment Agent
├── competition_analysis.txt  # Competition Analysis Agent
├── growth_analysis.txt       # Growth Potential Agent
├── swot_generation.txt       # SWOT Generator
├── bmc_generation.txt        # Business Model Canvas Generator
└── final_recommendation.txt  # Final Recommendation Agent
```

---

## 📚 RAG Pipeline Design

### Architecture
```
Knowledge Docs → Chunking → OpenAI Embeddings → SQLite Vector Store
                                                        ↓
Business Idea Query → Embed Query → Cosine Similarity Search → Top-K Chunks
                                                        ↓
                              Retrieved Context → Injected into Agent Prompt
```

### Implementation Details

| Step | Details |
|:---|:---|
| **Data Sources** | 8 business framework `.txt` files in `app/knowledge/` |
| **Chunking** | Paragraph-level split (`\n\n`), each chunk ~200-500 tokens |
| **Embedding Model** | `text-embedding-3-small` (1536-dim vectors) |
| **Vector Store** | Custom SQLite database (`vector_store.db`) — no binary dependencies |
| **Similarity** | Pure-Python cosine similarity computation |
| **Retrieval** | Top-2 most relevant chunks per agent query |
| **Injection** | `{retrieved_context}` variable in every agent prompt |

### Knowledge Base Frameworks
- `swot_analysis.txt` — SWOT methodology guidelines
- `lean_startup.txt` — Lean Startup + MVP principles
- `business_model_canvas.txt` — 9-block BMC framework
- `porter_five_forces.txt` — Porter's competitive forces model
- `market_research.txt` — TAM/SAM/SOM methodology
- `financial_validation.txt` — Break-even and unit economics
- `competitive_analysis.txt` — Differentiation strategies
- `startup_failure_patterns.txt` — Common startup failure modes

---

## 🤖 Agent Architecture & Pipeline

### Multi-Agent Design (Plan-and-Execute pattern)

The `AnalysisOrchestrator` runs **8 agents sequentially**, with each agent's output feeding into the next stages:

```
Step 1: Market Intelligence Agent    → market_score (0-25 pts)
Step 2: Competition Analysis Agent   → competition_score (0-20 pts)
Step 3: Financial Feasibility Agent  → financial_score (0-20 pts)
Step 4: Risk Assessment Agent        → risk_score (0-20 pts)
Step 5: Growth Potential Agent       → growth_score (0-15 pts)
Step 6: SWOT Generator               → Structured S/W/O/T grid
Step 6: BMC Generator                → 9-block Business Model Canvas
Step 7: Final Recommendation Agent  → 100-point explainable score + action plan
```

### Each Agent Outputs
```json
{
  "score": 21,
  "confidence": 87,
  "confidence_reason": "Strong TAM evidence with multiple framework alignments",
  "key_findings": ["..."],
  "risks": ["..."],
  "opportunities": ["..."],
  "reasoning": "...",
  "retrieved_knowledge_sources": ["Market Research", "Lean Startup"],
  "_audit_log": { "processing_time": 2.3, "agent_name": "Market Agent" }
}
```

### Guardrails & Safety
- **Prompt injection detection** — regex patterns block `"ignore previous instructions"` and similar attacks ([`security.py`](backend/app/utils/security.py))
- **Input sanitization** — HTML/control-character stripping on all user text fields
- **Payload size limits** — Title: 150 chars, text fields: 4000 chars max
- **Fallback responses** — Every agent has a `get_fallback_response()` method that returns safe defaults if the LLM call fails
- **JSON validation** — All agent outputs are validated as JSON before further processing; invalid responses trigger fallback

---

## 📊 Evaluation Framework

### Evaluation Dataset
- **40 business ideas** spanning 10 sectors: SaaS, E-commerce, AI/ML, Healthcare, EdTech, FinTech, Logistics, FoodTech, Creator Economy, Marketplaces
- Each idea includes: expected viability range, expected risk level, category

### Evaluation Metrics

| Metric | Description | Result |
|:---|:---|:---|
| **Average Viability Score** | Mean 100-pt score across all validated ideas | Computed per run |
| **Average Agent Confidence** | Mean confidence % across all agents | Computed per run |
| **Average Latency (sec)** | Time per idea validation end-to-end | Computed per run |
| **Viability Consistency Rate** | % of ideas scoring within expected range | Computed per run |
| **Risk Assessment Consistency** | % of risk levels matching expected level | Computed per run |
| **LLM-as-Judge Score** | GPT-4o rates each output 1-5 on relevance, accuracy, actionability | Available in evaluate.py |

### Running the Evaluation
```bash
# Dry run (mock responses, no API cost)
cd backend
venv\Scripts\python app\evaluation\evaluate.py --dry-run

# Real run with OpenAI (first 5 ideas)
venv\Scripts\python app\evaluation\evaluate.py 5

# Full benchmark (all 40 ideas)
venv\Scripts\python app\evaluation\evaluate.py 40
```

### LLM-as-Judge
The evaluation runner includes an automated LLM-as-judge mode that sends agent outputs to GPT-4o for objective quality scoring:
```python
# Rates each analysis on:
# - Relevance (1-5): Does it address the idea correctly?
# - Accuracy (1-5): Are claims grounded in retrieved frameworks?
# - Actionability (1-5): Are recommendations concrete and useful?
```

---

## 🛡️ Responsible AI & Limitations

### Hallucination Mitigation
- All agent responses are **grounded in retrieved business framework documents** via RAG
- Agents explicitly cite `retrieved_knowledge_sources` in every output
- Fallback responses activate when the LLM returns invalid or empty content
- JSON schema enforcement prevents unconstrained free-text responses

### Known Limitations
1. **Not a substitute for expert advice** — Results are AI-generated starting points, not professional financial or legal advice
2. **Knowledge cutoff** — The embedded business frameworks reflect general principles; rapidly evolving markets may not be captured
3. **No real-time market data** — Market size estimates are AI-generated based on training data, not live data sources
4. **English only** — All agents and prompts are optimized for English-language inputs
5. **API rate limits** — High concurrent usage is limited by OpenAI API rate quotas

### Data Privacy
- User business idea data is sent to the OpenAI API for analysis
- No user PII is included in API calls beyond the idea description
- All data is stored locally in the application database
- API keys are never hardcoded — stored in `.env` file excluded from version control

### AI Disclosure
The application displays **"⚡ Powered by GPT-4o AI"** in the UI footer so users always know they are interacting with an AI system.

---

## 🛠️ Tech Stack

| Layer | Technology |
|:---|:---|
| **Language** | Python 3.11+ |
| **LLM API** | OpenAI GPT-4o |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Vector Store** | Custom SQLite-backed cosine similarity store |
| **Backend API** | FastAPI with async/await |
| **Frontend** | React 18 |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Auth** | JWT (python-jose) |
| **PDF Reports** | ReportLab |
| **Deployment** | Docker + docker-compose |
| **Testing** | pytest + pytest-asyncio |

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/ai-business-idea-validator.git
cd ai-business-idea-validator
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Initialize database
venv\Scripts\python -c "from app.db.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Index knowledge frameworks into RAG vector store
venv\Scripts\python -c "from app.services.knowledge_base import rag_service; rag_service.chunk_and_index_frameworks()"

# Start backend
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm start
# Opens at http://localhost:3000
```

### 4. Docker (Alternative — runs everything)
```bash
docker-compose up --build
```

---

## 🧪 Running Tests

```bash
cd backend

# Run full test suite
venv\Scripts\python -m pytest

# Run evaluation benchmark (dry run, no API cost)
venv\Scripts\python app\evaluation\evaluate.py --dry-run

# Run with real API (first 3 ideas)
venv\Scripts\python app\evaluation\evaluate.py 3
```

---

## 📁 Project Structure

```
ai-business-idea-validator/
├── backend/
│   ├── app/
│   │   ├── agents/              # 8 specialized AI agents
│   │   │   ├── base_agent.py    # Abstract base with RAG + audit trail
│   │   │   ├── market_agent.py
│   │   │   ├── financial_agent.py
│   │   │   ├── risk_agent.py
│   │   │   ├── competition_agent.py
│   │   │   ├── growth_agent.py
│   │   │   ├── swot_generator.py
│   │   │   ├── bmc_generator.py
│   │   │   └── recommendation_agent.py
│   │   ├── prompts/             # Versioned prompt templates (.txt)
│   │   ├── knowledge/           # RAG knowledge base (8 frameworks)
│   │   ├── evaluation/          # 40-idea benchmark + evaluate.py
│   │   ├── monitoring/          # Latency + audit trail logging
│   │   ├── services/            # Orchestrator, RAG, report gen
│   │   ├── api/routes/          # FastAPI route handlers
│   │   ├── models/              # SQLAlchemy DB models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   └── utils/security.py   # Input sanitization + injection detection
│   ├── tests/                   # pytest test suite
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   └── src/
│       ├── components/          # React UI components
│       ├── services/api.js      # API service layer
│       └── styles/              # CSS stylesheets
├── docker-compose.yml
└── README.md
```

---

## 📈 Success Metrics

| Metric | Target | How Measured |
|:---|:---|:---|
| Viability score consistency | ≥ 70% within expected range | `evaluate.py` benchmark |
| Average agent confidence | ≥ 75% | Across all 40 benchmark ideas |
| End-to-end latency | < 90 seconds | Timed per analysis run |
| LLM-as-judge relevance score | ≥ 3.5 / 5.0 | GPT-4o auto-judge |
| Test suite pass rate | ≥ 80% | pytest |

### Bad Output Definition
The system defines these as failure modes that should be flagged:
- **Hallucination**: Citing specific market size numbers without RAG grounding
- **Off-topic**: Agent responding about something unrelated to the idea
- **Invalid JSON**: Agent returning malformed JSON (triggers fallback automatically)
- **Overconfident low-quality ideas**: Scoring weak ideas above 85/100

---

## 📋 API Endpoints

| Method | Endpoint | Description |
|:---|:---|:---|
| `POST` | `/api/v1/ideas/` | Submit a new business idea |
| `POST` | `/api/v1/analysis/{idea_id}/trigger` | Start multi-agent analysis |
| `GET` | `/api/v1/analysis/{idea_id}` | Retrieve analysis results |
| `GET` | `/api/v1/analysis/{idea_id}/report/pdf` | Download PDF report |
| `GET` | `/api/v1/analysis/{idea_id}/report/json` | Download JSON report |
| `POST` | `/api/v1/analysis/compare` | Compare two analyses |
| `GET` | `/api/v1/dashboard/stats` | Get dashboard statistics |
| `GET` | `/api/v1/dashboard/monitoring` | Get monitoring/audit stats |
| `POST` | `/api/v1/auth/register` | Register user |
| `POST` | `/api/v1/auth/login` | Login and get JWT token |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

**Status**: ✅ Production-Ready  
**Last Updated**: June 2026  
**Built with**: GPT-4o · FastAPI · React · RAG · Multi-Agent AI
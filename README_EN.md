[中文](./README.md) | English

# OnboardingBot - Intelligent Employee Onboarding System

A RAG-powered intelligent assistant for new employee onboarding, featuring knowledge base Q&A, salary calculation, multi-turn dialogue, and an admin dashboard.

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| LLM | qwen3.7-plus (Bailian API) | - |
| Embedding | text-embedding-v4 (DashScope) | - |
| RAG Framework | LangChain + LCEL | 1.3.11 |
| Vector Database | ChromaDB | 1.5.9 |
| Backend | FastAPI + Uvicorn | 0.139.0 |
| Data Processing | Pandas + NumPy | 3.0.3 |
| Frontend | Vue 3 + Vite | 3.5.39 |
| Runtime | Python | 3.12.10 |

## Project Structure

```
OnboardingBot/
├── backend/
│   ├── data/
│   │   ├── raw/                    # Source documents (PDF/TXT/DOCX/MD)
│   │   └── rules/                  # Structured CSV data tables
│   │       ├── salary.csv          # Salary & performance table
│   │       ├── users.csv           # User information table
│   │       ├── logs.csv            # Conversation logs table
│   │       └── config.csv          # System configuration table
│   ├── VectorStore/                # Chroma vector store
│   ├── src/
│   │   ├── tools/                  # Atomic utility functions
│   │   │   ├── calculator.py       # Salary calculation functions
│   │   │   └── file_manager.py     # Vector store / CSV management functions
│   │   ├── core/                   # RAG core modules
│   │   │   ├── rag_chain.py        # RAG retrieval chain (LCEL)
│   │   │   ├── tools.py            # Function Call tool wrappers
│   │   │   └── prompts.py          # Prompt templates
│   │   └── api/                    # FastAPI route layer
│   │       ├── main.py             # Application entry point
│   │       └── routes/
│   │           ├── auth.py         # Login authentication
│   │           ├── chat.py         # Intelligent dialogue (SSE streaming)
│   │           └── management.py   # Admin dashboard APIs
│   ├── tests/                      # Unit tests (30 tests)
│   ├── build_vectorstore.py        # Vector store build script
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api/                    # API service layer + Mock data
│   │   ├── views/                  # Page components
│   │   │   ├── LoginView.vue       # Login page
│   │   │   ├── ChatView.vue        # AI chat interface
│   │   │   ├── AdminView.vue       # Admin dashboard layout
│   │   │   ├── DocsView.vue        # Document management
│   │   │   ├── UsersView.vue       # User management
│   │   │   └── LogsView.vue        # Conversation logs
│   │   ├── router/index.js         # Route configuration
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
├── docs/                           # Documentation
├── start.ps1                       # PowerShell startup script
├── start.bat                       # Double-click to start (Windows)
├── stop.bat                        # Double-click to stop (Windows)
├── requirements.txt                # Python dependencies
├── DEVLOG.md                       # Dev log - Data Engineer
├── PHASE2_DEVLOG.md                # Dev log - Backend Lead
└── PHASE3_DEVLOG.md                # Dev log - Frontend Developer
```

## Quick Start

### Prerequisites

- Python 3.12.10
- Node.js 18+
- Bailian Platform API Key

### 1. Install Backend Dependencies

```bash
# Create virtual environment (skip if already created)
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Windows PowerShell
$env:API_KEY="your_dashscope_api_key"

# Or create a .env file in the project root
echo API_KEY=your_dashscope_api_key > .env
```

### 3. Build Vector Store

Place documents in `backend/data/raw/`, then run:

```bash
cd backend
python build_vectorstore.py
```

Supported formats: PDF, TXT, MD, DOCX

### 4. Initialize Data Tables

```bash
cd backend
python -c "from src.tools.calculator import init_salary_table; init_salary_table()"
```

### 5. One-Click Launch

```bash
# Double-click start.bat or run in terminal
.\start.ps1
```

The script automatically starts both backend and frontend services and opens the browser.

**Other commands:**

```powershell
.\start.ps1 -Stop          # Stop all services
.\start.ps1 -BackendOnly   # Start backend only
.\start.ps1 -FrontendOnly  # Start frontend only
.\stop.bat                 # Quick stop (double-click)
```

### 6. Manual Start (Alternative)

```bash
# Backend
cd backend
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

- Swagger Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Vite proxy configured: `/api/*` requests are forwarded to `http://localhost:8000`

### 7. Run Tests

```bash
cd backend
python -m pytest tests/ -v
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/login` | User login authentication |
| POST | `/api/chat` | Intelligent dialogue (SSE streaming) |
| GET | `/api/docs` | Document list |
| POST | `/api/docs/delete` | Delete document vectors |
| GET | `/api/logs` | Conversation log list |
| GET | `/api/users` | User list |
| GET | `/api/config` | System configuration |

## Core Features

### RAG Intelligent Q&A

- Vector retrieval via ChromaDB, Top-5 relevant document chunks as context
- Automatic citation annotation: `[Source: filename - Page X]`
- Multi-turn dialogue memory with context-aware follow-up

### Function Call Salary Calculation

LLM automatically detects calculation intent and invokes tools:

| Tool | Description |
|------|-------------|
| `calculate_net_salary_tool` | Comprehensive net salary calculation |
| `calculate_late_deduction_tool` | Late arrival deduction (50 CNY per occurrence) |
| `calculate_leave_deduction_tool` | Personal leave deduction (daily rate x days) |
| `calculate_overtime_pay_tool` | Overtime pay (hourly rate x hours x multiplier) |

### Admin Dashboard

- Login authentication (token cached in localStorage)
- Document management (list view + vector deletion cleanup)
- User management (list view, passwords excluded)
- Conversation logs (filterable by user ID / keyword)

### Frontend Features

- SSE streaming typewriter effect
- Highlighted clickable source tags with popup details
- Quick question shortcut buttons
- Session history auto-save (localStorage)
- Automatic Mock data fallback on API failure

## System Configuration

Configurable in `backend/data/rules/config.csv`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| chunk_size | 512 | Text chunk size |
| chunk_overlap | 50 | Text chunk overlap |
| embedding_model | text-embedding-v4 | Embedding model name |
| llm_model | qwen3.7-plus | Large language model name |
| max_response_length | 2000 | Max response length per turn |
| timeout_seconds | 30 | API call timeout |

## Demo Walkthrough

1. Visit `http://localhost:5173/login` and log in (default: admin / admin123)
2. Confirm the document list in the admin dashboard
3. Navigate to `/chat` and ask "What is the employee onboarding process?"
4. Observe the streaming output and highlighted source tags
5. Click a source tag to view the origin popup
6. Ask "How much is deducted for 3 late arrivals?" to verify Function Call accuracy
7. Return to the admin dashboard to view conversation logs with filter

## Dev Logs

- [DEVLOG.md](./DEVLOG.md) - Phase 1: Knowledge Asset & Computation Engine
- [PHASE2_DEVLOG.md](./PHASE2_DEVLOG.md) - Phase 2: RAG Engine & API Service
- [PHASE3_DEVLOG.md](./PHASE3_DEVLOG.md) - Phase 3: Interaction & UX Polish

## Acknowledgements

Thanks to the following team members for their contributions:

| Member | Role | Key Contributions |
|:-------|:-----|-------------------|
| xiaojieun | Phase 1 - Data Engineer | Knowledge base, vector store, computation engine, asset management functions |
| HanYu | Phase 2 - Backend Lead | RAG chain, FastAPI service, Function Call, streaming output |
| xbin | Phase 3 - Frontend Developer | Vue3 dual-panel UI, SSE streaming integration, admin dashboard |

---

> This project was completed as a team effort using a serial development workflow.

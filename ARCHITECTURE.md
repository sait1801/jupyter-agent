# Jupyter Agent - System Architecture

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      BROWSER (Frontend)                          │
│  ┌────────────────────┐              ┌─────────────────────┐    │
│  │   Notebook View    │              │   AI Agent Sidebar  │    │
│  │                    │              │                     │    │
│  │  ┌──────────────┐  │              │  ┌──────────────┐  │    │
│  │  │   Cell 1     │  │              │  │     Chat     │  │    │
│  │  │  [code...]   │  │              │  │              │  │    │
│  │  └──────────────┘  │              │  └──────────────┘  │    │
│  │                    │              │                     │    │
│  │  ┌──────────────┐  │              │  ┌──────────────┐  │    │
│  │  │   Cell 2     │  │              │  │   Analyze    │  │    │
│  │  │  [code...]   │  │              │  │              │  │    │
│  │  └──────────────┘  │              │  └──────────────┘  │    │
│  │                    │              │                     │    │
│  │  ┌──────────────┐  │              │  ┌──────────────┐  │    │
│  │  │  + Add Cell  │  │              │  │  Optimize    │  │    │
│  │  └──────────────┘  │              │  └──────────────┘  │    │
│  └────────────────────┘              └─────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                    HTTP/WebSocket (Fetch API)
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND SERVER (FastAPI)                      │
│                     http://localhost:8000                        │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ Kernel Manager   │  │   AI Agent       │  │  Notebook    │  │
│  │                  │  │  (Secret Sauce!) │  │  Storage     │  │
│  │ - Create kernel  │  │                  │  │              │  │
│  │ - Execute cells  │  │ - Error analysis │  │ - Save .ipynb│  │
│  │ - Track state    │  │ - Code gen       │  │ - Load .ipynb│  │
│  │ - Manage output  │  │ - Optimization   │  │ - List files │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
│           │                     │                                │
└───────────┼─────────────────────┼────────────────────────────────┘
            │                     │
            ▼                     ▼
    ┌──────────────┐      ┌─────────────────┐
    │   Jupyter    │      │  Google Gemini  │
    │   Kernel     │      │      API        │
    │              │      │                 │
    │ - Python     │      │ - Gemini 1.5    │
    │   execution  │      │   Pro           │
    │ - IPython    │      │ - Gemini 1.5    │
    │   runtime    │      │   Flash         │
    └──────────────┘      └─────────────────┘
```

## Component Details

### Frontend (HTML/CSS/JS)
**Location**: `frontend/`

**Files**:
- `index.html` - Main structure
- `styles.css` - Premium dark theme
- `app.js` - Application logic

**Responsibilities**:
- Render notebook cells
- Handle user input
- Display outputs and errors
- Communicate with backend API
- Manage AI sidebar

**Key Features**:
- Cell-based editing
- Real-time execution
- AI chat interface
- Error visualization
- Toast notifications

---

### Backend API (FastAPI)
**Location**: `backend/`  
**Port**: 8000

**Files**:
- `main.py` - API endpoints & routing
- `kernel_manager.py` - Jupyter integration
- `ai_agent.py` - AI intelligence
- `models.py` - Data schemas
- `config.py` - Configuration

**Endpoints**:

#### Kernel Management
```
POST   /kernel/create          → Create new kernel
POST   /kernel/{id}/restart    → Restart kernel
POST   /kernel/{id}/interrupt  → Interrupt execution
DELETE /kernel/{id}             → Shutdown kernel
```

#### Execution
```
POST   /execute                → Execute cell code
```

#### AI Agent
```
POST   /agent/analyze-error    → Analyze errors
POST   /agent/generate-code    → Generate code
POST   /agent/optimize         → Optimize notebook
```

#### Notebooks
```
POST   /notebook/save          → Save to .ipynb
GET    /notebook/load/{name}   → Load .ipynb
GET    /notebook/list          → List all notebooks
```

---

### Kernel Manager
**File**: `backend/kernel_manager.py`

**Responsibilities**:
- Create and manage Jupyter kernels
- Execute Python code in kernels
- Capture outputs (stdout, results, errors)
- Track execution counts
- Handle kernel lifecycle

**Key Classes**:
- `NotebookKernel` - Single kernel instance
- `KernelManagerService` - Manages multiple kernels

---

### AI Agent (THE SECRET SAUCE!)
**File**: `backend/ai_agent.py`

**The Innovation**:
Traditional assistants rewrite everything. We analyze context and make minimal fixes.

**Workflow**:
1. **Analyze** - Understand all cells and their dependencies
2. **Identify** - Find which cells need fixing
3. **Plan** - Decide minimal changes needed
4. **Suggest** - Recommend restart vs. continue
5. **Fix** - Provide targeted code changes

**Key Classes**:
- `NotebookCell` - Cell representation
- `NotebookAgent` - AI analysis engine
- `AgentService` - Model management

**Methods**:
- `analyze_error()` - Context-aware error analysis
- `suggest_code()` - Generate code based on context
- `optimize_notebook()` - Suggest improvements

---

### External Services

#### Jupyter Kernel
- **What**: IPython kernel for Python execution
- **How**: Via `jupyter-client` library
- **Why**: Provides isolated Python runtime

#### Google Gemini API
- **What**: Large Language Model API
- **Models**: Gemini 1.5 Pro, Gemini 1.5 Flash
- **How**: Via `google-generativeai` SDK
- **Why**: Powers intelligent code analysis

---

## Data Flow Examples

### Example 1: Execute Cell

```
User clicks "Run Cell"
    ↓
Frontend: app.js → CellManager.runCell()
    ↓
Frontend: API call → POST /execute
    ↓
Backend: main.py → execute_cell()
    ↓
Backend: kernel_manager.py → kernel.execute_cell()
    ↓
Jupyter Kernel: Execute Python code
    ↓
Backend: Collect outputs
    ↓
Frontend: Display results
```

### Example 2: Fix Error (The Secret Sauce!)

```
User runs cell with error
    ↓
Frontend: Detects error in response
    ↓
Frontend: Auto-trigger → AgentManager.autoAnalyzeError()
    ↓
Frontend: API call → POST /agent/analyze-error
    ↓
Backend: ai_agent.py → agent.analyze_error()
    ↓
Backend: Build notebook context (all cells)
    ↓
Gemini API: Analyze error with context
    ↓
Gemini API: Return minimal fixes + strategy
    ↓
Frontend: Display fixes in Analyze tab
    ↓
User: Click "Apply Fix"
    ↓
Frontend: Update specific cells only
    ↓
User: Run from where left off (no restart!)
```

### Example 3: Generate Code

```
User types in Chat: "Create a pandas dataframe"
    ↓
Frontend: app.js → AgentManager.generateCode()
    ↓
Frontend: API call → POST /agent/generate-code
    ↓
Backend: ai_agent.py → agent.suggest_code()
    ↓
Backend: Build context from existing cells
    ↓
Gemini API: Generate context-aware code
    ↓
Frontend: Display code in chat
    ↓
User: Click "Add to Notebook"
    ↓
Frontend: Create new cell with code
```

---

## State Management

### Frontend State (`app.js`)
```javascript
class AppState {
    kernelId: string           // Current kernel ID
    cells: Cell[]              // All notebook cells
    selectedModel: string      // AI model selection
    notebookName: string       // Current notebook name
}
```

### Backend State
- **Kernels**: Managed by `KernelManagerService`
- **AI Agents**: Managed by `AgentService`
- **Sessions**: One kernel per session (can be extended)

---

## Security Considerations

### Current Implementation
- ⚠️ No authentication (single user)
- ⚠️ No rate limiting
- ⚠️ CORS open for development
- ⚠️ API key in .env file

### Production Recommendations
- ✅ Add user authentication
- ✅ Implement rate limiting
- ✅ Restrict CORS origins
- ✅ Use secret management service
- ✅ Add input sanitization
- ✅ Implement quotas

---

## Scalability Considerations

### Current Design
- Single server
- One kernel per session
- In-memory state
- Local file storage

### For Production
- Load balancer
- Kernel pool/autoscaling
- Database for state
- Object storage for notebooks
- Message queue for async tasks
- Container orchestration (K8s)

---

## Technology Choices

### Why FastAPI?
- ✅ Modern async Python
- ✅ Automatic API docs
- ✅ Type safety with Pydantic
- ✅ WebSocket support (future)
- ✅ High performance

### Why Vanilla JS?
- ✅ No build step
- ✅ Fast development
- ✅ Small bundle size
- ✅ Easy to understand
- ✅ Direct control

### Why Jupyter Client?
- ✅ Standard protocol
- ✅ Well-tested
- ✅ Multi-language support
- ✅ Rich ecosystem

### Why Gemini?
- ✅ Excellent code understanding
- ✅ Long context window
- ✅ Fast inference
- ✅ Cost-effective

---

## Directory Structure Details

```
jupyter-agent/
│
├── .venv/                      # Python virtual environment
│   ├── Scripts/                # Windows executables
│   ├── Lib/                    # Python packages
│   └── ...
│
├── backend/
│   ├── __pycache__/           # Python cache (gitignored)
│   ├── notebooks/             # Saved .ipynb files
│   ├── main.py                # FastAPI app
│   ├── kernel_manager.py      # Kernel management
│   ├── ai_agent.py            # AI agent
│   ├── models.py              # Data models
│   ├── config.py              # Configuration
│   ├── requirements.txt       # Dependencies
│   ├── .env.example           # Env template
│   ├── .env                   # Your API key
│   └── README.md
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── README.md
│
├── README.md                  # Main docs
├── QUICKSTART.md              # Getting started
├── PROJECT_SUMMARY.md         # This file summary
├── ARCHITECTURE.md            # This file
├── .gitignore
├── setup.ps1                  # Windows setup
├── setup.sh                   # Mac/Linux setup
├── start-dev.ps1              # Windows dev launcher
└── start-dev.sh               # Mac/Linux dev launcher
```

---

## Key Innovations

### 1. Context-Aware Error Analysis
Unlike traditional AI assistants, our agent:
- Sees ALL cells, not just the error
- Understands variable dependencies
- Suggests minimal changes
- Preserves kernel state

### 2. Intelligent Execution Strategy
The AI decides:
- Which cells need fixing
- Whether kernel restart is needed
- Where to continue execution from
- What variables are affected

### 3. Clean Architecture
- Separation of concerns
- Type-safe APIs
- Async operations
- Modular design

---

## Performance Characteristics

### Typical Response Times
- Cell execution: ~100-500ms (depends on code)
- AI analysis: ~2-5s (Gemini API)
- Code generation: ~3-7s (Gemini API)
- File save/load: ~50-200ms

### Resource Usage
- Backend memory: ~100-200MB base
- Kernel memory: ~50-500MB (per kernel)
- Frontend: Minimal (vanilla JS)

---

This architecture is designed to be:
- ✅ **Fast** - Async operations, minimal overhead
- ✅ **Smart** - Context-aware AI
- ✅ **Scalable** - Modular components
- ✅ **Maintainable** - Clean code, good documentation
- ✅ **Extensible** - Easy to add features

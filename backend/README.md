# Jupyter Agent Backend

Smart AI-powered notebook execution engine with intelligent cell-level debugging.

## Features

- **Jupyter Kernel Management**: Full support for executing Python code in isolated kernels
- **Smart AI Agent**: Analyzes notebook context and suggests minimal, targeted fixes
- **Cell-Level Execution**: Execute individual cells and track their state
- **Error Analysis**: AI-powered error analysis that understands cell dependencies
- **Code Generation**: Context-aware code suggestions
- **Notebook Optimization**: Get suggestions to improve your notebook

## Setup

### 1. Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and add your Gemini API key:

```bash
copy .env.example .env
```

Edit `.env`:
```
GEMINI_API_KEY=your_actual_api_key_here
PORT=8000
HOST=0.0.0.0
```

### 4. Run the Server

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Kernel Management
- `POST /kernel/create` - Create a new kernel
- `POST /kernel/{kernel_id}/restart` - Restart a kernel
- `POST /kernel/{kernel_id}/interrupt` - Interrupt running code
- `DELETE /kernel/{kernel_id}` - Shutdown a kernel

### Cell Execution
- `POST /execute` - Execute a cell

### AI Agent (The Secret Sauce!)
- `POST /agent/analyze-error` - Analyze errors and get intelligent fixes
- `POST /agent/generate-code` - Generate code based on context
- `POST /agent/optimize` - Get notebook optimization suggestions

### Notebook Management
- `POST /notebook/save` - Save notebook to .ipynb
- `GET /notebook/load/{filename}` - Load notebook from .ipynb
- `GET /notebook/list` - List all notebooks

## Architecture

```
backend/
├── main.py              # FastAPI application
├── config.py            # Configuration management
├── models.py            # Pydantic models
├── kernel_manager.py    # Jupyter kernel management
├── ai_agent.py          # Smart AI agent (SECRET SAUCE!)
├── requirements.txt     # Python dependencies
└── notebooks/           # Saved notebooks
```

## The Secret Sauce

The AI agent is the key innovation. Unlike traditional notebook assistants that rewrite code from scratch:

1. **Context Awareness**: Analyzes ALL cells to understand dependencies
2. **Minimal Fixes**: Only modifies cells that actually need changes
3. **Smart Execution**: Decides whether to restart kernel or continue from specific cell
4. **Cell Dependencies**: Understands which cells depend on which variables

This makes development much faster because you don't lose your kernel state unnecessarily!

## Development

The backend is built with:
- **FastAPI**: Modern async web framework
- **Jupyter Client**: For kernel management
- **Google Generative AI**: For the smart agent
- **Pydantic**: For data validation

## License

MIT

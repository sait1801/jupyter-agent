import os
import logging
import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import nbformat

from config import config
from kernel_manager import kernel_manager
from ai_agent import agent_service, NotebookCell
from models import (
    CreateKernelResponse,
    ExecuteCellRequest,
    ExecuteCellResponse,
    AnalyzeErrorRequest,
    AnalyzeErrorResponse,
    GenerateCodeRequest,
    GenerateCodeResponse,
    OptimizeNotebookRequest,
    OptimizeNotebookResponse,
    NotebookCellModel,
    SaveNotebookRequest,
    LoadNotebookResponse,
    ChatRequest,
    ChatResponse
)
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Jupyter Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Kernel Management Endpoints ====================

@app.post("/kernel/create", response_model=CreateKernelResponse)
async def create_kernel():
    """Create a new Jupyter kernel."""
    try:
        kernel_id = await kernel_manager.create_kernel()
        return CreateKernelResponse(kernel_id=kernel_id, status="ready")
    except Exception as e:
        logger.error(f"Error creating kernel: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/kernel/{kernel_id}/restart")
async def restart_kernel(kernel_id: str):
    """Restart a Jupyter kernel."""
    try:
        await kernel_manager.restart_kernel(kernel_id)
        return {"status": "restarted"}
    except Exception as e:
        logger.error(f"Error restarting kernel: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute", response_model=ExecuteCellResponse)
async def execute_cell(request: ExecuteCellRequest):
    """Execute a code cell in a specific kernel."""
    try:
        result = await kernel_manager.execute_cell(
            request.kernel_id,
            request.code,
            request.cell_id
        )
        return ExecuteCellResponse(**result)
    except Exception as e:
        logger.error(f"Error executing cell: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== AI Agent Endpoints ====================

@app.post("/agent/analyze-error", response_model=AnalyzeErrorResponse)
async def analyze_error(request: AnalyzeErrorRequest):
    """Analyze an error in a notebook cell."""
    try:
        # Convert to NotebookCell objects
        cells = [
            NotebookCell(
                cell_id=cell.cell_id,
                code=cell.code,
                execution_count=cell.execution_count,
                outputs=cell.outputs,
                error=cell.error
            )
            for cell in request.cells
        ]
        
        # Get agent
        agent = agent_service.get_agent(request.model_name)
        
        # Analyze error
        result = await agent.analyze_error(cells, request.error_cell_id)
        
        return AnalyzeErrorResponse(**result)
    except Exception as e:
        logger.error(f"Error analyzing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/generate-code", response_model=GenerateCodeResponse)
async def generate_code(request: GenerateCodeRequest):
    """Generate code based on user request and notebook context."""
    try:
        # Convert to NotebookCell objects
        cells = [
            NotebookCell(
                cell_id=cell.cell_id,
                code=cell.code,
                execution_count=cell.execution_count,
                outputs=cell.outputs,
                error=cell.error
            )
            for cell in request.cells
        ]
        
        # Get agent
        agent = agent_service.get_agent(request.model_name)
        
        # Generate code
        result = await agent.suggest_code(cells, request.user_request)
        
        return GenerateCodeResponse(**result)
    except Exception as e:
        logger.error(f"Error generating code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/optimize", response_model=OptimizeNotebookResponse)
async def optimize_notebook(request: OptimizeNotebookRequest):
    """Get optimization suggestions for the entire notebook."""
    try:
        # Convert to NotebookCell objects
        cells = [
            NotebookCell(
                cell_id=cell.cell_id,
                code=cell.code,
                execution_count=cell.execution_count,
                outputs=cell.outputs,
                error=cell.error
            )
            for cell in request.cells
        ]
        
        # Get agent
        agent = agent_service.get_agent(request.model_name)
        
        # Optimize
        result = await agent.optimize_notebook(cells)
        
        return OptimizeNotebookResponse(**result)
    except Exception as e:
        logger.error(f"Error optimizing notebook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    Chat with AI agent - Cursor-like experience!
    The agent can directly manipulate cells through conversation.
    """
    try:
        # Convert to NotebookCell objects
        cells = [
            NotebookCell(
                cell_id=cell.cell_id,
                code=cell.code,
                execution_count=cell.execution_count,
                outputs=cell.outputs,
                error=cell.error
            )
            for cell in request.cells
        ]
        
        # Get agent
        agent = agent_service.get_agent(request.model_name)
        
        # Chat
        result = await agent.chat(cells, request.user_message, request.conversation_history)
        
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/notebook/save")
async def save_notebook(request: SaveNotebookRequest):
    """Save notebook to .ipynb file."""
    try:
        # Create notebook
        nb = nbformat.v4.new_notebook()
        
        # Add cells
        for cell in request.cells:
            if cell.cell_type == "code":
                nb_cell = nbformat.v4.new_code_cell(cell.code)
                nb_cell.execution_count = cell.execution_count
                nb_cell.outputs = cell.outputs
            else:
                nb_cell = nbformat.v4.new_markdown_cell(cell.code)
            
            nb.cells.append(nb_cell)
        
        # Save to file
        notebooks_dir = Path("notebooks")
        notebooks_dir.mkdir(exist_ok=True)
        
        filepath = notebooks_dir / request.filename
        with open(filepath, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        
        return {"status": "saved", "filename": request.filename}
    except Exception as e:
        logger.error(f"Error saving notebook: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/notebook/load/{filename}", response_model=LoadNotebookResponse)
async def load_notebook(filename: str):
    """Load notebook from .ipynb file."""
    try:
        filepath = Path("notebooks") / filename
        
        if not filepath.exists():
            raise HTTPException(status_code=404, detail="Notebook not found")
        
        # Load notebook
        with open(filepath, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Convert to our format
        cells = []
        for i, cell in enumerate(nb.cells):
            cell_model = NotebookCellModel(
                cell_id=f"cell-{i}",
                code=cell.source,
                cell_type=cell.cell_type,
                execution_count=getattr(cell, 'execution_count', None),
                outputs=[output for output in getattr(cell, 'outputs', [])]
            )
            cells.append(cell_model)
        
        return LoadNotebookResponse(filename=filename, cells=cells)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading notebook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notebook/list")
async def list_notebooks():
    """List all saved notebooks."""
    try:
        notebooks_dir = Path("notebooks")
        notebooks_dir.mkdir(exist_ok=True)
        
        notebooks = [
            {
                "filename": f.name,
                "size": f.stat().st_size,
                "modified": f.stat().st_mtime
            }
            for f in notebooks_dir.glob("*.ipynb")
        ]
        
        return {"notebooks": notebooks}
    except Exception as e:
        logger.error(f"Error listing notebooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down, cleaning up kernels...")
    await kernel_manager.shutdown_all()

# ==================== Terminal Endpoints ====================

class TerminalCommandRequest(BaseModel):
    command: str

@app.post("/terminal/execute")
async def execute_terminal_command(request: TerminalCommandRequest):
    """
    Execute a shell command and return the output.
    """
    try:
        # Use subprocess to run the command
        # shell=True allows using shell features like pipes and redirects, but be careful with input
        # Since this is a local dev tool, we assume the user (via agent) is authorized
        process = subprocess.run(
            request.command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd() # Execute in project root
        )
        
        return {
            "stdout": process.stdout,
            "stderr": process.stderr,
            "returncode": process.returncode
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )

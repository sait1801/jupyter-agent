"""Main FastAPI application."""
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import nbformat
from pathlib import Path
from typing import List

from config import config
from models import (
    ExecuteCellRequest, ExecuteCellResponse,
    CreateKernelResponse,
    AnalyzeErrorRequest, AnalyzeErrorResponse,
    GenerateCodeRequest, GenerateCodeResponse,
    OptimizeNotebookRequest, OptimizeNotebookResponse,
    SaveNotebookRequest, LoadNotebookResponse,
    NotebookCellModel,
    ChatRequest, ChatResponse
)
from kernel_manager import kernel_manager
from ai_agent import agent_service, NotebookCell

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Jupyter Agent API",
    description="Smart AI-powered notebook execution engine",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Jupyter Agent API is running",
        "version": "1.0.0"
    }


@app.post("/kernel/create", response_model=CreateKernelResponse)
async def create_kernel():
    """Create a new Jupyter kernel."""
    try:
        kernel_id = await kernel_manager.create_kernel()
        return CreateKernelResponse(
            kernel_id=kernel_id,
            status="created"
        )
    except Exception as e:
        logger.error(f"Error creating kernel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/kernel/{kernel_id}/restart")
async def restart_kernel(kernel_id: str):
    """Restart a kernel."""
    try:
        kernel = kernel_manager.get_kernel(kernel_id)
        if not kernel:
            raise HTTPException(status_code=404, detail="Kernel not found")
        
        await kernel.restart()
        return {"status": "restarted", "kernel_id": kernel_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restarting kernel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/kernel/{kernel_id}/interrupt")
async def interrupt_kernel(kernel_id: str):
    """Interrupt a running kernel."""
    try:
        kernel = kernel_manager.get_kernel(kernel_id)
        if not kernel:
            raise HTTPException(status_code=404, detail="Kernel not found")
        
        await kernel.interrupt()
        return {"status": "interrupted", "kernel_id": kernel_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error interrupting kernel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/kernel/{kernel_id}")
async def shutdown_kernel(kernel_id: str):
    """Shutdown a kernel."""
    try:
        await kernel_manager.shutdown_kernel(kernel_id)
        return {"status": "shutdown", "kernel_id": kernel_id}
    except Exception as e:
        logger.error(f"Error shutting down kernel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute", response_model=ExecuteCellResponse)
async def execute_cell(request: ExecuteCellRequest):
    """Execute a notebook cell."""
    try:
        kernel = kernel_manager.get_kernel(request.kernel_id)
        if not kernel:
            raise HTTPException(status_code=404, detail="Kernel not found")
        
        result = await kernel.execute_cell(request.code, request.cell_id)
        return ExecuteCellResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing cell: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/analyze-error", response_model=AnalyzeErrorResponse)
async def analyze_error(request: AnalyzeErrorRequest):
    """
    Analyze an error and get intelligent fix suggestions.
    
    This is the SECRET SAUCE - the agent analyzes the entire notebook context
    and suggests minimal, targeted fixes instead of rewriting everything.
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )

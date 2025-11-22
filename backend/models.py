"""Pydantic models for API requests and responses."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class CellOutput(BaseModel):
    """Output from a cell execution."""
    type: str
    data: Optional[Dict[str, Any]] = None
    text: Optional[str] = None
    name: Optional[str] = None
    execution_count: Optional[int] = None


class CellError(BaseModel):
    """Error from a cell execution."""
    ename: str
    evalue: str
    traceback: List[str]


class NotebookCellModel(BaseModel):
    """Model for a notebook cell."""
    cell_id: str
    code: str
    cell_type: str = "code"
    execution_count: Optional[int] = None
    outputs: List[Dict[str, Any]] = []
    error: Optional[Dict[str, Any]] = None


class ExecuteCellRequest(BaseModel):
    """Request to execute a cell."""
    kernel_id: str
    cell_id: str
    code: str


class ExecuteCellResponse(BaseModel):
    """Response from cell execution."""
    cell_id: str
    execution_count: Optional[int]
    outputs: List[Dict[str, Any]]
    error: Optional[Dict[str, Any]]
    status: str


class CreateKernelResponse(BaseModel):
    """Response when creating a kernel."""
    kernel_id: str
    status: str


class AnalyzeErrorRequest(BaseModel):
    """Request to analyze an error."""
    cells: List[NotebookCellModel]
    error_cell_id: str
    model_name: Optional[str] = None


class AnalyzeErrorResponse(BaseModel):
    """Response from error analysis."""
    analysis: str
    cells_to_fix: List[str]
    fixes: Dict[str, str]
    restart_needed: bool
    continue_from_cell: str
    explanation: str


class GenerateCodeRequest(BaseModel):
    """Request to generate code."""
    cells: List[NotebookCellModel]
    user_request: str
    model_name: Optional[str] = None


class GenerateCodeResponse(BaseModel):
    """Response with generated code."""
    code: str
    explanation: str
    cell_type: str = "code"
    dependencies: List[str] = []


class OptimizeNotebookRequest(BaseModel):
    """Request to optimize notebook."""
    cells: List[NotebookCellModel]
    model_name: Optional[str] = None


class Suggestion(BaseModel):
    """A single optimization suggestion."""
    cell_id: str
    issue: str
    suggested_fix: str
    priority: str


class OptimizeNotebookResponse(BaseModel):
    """Response with optimization suggestions."""
    suggestions: List[Suggestion]
    overall_assessment: str


class SaveNotebookRequest(BaseModel):
    """Request to save notebook."""
    filename: str
    cells: List[NotebookCellModel]


class LoadNotebookResponse(BaseModel):
    """Response when loading notebook."""
    filename: str
    cells: List[NotebookCellModel]


class ChatRequest(BaseModel):
    """Request to chat with AI agent."""
    cells: List[NotebookCellModel]
    user_message: str
    conversation_history: Optional[List[Dict[str, Any]]] = None
    model_name: Optional[str] = None


class ToolCall(BaseModel):
    """A tool call made by the agent."""
    id: str
    name: str
    arguments: Dict[str, Any]
    result: Dict[str, Any]


class ChatResponse(BaseModel):
    """Response from chat."""
    message: str
    tool_calls: List[ToolCall] = []
    finish_reason: str


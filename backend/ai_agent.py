"""AI Agent for intelligent notebook debugging and cell fixing."""
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from openai import AsyncOpenAI
from config import config

logger = logging.getLogger(__name__)

# Configure Gemini
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)

# Configure OpenAI
openai_client = None
if config.OPENAI_API_KEY:
    openai_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)


class NotebookCell:
    """Represents a notebook cell."""
    
    def __init__(self, cell_id: str, code: str, execution_count: Optional[int] = None, 
                 outputs: List[Dict] = None, error: Optional[Dict] = None):
        self.cell_id = cell_id
        self.code = code
        self.execution_count = execution_count
        self.outputs = outputs or []
        self.error = error
        
    def to_dict(self):
        return {
            'cell_id': self.cell_id,
            'code': self.code,
            'execution_count': self.execution_count,
            'outputs': self.outputs,
            'error': self.error
        }


class NotebookAgent:
    """
    Smart AI agent that understands notebook context and fixes cells intelligently.
    
    The key innovation: Instead of rewriting everything from scratch, this agent:
    1. Analyzes the entire notebook context
    2. Identifies which specific cells need fixing
    3. Plans the minimal changes needed
    4. Suggests whether to restart kernel or continue from error point
    
    Supports both OpenAI and Gemini models with distinction between:
    - Reasoning models (o1-preview, o1-mini): Use reasoning_effort parameter
    - Non-reasoning models (GPT-4o, GPT-4o-mini, Gemini): Use temperature parameter
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.model_name = model_name
        self.provider = self._get_provider()
        self.is_reasoning_model = self._is_reasoning_model()
        
        # Initialize model based on provider
        if self.provider == "gemini":
            self.gemini_model = genai.GenerativeModel(model_name)
        
    def _get_provider(self) -> str:
        """Determine which AI provider to use based on model name."""
        if self.model_name.startswith("gpt-") or self.model_name.startswith("o1"):
            return "openai"
        elif self.model_name.startswith("gemini"):
            return "gemini"
        else:
            # Default to OpenAI
            return "openai"
    
    def _is_reasoning_model(self) -> bool:
        """Check if this is a reasoning model (uses reasoning_effort instead of temperature)."""
        return any(self.model_name.startswith(rm) for rm in config.REASONING_MODELS)
        
    async def analyze_error(self, cells: List[NotebookCell], error_cell_id: str) -> Dict[str, Any]:
        """
        Analyze an error in context of all cells.
        
        Returns:
            - cells_to_fix: List of cell IDs that need fixing
            - fixes: Dict mapping cell_id to new code
            - plan: Explanation of what went wrong and the fix strategy
            - restart_needed: Whether kernel restart is recommended
            - continue_from: Cell ID to continue execution from
        """
        # Build notebook context
        notebook_context = self._build_notebook_context(cells, error_cell_id)
        
        prompt = f"""You are an expert Python programmer helping debug a Jupyter notebook.

NOTEBOOK CONTEXT:
{notebook_context}

The error occurred in cell {error_cell_id}.

Your task is to:
1. Analyze the error in the context of ALL cells
2. Identify which specific cells need to be fixed (could be just the error cell, or earlier cells)
3. Provide the corrected code for each cell that needs fixing
4. Decide if kernel restart is needed or if we can continue from a specific cell
5. Explain your reasoning

Respond in the following JSON format:
{{
    "analysis": "Your analysis of what went wrong and why",
    "cells_to_fix": ["cell_id_1", "cell_id_2"],
    "fixes": {{
        "cell_id_1": "corrected code here",
        "cell_id_2": "corrected code here"
    }},
    "restart_needed": true/false,
    "continue_from_cell": "cell_id_to_start_from",
    "explanation": "Step-by-step explanation of the fix strategy"
}}

IMPORTANT: 
- Only fix cells that actually need changes
- Preserve code in cells that are working correctly
- If the error is due to missing imports/setup in earlier cells, fix those cells
- If it's just a bug in the current cell, only fix that cell
- Consider variable state and dependencies between cells
"""

        try:
            response = await self._generate_response(prompt)
            parsed_response = self._parse_json_response(response)
            return parsed_response
            
        except Exception as e:
            logger.error(f"Error analyzing notebook: {e}")
            # Fallback: Just try to fix the error cell
            return {
                "analysis": f"Error in analysis: {str(e)}",
                "cells_to_fix": [error_cell_id],
                "fixes": {},
                "restart_needed": False,
                "continue_from_cell": error_cell_id,
                "explanation": "Using fallback strategy"
            }
    
    async def suggest_code(self, cells: List[NotebookCell], user_request: str) -> Dict[str, Any]:
        """
        Suggest code based on user request and notebook context.
        """
        notebook_context = self._build_notebook_context(cells)
        
        prompt = f"""You are an expert Python programmer helping write code in a Jupyter notebook.

CURRENT NOTEBOOK STATE:
{notebook_context}

USER REQUEST: {user_request}

Generate appropriate Python code that:
1. Builds on the existing notebook context
2. Follows best practices
3. Is well-commented
4. Fulfills the user's request

Respond in JSON format:
{{
    "code": "your generated code here",
    "explanation": "what this code does",
    "cell_type": "code",
    "dependencies": ["list of any new packages needed"]
}}
"""

        try:
            response = await self._generate_response(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return {
                "code": "# Error generating code",
                "explanation": str(e),
                "cell_type": "code",
                "dependencies": []
            }
    
    async def optimize_notebook(self, cells: List[NotebookCell]) -> Dict[str, Any]:
        """
        Suggest optimizations for the entire notebook.
        """
        notebook_context = self._build_notebook_context(cells)
        
        prompt = f"""You are an expert Python programmer reviewing a Jupyter notebook for optimization.

NOTEBOOK:
{notebook_context}

Analyze this notebook and suggest:
1. Code optimizations (performance, readability)
2. Better organization of cells
3. Missing error handling
4. Potential bugs or issues

Respond in JSON format:
{{
    "suggestions": [
        {{
            "cell_id": "cell_id",
            "issue": "description of issue",
            "suggested_fix": "corrected code or explanation",
            "priority": "high/medium/low"
        }}
    ],
    "overall_assessment": "general feedback on the notebook"
}}
"""

        try:
            response = await self._generate_response(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Error optimizing notebook: {e}")
            return {
                "suggestions": [],
                "overall_assessment": f"Error: {str(e)}"
            }
    
    async def chat(self, cells: List[NotebookCell], user_message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Chat with the agent. The agent has tools to manipulate cells.
        This is like Cursor - the AI can directly read, update, insert, and delete cells.
        
        Args:
            cells: Current notebook cells
            user_message: User's message
            conversation_history: Previous conversation messages
            
        Returns:
            Response with message and any tool calls made
        """
        from cell_tools import CellTool
        
        # Build context
        notebook_context = self._build_notebook_context(cells)
        
        # Build conversation messages
        messages = conversation_history or []
        
        # Add system message if this is the first message
        if not messages:
            system_message = """You are an expert AI coding assistant integrated into a Jupyter notebook environment.

You have tools to manipulate notebook cells:
- read_cells: Read code from cells
- update_cell: Modify existing cells
- insert_cell: Add new cells at any position  
- delete_cell: Remove cells
- run_cell: Execute cells to test them
- run_terminal_command: Run shell commands (pip install, file management, etc.)

When the user asks you to do something:
1. Use read_cells to understand the current state
2. Use the appropriate tools to make changes
3. Explain what you're doing and why
4. Use run_cell to verify your changes work

Be conversational and helpful. Think step by step."""
            messages.append({"role": "system", "content": system_message})
        
        # Add context about current notebook
        context_message = f"Current notebook state:\n{notebook_context}\n\nUser: {user_message}"
        messages.append({"role": "user", "content": context_message})
        
        # Only OpenAI supports function calling properly
        if self.provider == "openai":
            return await self._chat_with_tools_openai(messages, cells)
        else:
            # Fallback to regular chat for Gemini
            return await self._chat_without_tools(messages)
    
    async def _chat_with_tools_openai(self, messages: List[Dict], cells: List[NotebookCell]) -> Dict[str, Any]:
        """Chat with OpenAI using function calling."""
        from cell_tools import CellTool
        
        if not openai_client:
            raise ValueError("OpenAI client not configured")
        
        # Prepare cells state for tool execution
        cells_state = [cell.to_dict() for cell in cells]
        
        # Build API parameters
        api_params = {
            "model": self.model_name,
            "messages": messages,
            "tools": CellTool.get_tools_definition()
        }
        
        # Add temperature or reasoning_effort
        if self.is_reasoning_model:
            api_params["reasoning_effort"] = config.DEFAULT_REASONING_EFFORT
        else:
            api_params["temperature"] = config.DEFAULT_TEMPERATURE
        
        # Call OpenAI
        response = await openai_client.chat.completions.create(**api_params)
        
        choice = response.choices[0]
        message = choice.message
        
        # Check if agent wants to use tools
        tool_calls = []
        if message.tool_calls:
            for tool_call in message.tool_calls:
                import json
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                # Execute the tool
                tool_result = CellTool.execute_tool(tool_name, tool_args, cells_state)
                
                tool_calls.append({
                    "id": tool_call.id,
                    "name": tool_name,
                    "arguments": tool_args,
                    "result": tool_result
                })
        
        return {
            "message": message.content or "I'm working on it...",
            "tool_calls": tool_calls,
            "finish_reason": choice.finish_reason
        }
    
    async def _chat_without_tools(self, messages: List[Dict]) -> Dict[str, Any]:
        """Fallback chat without tools for Gemini."""
        # Extract just the last user message for Gemini
        user_message = messages[-1]["content"]
        
        response = await self._generate_gemini_response(user_message)
        
        return {
            "message": response,
            "tool_calls": [],
            "finish_reason": "stop"
        }
    
    def _build_notebook_context(self, cells: List[NotebookCell], highlight_cell: Optional[str] = None) -> str:
        """Build a string representation of the notebook context."""
        context_parts = []
        
        for i, cell in enumerate(cells):
            marker = " <<< ERROR HERE" if cell.cell_id == highlight_cell else ""
            context_parts.append(f"\n--- Cell {i+1} (ID: {cell.cell_id}){marker} ---")
            context_parts.append(f"Code:\n{cell.code}")
            
            if cell.execution_count:
                context_parts.append(f"Execution count: {cell.execution_count}")
            
            if cell.outputs:
                context_parts.append("Outputs:")
                for output in cell.outputs:
                    if output['type'] == 'stream':
                        context_parts.append(f"  {output['name']}: {output['text']}")
                    elif output['type'] == 'execute_result':
                        data = output.get('data', {})
                        if 'text/plain' in data:
                            context_parts.append(f"  Result: {data['text/plain']}")
            
            if cell.error:
                context_parts.append(f"ERROR: {cell.error['ename']}: {cell.error['evalue']}")
                context_parts.append(f"Traceback:\n" + "\n".join(cell.error['traceback']))
        
        return "\n".join(context_parts)
    
    async def _generate_response(self, prompt: str) -> str:
        """Generate response from AI model (OpenAI or Gemini)."""
        if self.provider == "openai":
            return await self._generate_openai_response(prompt)
        else:
            return await self._generate_gemini_response(prompt)
    
    async def _generate_openai_response(self, prompt: str) -> str:
        """Generate response from OpenAI."""
        if not openai_client:
            raise ValueError("OpenAI client not configured. Please set OPENAI_API_KEY in .env")
        
        # Build API parameters based on model type
        api_params = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        # Reasoning models use reasoning_effort, non-reasoning models use temperature
        if self.is_reasoning_model:
            api_params["reasoning_effort"] = config.DEFAULT_REASONING_EFFORT
        else:
            api_params["temperature"] = config.DEFAULT_TEMPERATURE
        
        response = await openai_client.chat.completions.create(**api_params)
        return response.choices[0].message.content
    
    async def _generate_gemini_response(self, prompt: str) -> str:
        """Generate response from Gemini."""
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.gemini_model.generate_content(prompt)
        )
        return response.text
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from model response."""
        import json
        import re
        
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            response = json_match.group(1)
        
        # Try to parse
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON object in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            raise ValueError("Could not parse JSON from response")


class AgentService:
    """Service for managing AI agents with different models."""
    
    def __init__(self):
        self.agents: Dict[str, NotebookAgent] = {}
        self.default_model = "gpt-4o-mini"
    
    def get_agent(self, model_name: Optional[str] = None) -> NotebookAgent:
        """Get or create an agent for a specific model."""
        model = model_name or self.default_model
        
        if model not in self.agents:
            self.agents[model] = NotebookAgent(model)
        
        return self.agents[model]


# Global agent service
agent_service = AgentService()

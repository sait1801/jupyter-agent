"""Tools for AI agents to manipulate notebook cells and run terminal commands."""
from typing import List, Dict, Any, Optional

class CellTool:
    """Tools for manipulating notebook cells and system operations."""
    
    @staticmethod
    def read_cells():
        return {
            "type": "function",
            "function": {
                "name": "read_cells",
                "description": "Read the code from one or all cells in the notebook. Use this to understand the current state of the notebook.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cell_id": {
                            "type": "string",
                            "description": "The ID of the specific cell to read. If not provided, returns all cells."
                        }
                    }
                }
            }
        }

    @staticmethod
    def update_cell():
        return {
            "type": "function",
            "function": {
                "name": "update_cell",
                "description": "Update the code in an existing cell. Use this to fix errors or improve code.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cell_id": {
                            "type": "string",
                            "description": "The ID of the cell to update"
                        },
                        "code": {
                            "type": "string",
                            "description": "The new code for the cell"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Brief explanation of why you're updating this cell"
                        }
                    },
                    "required": ["cell_id", "code", "reason"]
                }
            }
        }

    @staticmethod
    def insert_cell():
        return {
            "type": "function",
            "function": {
                "name": "insert_cell",
                "description": "Insert a new code cell at a specific position in the notebook.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code for the new cell"
                        },
                        "index": {
                            "type": "integer",
                            "description": "The position to insert the cell (0 = beginning, -1 = end). Default is -1 (end)."
                        },
                        "reason": {
                            "type": "string",
                            "description": "Brief explanation of what this cell does"
                        }
                    },
                    "required": ["code", "reason"]
                }
            }
        }

    @staticmethod
    def delete_cell():
        return {
            "type": "function",
            "function": {
                "name": "delete_cell",
                "description": "Delete a cell from the notebook. Use with caution!",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cell_id": {
                            "type": "string",
                            "description": "The ID of the cell to delete"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Brief explanation of why you're deleting this cell"
                        }
                    },
                    "required": ["cell_id", "reason"]
                }
            }
        }

    @staticmethod
    def run_cell():
        return {
            "type": "function",
            "function": {
                "name": "run_cell",
                "description": "Execute a specific cell and see its output. Use this after updating cells to verify they work.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cell_id": {
                            "type": "string",
                            "description": "The ID of the cell to run"
                        }
                    },
                    "required": ["cell_id"]
                }
            }
        }

    @staticmethod
    def run_terminal_command():
        return {
            "type": "function",
            "function": {
                "name": "run_terminal_command",
                "description": "Run a shell command in the terminal. Use this to install packages (pip install), manage files, or run scripts. Supports Bash/PowerShell syntax.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The shell command to execute."
                        }
                    },
                    "required": ["command"]
                }
            }
        }

    @staticmethod
    def get_openai_tool_definitions():
        """Get all tool definitions for OpenAI."""
        return [
            CellTool.read_cells(),
            CellTool.update_cell(),
            CellTool.insert_cell(),
            CellTool.delete_cell(),
            CellTool.run_cell(),
            CellTool.run_terminal_command()
        ]
    
    # Alias for compatibility if needed
    get_tools_definition = get_openai_tool_definitions

    @staticmethod
    def execute_tool(name: str, args: Dict[str, Any], cells_state: List[Dict] = None) -> Dict[str, Any]:
        """
        Simulate tool execution (returns the action to be taken).
        """
        if name == "read_cells":
            return {"action": "read_cells", "success": True}
        elif name == "update_cell":
            return {"action": "update_cell", "cell_id": args.get("cell_id"), "code": args.get("code"), "success": True}
        elif name == "insert_cell":
            return {"action": "insert_cell", "code": args.get("code"), "index": args.get("index", -1), "success": True}
        elif name == "delete_cell":
            return {"action": "delete_cell", "cell_id": args.get("cell_id"), "success": True}
        elif name == "run_cell":
            return {"action": "run_cell", "cell_id": args.get("cell_id"), "success": True}
        elif name == "run_terminal_command":
            return {"action": "run_terminal_command", "command": args.get("command"), "success": True}
        else:
            return {"error": f"Unknown tool: {name}", "success": False}

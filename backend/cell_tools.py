"""Tools for AI agents to manipulate notebook cells."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class CellTool:
    """Tools for manipulating notebook cells."""
    
    @staticmethod
    def get_tools_definition() -> List[Dict[str, Any]]:
        """Get OpenAI function calling definitions for cell manipulation tools."""
        return [
            {
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
            },
            {
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
            },
            {
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
            },
            {
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
            },
            {
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
        ]
    
    @staticmethod
    def execute_tool(tool_name: str, arguments: Dict[str, Any], cells_state: List[Dict]) -> Dict[str, Any]:
        """
        Execute a tool and return the result.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            cells_state: Current state of all cells
            
        Returns:
            Result of the tool execution
        """
        if tool_name == "read_cells":
            return CellTool._read_cells(arguments, cells_state)
        elif tool_name == "update_cell":
            return CellTool._update_cell(arguments, cells_state)
        elif tool_name == "insert_cell":
            return CellTool._insert_cell(arguments, cells_state)
        elif tool_name == "delete_cell":
            return CellTool._delete_cell(arguments, cells_state)
        elif tool_name == "run_cell":
            return CellTool._run_cell(arguments, cells_state)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    @staticmethod
    def _read_cells(args: Dict, cells: List[Dict]) -> Dict[str, Any]:
        """Read cells."""
        cell_id = args.get("cell_id")
        
        if cell_id:
            # Read specific cell
            for cell in cells:
                if cell["cell_id"] == cell_id:
                    return {
                        "success": True,
                        "cell": {
                            "id": cell["cell_id"],
                            "code": cell["code"],
                            "outputs": cell.get("outputs", []),
                            "error": cell.get("error")
                        }
                    }
            return {"success": False, "error": f"Cell {cell_id} not found"}
        else:
            # Read all cells
            return {
                "success": True,
                "cells": [
                    {
                        "id": cell["cell_id"],
                        "code": cell["code"],
                        "outputs": cell.get("outputs", []),
                        "error": cell.get("error")
                    }
                    for cell in cells
                ]
            }
    
    @staticmethod
    def _update_cell(args: Dict, cells: List[Dict]) -> Dict[str, Any]:
        """Update a cell."""
        return {
            "action": "update_cell",
            "cell_id": args["cell_id"],
            "code": args["code"],
            "reason": args.get("reason", ""),
            "success": True
        }
    
    @staticmethod
    def _insert_cell(args: Dict, cells: List[Dict]) -> Dict[str, Any]:
        """Insert a new cell."""
        return {
            "action": "insert_cell",
            "code": args["code"],
            "index": args.get("index", -1),
            "reason": args.get("reason", ""),
            "success": True
        }
    
    @staticmethod
    def _delete_cell(args: Dict, cells: List[Dict]) -> Dict[str, Any]:
        """Delete a cell."""
        return {
            "action": "delete_cell",
            "cell_id": args["cell_id"],
            "reason": args.get("reason", ""),
            "success": True
        }
    
    @staticmethod
    def _run_cell(args: Dict, cells: List[Dict]) -> Dict[str, Any]:
        """Request to run a cell."""
        return {
            "action": "run_cell",
            "cell_id": args["cell_id"],
            "success": True
        }

"""Jupyter kernel manager for executing notebook cells."""
import asyncio
import uuid
from typing import Dict, List, Optional, Any
from jupyter_client import KernelManager
import queue
import logging

logger = logging.getLogger(__name__)


class NotebookKernel:
    """Manages a single Jupyter kernel instance."""
    
    def __init__(self, kernel_id: str):
        self.kernel_id = kernel_id
        self.manager = KernelManager()
        self.client = None
        self.is_running = False
        
    async def start(self):
        """Start the kernel."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.manager.start_kernel)
        self.client = self.manager.client()
        self.client.start_channels()
        self.is_running = True
        logger.info(f"Kernel {self.kernel_id} started")
        
    async def execute_cell(self, code: str, cell_id: str) -> Dict[str, Any]:
        """Execute a cell and return results."""
        if not self.is_running:
            raise RuntimeError("Kernel is not running")
        
        loop = asyncio.get_event_loop()
        
        # Execute code
        msg_id = await loop.run_in_executor(
            None, 
            self.client.execute, 
            code
        )
        
        # Collect outputs
        outputs = []
        error = None
        execution_count = None
        
        while True:
            try:
                msg = await loop.run_in_executor(
                    None,
                    self.client.get_iopub_msg,
                    10  # timeout
                )
                
                msg_type = msg['msg_type']
                content = msg['content']
                
                if msg_type == 'execute_input':
                    execution_count = content.get('execution_count')
                    
                elif msg_type == 'execute_result':
                    outputs.append({
                        'type': 'execute_result',
                        'data': content.get('data', {}),
                        'execution_count': content.get('execution_count')
                    })
                    
                elif msg_type == 'display_data':
                    outputs.append({
                        'type': 'display_data',
                        'data': content.get('data', {})
                    })
                    
                elif msg_type == 'stream':
                    outputs.append({
                        'type': 'stream',
                        'name': content.get('name'),
                        'text': content.get('text')
                    })
                    
                elif msg_type == 'error':
                    error = {
                        'ename': content.get('ename'),
                        'evalue': content.get('evalue'),
                        'traceback': content.get('traceback', [])
                    }
                    
                elif msg_type == 'status':
                    if content.get('execution_state') == 'idle':
                        break
                        
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Error getting message: {e}")
                break
        
        return {
            'cell_id': cell_id,
            'execution_count': execution_count,
            'outputs': outputs,
            'error': error,
            'status': 'error' if error else 'success'
        }
    
    async def interrupt(self):
        """Interrupt the kernel."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.manager.interrupt_kernel)
        logger.info(f"Kernel {self.kernel_id} interrupted")
        
    async def restart(self):
        """Restart the kernel."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.manager.restart_kernel)
        logger.info(f"Kernel {self.kernel_id} restarted")
        
    async def shutdown(self):
        """Shutdown the kernel."""
        if self.client:
            self.client.stop_channels()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.manager.shutdown_kernel)
        self.is_running = False
        logger.info(f"Kernel {self.kernel_id} shutdown")


class KernelManagerService:
    """Manages multiple kernel instances."""
    
    def __init__(self):
        self.kernels: Dict[str, NotebookKernel] = {}
        
    async def create_kernel(self) -> str:
        """Create a new kernel and return its ID."""
        kernel_id = str(uuid.uuid4())
        kernel = NotebookKernel(kernel_id)
        await kernel.start()
        self.kernels[kernel_id] = kernel
        return kernel_id
    
    def get_kernel(self, kernel_id: str) -> Optional[NotebookKernel]:
        """Get a kernel by ID."""
        return self.kernels.get(kernel_id)
    
    async def shutdown_kernel(self, kernel_id: str):
        """Shutdown and remove a kernel."""
        kernel = self.kernels.get(kernel_id)
        if kernel:
            await kernel.shutdown()
            del self.kernels[kernel_id]
    
    async def shutdown_all(self):
        """Shutdown all kernels."""
        for kernel_id in list(self.kernels.keys()):
            await self.shutdown_kernel(kernel_id)


# Global kernel manager instance
kernel_manager = KernelManagerService()

// ==================== Configuration ====================
const API_BASE_URL = 'http://localhost:8000';

// ==================== State Management ====================
class AppState {
    constructor() {
        this.kernelId = null;
        this.cells = [];
        this.selectedModel = 'gpt-4o';  // Default to GPT-4o
        this.notebookName = 'Untitled Notebook';
        this.conversationHistory = [];
    }

    addCell(code = '', cellType = 'code', index = -1) {
        const cell = {
            id: `cell-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            code,
            cellType,
            executionCount: null,
            outputs: [],
            error: null
        };

        if (index === -1 || index >= this.cells.length) {
            this.cells.push(cell);
        } else {
            this.cells.splice(index, 0, cell);
        }

        return cell;
    }

    getCell(cellId) {
        return this.cells.find(c => c.id === cellId);
    }

    updateCell(cellId, updates) {
        const cell = this.getCell(cellId);
        if (cell) {
            Object.assign(cell, updates);
        }
    }

    deleteCell(cellId) {
        const index = this.cells.findIndex(c => c.id === cellId);
        if (index !== -1) {
            this.cells.splice(index, 1);
        }
    }

    addMessage(role, content) {
        this.conversationHistory.push({ role, content });
    }
}

const state = new AppState();

// ==================== API Client ====================
class APIClient {
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Request failed');
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async createKernel() {
        return this.request('/kernel/create', { method: 'POST' });
    }

    async restartKernel(kernelId) {
        return this.request(`/kernel/${kernelId}/restart`, { method: 'POST' });
    }

    async executeCell(kernelId, cellId, code) {
        return this.request('/execute', {
            method: 'POST',
            body: JSON.stringify({ kernel_id: kernelId, cell_id: cellId, code })
        });
    }

    async chat(cells, userMessage, conversationHistory, modelName) {
        return this.request('/agent/chat', {
            method: 'POST',
            body: JSON.stringify({
                cells: cells.map(c => ({
                    cell_id: c.id,
                    code: c.code,
                    execution_count: c.executionCount,
                    outputs: c.outputs,
                    error: c.error
                })),
                user_message: userMessage,
                conversation_history: conversationHistory,
                model_name: modelName
            })
        });
    }

    async saveNotebook(filename, cells) {
        return this.request('/notebook/save', {
            method: 'POST',
            body: JSON.stringify({
                filename,
                cells: cells.map(c => ({
                    cell_id: c.id,
                    code: c.code,
                    cell_type: c.cellType,
                    execution_count: c.executionCount,
                    outputs: c.outputs
                }))
            })
        });
    }

    async loadNotebook(filename) {
        return this.request(`/notebook/load/${filename}`);
    }

    async listNotebooks() {
        return this.request('/notebook/list');
    }
}

const api = new APIClient();

// ==================== UI Components ====================
class UI {
    static createCell(cell) {
        const cellElement = document.createElement('div');
        cellElement.className = 'cell';
        cellElement.dataset.cellId = cell.id;

        cellElement.innerHTML = `
            <div class="cell-header">
                <span class="cell-count">${cell.executionCount ? `[${cell.executionCount}]` : '[ ]'}</span>
                <div class="cell-actions">
                    <button class="btn-icon run-cell" title="Run Cell (Shift+Enter)">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M4 2L12 8L4 14V2Z"/>
                        </svg>
                    </button>
                    <button class="btn-icon delete-cell" title="Delete Cell">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M2 4H14M6 4V2H10V4M6 4V12M10 4V12M4 4V13C4 13.55 4.45 14 5 14H11C11.55 14 12 13.55 12 13V4"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div class="cell-editor">
                <textarea class="code-input" placeholder="# Enter your Python code here...">${cell.code}</textarea>
            </div>
            ${cell.outputs.length > 0 || cell.error ? '<div class="cell-output"></div>' : ''}
        `;

        // Event listeners
        const runBtn = cellElement.querySelector('.run-cell');
        runBtn.addEventListener('click', () => CellManager.runCell(cell.id));

        const deleteBtn = cellElement.querySelector('.delete-cell');
        deleteBtn.addEventListener('click', () => CellManager.deleteCell(cell.id));

        const codeInput = cellElement.querySelector('.code-input');
        codeInput.addEventListener('input', (e) => {
            state.updateCell(cell.id, { code: e.target.value });
        });

        // Shift+Enter to run
        codeInput.addEventListener('keydown', (e) => {
            if (e.shiftKey && e.key === 'Enter') {
                e.preventDefault();
                CellManager.runCell(cell.id);
            }
        });

        UI.updateCellOutput(cellElement, cell);

        return cellElement;
    }

    static updateCellOutput(cellElement, cell) {
        const existingOutput = cellElement.querySelector('.cell-output');

        if (cell.outputs.length === 0 && !cell.error) {
            if (existingOutput) {
                existingOutput.remove();
            }
            cellElement.classList.remove('cell-error', 'cell-running');
            return;
        }

        let outputElement = existingOutput;
        if (!outputElement) {
            outputElement = document.createElement('div');
            outputElement.className = 'cell-output';
            cellElement.appendChild(outputElement);
        }

        outputElement.innerHTML = '';

        // Render outputs
        cell.outputs.forEach(output => {
            const outputItem = document.createElement('div');
            outputItem.className = 'output-item';

            if (output.type === 'stream') {
                outputItem.innerHTML = `<pre class="output-stream">${this.escapeHtml(output.text)}</pre>`;
            } else if (output.type === 'execute_result' || output.type === 'display_data') {
                const data = output.data || {};
                if (data['text/plain']) {
                    outputItem.innerHTML = `<pre class="output-result">${this.escapeHtml(data['text/plain'])}</pre>`;
                }
            }

            outputElement.appendChild(outputItem);
        });

        // Render error
        if (cell.error) {
            const errorItem = document.createElement('div');
            errorItem.className = 'output-error';
            errorItem.innerHTML = `
                <div class="error-name">${this.escapeHtml(cell.error.ename)}: ${this.escapeHtml(cell.error.evalue)}</div>
                <pre class="error-traceback">${this.escapeHtml(cell.error.traceback.join('\n'))}</pre>
            `;
            outputElement.appendChild(errorItem);
            cellElement.classList.add('cell-error');
        } else {
            cellElement.classList.remove('cell-error');
        }

        // Update cell count
        const cellCount = cellElement.querySelector('.cell-count');
        cellCount.textContent = cell.executionCount ? `[${cell.executionCount}]` : '[ ]';
    }

    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    static showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'toastSlideIn 0.3s ease-out reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    static setKernelStatus(status) {
        const kernelStatus = document.getElementById('kernel-status');
        const indicator = kernelStatus.querySelector('.status-indicator');
        const text = kernelStatus.querySelector('span');

        indicator.className = 'status-indicator';

        if (status === 'idle') {
            indicator.classList.add('status-idle');
            text.textContent = 'Idle';
        } else if (status === 'busy') {
            indicator.classList.add('status-busy');
            text.textContent = 'Busy';
        } else if (status === 'error') {
            indicator.classList.add('status-error');
            text.textContent = 'Error';
        }
    }

    static addChatMessage(content, isUser = false) {
        const chatMessages = document.getElementById('chat-messages');
        const message = document.createElement('div');
        message.className = isUser ? 'user-message' : 'agent-message';

        message.innerHTML = `
            <div class="message-avatar">${isUser ? '👤' : '🤖'}</div>
            <div class="message-content">${content}</div>
        `;

        chatMessages.appendChild(message);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        return message;
    }

    static addToolCall(messageElement, toolName, args, result) {
        const content = messageElement.querySelector('.message-content');
        const toolCall = document.createElement('div');
        toolCall.className = 'tool-call';

        let status = 'success';
        if (result && result.error) status = 'error';

        // Format args for display
        const argsStr = Object.entries(args)
            .map(([k, v]) => `${k}: ${typeof v === 'string' && v.length > 50 ? v.substring(0, 50) + '...' : v}`)
            .join(', ');

        toolCall.innerHTML = `
            <div class="tool-header">
                <span class="tool-name">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
                    </svg>
                    ${toolName}
                </span>
                <span class="tool-status ${status}">${status}</span>
            </div>
            <div class="tool-body">${argsStr}</div>
        `;

        content.appendChild(toolCall);

        // Scroll to bottom
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// ==================== Cell Manager ====================
class CellManager {
    static async runCell(cellId) {
        if (!state.kernelId) {
            UI.showToast('No kernel running. Starting kernel...', 'info');
            await KernelManager.createKernel();
        }

        const cell = state.getCell(cellId);
        if (!cell) return;

        const cellElement = document.querySelector(`[data-cell-id="${cellId}"]`);
        cellElement.classList.add('cell-running');
        UI.setKernelStatus('busy');

        try {
            const result = await api.executeCell(state.kernelId, cellId, cell.code);

            state.updateCell(cellId, {
                executionCount: result.execution_count,
                outputs: result.outputs,
                error: result.error
            });

            UI.updateCellOutput(cellElement, state.getCell(cellId));
            UI.setKernelStatus('idle');
            return result;
        } catch (error) {
            UI.showToast(`Error executing cell: ${error.message}`, 'error');
            UI.setKernelStatus('error');
            throw error;
        } finally {
            cellElement.classList.remove('cell-running');
        }
    }

    static addCell(code = '', index = -1) {
        const cell = state.addCell(code, 'code', index);
        const cellElement = UI.createCell(cell);

        const container = document.getElementById('cells-container');
        if (index === -1 || index >= container.children.length) {
            container.appendChild(cellElement);
        } else {
            container.insertBefore(cellElement, container.children[index]);
        }

        // Focus the new cell
        setTimeout(() => {
            cellElement.querySelector('.code-input').focus();
        }, 100);

        return cell;
    }

    static deleteCell(cellId) {
        const cellElement = document.querySelector(`[data-cell-id="${cellId}"]`);
        if (cellElement) {
            cellElement.style.animation = 'slideIn 0.3s ease-out reverse';
            setTimeout(() => {
                cellElement.remove();
                state.deleteCell(cellId);
            }, 300);
        }
    }

    static renderAllCells() {
        const container = document.getElementById('cells-container');
        container.innerHTML = '';

        state.cells.forEach(cell => {
            const cellElement = UI.createCell(cell);
            container.appendChild(cellElement);
        });
    }

    static updateCellCode(cellId, newCode) {
        state.updateCell(cellId, { code: newCode });
        const cellElement = document.querySelector(`[data-cell-id="${cellId}"]`);
        if (cellElement) {
            cellElement.querySelector('.code-input').value = newCode;
        }
    }
}

// ==================== Kernel Manager ====================
class KernelManager {
    static async createKernel() {
        try {
            UI.showToast('Starting kernel...', 'info');
            const result = await api.createKernel();
            state.kernelId = result.kernel_id;
            UI.setKernelStatus('idle');
            UI.showToast('Kernel started successfully', 'success');
        } catch (error) {
            UI.showToast(`Failed to start kernel: ${error.message}`, 'error');
            UI.setKernelStatus('error');
        }
    }

    static async restartKernel() {
        if (!state.kernelId) {
            await this.createKernel();
            return;
        }

        try {
            UI.showToast('Restarting kernel...', 'info');
            await api.restartKernel(state.kernelId);

            // Clear execution counts
            state.cells.forEach(cell => {
                state.updateCell(cell.id, { executionCount: null, outputs: [], error: null });
            });
            CellManager.renderAllCells();

            UI.setKernelStatus('idle');
            UI.showToast('Kernel restarted successfully', 'success');
        } catch (error) {
            UI.showToast(`Failed to restart kernel: ${error.message}`, 'error');
            UI.setKernelStatus('error');
        }
    }
}

// ==================== Agent Manager ====================
class AgentManager {
    static async chat(userMessage) {
        try {
            // Add user message to UI and history
            UI.addChatMessage(userMessage, true);
            state.addMessage('user', userMessage);

            // Show loading state
            const loadingMsg = UI.addChatMessage('<div class="spinner"></div> Thinking...', false);

            // Call API
            const result = await api.chat(
                state.cells,
                userMessage,
                state.conversationHistory,
                state.selectedModel
            );

            // Remove loading message
            loadingMsg.remove();

            // Create agent message element
            const agentMsgElement = UI.addChatMessage(result.message || "I've processed your request.", false);
            state.addMessage('assistant', result.message);

            // Process tool calls
            if (result.tool_calls && result.tool_calls.length > 0) {
                for (const toolCall of result.tool_calls) {
                    // Visualize tool call
                    UI.addToolCall(agentMsgElement, toolCall.name, toolCall.arguments, toolCall.result);

                    // Apply tool effects to frontend state if needed
                    // (Most effects happen on backend, but we need to sync frontend)
                    await this.handleToolEffect(toolCall.name, toolCall.arguments, toolCall.result);
                }
            }

        } catch (error) {
            UI.showToast(`Error in chat: ${error.message}`, 'error');
            UI.addChatMessage(`Error: ${error.message}`, false);
        }
    }

    static async handleToolEffect(toolName, args, result) {
        // Sync frontend state with backend changes
        if (toolName === 'update_cell' && result.success) {
            CellManager.updateCellCode(args.cell_id, args.code);
            UI.showToast('Cell updated by AI', 'success');
        }
        else if (toolName === 'insert_cell' && result.success) {
            CellManager.addCell(args.code, args.index);
            UI.showToast('New cell created by AI', 'success');
        }
        else if (toolName === 'delete_cell' && result.success) {
            CellManager.deleteCell(args.cell_id);
            UI.showToast('Cell deleted by AI', 'info');
        }
        else if (toolName === 'run_cell' && result.success) {
            // We need to actually run it on frontend to see animation/updates
            await CellManager.runCell(args.cell_id);
        }
    }
}

// ==================== Notebook Manager ====================
class NotebookManager {
    static async save() {
        const filename = state.notebookName.endsWith('.ipynb')
            ? state.notebookName
            : `${state.notebookName}.ipynb`;

        try {
            await api.saveNotebook(filename, state.cells);
            UI.showToast('Notebook saved successfully', 'success');
        } catch (error) {
            UI.showToast(`Failed to save notebook: ${error.message}`, 'error');
        }
    }

    static async showLoadModal() {
        const modal = document.getElementById('load-modal');
        const notebooksList = document.getElementById('notebooks-list');

        try {
            const result = await api.listNotebooks();

            if (result.notebooks.length === 0) {
                notebooksList.innerHTML = '<p class="info-text">No saved notebooks found.</p>';
            } else {
                notebooksList.innerHTML = result.notebooks.map(nb => `
                    <div class="notebook-item" data-filename="${nb.filename}">
                        <div class="notebook-item-name">${nb.filename}</div>
                        <div class="notebook-item-meta">
                            Modified: ${new Date(nb.modified * 1000).toLocaleString()}
                        </div>
                    </div>
                `).join('');

                // Add click handlers
                notebooksList.querySelectorAll('.notebook-item').forEach(item => {
                    item.addEventListener('click', () => {
                        this.load(item.dataset.filename);
                        modal.classList.remove('active');
                    });
                });
            }

            modal.classList.add('active');
        } catch (error) {
            UI.showToast(`Failed to load notebooks: ${error.message}`, 'error');
        }
    }

    static async load(filename) {
        try {
            const result = await api.loadNotebook(filename);

            state.cells = result.cells.map(cell => ({
                id: cell.cell_id,
                code: cell.code,
                cellType: cell.cell_type,
                executionCount: cell.execution_count,
                outputs: cell.outputs || [],
                error: null
            }));

            state.notebookName = filename;
            document.getElementById('notebook-name').value = filename;

            CellManager.renderAllCells();
            UI.showToast('Notebook loaded successfully', 'success');
        } catch (error) {
            UI.showToast(`Failed to load notebook: ${error.message}`, 'error');
        }
    }
}

// ==================== Event Listeners ====================
document.addEventListener('DOMContentLoaded', () => {
    // Add initial cell
    CellManager.addCell();

    // Header buttons
    document.getElementById('add-cell-btn').addEventListener('click', () => CellManager.addCell());
    document.getElementById('restart-kernel-btn').addEventListener('click', () => KernelManager.restartKernel());
    document.getElementById('save-btn').addEventListener('click', () => NotebookManager.save());
    document.getElementById('load-btn').addEventListener('click', () => NotebookManager.showLoadModal());

    // Notebook name
    document.getElementById('notebook-name').addEventListener('change', (e) => {
        state.notebookName = e.target.value;
    });

    // Model selector
    document.getElementById('model-select').addEventListener('change', (e) => {
        state.selectedModel = e.target.value;
    });

    // Chat
    const sendChat = () => {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();

        if (message) {
            AgentManager.chat(message);
            input.value = '';
            input.style.height = 'auto'; // Reset height
        }
    };

    document.getElementById('send-chat-btn').addEventListener('click', sendChat);
    document.getElementById('chat-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChat();
        }
    });

    // Auto-resize textarea
    const chatInput = document.getElementById('chat-input');
    chatInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Sidebar toggle
    document.getElementById('toggle-sidebar').addEventListener('click', () => {
        document.getElementById('ai-sidebar').classList.toggle('collapsed');
    });

    // Modal close
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.modal').classList.remove('active');
        });
    });

    // Click outside modal to close
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });

    // Create kernel on startup
    KernelManager.createKernel();
});

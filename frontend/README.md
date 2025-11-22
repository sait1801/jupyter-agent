# Jupyter Agent Frontend

Beautiful, modern notebook interface with AI agent sidebar.

## Features

- **Jupyter-style Notebook**: Familiar cell-based interface
- **Real-time Execution**: Execute cells and see results immediately
- **AI Agent Sidebar**: Integrated AI assistant with multiple capabilities
- **Multiple LLM Support**: Choose between different Gemini models
- **Error Analysis**: Automatic error detection and intelligent fix suggestions
- **Code Generation**: Ask the AI to write code based on your notebook context
- **Optimization**: Get suggestions to improve your code
- **Save/Load**: Persist notebooks as .ipynb files

## Running the Frontend

Since this is a vanilla HTML/CSS/JS application, you can run it in several ways:

### Option 1: Using Python's HTTP Server

```bash
cd frontend
python -m http.server 5173
```

Then open http://localhost:5173 in your browser.

### Option 2: Using Node.js http-server

```bash
npm install -g http-server
cd frontend
http-server -p 5173
```

### Option 3: Using VS Code Live Server

1. Install the "Live Server" extension
2. Right-click on `index.html`
3. Select "Open with Live Server"

## Configuration

Make sure the backend is running on `http://localhost:8000`. If you're running the backend on a different port, update the `API_BASE_URL` in `app.js`:

```javascript
const API_BASE_URL = 'http://localhost:YOUR_PORT';
```

## Interface Guide

### Notebook Area
- **Add Cell**: Click the "+ Add Cell" button
- **Run Cell**: Click the play button or press Shift+Enter
- **Delete Cell**: Click the trash icon
- **Edit Code**: Click in the cell and start typing

### AI Sidebar

#### Chat Tab
- Ask questions about your code
- Request code generation
- Get explanations
- The AI understands your notebook context

#### Analyze Tab
- Automatically appears when a cell has an error
- Shows intelligent fix suggestions
- Indicates which cells need changes
- Suggests whether kernel restart is needed

#### Optimize Tab
- Click "Analyze & Optimize"
- Get suggestions for improving your code
- See priority levels for each suggestion

## Design

The interface features:
- **Dark Theme**: Easy on the eyes for long coding sessions
- **Premium Aesthetics**: Beautiful gradients and smooth animations
- **Responsive**: Works on desktop and tablet
- **Accessible**: Keyboard shortcuts and clear visual hierarchy
- **Modern Typography**: Inter and JetBrains Mono fonts

## Browser Compatibility

Works best on modern browsers:
- Chrome/Edge (recommended)
- Firefox
- Safari

## Development

The frontend is built with:
- **Vanilla HTML/CSS/JS**: No build step required!
- **Modern CSS**: CSS variables, Grid, Flexbox
- **Async/Await**: Modern JavaScript patterns
- **Fetch API**: For backend communication

## Tips

1. **Shift+Enter**: Run the current cell
2. **Auto-save**: The AI agent automatically analyzes errors
3. **Context Matters**: The AI sees all your cells, so it gives better suggestions
4. **Model Selection**: Try different models for different tasks (Pro for complex, Flash for speed)

## File Structure

```
frontend/
├── index.html      # Main HTML structure
├── styles.css      # All styles (dark theme, animations)
├── app.js          # Application logic
└── README.md       # This file
```

## License

MIT

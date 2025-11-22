# Quick Start Guide

Welcome to Jupyter Agent! This guide will get you up and running in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- A Gemini API key (get one at https://ai.google.dev/)

## Step 1: Setup Environment

### Windows
```powershell
.\setup.ps1
```

### Mac/Linux
```bash
chmod +x setup.sh
./setup.sh
```

## Step 2: Configure API Key

Edit `backend/.env` and add your Gemini API key:

```
GEMINI_API_KEY=your_actual_api_key_here
```

## Step 3: Start Backend

```bash
cd backend
..\.venv\Scripts\Activate.ps1  # Windows
# or
source ../.venv/bin/activate   # Mac/Linux

python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 4: Start Frontend

Open a new terminal:

```bash
cd frontend
python -m http.server 5173
```

## Step 5: Open in Browser

Navigate to: http://localhost:5173

## First Steps

### 1. Write Your First Cell

The notebook will have one empty cell. Try typing:

```python
print("Hello, Jupyter Agent!")
```

Press **Shift+Enter** to run it.

### 2. Try the AI Agent

Add another cell with some intentional error:

```python
import pandas as pd
df = pd.raed_csv("data.csv")  # Typo: raed instead of read
```

Run it (Shift+Enter). The AI will automatically:
- Detect the error
- Analyze the context
- Suggest a fix
- Show you the corrected code

Click "Apply Fix" and run again!

### 3. Ask for Code Generation

Click on the **Chat** tab in the AI sidebar and type:

```
Create a function to generate random data and plot it
```

The AI will generate context-aware code and let you add it to your notebook!

### 4. Optimize Your Notebook

After writing some code, go to the **Optimize** tab and click "Analyze & Optimize". The AI will suggest improvements!

## Keyboard Shortcuts

- **Shift+Enter**: Run current cell
- **Ctrl+S**: Save notebook (manual save trigger)

## Tips for Best Results

1. **Give Context**: The AI sees all your cells, so related code helps it understand better
2. **Use Chat**: Ask questions about your code or request new features
3. **Check Fixes**: Review AI suggestions before applying them
4. **Save Often**: Use the Save button to persist your work

## Example Workflow

Here's a typical workflow:

1. **Data Loading**
   ```python
   import pandas as pd
   df = pd.read_csv("mydata.csv")
   ```

2. **Exploration**
   ```python
   df.head()
   df.describe()
   ```

3. **Get AI Help** (if there's an error)
   - AI analyzes the error
   - Suggests which cell to fix
   - You apply the fix

4. **Continue** (without restarting!)
   - Fix is applied
   - Continue from where you left off
   - No need to re-run everything

## Troubleshooting

### Backend won't start
- Check that port 8000 is not in use
- Verify your Gemini API key is correct in `.env`
- Make sure virtual environment is activated

### Frontend can't connect
- Ensure backend is running on port 8000
- Check browser console for errors
- Try a different browser (Chrome/Edge recommended)

### AI not responding
- Verify Gemini API key is valid
- Check backend logs for errors
- Try a different model in the dropdown

## What's Next?

- Explore different AI models (Gemini Pro vs Flash)
- Try the optimization feature
- Save and load notebooks
- Build something amazing!

## Need Help?

- Check the main README.md
- Look at backend/README.md for API details
- Look at frontend/README.md for UI details

Happy coding! 🚀

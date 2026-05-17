# Software MRI - Quick Start Guide

## Prerequisites

Before you begin, ensure you have:
- **Python 3.11+** installed
- **Node.js 18+** and npm installed
- **Git** (to clone the repository)

Check your versions:
```bash
python3 --version  # Should be 3.11 or higher
node --version     # Should be 18 or higher
npm --version
```

---

## Installation & Setup

### Step 1: Navigate to Project Directory
```bash
cd software-mri
```

### Step 2: Run One-Shot Setup
This script creates a Python virtual environment, installs all dependencies, and sets up configuration:

**On Linux/Mac:**
```bash
bash scripts/setup.sh
```

**On Windows (PowerShell):**
```powershell
# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Copy environment template
copy .env.example .env
```

**On Windows (Git Bash):**
```bash
bash scripts/setup.sh
```

### Step 3: Configure Environment (Optional)
Edit the `.env` file to configure IBM Bob integration:

```bash
# Open .env in your editor
notepad .env  # Windows
nano .env     # Linux/Mac
```

**For demo/testing without Bob:**
- Leave `BOB_ENDPOINT` empty or commented out
- The system will use deterministic fallbacks

**To enable IBM Bob:**
```ini
BOB_ENDPOINT=http://localhost:7070
BOB_API_KEY=your-api-key-here
```

---

## Running the Application

You need **TWO terminal windows** running simultaneously:

### Terminal 1: Start Backend Server

**On Linux/Mac:**
```bash
bash scripts/run-backend.sh
```

**On Windows (PowerShell):**
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start backend
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**On Windows (Git Bash):**
```bash
bash scripts/run-backend.sh
```

**Expected Output:**
```
[software-mri] analyzing ./sample-repo ...
[software-mri] 18 modules, 24 edges
[bob] mode=REST available=False
INFO:     Uvicorn running on http://127.0.0.1:8000
```

The backend will be available at: **http://localhost:8000**

### Terminal 2: Start Frontend Dev Server

**On Linux/Mac:**
```bash
bash scripts/run-frontend.sh
```

**On Windows (PowerShell):**
```powershell
cd frontend
npm run dev
```

**On Windows (Git Bash):**
```bash
bash scripts/run-frontend.sh
```

**Expected Output:**
```
  VITE v5.4.1  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

The frontend will be available at: **http://localhost:5173**

---

## Accessing the Application

1. Open your browser and navigate to: **http://localhost:5173**
2. The application will automatically load and analyze the sample banking repository
3. You should see the dependency graph visualization

---

## Quick Demo Walkthrough

### 1. View Architecture Graph
- The main view shows the complete dependency graph
- Nodes are colored by domain (auth, billing, payments, etc.)
- Node size represents lines of code
- Click any node to see details

### 2. Check Blast Radius
- Click on `payments/processor.py` in the graph
- The right panel shows blast radius analysis
- See which modules would be affected by changes

### 3. View Technical Debt
- Click the **"Tech Debt"** tab at the top
- See the heatmap of problematic modules
- `legacy/old_gateway.py` should show high debt scores

### 4. Ask Natural Language Questions
- Click the **"Ask Bob"** tab
- Try queries like:
  - "How does authentication work?"
  - "What happens if we modernize the payment engine?"
  - "Explain the billing flow"

**Note:** Without Bob configured, you'll get deterministic fallback responses that still provide useful structural information.

---

## Manual Commands Reference

### Backend Commands

**Activate virtual environment:**
```bash
# Linux/Mac
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows Command Prompt
.venv\Scripts\activate.bat
```

**Start backend manually:**
```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Run backend tests:**
```bash
cd backend
pytest tests/
```

### Frontend Commands

**Start frontend dev server:**
```bash
cd frontend
npm run dev
```

**Build for production:**
```bash
cd frontend
npm run build
```

**Preview production build:**
```bash
cd frontend
npm run preview
```

---

## Troubleshooting

### Backend won't start

**Error: `ModuleNotFoundError: No module named 'fastapi'`**
- Solution: Activate virtual environment and reinstall dependencies
```bash
source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows
pip install -r backend/requirements.txt
```

**Error: `python3: command not found`**
- Solution: Install Python 3.11+ or use `python` instead of `python3`

### Frontend won't start

**Error: `npm: command not found`**
- Solution: Install Node.js from https://nodejs.org/

**Error: `Cannot find module 'react'`**
- Solution: Install frontend dependencies
```bash
cd frontend
npm install
```

### Port already in use

**Error: `Address already in use: 8000`**
- Solution: Kill the process using port 8000 or change the port
```bash
# Find process on port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in .env
BACKEND_PORT=8001
```

### Browser shows "Backend error"

**Error: "Backend error: Failed to fetch"**
- Solution: Ensure backend is running on http://localhost:8000
- Check backend terminal for errors
- Try accessing http://localhost:8000 directly in browser

### Bob integration not working

**Message: "Bob unavailable — using fallback"**
- This is normal if Bob isn't configured
- The system will still work with deterministic responses
- To enable Bob, configure `BOB_ENDPOINT` in `.env`

---

## Analyzing Your Own Repository

To analyze a different Python repository:

1. **Edit `.env` file:**
```ini
DEFAULT_REPO_PATH=/path/to/your/python/repo
```

2. **Restart the backend:**
- Stop the backend (Ctrl+C)
- Start it again with `bash scripts/run-backend.sh`

3. **Or use the API:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/your/repo"}'
```

---

## Stopping the Application

1. **Stop Backend:** Press `Ctrl+C` in Terminal 1
2. **Stop Frontend:** Press `Ctrl+C` in Terminal 2
3. **Deactivate virtual environment:**
```bash
deactivate
```

---

## Next Steps

- Read [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md) for the full thesis
- Check [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for technical details
- See [`docs/BOB_INTEGRATION.md`](docs/BOB_INTEGRATION.md) for Bob setup
- Review [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) for demo walkthrough
- Explore [`docs/PROJECT_ANALYSIS.md`](docs/PROJECT_ANALYSIS.md) for comprehensive analysis

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the documentation in the `docs/` folder
3. Check backend logs in Terminal 1
4. Check frontend logs in Terminal 2 and browser console (F12)
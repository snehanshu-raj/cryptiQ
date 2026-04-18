# 🚀 Quick Start - Judge Demo (Raspberry Pi 3)

## 1️⃣ Start Backend Server

```bash
cd /home/srj/cryptiq
source venv/bin/activate
pip install -q fastapi uvicorn requests
cd pq_lock
python3 judge_backend.py
```

**Expected Output:**
```
╔═══════════════════════════════════════════════════════════════╗
║   Quantum Lock Judge Demo Backend - Raspberry Pi 3            ║
║   Port: 8001                                                 ║
║   Authentication: Enabled (Password-based)                    ║
║   Endpoints:                                                  ║
║   - POST /api/authenticate       (Login with password)        ║
║   - POST /api/rsa-attack         (Shor's algorithm demo)      ║
║   - POST /api/quantum-attack     (Quantum attack details)     ║
║   - POST /api/pq-attack          (PQ defense demo)            ║
║   - POST /api/send-control-signal (Send unlock signal)        ║
║   - GET  /health                 (Health check)               ║
╚═══════════════════════════════════════════════════════════════╝

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

✅ Backend is ready. Keep this terminal open.

---

## 2️⃣ Open Frontend (New Terminal)

### Option A: Local File (No server)
```bash
# On your computer (with backend running on same machine):
open /home/srj/cryptiq/pq_lock/judge_demo_ui.html
```

### Option B: Web Server
```bash
# New terminal on RPi:
cd /home/srj/cryptiq/pq_lock
python3 -m http.server 8000

# Then open in browser:
http://localhost:8000/judge_demo_ui.html
```

### Option C: Remote Access (Via WiFi)
```bash
# On RPi - get IP:
hostname -I
# e.g., 192.168.1.100

# On judge's laptop:
http://192.168.1.100:8000/judge_demo_ui.html
```

---

## 3️⃣ Login to Judge UI

| Field    | Value          |
|----------|----------------|
| Password | `quantum2026`  |

Click **AUTHENTICATE**

---

## 4️⃣ Run Demo

### Tab 1: Classical RSA (Vulnerable)
- Shows RSA public key
- Click "START RSA ATTACK"
- Watch: Factors recovered in 0.045 seconds
- Result: **LOCK COMPROMISED**

### Tab 2: Quantum Attack (Detailed)
- Shows quantum circuit execution
- Quantum Fourier Transform
- Phase measurement
- Result: **Private key d=3 recovered**

### Tab 3: Post-Quantum (Secure)
- Click "ATTEMPT QUANTUM ATTACK"
- All 4 quantum attacks fail
- Result: **LOCK REMAINS SECURE**

---

## ✅ Testing Checklist

```bash
# Terminal 1: Backend running
# (You should see "Uvicorn running on http://0.0.0.0:8001")

# Terminal 2: Test health endpoint
curl http://localhost:8001/health

# Terminal 3: Open frontend
cd /home/srj/cryptiq/pq_lock
python3 -m http.server 8000
# Then open: http://localhost:8000/judge_demo_ui.html
```

---

## 🔑 Key Features

✅ **Authentication** - Password-protected access  
✅ **3 Attack Scenarios** - RSA vulnerable, Quantum powerful, PQ secure  
✅ **Real Backend API** - FastAPI server on port 8001  
✅ **No Build Required** - Single HTML file, no compilation  
✅ **Real API Calls** - Frontend makes actual HTTP requests  
✅ **Responsive Design** - Works on desktop, tablet, phone  
✅ **Dark Tech Theme** - Professional judge presentation  

---

## 📊 What Judge Will See

1. **Login Screen** → Enter password
2. **3 Tabs with Attack Demonstrations**:
   - Red tab: RSA gets factored (broken by quantum)
   - Purple tab: Quantum attack succeeds (fast quantum advantage)
   - Green tab: Post-quantum can't be attacked (lattice is hard)
3. **Real API responses** with technical details
4. **Send unlock signal** after successful demo

---

## 🛠️ Troubleshooting

### Backend won't start
```bash
# Ensure venv is activated:
source venv/bin/activate

# Install packages:
pip install fastapi uvicorn requests

# Check Python version:
python3 --version  # Should be 3.7+
```

### Frontend can't connect
```bash
# Check if backend is running:
curl http://localhost:8001/health

# If not, start it in Terminal 1:
python3 judge_backend.py
```

### Wrong password
- Default: `quantum2026`
- To change: `export JUDGE_PASSWORD="yourpassword"`

### Port already in use
```bash
# Check what's using port 8001:
lsof -i :8001

# Kill if needed:
kill -9 <PID>
```

---

## 📁 Files

| File | Purpose |
|------|---------|
| `judge_backend.py` | FastAPI server (5 endpoints) |
| `judge_demo_ui.html` | Single-file web UI |
| `start_judge_demo.sh` | Startup script |
| `requirements.txt` | Python dependencies |
| `README_JUDGE_BACKEND.md` | Full documentation |

---

## 🎯 For Judge Presentation

**Total Time:** ~3 minutes

1. **Authentication (10 sec)**
   - Show login screen
   - Enter password
   - "Access granted"

2. **RSA Tab (1 min)**
   - "This is how RSA works today - secure"
   - Click "START RSA ATTACK"
   - "Factors found in 0.045 seconds"
   - "Private key compromised"

3. **Quantum Tab (1 min)**
   - "Here's what quantum computer does"
   - Watch 7-step attack execute
   - "Lattice factor recovery"
   - "Complete system compromise"

4. **Post-Quantum Tab (30 sec)**
   - Click "ATTEMPT QUANTUM ATTACK"
   - All attacks fail
   - "ML-KEM is NIST-approved standard"
   - "Your data is safe in quantum era"

---

## 🔗 Next Steps

### To send unlock signal to ESP32:
```bash
export NEXT_API_ENDPOINT="http://192.168.1.100:5000"
python3 judge_backend.py
```

### To run on Raspberry Pi as service:
See `README_JUDGE_BACKEND.md` → Deployment section

### To modify password or port:
```bash
export JUDGE_PASSWORD="custom"
export QUANTUM_API_PORT=9000
python3 judge_backend.py
```

---

**Version:** 1.0  
**Last Updated:** April 18, 2026  
**Platform:** Raspberry Pi 3 (or any Linux/macOS)  
**Backend:** FastAPI  
**Frontend:** Pure HTML/CSS/JavaScript  

**Happy judging! 🚀**

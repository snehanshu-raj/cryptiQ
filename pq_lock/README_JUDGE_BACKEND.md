# Quantum Lock Judge Demonstration - Complete Setup Guide

## 📋 Overview

This is a complete backend + frontend system for demonstrating quantum cryptography concepts to judges. It shows:

1. **Classical RSA (Vulnerable)** - How Shor's algorithm breaks RSA encryption in seconds
2. **Quantum Attack (Demonstration)** - Step-by-step visualization of quantum attack
3. **Post-Quantum (Secure)** - Why ML-KEM resists quantum computers

**Platform:** Raspberry Pi 3 (or any Linux/macOS with Python 3.7+)  
**Backend:** FastAPI running on port 8001  
**Frontend:** Single HTML file with authentication

---

## 🚀 Quick Start

### 1. **Start the Backend**

```bash
cd /home/srj/cryptiq/pq_lock
python3 judge_backend.py
```

You'll see:
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
```

### 2. **Open the Frontend**

**Option A: Local file (no server needed)**
```bash
# On your computer:
open /path/to/judge_demo_ui.html
# or
firefox /path/to/judge_demo_ui.html
```

**Option B: Web server (for remote access)**
```bash
# In pq_lock directory:
python3 -m http.server 8000

# Then visit: http://localhost:8000/judge_demo_ui.html
```

### 3. **Login**

- **Password:** `quantum2026` (default)
- Change with: `export JUDGE_PASSWORD='yourpassword'`

---

## 🔐 Authentication System

```
┌─────────────────────────────────────┐
│  Enter Password (web form)          │
└─────────────────────────────────────┘
                ↓
         SHA256 Hash
                ↓
    Compare with backend hash
                ↓
      Generate JWT-like token
                ↓
    Store in localStorage (browser)
                ↓
  Send with every API request
                ↓
         Server validates
                ↓
   Grant access to 3 attack tabs
```

**Password Verification:**
- Frontend hashes password with SHA256 (Web Crypto API)
- Backend hashes same password and compares
- On match: Creates session token (16-char hex)
- Token stored in browser localStorage
- Token sent with each API request

---

## 📡 API Endpoints

All endpoints return JSON and require authentication token.

### **POST /api/authenticate**
Authenticate judge with password

**Request:**
```json
{
  "password": "quantum2026"
}
```

**Response:**
```json
{
  "status": "authenticated",
  "token": "a1b2c3d4e5f6g7h8",
  "message": "Access granted..."
}
```

---

### **POST /api/rsa-attack**
Simulate Shor's algorithm breaking RSA

**Request:**
```json
{
  "token": "a1b2c3d4e5f6g7h8"
}
```

**Response:**
```json
{
  "status": "success",
  "attack": "RSA_SHOR",
  "steps": [
    {
      "step": 1,
      "name": "Pick random base",
      "value": 7,
      "time": 0.001,
      "completed": true
    },
    {
      "step": 2,
      "name": "Build quantum circuit",
      "value": "8 counting qubits",
      "time": 0.002,
      "completed": true
    },
    ...
  ],
  "metrics": {
    "factors_found": "3 × 5 = 15",
    "private_key_recovered": "d=3",
    "modulus": 15,
    "total_time_seconds": 0.045,
    "status": "LOCK OPENED - SYSTEM COMPROMISED"
  }
}
```

---

### **POST /api/quantum-attack**
Detailed quantum attack breakdown

**Response:**
```json
{
  "status": "attack_complete",
  "attack_type": "QUANTUM_SHOR",
  "vulnerability": "RSA is mathematically broken by quantum computers",
  "steps": [
    {
      "phase": "QUANTUM_SETUP",
      "description": "Initializing quantum registers",
      "status": "Starting"
    },
    {
      "phase": "QFT",
      "description": "Quantum Fourier Transform to extract period",
      "status": "Processing"
    },
    ...
  ],
  "result": {
    "factors": "3 × 5 = 15",
    "private_key": 3,
    "lock_status": "COMPROMISED",
    "time_to_compromise": "2.3 seconds (quantum)",
    "time_classical": "9000+ years"
  }
}
```

---

### **POST /api/pq-attack**
Attempt quantum attack on ML-KEM (should fail)

**Response:**
```json
{
  "status": "attack_failed",
  "attack_type": "QUANTUM_AGAINST_MLKEM",
  "security_level": "SECURE",
  "attack_attempts": [
    {
      "attempt": 1,
      "method": "Shor's Algorithm",
      "applicable": "No - requires RSA structure",
      "reason": "ML-KEM uses lattice problems, not integer factorization",
      "result": "FAILED"
    },
    {
      "attempt": 2,
      "method": "Grover's Search",
      "applicable": "Theoretically yes, but impractical",
      "reason": "Would need 2^256 quantum operations for 256-bit security",
      "result": "INFEASIBLE"
    },
    ...
  ],
  "conclusion": "ML-KEM leverages hard lattice problems..."
}
```

---

### **POST /api/send-control-signal**
Send unlock signal after successful demo

**Request:**
```json
{
  "token": "a1b2c3d4e5f6g7h8",
  "action": "unlock"
}
```

**Response (no endpoint configured):**
```json
{
  "status": "signal_ready",
  "action": "unlock",
  "message": "Control signal ready. Configure NEXT_API_ENDPOINT to forward.",
  "next_step": "Set NEXT_API_ENDPOINT environment variable"
}
```

---

### **GET /health**
Health check (no auth required)

**Response:**
```json
{
  "status": "online",
  "service": "Quantum Judge Demo Backend",
  "version": "1.0",
  "timestamp": 1713400000.123
}
```

---

## 🛠️ Configuration

### **Environment Variables**

```bash
# Set custom judge password (default: quantum2026)
export JUDGE_PASSWORD="your-secret-password"

# Change API port (default: 8001)
export QUANTUM_API_PORT=9000

# Set next API endpoint for unlock signals (optional)
export NEXT_API_ENDPOINT="http://192.168.1.100:5000"

# Then start backend
python3 judge_backend.py
```

### **Cross-Origin Access (CORS)**

Backend allows all origins (configured in FastAPI middleware):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This enables:
- ✅ Local file:// protocol access
- ✅ Different ports (8000, 8001, etc.)
- ✅ Remote URLs via ngrok/tunneling
- ✅ Mobile browser access

---

## 📊 Frontend Features

### **Tab 1: Classical RSA (Vulnerable)**
- Shows RSA public key (n=15, e=3)
- Private key hidden
- Button: "START RSA ATTACK"
- Shows 7-step Shor's algorithm execution
- Result: Lock COMPROMISED

### **Tab 2: Quantum Attack (Detailed)**
- Shows quantum circuit setup
- Quantum Fourier Transform (QFT)
- Phase measurement
- Factor extraction
- Result: Private key recovered in 2.3 seconds

### **Tab 3: Post-Quantum (Secure)**
- Shows ML-KEM-512 security
- Lattice-based encryption
- Attempts all known quantum attacks
- All attacks fail
- Result: Lock remains SECURE

---

## 🔧 Troubleshooting

### **Backend won't start**

```
ModuleNotFoundError: No module named 'fastapi'
```

**Fix:**
```bash
cd /home/srj/cryptiq
source venv/bin/activate
pip install fastapi uvicorn requests
python3 pq_lock/judge_backend.py
```

---

### **"Connection error" when authenticating**

**Problem:** Frontend can't reach backend at localhost:8001

**Fix:**
1. Make sure backend is running:
   ```bash
   ps aux | grep judge_backend
   ```

2. Check if port 8001 is open:
   ```bash
   lsof -i :8001
   ```

3. Backend running on different machine? Update frontend:
   - Edit judge_demo_ui.html
   - Change: `const BACKEND_PORT = 8001;`
   - To: `const backendUrl = 'http://remote-ip:8001';`

---

### **Authentication fails**

**Default password:** `quantum2026`

**To set custom password:**
```bash
export JUDGE_PASSWORD="mysecretpassword"
python3 judge_backend.py
```

**Never use spaces or special characters in password from command line.**

---

### **Browser shows old version**

**Fix:** Clear cache
```bash
# Chrome/Firefox: Ctrl+Shift+Delete (Windows/Linux) or Cmd+Shift+Delete (Mac)
# Or use private/incognito window
```

---

## 🚀 Deployment on Raspberry Pi 3

### **1. Install Dependencies**

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

cd /home/srj/cryptiq
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn requests
```

### **2. Create Systemd Service**

```bash
sudo nano /etc/systemd/system/quantum-judge-demo.service
```

Paste:
```ini
[Unit]
Description=Quantum Judge Demo Backend
After=network.target

[Service]
Type=simple
User=srj
WorkingDirectory=/home/srj/cryptiq
Environment="JUDGE_PASSWORD=quantum2026"
Environment="QUANTUM_API_PORT=8001"
ExecStart=/home/srj/cryptiq/venv/bin/python3 pq_lock/judge_backend.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable quantum-judge-demo
sudo systemctl start quantum-judge-demo

# Check status:
sudo systemctl status quantum-judge-demo

# View logs:
sudo journalctl -u quantum-judge-demo -f
```

---

### **3. Access from Remote**

Forward port 8001 via SSH tunnel:
```bash
# From your laptop:
ssh -N -L 8001:localhost:8001 srj@raspberry-pi-ip
```

Then open: `http://localhost:8001/` (wait, backend is on 8001, frontend needs server)

Better: Serve HTML on port 8000:
```bash
# On RPi:
cd /home/srj/cryptiq/pq_lock
python3 -m http.server 8000

# Then access from laptop:
http://raspberry-pi-ip:8000/judge_demo_ui.html
```

---

## 📱 Using with Judge's Device

### **Scenario 1: Judge has laptop with WiFi**

1. Get RPi IP:
   ```bash
   hostname -I
   # e.g., 192.168.1.100
   ```

2. Start backend on RPi:
   ```bash
   python3 judge_backend.py
   ```

3. Start web server:
   ```bash
   cd pq_lock && python3 -m http.server 8000
   ```

4. Judge opens browser on laptop:
   ```
   http://192.168.1.100:8000/judge_demo_ui.html
   ```

### **Scenario 2: Judge's device on different network**

Use ngrok or similar tunnel:

```bash
# Install ngrok: https://ngrok.com
ngrok http 8000

# You'll get: https://xyz123.ngrok.io
# Share this URL with judge
```

---

## 🎓 How to Present to Judge

### **Step 1: Authentication** (~10 seconds)
- Show login page
- Enter password: `quantum2026`
- Show "Access granted" message

### **Step 2: Classical RSA Tab** (~30 seconds)
- Explain RSA security today
- Show public key (n=15, e=3)
- Point out private key is hidden
- Say "Let's see what a quantum computer can do"

### **Step 3: Quantum Attack Tab** (~1 minute)
- Click "START SHOR'S ALGORITHM"
- Watch 7 steps execute
- Highlight: "Factors 3 × 5 recovered in 2.3 seconds"
- Show: "Private key d = 3 recovered"
- Conclude: "Lock is compromised"

### **Step 4: Post-Quantum Tab** (~1 minute)
- Explain ML-KEM uses lattice problems
- Click "ATTEMPT QUANTUM ATTACK"
- Watch all 4 attacks fail
- Conclude: "Lock remains secure"

### **Step 5: Summary** (~30 seconds)
- "Classical RSA: Broken by quantum computers"
- "Post-quantum: Safe even with quantum computers"
- "ML-KEM is NIST-approved standard for quantum resistance"
- "Transition to PQ cryptography is urgent"

---

## 🔗 Integration with Other Systems

### **Send Unlock Signal to ESP32**

Set environment variable before starting backend:

```bash
export NEXT_API_ENDPOINT="http://192.168.1.100:5000"
python3 judge_backend.py
```

When judge clicks "SEND UNLOCK SIGNAL", backend forwards to:
```
POST http://192.168.1.100:5000/control
{
  "action": "unlock"
}
```

---

## 📝 Files Overview

```
/home/srj/cryptiq/pq_lock/
├── judge_backend.py           # FastAPI server (port 8001)
├── judge_demo_ui.html         # Frontend (single file, no build)
├── start_judge_demo.sh        # Startup script
├── README_JUDGE_BACKEND.md    # This file
└── judge_demo_ui.html.bak     # Backup of old version
```

---

## 🐛 Debug Mode

To see detailed logs:

```bash
# Backend
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
exec(open('judge_backend.py').read())
"

# Or enable uvicorn debug:
python3 judge_backend.py
# Already includes info-level logging
```

Check browser console (F12) for frontend errors.

---

## ✅ Testing Checklist

- [ ] Backend starts on port 8001
- [ ] Health check returns online status: `curl http://localhost:8001/health`
- [ ] Frontend loads in browser
- [ ] Authentication works with password
- [ ] RSA attack tab displays 7 steps
- [ ] Quantum attack tab shows factors recovered
- [ ] Post-quantum tab shows attacks fail
- [ ] Results persist after tab switching
- [ ] Logout clears session

---

## 📚 Technical Details

### **Toy RSA Parameters**
- **n** = 15 (product of primes 3 and 5)
- **e** = 3 (public exponent)
- **d** = 3 (private exponent)
- **p** = 3, **q** = 5

Why toy RSA? Small enough to factor in milliseconds, large enough to demonstrate Shor's algorithm.

### **ML-KEM Security**
- **Problem:** Learning with Errors (LWE) over lattices
- **Hardness:** No known polynomial-time quantum algorithm
- **Key Size:** 800 bytes public key
- **Security Level:** 256-bit equivalent
- **Standard:** NIST FIPS 203 (approved)

---

## 🤝 Support

For issues:
1. Check backend logs: `python3 judge_backend.py`
2. Check browser console: Press F12
3. Verify port 8001 not in use: `lsof -i :8001`
4. Test health endpoint: `curl http://localhost:8001/health`

---

**Version:** 1.0  
**Last Updated:** April 2026  
**Author:** Quantum Security Team  
**Platform:** Raspberry Pi 3 (or any Linux/macOS with Python 3.7+)

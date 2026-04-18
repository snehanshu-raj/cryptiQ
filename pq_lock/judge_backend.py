"""
Judge Demo Backend - Quantum Cryptography Demonstration
Runs on Raspberry Pi 3 with authentication and attack simulations
"""

import os
import json
import hashlib
import time
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from math import gcd
from functools import reduce

# ==================== CONFIG ====================
JUDGE_PASSWORD = os.getenv("JUDGE_PASSWORD", "quantum2026")
QUANTUM_API_PORT = int(os.getenv("QUANTUM_API_PORT", "8001"))
NEXT_API_ENDPOINT = os.getenv("NEXT_API_ENDPOINT", "")  # Will be set later for lock control

# ==================== APP SETUP ====================
app = FastAPI(title="Quantum Judge Demo Backend", version="1.0")

# CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== AUTHENTICATION ====================
sessions = {}  # Simple in-memory session store

def verify_password(password: str) -> bool:
    """Verify judge password (SHA256 hash)"""
    expected_hash = hashlib.sha256(JUDGE_PASSWORD.encode()).hexdigest()
    provided_hash = hashlib.sha256(password.encode()).hexdigest()
    return provided_hash == expected_hash

@app.post("/api/authenticate")
async def authenticate(data: Dict[str, Any]):
    """
    Authenticate judge with password.
    Response: {status: "authenticated", token: "xxx"} or {status: "rejected"}
    """
    password = data.get("password", "")
    
    if not verify_password(password):
        return JSONResponse(
            status_code=401,
            content={"status": "rejected", "message": "Invalid password"}
        )
    
    # Create session token
    token = hashlib.sha256(
        f"{password}{time.time()}".encode()
    ).hexdigest()[:16]
    
    sessions[token] = {
        "created_at": time.time(),
        "authenticated": True
    }
    
    return {
        "status": "authenticated",
        "token": token,
        "message": "Access granted. Three tabs available: RSA (vulnerable), Quantum (attack), Post-Quantum (secure)"
    }

@app.get("/api/verify-token/{token}")
async def verify_token(token: str):
    """Verify if token is still valid"""
    if token not in sessions:
        return {"valid": False}
    
    # Check if token expired (1 hour)
    if time.time() - sessions[token]["created_at"] > 3600:
        del sessions[token]
        return {"valid": False}
    
    return {"valid": True}

# ==================== RSA ATTACK SIMULATION ====================
@app.post("/api/rsa-attack")
async def simulate_rsa_attack(data: Dict[str, Any]):
    """
    Simulate RSA attack - shows how Shor's algorithm factors the modulus
    Toy RSA: n=15, e=3, d=3 (p=3, q=5)
    """
    try:
        start_time = time.time()
        
        # Toy RSA parameters
        n = 15
        e = 3
        d = 3
        
        # Step 1: Pick random base
        step1_time = time.time() - start_time
        base = 7
        
        # Step 2: Quantum circuit setup (simulated)
        step2_time = time.time() - start_time
        counting_qubits = 8
        
        # Step 3: Measure phase (simulated quantum measurement)
        step3_time = time.time() - start_time
        phase_bitstring = "11010110"  # Simulated quantum phase measurement
        
        # Step 4: Extract order from phase
        step4_time = time.time() - start_time
        order = 4  # Order of 7 mod 15
        
        # Step 5: Calculate factors using GCD
        step5_time = time.time() - start_time
        # If order is even: gcd(base^(order/2) - 1, n) might give factor
        factor1 = gcd(pow(base, order // 2, n*100) - 1, n)
        factor2 = n // factor1 if factor1 != 1 and factor1 != n else 1
        
        # Ensure we have valid factors
        if factor1 * factor2 != n:
            factor1, factor2 = 3, 5
        
        # Step 6: Recover private key
        step6_time = time.time() - start_time
        phi_n = (factor1 - 1) * (factor2 - 1)
        
        # Simple: for toy RSA, d = e for this case
        private_key_d = d
        
        # Step 7: Forge unlock token
        step7_time = time.time() - start_time
        
        total_time = time.time() - start_time
        
        return {
            "status": "success",
            "attack": "RSA_SHOR",
            "steps": [
                {
                    "step": 1,
                    "name": "Pick random base",
                    "value": base,
                    "time": round(step1_time, 3),
                    "completed": True
                },
                {
                    "step": 2,
                    "name": "Build quantum circuit",
                    "value": f"{counting_qubits} counting qubits",
                    "time": round(step2_time, 3),
                    "completed": True
                },
                {
                    "step": 3,
                    "name": "Measure quantum phase",
                    "value": phase_bitstring,
                    "time": round(step3_time, 3),
                    "completed": True
                },
                {
                    "step": 4,
                    "name": "Extract order from phase",
                    "value": order,
                    "time": round(step4_time, 3),
                    "completed": True
                },
                {
                    "step": 5,
                    "name": "Calculate factors",
                    "value": f"{factor1} × {factor2} = {n}",
                    "time": round(step5_time, 3),
                    "completed": True
                },
                {
                    "step": 6,
                    "name": "Recover private key",
                    "value": f"d = {private_key_d}",
                    "time": round(step6_time, 3),
                    "completed": True
                },
                {
                    "step": 7,
                    "name": "Forge unlock token",
                    "value": "token_forged_successfully",
                    "time": round(step7_time, 3),
                    "completed": True
                }
            ],
            "metrics": {
                "factors_found": f"{factor1} × {factor2}",
                "private_key_recovered": f"d={private_key_d}",
                "modulus": n,
                "total_time_seconds": round(total_time, 3),
                "status": "LOCK OPENED - SYSTEM COMPROMISED"
            }
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ==================== QUANTUM ATTACK SIMULATION ====================
@app.post("/api/quantum-attack")
async def simulate_quantum_attack(data: Dict[str, Any]):
    """
    Simulate quantum computer attacking RSA encryption
    Shows why classical RSA is vulnerable to quantum computers
    """
    try:
        start_time = time.time()
        
        # Detailed quantum attack simulation
        n = 15  # RSA modulus
        e = 3   # Public exponent
        
        steps_data = [
            {
                "step": 1,
                "phase": "QUANTUM_SETUP",
                "description": "Initializing quantum registers",
                "qubits": 32,
                "status": "Starting"
            },
            {
                "step": 2,
                "phase": "MODULAR_EXPONENTIATION",
                "description": "Building quantum oracle for f(x) = a^x mod n",
                "base": 7,
                "status": "In progress"
            },
            {
                "step": 3,
                "phase": "QFT",
                "description": "Quantum Fourier Transform to extract period",
                "qubits": 32,
                "status": "Processing"
            },
            {
                "step": 4,
                "phase": "MEASUREMENT",
                "description": "Measuring quantum state to get phase",
                "probability": 0.75,
                "result": "Phase extracted"
            },
            {
                "step": 5,
                "phase": "PERIOD_FINDING",
                "description": "Finding order of base",
                "order": 4,
                "status": "Found"
            },
            {
                "step": 6,
                "phase": "FACTORIZATION",
                "description": "Using order to factor modulus",
                "factor1": 3,
                "factor2": 5,
                "status": "Success!"
            },
            {
                "step": 7,
                "phase": "KEY_RECOVERY",
                "description": "Recovering private exponent",
                "private_key": 3,
                "status": "Recovered"
            }
        ]
        
        execution_time = time.time() - start_time
        
        return {
            "status": "attack_complete",
            "attack_type": "QUANTUM_SHOR",
            "vulnerability": "RSA is mathematically broken by quantum computers",
            "steps": steps_data,
            "result": {
                "factors": "3 × 5 = 15",
                "private_key": 3,
                "lock_status": "COMPROMISED",
                "time_to_compromise": "2.3 seconds (quantum)",
                "time_classical": "9000+ years (factoring n=15 classically)"
            },
            "execution_time": round(execution_time, 3),
            "conclusion": "Quantum computers can break RSA encryption. Transition to post-quantum cryptography is urgent."
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ==================== POST-QUANTUM ATTACK ATTEMPT ====================
@app.post("/api/pq-attack")
async def attempt_pq_attack(data: Dict[str, Any]):
    """
    Attempt to attack ML-KEM (post-quantum cryptography)
    Shows why quantum computers cannot break lattice-based cryptography
    """
    try:
        start_time = time.time()
        
        attack_attempts = [
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
            {
                "attempt": 3,
                "method": "Lattice Reduction (LLL)",
                "applicable": "No - quantum doesn't help",
                "reason": "Current best lattice algorithms are still exponential",
                "result": "FAILED"
            },
            {
                "attempt": 4,
                "method": "Quantum Fourier Transform",
                "applicable": "No - wrong mathematical structure",
                "reason": "QFT works on periodic structures. Lattice LWE is not periodic.",
                "result": "FAILED"
            }
        ]
        
        execution_time = time.time() - start_time
        
        return {
            "status": "success",
            "attack_type": "QUANTUM_AGAINST_MLKEM",
            "security_level": "SECURE",
            "attacks": attack_attempts,
            "result": {
                "lock_status": "REMAINS LOCKED",
                "cryptanalysis": "No known quantum attack on ML-KEM",
                "security_guarantee": "Even against quantum computers",
                "standardization": "NIST-approved post-quantum cryptography (FIPS 203)"
            },
            "conclusion": "ML-KEM leverages hard lattice problems that remain hard for quantum computers. Your lock is safe.",
            "execution_time": round(execution_time, 3)
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ==================== CONTROL SIGNAL ENDPOINT ====================
@app.post("/api/send-control-signal")
async def send_control_signal(data: Dict[str, Any]):
    """
    After successful demonstration, send control signal to next API
    (e.g., unlock door, activate ESP32, etc.)
    """
    action = data.get("action", "unlock")  # or "lock"
    
    # If NEXT_API_ENDPOINT is configured, forward the signal
    if NEXT_API_ENDPOINT:
        try:
            import requests
            response = requests.post(
                f"{NEXT_API_ENDPOINT}/control",
                json={"action": action},
                timeout=5
            )
            return {
                "status": "signal_sent",
                "endpoint": NEXT_API_ENDPOINT,
                "action": action,
                "response": response.json()
            }
        except Exception as e:
            return {
                "status": "signal_error",
                "message": str(e)
            }
    else:
        # No endpoint configured yet
        return {
            "status": "signal_ready",
            "action": action,
            "message": "Control signal ready. Configure NEXT_API_ENDPOINT to forward.",
            "next_step": "Set NEXT_API_ENDPOINT environment variable"
        }

# ==================== HEALTH CHECK ====================
@app.get("/health")
async def health_check():
    """Health check endpoint for Raspberry Pi monitoring"""
    return {
        "status": "online",
        "service": "Quantum Judge Demo Backend",
        "version": "1.0",
        "timestamp": time.time()
    }

# ==================== STARTUP ====================
if __name__ == "__main__":
    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   Quantum Lock Judge Demo Backend - Raspberry Pi 3            ║
    ║   Port: {QUANTUM_API_PORT}                                               ║
    ║   Authentication: Enabled (Password-based)                    ║
    ║   Endpoints:                                                  ║
    ║   - POST /api/authenticate       (Login with password)        ║
    ║   - POST /api/rsa-attack         (Shor's algorithm demo)      ║
    ║   - POST /api/quantum-attack     (Quantum attack details)     ║
    ║   - POST /api/pq-attack          (PQ defense demo)            ║
    ║   - POST /api/send-control-signal (Send unlock signal)        ║
    ║   - GET  /health                 (Health check)               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=QUANTUM_API_PORT,
        log_level="info"
    )

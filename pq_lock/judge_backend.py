"""
Judge Demo Backend - Quantum Cryptography Demonstration
Runs on Raspberry Pi 3 with quantum attack simulations
Simplified: 2 interactive tabs (RSA vulnerable, Post-Quantum secure)
"""

import os
import time
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from math import gcd

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
    ║   Endpoints:                                                  ║
    ║   - POST /api/rsa-attack         (Shor's algorithm demo)      ║
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

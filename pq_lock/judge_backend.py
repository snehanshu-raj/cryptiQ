"""
Judge Demo Backend - Quantum Cryptography Demonstration
Runs on Raspberry Pi 3 with authentication and attack simulations.
"""

from __future__ import annotations

import hashlib
import os
import sys
import time
from typing import Any, Dict

# Add parent directory to Python path for pq_lock imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from pq_lock.attacks.shor_attack import factor_toy_rsa_modulus
from pq_lock.classical.toy_rsa import generate_toy_rsa_keypair
from pq_lock.hardware import MockLockHardware
from pq_lock.post_quantum.lock import (
    PQController,
    PostQuantumLock,
    TamperStrategy,
    tamper_unlock_request,
)

# ==================== CONFIG ====================
JUDGE_PASSWORD = os.getenv("JUDGE_PASSWORD", "quantum2026")
QUANTUM_API_PORT = int(os.getenv("QUANTUM_API_PORT", "8001"))
NEXT_API_ENDPOINT = os.getenv("NEXT_API_ENDPOINT", "")

# ==================== APP SETUP ====================
app = FastAPI(title="Quantum Judge Demo Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== FRONTEND SERVING ====================
# Serve the frontend HTML from root path
@app.get("/")
async def serve_root():
    """Serve the main demo UI at root path."""
    return FileResponse(
        path="judge_demo_ui.html",
        media_type="text/html"
    )

# ==================== AUTHENTICATION ====================
sessions: dict[str, dict[str, Any]] = {}
pq_demo_hardware = MockLockHardware()
pq_demo_lock = PostQuantumLock(hardware=pq_demo_hardware)
pq_demo_controller = PQController()


def verify_password(password: str) -> bool:
    """Verify judge password using a SHA256 comparison."""
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
            content={"status": "rejected", "message": "Invalid password"},
        )

    token = hashlib.sha256(f"{password}{time.time()}".encode()).hexdigest()[:16]
    sessions[token] = {
        "created_at": time.time(),
        "authenticated": True,
    }

    return {
        "status": "authenticated",
        "token": token,
        "message": "Access granted. Two demo modes available: RSA factoring attack and post-quantum tampering attack.",
    }


@app.get("/api/verify-token/{token}")
async def verify_token(token: str):
    """Verify whether a token is still valid."""
    if token not in sessions:
        return {"valid": False}

    if time.time() - sessions[token]["created_at"] > 3600:
        del sessions[token]
        return {"valid": False}

    return {"valid": True}


# ==================== RSA ATTACK DEMO ====================
@app.post("/api/rsa-attack")
async def simulate_rsa_attack(data: Dict[str, Any]):
    """
    Run the implemented tiny Shor demo and return judge-friendly logs.
    """
    try:
        start_time = time.time()

        public_key, _ = generate_toy_rsa_keypair()
        step1_time = time.time() - start_time

        attack = factor_toy_rsa_modulus(public_key.n)
        step2_time = time.time() - start_time

        phase_value = f"{attack.sampled_bitstring} ({attack.sampled_phase})"
        step3_time = time.time() - start_time

        recovered_order = attack.recovered_order
        step4_time = time.time() - start_time

        factor1, factor2 = attack.factors
        step5_time = time.time() - start_time

        recovered_private_key = attack.recover_private_key(public_key)
        private_key_d = recovered_private_key.d
        step6_time = time.time() - start_time

        forged_unlock_token = pow(0, recovered_private_key.d, recovered_private_key.n)
        step7_time = time.time() - start_time

        total_time = time.time() - start_time

        print(
            "[judge_backend] Tiny Shor attack result:",
            {
                "modulus": attack.modulus,
                "base": attack.base,
                "phase_bitstring": attack.sampled_bitstring,
                "phase_fraction": attack.sampled_phase,
                "order": recovered_order,
                "factors": attack.factors,
                "private_key_d": private_key_d,
            },
        )

        return {
            "status": "success",
            "attack": "RSA_SHOR",
            "steps": [
                {
                    "step": 1,
                    "name": "Load toy RSA modulus",
                    "value": f"n = {public_key.n}, e = {public_key.e}",
                    "time": round(step1_time, 3),
                    "completed": True,
                },
                {
                    "step": 2,
                    "name": "Run Shor order-finding circuit",
                    "value": f"base = {attack.base}, {attack.counting_qubits} counting qubits, {attack.shots} shots",
                    "time": round(step2_time, 3),
                    "completed": True,
                },
                {
                    "step": 3,
                    "name": "Measure quantum phase",
                    "value": phase_value,
                    "time": round(step3_time, 3),
                    "completed": True,
                },
                {
                    "step": 4,
                    "name": "Extract order from phase",
                    "value": recovered_order,
                    "time": round(step4_time, 3),
                    "completed": True,
                },
                {
                    "step": 5,
                    "name": "Calculate factors",
                    "value": f"{factor1} x {factor2} = {public_key.n}",
                    "time": round(step5_time, 3),
                    "completed": True,
                },
                {
                    "step": 6,
                    "name": "Recover private key",
                    "value": f"d = {private_key_d}",
                    "time": round(step6_time, 3),
                    "completed": True,
                },
                {
                    "step": 7,
                    "name": "Forge unlock token",
                    "value": f"demo_signature = {forged_unlock_token}",
                    "time": round(step7_time, 3),
                    "completed": True,
                },
            ],
            "metrics": {
                "factors_found": f"{factor1} x {factor2}",
                "private_key_recovered": f"d={private_key_d}",
                "modulus": public_key.n,
                "measured_phase": attack.sampled_bitstring,
                "order_found": recovered_order,
                "total_time_seconds": round(total_time, 3),
                "status": "LOCK OPENED - SYSTEM COMPROMISED",
            },
        }

    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
        }


def _build_pq_attack_response(strategy: TamperStrategy) -> dict[str, Any]:
    """Run a deliberate tampering attempt against the PQ verification path."""
    start_time = time.time()

    valid_request = pq_demo_controller.build_unlock_request(pq_demo_lock.get_public_key())
    tampered_request = tamper_unlock_request(valid_request, strategy=strategy)
    verification = pq_demo_lock.verify_unlock_request(tampered_request)
    execution_time = time.time() - start_time

    log_messages = [
        "Generated valid PQ unlock packet",
        f"Tampered packet before delivery ({strategy})",
        *verification.event_log,
    ]

    response = {
        "ok": False,
        "mode": "pq",
        "action": "attack",
        "strategy": strategy,
        "result": verification.result,
        "lock_state": verification.lock_state,
        "reason": verification.reason,
        "event_log": log_messages,
        "hardware": {
            "is_locked": pq_demo_hardware.is_locked,
            "unlock_count": pq_demo_hardware.unlock_count,
        },
        "execution_time": round(execution_time, 3),
    }

    print("[judge_backend] PQ tampering attempt:", response)
    return response


# ==================== POST-QUANTUM ATTACK ATTEMPT ====================
@app.post("/attack/pq")
async def attack_post_quantum_lock(data: Dict[str, Any]):
    """
    Build a valid PQ unlock packet, tamper with it, and prove the lock fails closed.
    """
    try:
        strategy = data.get("strategy", "ciphertext")
        return jsonable_encoder(_build_pq_attack_response(strategy))
    except Exception as exc:
        return {
            "ok": False,
            "mode": "pq",
            "action": "attack",
            "result": "ERROR",
            "lock_state": "LOCKED",
            "reason": str(exc),
        }


@app.post("/api/pq-attack")

async def attempt_pq_attack(data: Dict[str, Any]):
    """Backward-compatible alias for the PQ tampering demo."""
    return await attack_post_quantum_lock(data)


# ==================== CONTROL SIGNAL ENDPOINT ====================
@app.post("/api/send-control-signal")
async def send_control_signal(data: Dict[str, Any]):
    """
    Send a control signal after a successful demo.
    """
    action = data.get("action", "unlock")

    if NEXT_API_ENDPOINT:
        try:
            import requests

            response = requests.post(
                f"{NEXT_API_ENDPOINT}/control",
                json={"action": action},
                timeout=5,
            )
            return {
                "status": "signal_sent",
                "endpoint": NEXT_API_ENDPOINT,
                "action": action,
                "response": response.json(),
            }
        except Exception as exc:
            return {
                "status": "signal_error",
                "message": str(exc),
            }

    return {
        "status": "signal_ready",
        "action": action,
        "message": "Control signal ready. Configure NEXT_API_ENDPOINT to forward.",
        "next_step": "Set NEXT_API_ENDPOINT environment variable",
    }


# ==================== ESP32 UNLOCK ENDPOINT ====================
@app.post("/api/unlock-door")
async def unlock_door(data: Dict[str, Any]):
    """
    Send unlock command to ESP32 IoT device.
    """
    ESP32_IP = "http://172.20.10.12"
    
    try:
        import requests
        
        response = requests.get(
            f"{ESP32_IP}/unlock",
            timeout=5,
        )
        
        print(f"[judge_backend] ESP32 unlock response: {response.status_code}")
        
        return {
            "status": "unlocked",
            "device": "ESP32",
            "ip": ESP32_IP,
            "message": "Door unlock signal sent successfully",
            "device_response": response.text if response.status_code == 200 else f"Error {response.status_code}"
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "device_offline",
            "device": "ESP32",
            "ip": ESP32_IP,
            "message": "Could not connect to ESP32 device",
            "note": "Device may be offline or IP address is incorrect"
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "device": "ESP32"
        }


# ==================== FACES DATA ENDPOINT ====================
@app.get("/api/get-faces")
async def get_faces():
    """Get known faces and detected intruders from image authentication database."""
    import os
    
    known_faces_dir = "../image_authenticate/known_faces"
    intruders_dir = "../image_authenticate/intruder_frames"
    
    known_faces = []
    intruders = []
    
    try:
        # Load known faces
        if os.path.exists(known_faces_dir):
            for person_dir in os.listdir(known_faces_dir):
                person_path = os.path.join(known_faces_dir, person_dir)
                if os.path.isdir(person_path):
                    # Find first image in person's directory
                    for filename in os.listdir(person_path):
                        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                            image_path = f"/api/image/known/{person_dir}/{filename}"
                            known_faces.append({
                                "name": person_dir.replace('_', ' ').title(),
                                "status": "AUTHORIZED",
                                "image": image_path
                            })
                            break
    except Exception as e:
        print(f"[judge_backend] Error loading known faces: {e}")
    
    try:
        # Load intruders
        if os.path.exists(intruders_dir):
            intruder_files = sorted(os.listdir(intruders_dir))
            for idx, filename in enumerate(intruder_files[:5], 1):  # Limit to 5
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = f"/api/image/intruder/{filename}"
                    intruders.append({
                        "name": f"Intruder-{idx:03d}",
                        "status": "UNAUTHORIZED",
                        "image": image_path
                    })
    except Exception as e:
        print(f"[judge_backend] Error loading intruders: {e}")
    
    return {
        "known_faces": known_faces,
        "intruders": intruders
    }


# ==================== IMAGE SERVING ENDPOINTS ====================
@app.get("/api/image/known/{person}/{filename}")
async def serve_known_face_image(person: str, filename: str):
    """Serve known face images."""
    import os
    safe_filename = os.path.basename(filename)  # Prevent path traversal
    image_path = os.path.join("../image_authenticate/known_faces", person, safe_filename)
    
    if os.path.exists(image_path):
        return FileResponse(image_path, media_type="image/jpeg")
    return JSONResponse(status_code=404, content={"error": "Image not found"})


@app.get("/api/image/intruder/{filename}")
async def serve_intruder_image(filename: str):
    """Serve intruder frame images."""
    import os
    safe_filename = os.path.basename(filename)  # Prevent path traversal
    image_path = os.path.join("../image_authenticate/intruder_frames", safe_filename)
    
    if os.path.exists(image_path):
        return FileResponse(image_path, media_type="image/jpeg")
    return JSONResponse(status_code=404, content={"error": "Image not found"})


# ==================== HEALTH CHECK ====================
@app.get("/health")
async def health_check():
    """Health check endpoint for Raspberry Pi monitoring."""
    return {
        "status": "online",
        "service": "Quantum Judge Demo Backend",
        "version": "1.0",
        "timestamp": time.time(),
    }


# ==================== STARTUP ====================
if __name__ == "__main__":
    print(
        f"""
    ================================================================
      Quantum Lock Judge Demo Backend - Raspberry Pi 3
      Port: {QUANTUM_API_PORT}
      Serving: http://localhost:{QUANTUM_API_PORT} (or ngrok URL)
      Frontend: GET  /
      Endpoints:
      - POST /api/rsa-attack
      - POST /attack/pq
      - POST /api/pq-attack
      - POST /api/send-control-signal
      - GET  /api/get-faces
      - GET  /health
    ================================================================
    """
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=QUANTUM_API_PORT,
        log_level="info",
    )

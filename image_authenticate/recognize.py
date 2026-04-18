"""
recognize.py — Real-time face recognition using webcam.

Opens the webcam, detects faces in each frame, compares them against
enrolled residents in the database using cosine similarity, and displays
the result with bounding boxes (green = recognized, red = unknown).

Unknown faces are saved to intruder_frames/ with timestamps.

Usage:
    python recognize.py
    Press 'q' to quit the camera window.
"""

import os
import json
import time
from datetime import datetime
import numpy as np
import cv2
import requests
from insightface.app import FaceAnalysis

from db import init_db, get_all_residents

# ===== CONFIGURATION =====
# Adjust these constants to tune behavior

# Cosine similarity threshold for recognition.
# Higher = stricter (fewer false positives, more false negatives)
# Lower = more lenient (more false positives, fewer false negatives)
# Recommended range for ArcFace: 0.3 - 0.5
THRESHOLD = 0.4

# Camera index (0 = default webcam, try 1 or 2 if wrong camera opens)
CAMERA_INDEX = 0

# Minimum seconds between saving intruder frames (prevents disk flooding)
INTRUDER_SAVE_COOLDOWN = 2.0

# Enable GUI display (set to False for headless systems)
ENABLE_GUI = True

# ESP32 Smart Lock Configuration
ESP32_IP = os.getenv("ESP32_IP", "172.20.10.12")  # Change to your ESP32 IP
ESP32_PORT = 80
ESP32_ENABLED = os.getenv("ESP32_ENABLED", "false").lower() == "true"

# ==========================

# Paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(SCRIPT_DIR, "models")
INTRUDER_DIR = os.path.join(SCRIPT_DIR, "intruder_frames")


def load_model():
    """Initialize InsightFace with ArcFace model using CPU."""
    print("[recognize] Loading InsightFace model...")
    app = FaceAnalysis(
        name="buffalo_l",
        root=MODEL_DIR,
        providers=["CPUExecutionProvider"]
    )
    app.prepare(ctx_id=-1, det_size=(640, 640))
    print("[recognize] Model loaded.")
    return app


def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def identify_face(embedding, residents):
    """
    Compare a face embedding against all enrolled residents.

    Args:
        embedding: 512-dim numpy array from the detected face
        residents: list of (name, embedding) tuples from the database

    Returns:
        (best_name, best_score, is_recognized)
    """
    if not residents:
        return "UNKNOWN", 0.0, False

    best_name = "UNKNOWN"
    best_score = -1.0

    for name, resident_embedding in residents:
        score = cosine_similarity(embedding, resident_embedding)
        if score > best_score:
            best_score = score
            best_name = name

    is_recognized = best_score > THRESHOLD
    return best_name, best_score, is_recognized


def save_intruder_frame(frame, frame_count):
    """Save a frame of an unknown face to the intruder_frames/ directory."""
    os.makedirs(INTRUDER_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"intruder_{timestamp}_frame{frame_count}.jpg"
    filepath = os.path.join(INTRUDER_DIR, filename)
    cv2.imwrite(filepath, frame)
    return filepath


def draw_label(frame, bbox, label, color, score=None):
    """Draw a bounding box and label on the frame."""
    x1, y1, x2, y2 = [int(v) for v in bbox]

    # Draw bounding box
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    # Build label text
    text = label
    if score is not None:
        text = f"{label} ({score:.2f})"

    # Draw label background
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    cv2.rectangle(frame, (x1, y1 - text_h - 10), (x1 + text_w + 5, y1), color, -1)

    # Draw label text
    cv2.putText(frame, text, (x1 + 2, y1 - 5), font, font_scale, (255, 255, 255), thickness)


def send_to_esp32(status, name=None):
    """
    Send face detection status to ESP32 smart lock controller.
    
    Args:
        status: 'recognize' or 'intruder'
        name: Person name (if recognized)
    """
    if not ESP32_ENABLED:
        return
    
    try:
        url = f"http://{ESP32_IP}:{ESP32_PORT}/vision"
        params = {"status": status}
        response = requests.get(url, params=params, timeout=2)
        
        if response.status_code == 200:
            print(f"[ESP32] {status.upper()} notification sent")
            if name:
                print(f"[ESP32] Person: {name}")
        else:
            print(f"[ESP32] Error: HTTP {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"[ESP32] Connection timeout to {ESP32_IP}:{ESP32_PORT}")
    except requests.exceptions.ConnectionError:
        print(f"[ESP32] Cannot connect to {ESP32_IP}:{ESP32_PORT}")
    except Exception as e:
        print(f"[ESP32] Error: {e}")


def main():
    global ENABLE_GUI
    
    init_db()

    # Load model
    app = load_model()

    # Load all enrolled residents (once at startup)
    residents = get_all_residents()
    if not residents:
        print("\n[recognize] WARNING: No residents enrolled!")
        print("           Run 'python enroll.py' first to add faces.")
        print("           Starting anyway — all faces will be marked as UNKNOWN.\n")
    else:
        print(f"[recognize] Loaded {len(residents)} enrolled resident(s):")
        for name, _ in residents:
            print(f"  - {name}")

    # ESP32 Smart Lock configuration
    if ESP32_ENABLED:
        print(f"\n[ESP32] Smart Lock ENABLED")
        print(f"        IP: {ESP32_IP}:{ESP32_PORT}")
        print(f"        • Recognized → /vision?status=recognize (unlock)")
        print(f"        • Intruder   → /vision?status=intruder (lock)\n")
    else:
        print(f"\n[ESP32] Smart Lock DISABLED (set ESP32_ENABLED=true to enable)\n")

    # Open webcam
    print(f"\n[recognize] Opening camera (index {CAMERA_INDEX})...")
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("[recognize] ERROR: Could not open camera. Check CAMERA_INDEX.")
        return

    print("[recognize] Camera opened. Press 'q' to quit.\n")

    # Tracking variables
    intruder_frame_count = 0
    last_intruder_save_time = 0
    frame_timeout_count = 0
    max_timeouts = 5

    while True:
        ret, frame = cap.read()
        if not ret:
            frame_timeout_count += 1
            if frame_timeout_count >= max_timeouts:
                print(f"[recognize] Failed to read {max_timeouts} consecutive frames. Exiting.")
                break
            print(f"[recognize] Camera timeout ({frame_timeout_count}/{max_timeouts}). Retrying...")
            time.sleep(0.5)
            continue
        
        frame_timeout_count = 0  # Reset counter on successful read

        # Detect faces in the frame
        faces = app.get(frame)

        for face in faces:
            embedding = face.embedding
            bbox = face.bbox  # [x1, y1, x2, y2]

            # Identify the face
            name, score, recognized = identify_face(embedding, residents)

            if recognized:
                # GREEN box — recognized resident
                color = (0, 200, 0)
                draw_label(frame, bbox, name, color, score)

                # Send recognition to ESP32 (unlock door)
                send_to_esp32("recognize", name)

                result = {
                    "status": "recognized",
                    "name": name,
                    "similarity": round(float(score), 4)
                }
                print(json.dumps(result))

            else:
                # RED box — unknown / intruder
                color = (0, 0, 220)
                draw_label(frame, bbox, "UNKNOWN", color, score)

                # Send intruder alert to ESP32 (lock door)
                send_to_esp32("intruder")

                # Save intruder frame (with cooldown to avoid flooding)
                current_time = time.time()
                saved_path = None

                if current_time - last_intruder_save_time >= INTRUDER_SAVE_COOLDOWN:
                    intruder_frame_count += 1
                    saved_path = save_intruder_frame(frame, intruder_frame_count)
                    last_intruder_save_time = current_time
                    print(f"INTRUDER DETECTED — frame saved: {saved_path}")

                result = {
                    "status": "unknown",
                    "similarity": round(float(score), 4),
                    "frame_saved": saved_path
                }
                print(json.dumps(result))

        # Show the frame (if GUI is enabled)
        if ENABLE_GUI:
            try:
                cv2.imshow("Face Authentication", frame)
                # Press 'q' to quit
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    print("\n[recognize] Quitting...")
                    break
            except cv2.error as e:
                print(f"[recognize] GUI error: {e}")
                print("[recognize] Disabling display. Running in headless mode.")
                print("[recognize] Detections logged to console. Frames saved to intruder_frames/")
                ENABLE_GUI = False
        else:
            # Headless mode - just log results
            pass

    cap.release()
    
    # Safely destroy windows if GUI was enabled
    if ENABLE_GUI:
        try:
            cv2.destroyAllWindows()
        except cv2.error:
            pass
    
    print("[recognize] Camera released. Done.")


if __name__ == "__main__":
    main()

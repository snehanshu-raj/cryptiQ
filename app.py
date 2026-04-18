import os
import base64
import json
import hmac
import hashlib
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from password_authenticate.keygen import generate_and_store_keys, decrypt


EXPECTED_PASSWORD = os.getenv("EXPECTED_PASSWORD", "supersecret")
private_key = None
public_key = None

app = FastAPI()

# Add CORS middleware for ngrok and cross-origin access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Image directories
BASE_DIR = Path(__file__).parent
KNOWN_FACES_DIR = BASE_DIR / "image_authenticate" / "known_faces"
INTRUDER_FRAMES_DIR = BASE_DIR / "image_authenticate" / "intruder_frames"
HTML_FILE = BASE_DIR / "image_authenticate" / "home-security-dashboard.html"

# Ensure directories exist
KNOWN_FACES_DIR.mkdir(parents=True, exist_ok=True)
INTRUDER_FRAMES_DIR.mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Generate and store RSA keys on app startup."""
    global private_key, public_key
    public_key, private_key = generate_and_store_keys()
    print(f"RSA keys generated: n={private_key['n']}, e={public_key['e']}, d={private_key['d']}")


@app.get("/public-key")
async def get_public_key_endpoint():
    """Return the public key as JSON."""
    return {"public_key": public_key}


@app.post("/authenticate")
async def authenticate(payload: dict):
    """
    Authenticate using RSA-encrypted password hash.
    Expects: {"encrypted_password": "<base64 string of encrypted hash>"}
    """
    if private_key is None:
        raise HTTPException(status_code=500, detail="Authentication failed.")
    
    try:
        # Get the encrypted password from request
        encrypted_password_b64 = payload.get("encrypted_password")
        if not encrypted_password_b64:
            raise HTTPException(status_code=401, detail="Authentication failed.")
        
        # Base64 decode to get the integer bytes
        encrypted_bytes = base64.b64decode(encrypted_password_b64)
        encrypted_int = int.from_bytes(encrypted_bytes, byteorder='big')
        
        # Decrypt using toy RSA
        decrypted_int = decrypt(encrypted_int, private_key)
        
        # The decrypted value should be a hash of the password
        # Verify by hashing the expected password and comparing
        expected_password_hash = hashlib.sha256(EXPECTED_PASSWORD.encode('utf-8')).digest()
        expected_hash_int = int.from_bytes(expected_password_hash[:2], byteorder='big')
        expected_hash_int = expected_hash_int % private_key['n']
        
        # Compare encrypted/decrypted hash
        if decrypted_int == expected_hash_int:
            return {"status": "success", "message": "Authenticated."}
        else:
            raise HTTPException(status_code=401, detail="Authentication failed.")
    
    except HTTPException:
        raise
    except Exception as e:
        # Never expose decryption error details
        print(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed.")


# ===== IMAGE DASHBOARD ENDPOINTS =====

@app.get("/")
async def serve_dashboard():
    """Serve the main security dashboard HTML file."""
    if not HTML_FILE.exists():
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return FileResponse(HTML_FILE, media_type="text/html")


@app.get("/api/resident-images")
async def get_resident_images():
    """Get list of resident images from known_faces directory."""
    try:
        images = []
        valid_extensions = {".jpg", ".jpeg", ".png"}
        
        # Recursively find all image files
        if KNOWN_FACES_DIR.exists():
            for file_path in KNOWN_FACES_DIR.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in valid_extensions:
                    # Return relative path from known_faces
                    relative_path = str(file_path.relative_to(KNOWN_FACES_DIR))
                    images.append(relative_path)
        
        return JSONResponse({"images": sorted(images)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/resident-image/{filename:path}")
async def get_resident_image(filename: str):
    """Serve a specific resident image with path traversal protection."""
    # Reject path traversal attempts
    if ".." in filename or filename.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = KNOWN_FACES_DIR / filename
    
    # Ensure file is within known_faces directory
    try:
        file_path.relative_to(KNOWN_FACES_DIR)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(file_path)


@app.get("/api/intruder-images")
async def get_intruder_images():
    """Get list of intruder images, sorted newest first."""
    try:
        images = []
        
        # Find all JPG files in intruder_frames
        if INTRUDER_FRAMES_DIR.exists():
            for file_path in sorted(INTRUDER_FRAMES_DIR.glob("*.jpg"), reverse=True):
                if file_path.is_file():
                    images.append(file_path.name)
        
        return JSONResponse({"images": images})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/intruder-image/{filename:path}")
async def get_intruder_image(filename: str):
    """Serve a specific intruder image with path traversal protection."""
    # Reject path traversal attempts
    if ".." in filename or filename.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = INTRUDER_FRAMES_DIR / filename
    
    # Ensure file is within intruder_frames directory and is a JPG
    try:
        file_path.relative_to(INTRUDER_FRAMES_DIR)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    if not file_path.exists() or not filename.lower().endswith('.jpg'):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(file_path)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

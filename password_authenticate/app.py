import os
import base64
import json
import hmac
import hashlib
from fastapi import FastAPI, HTTPException
import uvicorn
from password_authenticate.keygen import generate_and_store_keys, decrypt


EXPECTED_PASSWORD = os.getenv("EXPECTED_PASSWORD", "supersecret")
private_key = None
public_key = None

app = FastAPI()


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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

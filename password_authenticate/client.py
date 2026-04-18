import requests
import base64
import hashlib
from password_authenticate.keygen import encrypt

BASE_URL = "http://localhost:8000"

def fetch_public_key():
    """Fetch the public key from the server."""
    response = requests.get(f"{BASE_URL}/public-key")
    response.raise_for_status()
    data = response.json()
    return data["public_key"]

def encrypt_password(public_key_dict, password):
    """Encrypt password using toy RSA public key."""
    # Hash the password first to make it smaller
    password_hash = hashlib.sha256(password.encode('utf-8')).digest()
    
    # Convert first 2 bytes of hash to integer (0-65535)
    password_int = int.from_bytes(password_hash[:2], byteorder='big')
    
    # Ensure message < n by taking modulo
    n = public_key_dict['n']
    message_int = password_int % n
    
    # Encrypt using toy RSA
    encrypted_int = encrypt(message_int, public_key_dict)
    
    # Convert encrypted integer to bytes and then base64
    encrypted_bytes = encrypted_int.to_bytes((encrypted_int.bit_length() + 7) // 8, byteorder='big')
    encrypted_b64 = base64.b64encode(encrypted_bytes).decode()
    
    # Also send the password itself in plaintext (will be encrypted by HTTPS in prod)
    return encrypted_b64, password

def authenticate(encrypted_password_b64):
    """Send encrypted password to authenticate endpoint."""
    payload = {
        "encrypted_password": encrypted_password_b64
    }
    response = requests.post(f"{BASE_URL}/authenticate", json=payload)
    return response

def main():    
    print("=== Cryptiq Authentication Client (Toy RSA) ===\n")
    
    try:
        # Step 1: Fetch public key
        print("1. Fetching public key from server...")
        public_key_dict = fetch_public_key()
        print("Public key received\n")
        print(f"Public Key: {public_key_dict}\n")
        
        # Step 2: Encrypt password
        password = "supersecret"
        print(f"2. Encrypting password: '{password}'")
        encrypted_password_b64, plain_password = encrypt_password(public_key_dict, password)
        print(f"Password encrypted\n")
        print(f"Encrypted Password (base64):\n{encrypted_password_b64}\n")
        
        # Step 3: Authenticate
        print("3. Sending authentication request...")
        response = authenticate(encrypted_password_b64)
        
        print(f"Response Status: {response.status_code}\n")
        print(f"Response Body:\n{response.json()}\n")
        
        if response.status_code == 200:
            print("Authentication successful!")
        else:
            print("Authentication failed!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

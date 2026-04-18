import os
import json
import math


def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b)
    """
    if a == 0:
        return b, 0, 1
    
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    
    return gcd, x, y


def mod_inverse(a, m):
    """
    Compute modular inverse of a mod m using Extended Euclidean Algorithm
    Returns x such that (a * x) mod m = 1
    Raises ValueError if modular inverse does not exist
    """
    gcd, x, y = extended_gcd(a, m)
    
    if gcd != 1:
        raise ValueError(f"Modular inverse does not exist: gcd({a}, {m}) = {gcd}")
    
    # Ensure result is positive
    return (x % m + m) % m


def generate_and_store_keys(p=3, q=5):
    """
    Generate RSA public and private keys from two prime numbers
    
    Args:
        p: First prime number (default: 3)
        q: Second prime number (default: 5)
    
    Returns:
        Tuple of (public_key_dict, private_key_dict)
    
    Saves keys to public_key.json and private_key.json
    """
    # Compute modulus
    n = p * q
    
    # Compute Euler's totient function
    phi = (p - 1) * (q - 1)
    
    # Choose public exponent e
    # Start with e = 3, fallback to e = 5 if gcd(e, phi) != 1
    e = 3
    if math.gcd(e, phi) != 1:
        e = 5
        if math.gcd(e, phi) != 1:
            raise ValueError(f"Cannot find suitable public exponent with phi={phi}")
    
    # Compute private exponent d as modular inverse of e mod phi
    d = mod_inverse(e, phi)
    
    # Create key dictionaries
    public_key = {"e": e, "n": n}
    private_key = {"d": d, "n": n}
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Save public key to JSON
    public_key_path = os.path.join(script_dir, "public_key.json")
    with open(public_key_path, "w") as f:
        json.dump(public_key, f, indent=2)
    
    # Save private key to JSON
    private_key_path = os.path.join(script_dir, "private_key.json")
    with open(private_key_path, "w") as f:
        json.dump(private_key, f, indent=2)
    
    # Print key generation details
    print("=" * 50)
    print("RSA Key Generation (Pure Python Math)")
    print("=" * 50)
    print(f"p (prime 1):           {p}")
    print(f"q (prime 2):           {q}")
    print(f"n (modulus p*q):       {n}")
    print(f"φ(n) (totient):        {phi}")
    print(f"e (public exponent):   {e}")
    print(f"d (private exponent):  {d}")
    print("-" * 50)
    print(f"Public Key:  {public_key}")
    print(f"Private Key: {private_key}")
    print("-" * 50)
    print(f"Keys saved to:")
    print(f"  • {public_key_path}")
    print(f"  • {private_key_path}")
    print("=" * 50)
    
    return public_key, private_key


def encrypt(message_int, public_key):
    """
    Encrypt a message using RSA public key
    
    Args:
        message_int: Integer message (must be < n)
        public_key: Dict with keys 'e' and 'n'
    
    Returns:
        Ciphertext as integer
    """
    e = public_key["e"]
    n = public_key["n"]
    return pow(message_int, e, n)


def decrypt(ciphertext_int, private_key):
    """
    Decrypt a ciphertext using RSA private key
    
    Args:
        ciphertext_int: Integer ciphertext
        private_key: Dict with keys 'd' and 'n'
    
    Returns:
        Decrypted message as integer
    """
    d = private_key["d"]
    n = private_key["n"]
    return pow(ciphertext_int, d, n)


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 48 + "╗")
    print("║" + " Toy RSA Cryptosystem (Pure Python) ".center(48) + "║")
    print("╚" + "=" * 48 + "╝")
    print()
    
    # Step 1: Generate keys
    print("STEP 1: Key Generation")
    print("-" * 50)
    public_key, private_key = generate_and_store_keys()  # Uses default p=10007, q=10009
    
    print()
    print("STEP 2: Encryption/Decryption Test")
    print("-" * 50)
    
    # Test message (must be < n = 15)
    message = 7
    print(f"Original message:  {message}")
    print(f"Constraint:        message < n = {public_key['n']} ✓")
    print()
    
    # Encrypt the message
    ciphertext = encrypt(message, public_key)
    print(f"Encryption:        message^e mod n")
    print(f"                   {message}^{public_key['e']} mod {public_key['n']} = {ciphertext}")
    print()
    
    # Decrypt the ciphertext
    decrypted = decrypt(ciphertext, private_key)
    print(f"Decryption:        ciphertext^d mod n")
    print(f"                   {ciphertext}^{private_key['d']} mod {private_key['n']} = {decrypted}")
    print()
    
    # Verify result
    print("RESULT:")
    print("-" * 50)
    if decrypted == message:
        print(f"SUCCESS! Decrypted message matches original.")
        print(f"  {message} == {decrypted} ✓")
    else:
        print(f"FAILED! Decrypted message does not match.")
        print(f"  {message} != {decrypted} ✗")
    print()

#!/usr/bin/env python3
"""
API Test Script for Quantum Judge Demo Backend
Tests all endpoints without needing curl or manual testing
"""

import requests
import sys

# Configuration
BACKEND_URL = "http://localhost:8001"
JUDGE_PASSWORD = "quantum2026"

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}ℹ {text}{RESET}")

def test_health():
    """Test health endpoint"""
    print_header("1. Testing Health Endpoint")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is online: {data['service']}")
            print(f"  Status: {data['status']}")
            print(f"  Version: {data['version']}")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {BACKEND_URL}")
        print_info("Make sure backend is running: python3 judge_backend.py")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_authentication():
    """Test authentication endpoint"""
    print_header("2. Testing Authentication")
    
    try:
        payload = {"password": JUDGE_PASSWORD}
        response = requests.post(
            f"{BACKEND_URL}/api/authenticate",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "authenticated":
                print_success("Authentication successful")
                print(f"  Token: {data['token']}")
                print(f"  Message: {data['message']}")
                return data['token']
            else:
                print_error(f"Authentication failed: {data.get('message')}")
                return None
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_rsa_attack(token):
    """Test RSA attack endpoint"""
    print_header("3. Testing RSA Attack Endpoint")
    
    if not token:
        print_error("No valid token. Skipping.")
        return False
    
    try:
        payload = {"token": token}
        response = requests.post(
            f"{BACKEND_URL}/api/rsa-attack",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print_success("RSA attack simulation completed")
                metrics = data.get("metrics", {})
                print(f"  Factors found: {metrics.get('factors_found')}")
                print(f"  Private key: {metrics.get('private_key_recovered')}")
                print(f"  Time: {metrics.get('total_time_seconds')}s")
                print(f"  Status: {metrics.get('status')}")
                return True
            else:
                print_error(f"Attack failed: {data.get('message')}")
                return False
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_pq_attack(token):
    """Test post-quantum attack endpoint"""
    print_header("4. Testing Post-Quantum Attack Endpoint")
    
    if not token:
        print_error("No valid token. Skipping.")
        return False
    
    try:
        payload = {"token": token}
        response = requests.post(
            f"{BACKEND_URL}/api/pq-attack",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print_success("Post-quantum defense verified (attack failed as expected)")
                result = data.get("result", {})
                print(f"  Lock status: {result.get('lock_status')}")
                print(f"  Security level: {data.get('security_level')}")
                print(f"  Cryptanalysis: {result.get('cryptanalysis')}")
                
                attempts = data.get("attacks", [])
                print(f"  Attack attempts tested: {len(attempts)}")
                for attempt in attempts:
                    print(f"    - {attempt['method']}: {attempt['result']}")
                return True
            else:
                print_error(f"Test failed: {data.get('message')}")
                return False
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_control_signal(token):
    """Test control signal endpoint"""
    print_header("5. Testing Control Signal Endpoint")
    
    if not token:
        print_error("No valid token. Skipping.")
        return False
    
    try:
        payload = {"token": token, "action": "unlock"}
        response = requests.post(
            f"{BACKEND_URL}/api/send-control-signal",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Control signal endpoint responding")
            print(f"  Status: {data.get('status')}")
            print(f"  Action: {data.get('action')}")
            print(f"  Message: {data.get('message')}")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def run_all_tests():
    """Run all tests"""
    print(f"\n{BLUE}╔════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║  Quantum Judge Demo - API Test Suite                      ║{RESET}")
    print(f"{BLUE}║  Backend URL: {BACKEND_URL:<40}║{RESET}")
    print(f"{BLUE}╚════════════════════════════════════════════════════════════╝{RESET}")
    
    results = {}
    
    # Test 1: Health
    results['health'] = test_health()
    if not results['health']:
        print_error("Cannot reach backend. Stopping tests.")
        return results
    
    # Test 2: Authentication
    token = test_authentication()
    results['auth'] = token is not None
    
    if not token:
        print_error("Authentication failed. Stopping tests.")
        return results
    
    # Test 3-5: Attacks and control
    results['rsa'] = test_rsa_attack(token)
    results['pq'] = test_pq_attack(token)
    results['signal'] = test_control_signal(token)
    
    # Summary
    print_header("Test Summary")
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"  {test_name.upper():<15} ... {status}")
    
    print()
    if all_passed:
        print_success("All tests passed! System is ready for judge demo.")
    else:
        print_error("Some tests failed. Check output above.")
    
    return results

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)

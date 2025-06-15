#!/usr/bin/env python3

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_drug_check():
    """Test the /v1/check endpoint with various scenarios"""
    print("\n=== Testing /v1/check endpoint ===")
    
    # Test 1: Check a drug with known allergies
    print("\nTest 1: Check Amoxil with penicillin allergy")
    payload = {
        "drug": {
            "name": "Amoxil"
        },
        "patient": {
            "allergies": [
                {"name": "Penicillin"}
            ]
        },
        "options": {
            "include_cross_reactivity": True,
            "include_evidence": True
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/check", json=payload)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Drug: {result['drug']['name']}")
            print(f"Safe: {result['safe']}")
            print(f"Contraindications: {len(result['contraindications'])}")
            for c in result['contraindications']:
                print(f"  - {c['name']} ({c['severity']}): {c['description']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 2: Check a drug with no known allergies
    print("\nTest 2: Check Advil with no allergies")
    payload = {
        "drug": {
            "name": "Advil"
        },
        "patient": {
            "allergies": []
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/check", json=payload)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Drug: {result['drug']['name']}")
            print(f"Safe: {result['safe']}")
            print(f"Contraindications: {len(result['contraindications'])}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 3: Check a drug with a condition contraindication
    print("\nTest 3: Check Tetracycline with pregnancy")
    payload = {
        "drug": {
            "name": "Tetracycline"
        },
        "patient": {
            "conditions": [
                {"name": "Pregnancy"}
            ]
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/check", json=payload)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Drug: {result['drug']['name']}")
            print(f"Safe: {result['safe']}")
            print(f"Contraindications: {len(result['contraindications'])}")
            for c in result['contraindications']:
                print(f"  - {c['name']} ({c['severity']}): {c['description']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 4: Check a drug with cross-reactivity
    print("\nTest 4: Check Keflex with penicillin allergy (cross-reactivity)")
    payload = {
        "drug": {
            "name": "Keflex"
        },
        "patient": {
            "allergies": [
                {"name": "Penicillin"}
            ]
        },
        "options": {
            "include_cross_reactivity": True
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/check", json=payload)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Drug: {result['drug']['name']}")
            print(f"Safe: {result['safe']}")
            print(f"Contraindications: {len(result['contraindications'])}")
            for c in result['contraindications']:
                print(f"  - {c['name']} ({c['severity']}): {c['description']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 5: Check a non-existent drug
    print("\nTest 5: Check non-existent drug")
    payload = {
        "drug": {
            "name": "NonExistentDrug123"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/check", json=payload)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

def test_drug_info():
    """Test the /v1/drug/{identifier} endpoint"""
    print("\n=== Testing /v1/drug/{identifier} endpoint ===")
    
    # Test 1: Get info for a known drug by name
    print("\nTest 1: Get info for Amoxil by name")
    try:
        response = requests.get(f"{BASE_URL}/v1/drug/Amoxil")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Drug: {result['drug']['name']}")
            print(f"Generic name: {result['drug']['generic_name']}")
            print(f"Ingredients: {len(result['drug']['ingredients'])}")
            for i in result['drug']['ingredients']:
                print(f"  - {i['name']} ({i['type']})")
            print(f"Contraindications: {len(result['contraindications'])}")
            print(f"Warnings: {len(result['warnings'])}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 2: Get info for a known drug by rxcui
    print("\nTest 2: Get info for a drug by rxcui")
    try:
        response = requests.get(f"{BASE_URL}/v1/drug/723?identifier_type=rxcui")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Drug: {result['drug']['name']}")
            print(f"RxCUI: {result['drug']['rxcui']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 3: Get info for a non-existent drug
    print("\nTest 3: Get info for a non-existent drug")
    try:
        response = requests.get(f"{BASE_URL}/v1/drug/NonExistentDrug123")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

def test_allergy_info():
    """Test the /v1/allergy/{name} endpoint"""
    print("\n=== Testing /v1/allergy/{name} endpoint ===")
    
    # Test 1: Get info for a known allergy
    print("\nTest 1: Get info for Penicillin allergy")
    try:
        response = requests.get(f"{BASE_URL}/v1/allergy/Penicillin")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Allergy: {result['allergy']['name']}")
            print(f"Type: {result['allergy']['type']}")
            print(f"Related ingredients: {len(result['related_ingredients'])}")
            for i in result['related_ingredients']:
                print(f"  - {i['name']} ({i['relationship']})")
            print(f"Related drugs: {len(result['related_drugs'])}")
            print(f"Cross-reactivity: {len(result['cross_reactivity'])}")
            for c in result['cross_reactivity']:
                print(f"  - {c['name']} ({c['evidence_level']}): {c['description']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 2: Get info for a non-existent allergy
    print("\nTest 2: Get info for a non-existent allergy")
    try:
        response = requests.get(f"{BASE_URL}/v1/allergy/NonExistentAllergy123")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

def test_batch_check():
    """Test the /v1/batch/check endpoint"""
    print("\n=== Testing /v1/batch/check endpoint ===")
    
    # Test batch check with multiple drugs and allergies
    print("\nTest: Batch check multiple drugs with allergies")
    payload = {
        "drugs": [
            {"name": "Amoxil"},
            {"name": "Advil"},
            {"name": "Keflex"},
            {"name": "NonExistentDrug123"}
        ],
        "patient": {
            "allergies": [
                {"name": "Penicillin"},
                {"name": "NSAIDs"}
            ],
            "conditions": [
                {"name": "Pregnancy"}
            ]
        },
        "options": {
            "include_cross_reactivity": True
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/v1/batch/check", json=payload)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Results count: {len(result['results'])}")
            for r in result['results']:
                if 'error' in r:
                    print(f"Drug: {r['drug']['name']} - Error: {r['error']}")
                else:
                    print(f"Drug: {r['drug']['name']} - Safe: {r['safe']} - Contraindications: {len(r['contraindications'])}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

def main():
    print("Starting API tests...")
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/v1/drug/Amoxil")
        if response.status_code not in [200, 404]:
            print(f"Warning: API may not be running correctly. Status code: {response.status_code}")
            print("Make sure the API server is running on http://localhost:5000")
            choice = input("Continue with tests anyway? (y/n): ")
            if choice.lower() != 'y':
                sys.exit(1)
    except Exception as e:
        print(f"Error connecting to API: {e}")
        print("Make sure the API server is running on http://localhost:5000")
        sys.exit(1)
    
    # Run tests
    test_drug_check()
    test_drug_info()
    test_allergy_info()
    test_batch_check()
    
    print("\nAll tests completed.")

if __name__ == "__main__":
    main()

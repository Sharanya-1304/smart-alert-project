import requests
import json

try:
    print("Testing http://127.0.0.1:5000/ endpoint...")
    response = requests.get('http://127.0.0.1:5000/', timeout=5)
    print(f"✓ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Welcome page loaded successfully!")
        if "Active Users" in response.text or "active_users" in response.text:
            print("✓ Active users counter is present in the page")
        else:
            print("⚠ Active users counter not found in page content")
    else:
        print(f"✗ Unexpected status code: {response.status_code}")
        print(f"Response text: {response.text[:500]}")
        
except Exception as e:
    print(f"✗ Error testing endpoint: {e}")
    import traceback
    traceback.print_exc()

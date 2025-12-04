#!/usr/bin/env python3
"""
Script untuk test API WhatsApp Reminder
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
FLASK_URL = "http://localhost:5000"
NODE_URL = "http://localhost:3000"

def test_node_api():
    """Test Node.js WhatsApp API directly"""
    print("\n" + "="*50)
    print("🧪 Testing Node.js API")
    print("="*50)
    
    url = f"{NODE_URL}/send"
    payload = {
        "phone": "6285857768760",
        "message": "🧪 Test message from test script"
    }
    
    try:
        print(f"📤 Sending POST to {url}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"📥 Status Code: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Node.js API test PASSED")
            return True
        else:
            print("❌ Node.js API test FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_flask_send_one():
    """Test Flask send_one endpoint"""
    print("\n" + "="*50)
    print("🧪 Testing Flask send_one API")
    print("="*50)
    
    # First, get list of reminders
    try:
        list_url = f"{FLASK_URL}/list?format=json"
        print(f"📤 Getting reminders from {list_url}")
        
        response = requests.get(list_url, timeout=10)
        reminders = response.json()
        
        if not reminders:
            print("⚠️ No reminders found in database")
            print("💡 Add a reminder first via the web interface")
            return False
        
        print(f"📋 Found {len(reminders)} reminders")
        
        # Test send_one with first reminder
        reminder_id = reminders[0]['id']
        send_url = f"{FLASK_URL}/send_one/{reminder_id}"
        
        print(f"📤 Sending POST to {send_url}")
        response = requests.post(send_url, timeout=10)
        
        print(f"📥 Status Code: {response.status_code}")
        print(f"📥 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Flask send_one test PASSED")
            return True
        else:
            print("❌ Flask send_one test FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_automatic_reminders():
    """Test automatic reminder function"""
    print("\n" + "="*50)
    print("🧪 Testing Automatic Reminders Logic")
    print("="*50)
    
    try:
        # Import the function
        import sys
        sys.path.append('.')
        from whatsapp_reminder_app import send_automatic_reminders
        
        print("📤 Calling send_automatic_reminders()...")
        result = send_automatic_reminders()
        
        print(f"📥 Result: {json.dumps(result, indent=2)}")
        
        if result['status'] == 'completed':
            print(f"✅ Automatic reminders test PASSED")
            print(f"   Sent: {result['sent_count']}")
            print(f"   Failed: {result['failed_count']}")
            return True
        else:
            print("❌ Automatic reminders test FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_services():
    """Check if services are running"""
    print("\n" + "="*50)
    print("🔍 Checking Services")
    print("="*50)
    
    services = {
        "Flask (Python)": FLASK_URL,
        "Node.js (WhatsApp)": NODE_URL
    }
    
    all_running = True
    
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 404]:  # 404 is ok, means server is running
                print(f"✅ {name} is running at {url}")
            else:
                print(f"⚠️ {name} returned status {response.status_code}")
                all_running = False
        except Exception as e:
            print(f"❌ {name} is NOT running at {url}")
            print(f"   Error: {str(e)}")
            all_running = False
    
    return all_running

def main():
    print("\n" + "="*60)
    print("🚀 WhatsApp Reminder API Test Suite")
    print("="*60)
    
    # Check services first
    if not check_services():
        print("\n❌ Some services are not running!")
        print("💡 Please start both Flask and Node.js servers first:")
        print("   1. cd wa-bot && node index.js")
        print("   2. python whatsapp_reminder_app.py")
        return
    
    # Run tests
    results = []
    
    results.append(("Node.js API", test_node_api()))
    results.append(("Flask send_one", test_flask_send_one()))
    results.append(("Automatic Reminders", test_automatic_reminders()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n🎯 Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()

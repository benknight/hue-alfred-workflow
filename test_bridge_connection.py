#!/usr/bin/env python3
"""
Hue Bridge Connection Test Script

This script helps test bridge connectivity and diagnose issues.
Run this script from the terminal to test your bridge connection.

Usage: python3 test_bridge_connection.py [bridge_ip]
"""

import sys
import json
import requests
from urllib.parse import urlparse

def test_discovery():
    """Test the Hue discovery service"""
    print("Testing Hue bridge discovery...")
    try:
        r = requests.get('https://discovery.meethue.com', timeout=5)
        r.raise_for_status()
        bridges = r.json()
        
        if not isinstance(bridges, list):
            print(f"❌ Discovery returned unexpected format: {type(bridges)}")
            return None
            
        if len(bridges) == 0:
            print("❌ No bridges found via discovery service")
            return None
            
        print(f"✅ Found {len(bridges)} bridge(s):")
        for i, bridge in enumerate(bridges):
            if isinstance(bridge, dict):
                ip = bridge.get('internalipaddress', 'Unknown IP')
                bridge_id = bridge.get('id', 'Unknown ID')
                print(f"  Bridge {i+1}: {ip} (ID: {bridge_id})")
            else:
                print(f"  Bridge {i+1}: Invalid format - {bridge}")
                
        return bridges[0].get('internalipaddress') if bridges and isinstance(bridges[0], dict) else None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Discovery failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Discovery error: {e}")
        return None

def test_bridge_connection(bridge_ip):
    """Test connection to a specific bridge"""
    print(f"\nTesting connection to bridge at {bridge_ip}...")
    
    # Test basic connectivity
    try:
        r = requests.get(f'http://{bridge_ip}/api/config', timeout=5)
        r.raise_for_status()
        print("✅ Bridge is reachable")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot reach bridge: {e}")
        return False
    
    # Test API response format
    try:
        data = r.json()
        print(f"✅ Bridge returns valid JSON")
        
        if isinstance(data, list):
            print("ℹ️  Bridge returns responses as lists")
            if len(data) > 0 and isinstance(data[0], dict):
                if 'error' in data[0]:
                    error = data[0]['error']
                    print(f"❌ Bridge returned error: {error.get('description', 'Unknown')}")
                    if error.get('type') == 1:
                        print("   This is normal - you need to create a user account")
                else:
                    print("✅ List format response looks valid")
        elif isinstance(data, dict):
            print("ℹ️  Bridge returns responses as dictionaries")
            if 'name' in data:
                print(f"   Bridge name: {data['name']}")
            if 'modelid' in data:
                print(f"   Bridge model: {data['modelid']}")
            if 'bridgeid' in data:
                print(f"   Bridge ID: {data['bridgeid']}")
        else:
            print(f"❌ Unexpected response format: {type(data)}")
            
    except ValueError as e:
        print(f"❌ Bridge returned invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error processing response: {e}")
        return False
        
    return True

def test_user_creation(bridge_ip):
    """Test creating a new user (requires button press)"""
    print(f"\nTesting user creation (you have 30 seconds to press the bridge button)...")
    print("Press the button on your Hue bridge NOW, then press Enter to continue...")
    input()
    
    try:
        payload = {'devicetype': 'Hue Bridge Test Script'}
        r = requests.post(f'http://{bridge_ip}/api', 
                         data=json.dumps(payload), 
                         headers={'Content-Type': 'application/json'},
                         timeout=5)
        r.raise_for_status()
        
        response = r.json()
        print(f"Raw response: {response}")
        
        # Handle different response formats
        if isinstance(response, list) and len(response) > 0:
            resp = response[0]
        elif isinstance(response, dict):
            resp = response
        else:
            print(f"❌ Unexpected response format: {type(response)}")
            return None
            
        if 'error' in resp:
            error = resp['error']
            if error.get('type') == 101:
                print("❌ Button not pressed in time. Try again!")
            else:
                print(f"❌ Error: {error.get('description', 'Unknown error')}")
            return None
        elif 'success' in resp:
            username = resp['success']['username']
            print(f"✅ Success! Created user: {username}")
            return username
        else:
            print(f"❌ Unexpected response structure: {resp}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_full_state(bridge_ip, username):
    """Test getting full bridge state"""
    print(f"\nTesting full state retrieval...")
    
    try:
        r = requests.get(f'http://{bridge_ip}/api/{username}', timeout=5)
        r.raise_for_status()
        
        data = r.json()
        
        # Handle different response formats
        if isinstance(data, list):
            print("ℹ️  Bridge returned list format")
            if len(data) > 0 and isinstance(data[0], dict) and 'error' in data[0]:
                print(f"❌ Error: {data[0]['error'].get('description', 'Unknown')}")
                return False
            elif len(data) > 0:
                data = data[0]  # Use first element
            else:
                print("❌ Empty response")
                return False
                
        if not isinstance(data, dict):
            print(f"❌ Unexpected data format: {type(data)}")
            return False
            
        # Check required keys
        required_keys = ['lights', 'groups', 'config']
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            print(f"⚠️  Missing keys: {missing_keys}")
            print(f"   Available keys: {list(data.keys())}")
        else:
            print("✅ All required keys present")
            
        # Check lights
        if 'lights' in data:
            lights = data['lights']
            if isinstance(lights, dict):
                print(f"✅ Found {len(lights)} lights")
                for lid, light in list(lights.items())[:3]:  # Show first 3
                    name = light.get('name', 'Unknown')
                    state = light.get('state', {})
                    on_state = state.get('on', 'Unknown')
                    print(f"   Light {lid}: {name} (on: {on_state})")
            else:
                print(f"❌ Lights data is not a dictionary: {type(lights)}")
                
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("Hue Bridge Connection Test")
    print("=" * 30)
    
    # Get bridge IP
    bridge_ip = None
    if len(sys.argv) > 1:
        bridge_ip = sys.argv[1]
        print(f"Using provided bridge IP: {bridge_ip}")
    else:
        bridge_ip = test_discovery()
        
    if not bridge_ip:
        print("\n❌ No bridge IP available. Please provide one as argument:")
        print("   python3 test_bridge_connection.py 192.168.1.100")
        return
        
    # Test basic connection
    if not test_bridge_connection(bridge_ip):
        print("\n❌ Bridge connection failed. Check IP address and network.")
        return
        
    # Test user creation
    username = test_user_creation(bridge_ip)
    if not username:
        print("\n❌ User creation failed. The workflow setup will also fail.")
        return
        
    # Test full state
    if test_full_state(bridge_ip, username):
        print("\n✅ All tests passed! Your bridge should work with the Alfred workflow.")
        print(f"   Bridge IP: {bridge_ip}")
        print(f"   Username: {username}")
    else:
        print("\n❌ Full state test failed. There may be compatibility issues.")
        
    print(f"\nTo set up the Alfred workflow manually:")
    print(f"1. In Alfred, type: hue {bridge_ip}")
    print(f"2. Press the bridge button when prompted")
    print(f"3. Complete the setup")

if __name__ == "__main__":
    main()
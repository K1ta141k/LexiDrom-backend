#!/usr/bin/env python3
"""
Test runner for Random Text API
Simple script to run tests and check API functionality
"""

import asyncio
import httpx
import json
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Test configuration
BASE_URL = "http://localhost:8000"
RANDOM_TEXT_BASE = f"{BASE_URL}/random-text"

async def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{RANDOM_TEXT_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

async def test_dataset_info():
    """Test the dataset info endpoint"""
    print("🔍 Testing dataset info...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{RANDOM_TEXT_BASE}/info")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Dataset info: {data}")
                return True
            else:
                print(f"❌ Dataset info failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Dataset info error: {e}")
        return False

async def test_random_text():
    """Test the random text endpoint"""
    print("🔍 Testing random text...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{RANDOM_TEXT_BASE}/random")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Random text retrieved:")
                print(f"   Length: {data['length']} characters")
                print(f"   Source: {data['source']}")
                print(f"   ID: {data['id']}")
                print(f"   Text preview: {data['text'][:100]}...")
                return True
            else:
                print(f"❌ Random text failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Random text error: {e}")
        return False

async def test_random_text_with_constraints():
    """Test random text with length constraints"""
    print("🔍 Testing random text with constraints...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{RANDOM_TEXT_BASE}/random?min_length=200&max_length=500")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Constrained random text:")
                print(f"   Length: {data['length']} characters (should be 200-500)")
                print(f"   Text preview: {data['text'][:100]}...")
                return True
            else:
                print(f"❌ Constrained random text failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Constrained random text error: {e}")
        return False

async def test_multiple_random_texts():
    """Test multiple random texts endpoint"""
    print("🔍 Testing multiple random texts...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{RANDOM_TEXT_BASE}/random-multiple?count=3")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Multiple random texts retrieved:")
                print(f"   Total count: {data['total_count']}")
                for i, text in enumerate(data['texts']):
                    print(f"   Text {i+1}: {text['length']} chars, source: {text['source']}")
                return True
            else:
                print(f"❌ Multiple random texts failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Multiple random texts error: {e}")
        return False

async def test_error_handling():
    """Test error handling"""
    print("🔍 Testing error handling...")
    try:
        async with httpx.AsyncClient() as client:
            # Test with invalid count
            response = await client.get(f"{RANDOM_TEXT_BASE}/random-multiple?count=0")
            if response.status_code == 200:  # API should handle gracefully
                print("✅ Error handling test passed")
                return True
            else:
                print(f"❌ Error handling test failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error handling test error: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Random Text API Tests...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Dataset Info", test_dataset_info),
        ("Random Text", test_random_text),
        ("Random Text with Constraints", test_random_text_with_constraints),
        ("Multiple Random Texts", test_multiple_random_texts),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Random Text API is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the API implementation.")
        return False

def main():
    """Main function"""
    try:
        result = asyncio.run(run_all_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test runner error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
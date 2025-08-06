"""
Real API Connection Check

This script checks if the Keywords AI API server is accessible and provides
guidance on running real API tests.
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv
load_dotenv(override=True)

async def check_api_connection():
    """Check if the API server is accessible"""
    
    api_key = os.getenv("KEYWORDSAI_API_KEY")
    base_url = os.getenv("KEYWORDSAI_BASE_URL", "http://localhost:8000")
    
    print("🔍 Keywords AI API Connection Check")
    print("=" * 50)
    print(f"API Key: {api_key[:10]}..." if api_key else "❌ No API key found")
    print(f"Base URL: {base_url}")
    print()
    
    if not api_key:
        print("❌ KEYWORDSAI_API_KEY not found in environment")
        print("   Please check your .env file")
        return False
    
    # Test basic connectivity
    try:
        print("🔗 Testing basic connectivity...")
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base_url.rstrip('/')}/")
            print(f"✅ Server responded with status: {response.status_code}")
            
            # Test evaluators endpoint
            print("🧪 Testing evaluators endpoint...")
            headers = {"Authorization": f"Bearer {api_key}"}
            eval_response = await client.get(
                f"{base_url.rstrip('/')}/evaluators/",
                headers=headers
            )
            print(f"✅ Evaluators endpoint responded with status: {eval_response.status_code}")
            
            if eval_response.status_code == 200:
                data = eval_response.json()
                if 'results' in data:
                    print(f"📊 Found {len(data['results'])} evaluators")
                    if data['results']:
                        print(f"   First evaluator: {data['results'][0].get('name', 'Unknown')}")
                
            return True
            
    except httpx.ConnectError as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("💡 Possible solutions:")
        print("   1. Make sure the Keywords AI server is running")
        print("   2. Check if the base URL is correct in .env")
        print("   3. Verify network connectivity")
        print("   4. Check if the server is running on a different port")
        return False
        
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP error: {e.response.status_code} - {e.response.text}")
        if e.response.status_code == 401:
            print("   This might be an authentication issue")
        elif e.response.status_code == 404:
            print("   The endpoint might not exist or the URL might be wrong")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main function"""
    result = asyncio.run(check_api_connection())
    
    print()
    if result:
        print("🎉 API connection successful!")
        print("   You can now run real API tests with:")
        print("   python -m pytest tests/test_keywords_ai_api_integration.py -v -s")
    else:
        print("🚫 API connection failed")
        print("   Real API tests will not work until the connection is established")
        print("   You can still run mock tests with:")
        print("   python -m pytest tests/ -k 'not test_keywords_ai_api_integration' -v")


if __name__ == "__main__":
    main()
"""
Test client for the LLM Code Deployment API
Run this to test your deployment locally
"""
import asyncio
import httpx
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config


async def test_round_1():
    """Test Round 1: Build and deploy"""
    print("=" * 60)
    print("Testing Round 1: Build and Deploy")
    print("=" * 60)
    
    request_data = {
        "email": "test@example.com",
        "secret": config.STUDENT_SECRET,
        "task": "test-task-001",
        "round": 1,
        "nonce": "test-nonce-abc123",
        "brief": "Create a simple web page that displays 'Hello World' with a modern design. Add a button that changes the text color when clicked.",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "Page displays 'Hello World'",
            "Page has a button that changes color"
        ],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": []
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print("\n📤 Sending Round 1 request...")
            response = await client.post(
                "http://localhost:7860/request",
                json=request_data
            )
            
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print("\n⏳ Processing in background... Check logs for progress")
                print("\n💡 Check status with:")
                print(f"   curl http://localhost:7860/status/{request_data['task']}")
                
                # Wait a bit and check status
                print("\n⏳ Waiting 5 seconds before checking status...")
                await asyncio.sleep(5)
                
                status_response = await client.get(
                    f"http://localhost:7860/status/{request_data['task']}"
                )
                print(f"\n📊 Current Status:")
                print(json.dumps(status_response.json(), indent=2))
            
        except Exception as e:
            print(f"❌ Error: {e}")


async def test_round_2():
    """Test Round 2: Revision"""
    print("\n" + "=" * 60)
    print("Testing Round 2: Revision")
    print("=" * 60)
    
    request_data = {
        "email": "test@example.com",
        "secret": config.STUDENT_SECRET,
        "task": "test-task-001",
        "round": 2,
        "nonce": "test-nonce-xyz789",
        "brief": "Update the page to also display the current date and time. Add a refresh button to update the time.",
        "checks": [
            "README.md updated with new features",
            "Page displays current date and time",
            "Page has refresh button"
        ],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": []
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print("\n📤 Sending Round 2 request...")
            response = await client.post(
                "http://localhost:7860/request",
                json=request_data
            )
            
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print("\n⏳ Processing in background... Check logs for progress")
                
        except Exception as e:
            print(f"❌ Error: {e}")


async def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:7860/")
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("\n💡 Make sure the server is running:")
            print("   python -m src.main")


async def main():
    """Run all tests"""
    print("\n🚀 LLM Code Deployment API - Test Client\n")
    
    # Test health
    await test_health()
    
    print("\n" + "=" * 60)
    choice = input("\nRun Round 1 test? (y/n): ").strip().lower()
    if choice == 'y':
        await test_round_1()
    
    print("\n" + "=" * 60)
    choice = input("\nRun Round 2 test? (requires Round 1 to be completed) (y/n): ").strip().lower()
    if choice == 'y':
        await test_round_2()
    
    print("\n" + "=" * 60)
    print("✅ Testing complete!")
    print("\n💡 Tips:")
    print("   - Check the console logs of main.py for detailed progress")
    print("   - Check your GitHub account for new repositories")
    print("   - Visit the GitHub Pages URL to see the deployed app")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

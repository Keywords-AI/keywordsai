"""
Respan Prompt API Workflow Example

This example demonstrates how to use the PromptAPI to:
1. Create a new prompt
2. Create versions with different configurations
3. List and retrieve prompts and versions
4. Update prompt and version properties
5. Clean up resources

This follows the testing strategy of using real API calls for demonstration.
"""

from dotenv import load_dotenv

load_dotenv(override=True)


import asyncio
import os
from datetime import datetime, timezone
from respan.prompts.api import PromptAPI
from respan_sdk.respan_types.prompt_types import Prompt, PromptVersion


async def prompt_workflow_example():
    """
    Comprehensive example of prompt management workflow.

    This example shows both synchronous and asynchronous usage patterns.
    """

    # Initialize the API client using dotenv
    api_key = os.getenv("RESPAN_API_KEY")
    base_url = os.getenv("RESPAN_BASE_URL")
    
    if not api_key or not base_url:
        print("❌ Missing environment variables!")
        print("Please set RESPAN_API_KEY and RESPAN_BASE_URL in your .env file")
        return

    client = PromptAPI(api_key=api_key, base_url=base_url)

    print("🚀 Respan Prompt API Workflow Example")
    print("=" * 50)
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else api_key}")
    print(f"🌐 Base URL: {base_url}")
    print(f"🔗 Full URL will be: {base_url.rstrip('/')}/api/prompts")

    try:
        # Step 1: Create a new prompt
        print("\n📝 Step 1: Creating a new prompt...")
        prompt = await client.acreate()
        print(f"✅ Created prompt with ID: {prompt.prompt_id}")
        print(f"   Name: {prompt.name}")
        print(f"   Description: {prompt.description}")
        print(f"🔍 JSON Response: {prompt.model_dump_json(indent=2)}")

        # Step 2: Update the prompt with meaningful information
        print("\n✏️  Step 2: Updating prompt metadata...")
        updated_prompt_data = Prompt(
            name="Customer Support Assistant",
            description="AI assistant for handling customer support inquiries with professional tone",
            prompt_id=prompt.prompt_id,  # Include the required prompt_id
        )
        updated_prompt = await client.aupdate(prompt.prompt_id, updated_prompt_data)
        print(f"✅ Updated prompt: {updated_prompt.name}")
        print(f"🔍 JSON Response: {updated_prompt.model_dump_json(indent=2)}")

        # Step 3: Create a prompt version with specific configuration
        print("\n🔧 Step 3: Creating a prompt version...")
        version_data = PromptVersion(
            prompt_version_id="version-001",
            description="Initial customer support version with professional tone",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            version=1,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional customer support assistant. Always be helpful, polite, and provide clear solutions to customer problems.",
                },
                {"role": "user", "content": "{{customer_inquiry}}"},
            ],
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=2048,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            variables={"customer_inquiry": "Customer's question or issue"},
            parent_prompt=prompt.prompt_id,
        )

        version = await client.acreate_version(prompt.prompt_id, version_data)
        print(f"✅ Created version {version.version}")
        print(f"   Model: {version.model}")
        print(f"   Temperature: {version.temperature}")
        print(f"   Messages: {len(version.messages)} messages")
        print(f"🔍 JSON Response: {version.model_dump_json(indent=2)}")

        # Step 4: Create another version with different settings
        print("\n🔧 Step 4: Creating a second version with different settings...")
        version_data_v2 = PromptVersion(
            prompt_version_id="version-002",
            description="More creative version with higher temperature",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            version=2,
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly and creative customer support assistant. Use a warm, conversational tone while solving customer problems efficiently.",
                },
                {"role": "user", "content": "{{customer_inquiry}}"},
            ],
            model="gpt-4o-mini",
            temperature=0.9,
            max_tokens=1500,
            top_p=0.95,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            variables={"customer_inquiry": "Customer's question or issue"},
            parent_prompt=prompt.prompt_id,
        )

        version_v2 = await client.acreate_version(prompt.prompt_id, version_data_v2)
        print(f"✅ Created version {version_v2.version}")
        print(f"   Model: {version_v2.model}")
        print(f"   Temperature: {version_v2.temperature}")

        # Step 5: List all prompts
        print("\n📋 Step 5: Listing all prompts...")
        prompts_list = await client.alist(page_size=5)
        print(f"✅ Found {prompts_list.count} total prompts")
        for p in prompts_list.results[:3]:  # Show first 3
            print(f"   - {p.name} (ID: {p.prompt_id})")

        # Step 6: List versions for our prompt
        print(f"\n📋 Step 6: Listing versions for prompt {prompt.prompt_id}...")
        versions_list = await client.alist_versions(prompt.prompt_id)
        print(f"✅ Found {versions_list.count} versions")
        for v in versions_list.results:
            print(f"   - Version {v.version}: {v.description}")
            print(f"     Model: {v.model}, Temperature: {v.temperature}")

        # Step 7: Retrieve a specific version
        print(f"\n🔍 Step 7: Retrieving version 1 details...")
        retrieved_version = await client.aget_version(prompt.prompt_id, 1)  # Get version 1
        print(f"✅ Retrieved version {retrieved_version.version}")
        print(f"   Description: {retrieved_version.description}")
        print(f"   Variables: {retrieved_version.variables}")
        print(f"   Readonly: {retrieved_version.readonly}")

        # Step 8: Update a version (skip if readonly)
        if retrieved_version.readonly:
            print(f"\n⚠️  Step 8: Skipping version update - version {retrieved_version.version} is readonly")
            print("   This is expected behavior - versions may become readonly after creation")
        else:
            print(f"\n✏️  Step 8: Updating version 1...")
            # Only send the fields we want to update, not a full PromptVersion object
            update_version_data = {
                "description": "Updated: Professional customer support with improved clarity",
                "temperature": 0.6,  # Slightly lower temperature
                "max_tokens": 2500,  # More tokens
            }
            updated_version = await client.aupdate_version(
                prompt.prompt_id, 1, update_version_data
            )
            print(f"✅ Updated version {updated_version.version}")
            print(f"   New description: {updated_version.description}")
            print(f"   New temperature: {updated_version.temperature}")
            print(f"   New max_tokens: {updated_version.max_tokens}")
            print(f"🔍 JSON Response: {updated_version.model_dump_json(indent=2)}")

        # Step 9: Demonstrate synchronous API usage
        print("\n🔄 Step 9: Demonstrating synchronous API usage...")
        sync_prompts = client.list(page_size=3)  # No await needed
        print(f"✅ Synchronously retrieved {len(sync_prompts.results)} prompts")

        # Step 10: Get the updated prompt details
        print(f"\n🔍 Step 10: Getting final prompt details...")
        final_prompt = await client.aget(prompt.prompt_id)
        print(f"✅ Final prompt state:")
        print(f"   Name: {final_prompt.name}")
        print(f"   Versions: {final_prompt.commit_count}")
        print(f"   Starred: {final_prompt.starred}")

        print("\n✨ Workflow completed successfully!")
        print("\n💡 Next steps:")
        print("   - Use the prompt versions in your applications")
        print("   - Test different configurations for optimal results")
        print("   - Monitor performance and iterate on prompt designs")

        # Note: In a real scenario, you might want to clean up test resources
        # print(f"\n🧹 Cleaning up: Deleting test prompt...")
        # await client.adelete(prompt.prompt_id)
        # print("✅ Cleanup completed")

    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Try to get more details about the HTTP error
        if hasattr(e, 'response'):
            print(f"📊 HTTP Status: {e.response.status_code}")
            print(f"📋 Response Headers: {dict(e.response.headers)}")
            try:
                response_text = e.response.text
                print(f"📄 Response Body: {response_text}")
                
                # Try to parse as JSON for better formatting
                try:
                    import json
                    response_json = e.response.json()
                    print(f"🔍 Response JSON (formatted):")
                    print(json.dumps(response_json, indent=2))
                except:
                    pass
            except:
                print("📄 Could not read response body")
        
        # Print request details if available
        if hasattr(e, 'request'):
            print(f"🔗 Request URL: {e.request.url}")
            print(f"📤 Request Method: {e.request.method}")
            if hasattr(e.request, 'content') and e.request.content:
                try:
                    print(f"📤 Request Body: {e.request.content.decode()}")
                except:
                    print("📤 Request Body: (could not decode)")
        
        print("💡 Make sure you have:")
        print("   - Valid API key")
        print("   - Correct base URL")
        print("   - Respan server running (if using local)")


def sync_prompt_example():
    """
    Example using only synchronous methods.
    """
    print("\n🔄 Synchronous Prompt API Example")
    print("=" * 40)

    # Initialize client using dotenv
    api_key = os.getenv("RESPAN_API_KEY")
    base_url = os.getenv("RESPAN_BASE_URL")
    
    if not api_key or not base_url:
        print("❌ Missing environment variables!")
        print("Please set RESPAN_API_KEY and RESPAN_BASE_URL in your .env file")
        return
        
    client = PromptAPI(api_key=api_key, base_url=base_url)

    try:
        # Create prompt (sync)
        prompt = client.create()
        print(f"✅ Created prompt: {prompt.prompt_id}")
        print(f"🔍 JSON Response: {prompt.model_dump_json(indent=2)}")

        # List prompts (sync)
        prompts = client.list(page_size=5)
        print(f"✅ Listed {len(prompts.results)} prompts")
        print(f"🔍 JSON Response: {prompts.model_dump_json(indent=2)}")

        # Get prompt details (sync)
        details = client.get(prompt.prompt_id)
        print(f"✅ Retrieved prompt: {details.name}")
        print(f"🔍 JSON Response: {details.model_dump_json(indent=2)}")

        print("✅ Synchronous example completed!")

    except Exception as e:
        print(f"❌ Sync error: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Try to get more details about the HTTP error
        if hasattr(e, 'response'):
            print(f"📊 HTTP Status: {e.response.status_code}")
            try:
                response_text = e.response.text
                print(f"📄 Response Body: {response_text}")
                
                # Try to parse as JSON for better formatting
                try:
                    import json
                    response_json = e.response.json()
                    print(f"🔍 Response JSON (formatted):")
                    print(json.dumps(response_json, indent=2))
                except:
                    pass
            except:
                print("📄 Could not read response body")


if __name__ == "__main__":
    print("Respan Prompt API Examples")
    print("================================")
    print()
    print("This example demonstrates the Respan Prompt API.")
    print("Please update the API key and base URL before running.")
    print()

    # Run async example
    asyncio.run(prompt_workflow_example())

    print("\n" + "=" * 50)

    # Run sync example
    sync_prompt_example()

    print("\n🎉 All examples completed!")
    print("\nFor more information, check out:")
    print("- Respan Documentation: https://docs.respan.ai")
    print("- API Reference: https://docs.respan.ai/api")
    print("- Testing Guide: https://github.com/Repsan/respan/blob/main/python-sdks/respan/TESTING_STRATEGY.md")
